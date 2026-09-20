from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

NOME_GRUPO = "Operador de Escala"

PERMISSOES_POR_MODEL = {
    "cicloferias": ["add", "change", "view"],
    "preferenciaferias": ["change", "view"],
    "alocacaoferias": ["change", "view"],
    "historicoferias": ["add", "change", "view"],
    "funcionario": ["view"],
    "plantao": ["view"],
    "posto": ["view"],
    "postoplantaocapacidade": ["view"],
}


class Command(BaseCommand):
    help = (
        "Cria (ou atualiza) o grupo 'Operador de Escala' com as permissões "
        "definidas na especificação. Rode depois do migrate."
    )

    def handle(self, *args, **options):
        grupo, criado = Group.objects.get_or_create(name=NOME_GRUPO)

        total = 0
        for model_name, acoes in PERMISSOES_POR_MODEL.items():
            for acao in acoes:
                codename = f"{acao}_{model_name}"
                try:
                    permissao = Permission.objects.get(
                        codename=codename, content_type__app_label="ferias"
                    )
                except Permission.DoesNotExist:
                    self.stderr.write(
                        self.style.WARNING(f"Permissão '{codename}' não encontrada — pulando.")
                    )
                    continue
                grupo.permissions.add(permissao)
                total += 1

        acao_texto = "criado" if criado else "atualizado"
        self.stdout.write(
            self.style.SUCCESS(f"Grupo '{NOME_GRUPO}' {acao_texto} com {total} permissões.")
        )
