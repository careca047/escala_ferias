# Escala de férias

Estrutura inicial do projeto Django, baseada na especificação consolidada
(`especificacao_escala_ferias.md`).

## O que já está pronto

- Projeto Django configurado (`config/`), lendo `SECRET_KEY`, `DEBUG`,
  `ALLOWED_HOSTS` e `DATABASE_URL` de variáveis de ambiente.
- App `ferias` com os models de toda a estrutura de dados definida na
  especificação: `Plantao`, `Posto`, `PostoPlantaoCapacidade`,
  `Funcionario`, `CicloFerias`, `HistoricoFerias`, `PreferenciaFerias` e
  `AlocacaoFerias` (com a validação da observação obrigatória quando o
  status é "decidido pelo operador").
- Todos os models já registrados no Django Admin, com listagens e filtros
  básicos — o operador já consegue cadastrar funcionários, plantões,
  postos e capacidades assim que o banco estiver rodando.
- Grupo de permissões "Operador de Escala": rode `python manage.py criar_grupo_operador`
  depois do `migrate`. Ele fica definido em
  `ferias/management/commands/criar_grupo_operador.py`, com acesso de
  edição só aos models operacionais (Ciclo, Preferências, Alocações,
  Histórico) e de visualização aos estruturais (Funcionário, Plantão,
  Posto, Capacidade) — sem acesso a Usuários/Grupos.
- Configuração de debug do VS Code (`.vscode/launch.json`), pra rodar o
  servidor com F5 direto pelo editor.

## O que ainda falta construir

- O algoritmo de alocação em si (as 2 passadas por posto+plantão).
- A tela customizada de resolução de pendências para o operador.
- A ação de formalizar a escala e a geração do PDF final.
- As páginas mobile-first para o funcionário escolher os 3 meses.

## Como rodar localmente

1. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Copie o arquivo de variáveis de ambiente:
   ```bash
   cp .env.example .env
   ```
   Em desenvolvimento, pode deixar `DATABASE_URL` como está — sem uma
   connection string do Postgres, o projeto cai para SQLite local
   automaticamente.
4. Rode as migrações, crie um usuário administrador e crie o grupo do operador:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py criar_grupo_operador
   ```
5. Suba o servidor:
   ```bash
   python manage.py runserver
   ```
6. Acesse `http://127.0.0.1:8000/admin/` e entre com o usuário criado.

## Controle de acesso

- **Seu usuário** (o desenvolvedor): crie com `python manage.py createsuperuser`.
  Acesso total a tudo no admin.
- **Usuário do operador**: crie pelo próprio admin (Usuários > Adicionar
  usuário), marque "Membro da equipe" (não marque "Superusuário"), e
  vincule ao grupo "Operador de Escala" — criado ao rodar
  `python manage.py criar_grupo_operador`.
- O login do admin nunca dá acesso ao código-fonte, ao repositório ou à
  hospedagem — são credenciais completamente separadas.

## Próximos passos de infraestrutura (definidos anteriormente)

- Hospedagem: Render (free tier).
- Banco de dados: Postgres gratuito e persistente via Supabase ou Neon
  (não usar o Postgres gratuito do próprio Render, que expira em 30 dias).
