from django.core.exceptions import ValidationError
from django.db import models


class Plantao(models.Model):
    """Um dos 4 plantões do setor (2 diurnos + 2 noturnos)."""

    class Turno(models.TextChoices):
        DIURNO = "diurno", "Diurno"
        NOTURNO = "noturno", "Noturno"

    nome = models.CharField(max_length=50)
    turno = models.CharField(max_length=10, choices=Turno.choices)

    class Meta:
        verbose_name = "Plantão"
        verbose_name_plural = "Plantões"
        ordering = ["turno", "nome"]

    def __str__(self):
        return self.nome


class Posto(models.Model):
    """Pátio, Central de rádio ou Serviço de rua."""

    class Tipo(models.TextChoices):
        PATIO = "patio", "Pátio"
        CENTRAL = "central", "Central de rádio"
        OPERACIONAL = "operacional", "Serviço de rua"

    nome = models.CharField(max_length=20, choices=Tipo.choices, unique=True)

    class Meta:
        verbose_name = "Posto"
        verbose_name_plural = "Postos"

    def __str__(self):
        return self.get_nome_display()


class PostoPlantaoCapacidade(models.Model):
    """Quantas pessoas cobrem um posto específico em um plantão específico.

    Ex.: Central de rádio + Diurno A = 2; Central de rádio + Noturno A = 1.
    Fica em tabela em vez de fixo no código para poder ajustar sem migração.
    """

    posto = models.ForeignKey(Posto, on_delete=models.CASCADE, related_name="capacidades")
    plantao = models.ForeignKey(Plantao, on_delete=models.CASCADE, related_name="capacidades")
    capacidade = models.PositiveSmallIntegerField(
        help_text="Quantas pessoas cobrem esse posto nesse plantão ao mesmo tempo"
    )

    class Meta:
        verbose_name = "Capacidade de posto por plantão"
        verbose_name_plural = "Capacidades de posto por plantão"
        constraints = [
            models.UniqueConstraint(fields=["posto", "plantao"], name="unica_capacidade_posto_plantao")
        ]

    def __str__(self):
        return f"{self.posto} · {self.plantao}: {self.capacidade}"


class Funcionario(models.Model):
    nome = models.CharField(max_length=150)
    data_registro_funcional = models.DateField(help_text="Define a antiguidade para fins de desempate")
    plantao = models.ForeignKey(Plantao, on_delete=models.PROTECT, related_name="funcionarios")
    posto_atual = models.ForeignKey(Posto, on_delete=models.PROTECT, related_name="funcionarios")
    habilitado_central = models.BooleanField(
        default=False, verbose_name="Habilitado para Central de rádio"
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"
        ordering = ["data_registro_funcional"]

    def __str__(self):
        return self.nome


class CicloFerias(models.Model):
    """Representa um ano/ciclo de férias, com os parâmetros de negócio daquele ano."""

    class Status(models.TextChoices):
        ABERTO = "aberto", "Aberto"
        FECHADO = "fechado", "Fechado"

    ano = models.PositiveSmallIntegerField(unique=True)
    meses_disponiveis = models.JSONField(
        default=list,
        help_text="Lista dos meses (1-12) disponíveis para escolha. Padrão: março a dezembro.",
    )
    teto_mensal_setor = models.PositiveSmallIntegerField(
        default=6, help_text="Máximo de pessoas de férias por mês, somando o setor inteiro"
    )
    minimo_habilitados_central = models.PositiveSmallIntegerField(
        default=6, help_text="Mínimo de funcionários habilitados para a Central de rádio disponíveis por mês"
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ABERTO)
    data_formalizacao = models.DateTimeField(null=True, blank=True)
    formalizado_por = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ciclos_formalizados",
    )

    class Meta:
        verbose_name = "Ciclo de férias"
        verbose_name_plural = "Ciclos de férias"
        ordering = ["-ano"]

    def __str__(self):
        return f"Ciclo {self.ano}"


class HistoricoFerias(models.Model):
    """Mês de férias que o funcionário já tirou em um ano — alimenta o bloqueio dos últimos 2 anos."""

    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name="historico_ferias")
    ano = models.PositiveSmallIntegerField()
    mes = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = "Histórico de férias"
        verbose_name_plural = "Históricos de férias"
        constraints = [
            models.UniqueConstraint(fields=["funcionario", "ano"], name="unico_historico_funcionario_ano")
        ]
        ordering = ["-ano"]

    def __str__(self):
        return f"{self.funcionario} — {self.mes}/{self.ano}"


class PreferenciaFerias(models.Model):
    """As 3 opções de mês que o funcionário escolheu, em ordem de preferência, para um ciclo."""

    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name="preferencias")
    ciclo = models.ForeignKey(CicloFerias, on_delete=models.CASCADE, related_name="preferencias")
    mes_1 = models.PositiveSmallIntegerField(verbose_name="1ª opção")
    mes_2 = models.PositiveSmallIntegerField(verbose_name="2ª opção")
    mes_3 = models.PositiveSmallIntegerField(verbose_name="3ª opção")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Preferência de férias"
        verbose_name_plural = "Preferências de férias"
        constraints = [
            models.UniqueConstraint(fields=["funcionario", "ciclo"], name="unica_preferencia_funcionario_ciclo")
        ]

    def __str__(self):
        return f"{self.funcionario} — ciclo {self.ciclo.ano}"


class AlocacaoFerias(models.Model):
    """Resultado final: o mês alocado para o funcionário naquele ciclo, e como se chegou lá."""

    class Status(models.TextChoices):
        AUTO = "auto", "Auto-alocado"
        OPERADOR = "operador", "Decidido pelo operador"
        PENDENTE = "pendente", "Pendente"

    class Motivo(models.TextChoices):
        POSTO = "posto", "Conflito de posto"
        TETO_SETOR = "teto_setor", "Teto do setor"
        HABILITADOS = "habilitados", "Mínimo de habilitados"
        OUTRO = "outro", "Outro"

    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name="alocacoes")
    ciclo = models.ForeignKey(CicloFerias, on_delete=models.CASCADE, related_name="alocacoes")
    mes_alocado = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDENTE)
    motivo = models.CharField(max_length=15, choices=Motivo.choices, null=True, blank=True)
    observacao = models.TextField(
        blank=True, help_text="Obrigatório quando o status é 'Decidido pelo operador'"
    )
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Alocação de férias"
        verbose_name_plural = "Alocações de férias"
        constraints = [
            models.UniqueConstraint(fields=["funcionario", "ciclo"], name="unica_alocacao_funcionario_ciclo")
        ]

    def clean(self):
        if self.status == self.Status.OPERADOR and not self.observacao.strip():
            raise ValidationError(
                {"observacao": "A observação é obrigatória quando a alocação é decidida pelo operador."}
            )

    def __str__(self):
        return f"{self.funcionario} — ciclo {self.ciclo.ano}"
