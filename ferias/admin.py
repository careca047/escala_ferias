from django.contrib import admin

from .models import (
    AlocacaoFerias,
    CicloFerias,
    Funcionario,
    HistoricoFerias,
    Plantao,
    Posto,
    PostoPlantaoCapacidade,
    PreferenciaFerias,
)


@admin.register(Plantao)
class PlantaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "turno")
    list_filter = ("turno",)


@admin.register(Posto)
class PostoAdmin(admin.ModelAdmin):
    list_display = ("nome",)


@admin.register(PostoPlantaoCapacidade)
class PostoPlantaoCapacidadeAdmin(admin.ModelAdmin):
    list_display = ("posto", "plantao", "capacidade")
    list_filter = ("posto", "plantao")


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "plantao",
        "posto_atual",
        "habilitado_central",
        "data_registro_funcional",
        "ativo",
    )
    list_filter = ("plantao", "posto_atual", "habilitado_central", "ativo")
    search_fields = ("nome",)
    ordering = ("data_registro_funcional",)


@admin.register(CicloFerias)
class CicloFeriasAdmin(admin.ModelAdmin):
    list_display = (
        "ano",
        "status",
        "teto_mensal_setor",
        "minimo_habilitados_central",
        "data_formalizacao",
    )
    list_filter = ("status",)


@admin.register(HistoricoFerias)
class HistoricoFeriasAdmin(admin.ModelAdmin):
    list_display = ("funcionario", "ano", "mes")
    list_filter = ("ano",)
    search_fields = ("funcionario__nome",)


@admin.register(PreferenciaFerias)
class PreferenciaFeriasAdmin(admin.ModelAdmin):
    list_display = ("funcionario", "ciclo", "mes_1", "mes_2", "mes_3", "criado_em")
    list_filter = ("ciclo",)
    search_fields = ("funcionario__nome",)


@admin.register(AlocacaoFerias)
class AlocacaoFeriasAdmin(admin.ModelAdmin):
    list_display = ("funcionario", "ciclo", "mes_alocado", "status", "motivo", "atualizado_em")
    list_filter = ("ciclo", "status", "motivo")
    search_fields = ("funcionario__nome",)
