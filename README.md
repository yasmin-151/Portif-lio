# Arquitetura de Microserviços: Portfólio Acadêmico & Serviço de Notificações

Este repositório contém o ecossistema completo do Portfólio Acadêmico integrado a um Microserviço independente de Notificações em Tempo Real via API REST (Polling).

---

## Estrutura Sugerida de Pastas

Para que o passo a passo funcione perfeitamente, o ideal é criar uma pasta principal no seu computador (por exemplo, `MeusProjetos`) e clonar os dois repositórios dentro dela:

```text
MeusProjetos/
├── djangotutorial/     (Seu projeto do Portfólio - Porta 8000)
└── notificacao_ms/     (Seu projeto do Microserviço - Porta 8001)

```

---

## Passo 1: Configurando e Executando o Microserviço (Porta 8001)

Abra o seu terminal (PowerShell ou Bash) na pasta principal `MeusProjetos` e execute a sequência abaixo:

```powershell
# 1. Clonar o repositório do Microserviço (Substitua pelo seu link real do GitHub)
git clone [https://github.com/SEU_USUARIO/notificacao_ms.git](https://github.com/SEU_USUARIO/notificacao_ms.git)
cd notificacao_ms

# 2. Criar e ativar o ambiente virtual (venv)
python -m venv .venv
# No Windows (PowerShell):
.venv\Scripts\Activate.ps1
# No Linux/Mac:
source .venv/bin/activate

# 3. Instalar as dependências necessárias
pip install django django-cors-headers djangorestframework requests

# 4. Rodar as migrações para criar o Banco de Dados local (SQLite)
python manage.py makemigrations
python manage.py migrate

# 5. Criar um usuário Administrador para acessar o painel
# (Insira um nome, e-mail e senha que você lembre facilmente)
python manage.py createsuperuser

# 6. Iniciar o servidor explicitamente na porta 8001
python manage.py runserver 8001

```

### Configuração Inicial Obrigatória no Admin (Porta 8001)

1. Acesse o painel administrativo do microserviço: http://127.0.0.1:8001/admin/
2. Vá na seção Empresas e clique em Adicionar empresa.
* Nome: Portfolio
* Token: dc0e0a220a754996
* Clique em Salvar.


3. Vá na seção Targets (Alvos) e clique em Adicionar target.
* Empresa: Selecione Portfolio
* User id: 1
* Clique em Salvar.



Deixe esse terminal aberto e o servidor rodando na porta 8001.

---

## Passo 2: Configurando e Executando o Portfólio (Porta 8000)

Abra um segundo terminal na pasta principal `MeusProjetos` e execute os comandos:

```powershell
# 1. Clonar o repositório do Portfólio (Substitua pelo seu link real do GitHub)
git clone [https://github.com/SEU_USUARIO/djangotutorial.git](https://github.com/SEU_USUARIO/djangotutorial.git)
cd djangotutorial

# 2. Criar e ativar o ambiente virtual (venv)
python -m venv .venv
# No Windows (PowerShell):
.venv\Scripts\Activate.ps1
# No Linux/Mac:
source .venv/bin/activate

# 3. Instalar as dependências do Portfólio
pip install django django-cors-headers djangorestframework requests

# 4. Rodar as migrações e criar o usuário do Portfólio
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

```

Atenção: Certifique-se de que o usuário criado aqui seja o primeiro do banco para que o Django atribua automaticamente o ID 1, batendo com o Target que configuramos no microserviço.

```powershell
# 5. Iniciar o servidor do Portfólio na porta padrão (8000)
python manage.py runserver

```

---

## Passo 3: Testando a Integração de Ponta a Ponta

1. Abra o seu navegador e faça login no Admin do Portfólio (http://127.0.0.1:8000/admin/) com a conta do usuário ID 1 que você acabou de criar.
2. Acesse a página inicial do seu Portfólio: http://127.0.0.1:8000/portifolio/home/
3. Verificação do Sino: O ícone do sino deverá aparecer no menu superior direito exibindo o badge com o número 0 (na cor verde), indicando que o JavaScript do Portfólio conseguiu se conectar com o microserviço com sucesso.

### Testando o Envio Automático em Tempo Real (Script Externo)

Abra um terceiro terminal na pasta do microserviço (notificacao_ms), certifique-se de que a .venv está ativa e execute o script simulador que criamos:

```powershell
python enviar_alertas.py

```

* O que observar: O script Python começará a gerar e postar um alerta aleatório na API a cada 10 segundos. Olhe para a tela do seu Portfólio no navegador: sem atualizar a página, o contador do sino aumentará sozinho via Polling!
* Interação: Clique no sino para abrir o dropdown, veja os títulos destacados em negrito e clique no botão "Marcar todas como lidas" para ver todo o painel e o contador zerarem instantaneamente sem recarregar a página.

```

```
