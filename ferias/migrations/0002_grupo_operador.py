from django.db import migrations

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

NOME_GRUPO = "Operador de Escala"


def criar_grupo_operador(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    grupo, _ = Group.objects.get_or_create(name=NOME_GRUPO)

    for model_name, acoes in PERMISSOES_POR_MODEL.items():
        for acao in acoes:
            codename = f"{acao}_{model_name}"
            try:
                permissao = Permission.objects.get(
                    codename=codename, content_type__app_label="ferias"
                )
            except Permission.DoesNotExist:
                continue
            grupo.permissions.add(permissao)


def remover_grupo_operador(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name=NOME_GRUPO).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("ferias", "0001_initial"),
        ("auth", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(criar_grupo_operador, remover_grupo_operador),
    ]
