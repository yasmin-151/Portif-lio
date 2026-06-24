# Exercicio: Microservico de Notificacao

## Contexto

Nos exercicios anteriores, voce construiu um **portfolio pessoal** com Django Templates e aprendeu a criar **APIs REST** com Django REST Framework. Agora vamos dar um passo alem e entrar no mundo dos **microservicos**.

A ideia e simples: vamos criar um **servico independente de notificacoes** que pode ser usado por **qualquer sistema**. O seu projeto do portfolio (porta 8000) vai consumir esse microservico (porta 8001) para exibir notificacoes em tempo real no sino do menu.

### Por que um microservico?

Imagine que a empresa tem varios sistemas internos: um e-commerce, um sistema de RH, o portfolio dos alunos. Todos precisam enviar notificacoes para seus usuarios. Em vez de cada sistema implementar seu proprio sistema de notificacoes, criamos **um unico microservico** que todos compartilham.

```
Sistema A (e-commerce)  ──┐
                          ├──→  Microservico de Notificacao (porta 8001)
Sistema B (RH)          ──┤         - Armazena notificacoes
                          │         - Controla leitura
Portfolio (porta 8000)  ──┘         - API REST
```

Cada sistema se registra como uma **Empresa** no microservico e recebe um **hash de 16 caracteres** que funciona como chave de acesso. A comunicacao entre os sistemas e feita via **headers HTTP** — sem JWT, sem login. Simples e direto.

---

## O que vamos fazer

### Parte 1 — Microservico de Notificacao (projeto novo, porta 8001)

1. Criar um novo projeto Django
2. Criar os models: `Empresa`, `Target`, `Notification`
3. Registrar no Django Admin para gerenciar dados
4. Criar autenticacao customizada via headers
5. Criar os endpoints da API (leitura + criacao de notificacoes)

### Parte 2 — Integrar no Portfolio (projeto existente, porta 8000)

6. Adicionar um sino no menu de navegacao (`base.html`)
7. Escrever JavaScript que consulta o microservico a cada **5 segundos**
8. Exibir: **X** (sem conexao), **0** (sem mensagens), **N** (mensagens nao lidas)
9. Click no sino abre dropdown com as mensagens

### Fluxo completo

```
Outro Sistema (ex: RH)                   Microservico (porta 8001)
       │                                          │
       │  POST /api/notificacoes/criar/            │
       │  Header: X-Api-Key                ──→    │  Cria notificacao
       │  Body: {user_id, mensagem}               │  para o target
       │                                          │
       │  (Tambem pode criar pelo Django Admin)   │
       │                                          │

Portfolio (porta 8000)                    Microservico (porta 8001)
       │                                          │
       │  A cada 5 segundos (polling):            │
       │                                          │
       │  GET /api/notificacoes/nao-lidas/        │
       │  Headers: X-Api-Key, X-User-Id    ──→    │  Valida hash da empresa
       │                                          │  Busca target pelo user_id
       │          ←── { "count": 3 }              │  Conta nao lidas
       │                                          │
       │  Atualiza o badge do sino: 3             │
       │                                          │
       │  Click no sino:                          │
       │                                          │
       │  GET /api/notificacoes/?is_read=false     │
       │  Headers: X-Api-Key, X-User-Id    ──→    │  Retorna notificacoes
       │                                          │
       │          ←── [ {mensagem, ...}, ... ]     │
       │                                          │
       │  Exibe dropdown com mensagens            │
       │                                          │
       │  Click em "marcar como lida":            │
       │                                          │
       │  PATCH /api/notificacoes/5/lida/          │
       │  Headers: X-Api-Key, X-User-Id    ──→    │  Marca is_read = True
       │                                          │
```

---

## Pre-requisitos

- Ter completado os exercicios anteriores (portfolio com templates e DRF)
- Python 3 instalado
- Conhecimento basico de Django e DRF (das aulas anteriores)

---

# PARTE 1 — Microservico de Notificacao

Vamos criar um **projeto Django totalmente separado** do portfolio. Esse projeto vai rodar na porta **8001**.

> **IMPORTANTE:** O microservico e um projeto **completamente independente**. Ele deve ficar em uma **pasta separada** e em um **repositorio Git separado** do portfolio. Isso e uma caracteristica fundamental de microservicos — cada servico tem seu proprio codigo, seu proprio banco de dados e seu proprio repositorio.

## Passo 1: Criar o projeto

Abra o terminal e crie uma nova pasta para o microservico. **Nao crie dentro do projeto do portfolio** — sao projetos independentes.

```bash
# Volte para a pasta raiz dos seus projetos
cd ~/Projetos   # ou onde voce organiza seus projetos

# Crie a pasta do microservico
mkdir notificacao_ms
cd notificacao_ms

# Inicialize um repositorio Git separado
git init

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# Instale as dependencias
pip install django djangorestframework django-cors-headers

# Crie o projeto Django
django-admin startproject notificacao_ms .

# Crie o app
python manage.py startapp notificacoes
```

Crie tambem um arquivo `.gitignore` na raiz do projeto:

```
venv/db.sqlite3__pycache__/*.pyc
```

> **Lembre-se:** ao final do exercicio, crie um **repositorio no GitHub** para o microservico e faca o push. Voce vai ter **dois repositorios**: um para o portfolio e outro para o microservico.

## Passo 2: Configurar o `settings.py`

Abra `notificacao_ms/settings.py` e faca as seguintes alteracoes:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'notificacoes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',          # Adicionar ANTES do CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Permitir que o portfolio (porta 8000) acesse o microservico (porta 8001)
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# DRF — sem autenticacao padrao (vamos usar headers customizados)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
}
```

> **Por que `django-cors-headers`?**
>
> O navegador bloqueia requisicoes entre origens diferentes (porta 8000 → porta 8001) por seguranca. Isso se chama **CORS** (Cross-Origin Resource Sharing). O `django-cors-headers` configura os headers necessarios para permitir essas requisicoes.

---

## Passo 3: Criar os Models

Abra `notificacoes/models.py` e crie os tres models:

```python
import secrets
from django.db import models


class Empresa(models.Model):
    """
    Representa um sistema/cliente que usa o microservico.
    Cada empresa recebe um hash unico de 16 caracteres para autenticacao.
    """
    nome = models.CharField(max_length=200, unique=True)
    hash = models.CharField(max_length=16, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.hash:
            self.hash = secrets.token_hex(8)  # 8 bytes = 16 caracteres hex
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nome


class Target(models.Model):
    """
    Vincula um usuario de um sistema externo ao microservico.
    O user_id e o ID do usuario no sistema cliente (ex: User.id do portfolio).
    """
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='targets')
    user_id = models.IntegerField()

    class Meta:
        verbose_name = 'Target'
        verbose_name_plural = 'Targets'
        unique_together = ['empresa', 'user_id']  # Nao pode repetir usuario na mesma empresa

    def __str__(self):
        return f'{self.empresa.nome} - User {self.user_id}'


class Notification(models.Model):
    """
    Uma notificacao enviada para um target especifico.
    """
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name='notificacoes')
    mensagem = models.TextField()
    is_read = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notificacao'
        verbose_name_plural = 'Notificacoes'
        ordering = ['-criado_em']

    def __str__(self):
        status = 'Lida' if self.is_read else 'Nao lida'
        return f'[{status}] {self.mensagem[:50]}'
```

### Entendendo os models

| Model | Campo | Descricao |
|-------|-------|-----------|
| **Empresa** | `nome` | Nome do sistema (ex: "Portfolio UAST") |
| | `hash` | Chave de 16 caracteres, gerada automaticamente. Serve como API Key. |
| **Target** | `empresa` | FK — a qual empresa esse target pertence |
| | `user_id` | ID do usuario no sistema cliente (ex: `request.user.id` do portfolio) |
| **Notification** | `target` | FK — para quem e a notificacao |
| | `mensagem` | Texto da notificacao |
| | `is_read` | Se ja foi lida (padrao: False) |
| | `criado_em` | Data/hora de criacao |

> **Por que `user_id` e um IntegerField e nao um ForeignKey?**
>
> Porque o microservico **nao conhece** os usuarios do portfolio. Ele nao tem acesso ao banco do portfolio. O `user_id` e apenas um numero que identifica o usuario no sistema cliente. Isso e uma caracteristica fundamental de microservicos: **cada servico tem seu proprio banco de dados**.

Aplique as migracoes:

```bash
python manage.py makemigrations notificacoes
python manage.py migrate
```

---

## Passo 4: Registrar no Django Admin

Abra `notificacoes/admin.py`:

```python
from django.contrib import admin
from .models import Empresa, Target, Notification


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'hash']
    readonly_fields = ['hash']


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'user_id']
    list_filter = ['empresa']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['target', 'mensagem_curta', 'is_read', 'criado_em']
    list_filter = ['is_read', 'target__empresa']
    list_editable = ['is_read']

    def mensagem_curta(self, obj):
        return obj.mensagem[:60] + '...' if len(obj.mensagem) > 60 else obj.mensagem
    mensagem_curta.short_description = 'Mensagem'
```

Crie o superusuario:

```bash
python manage.py createsuperuser
```

---

## Passo 5: Autenticacao por Headers

A autenticacao do microservico e feita por **headers HTTP customizados**. Nao usamos JWT nem login — o sistema cliente envia dois headers em cada requisicao:

| Header | Descricao | Exemplo |
|--------|-----------|---------|
| `X-Api-Key` | Hash da empresa (16 caracteres) | `a3f8b2c1d4e5f6a7` |
| `X-User-Id` | ID do usuario no sistema cliente | `1` |

O microservico valida o `X-Api-Key` para encontrar a **Empresa**, e usa o `X-User-Id` junto com a empresa para encontrar o **Target**.

Crie o arquivo `notificacoes/authentication.py`:

```python
from rest_framework.exceptions import AuthenticationFailed
from .models import Empresa, Target


def get_empresa_from_headers(request):
    """
    Extrai e valida o header X-Api-Key.
    Retorna a Empresa correspondente.
    """
    api_key = request.headers.get('X-Api-Key')

    if not api_key:
        raise AuthenticationFailed('Header X-Api-Key e obrigatorio.')

    try:
        empresa = Empresa.objects.get(hash=api_key)
    except Empresa.DoesNotExist:
        raise AuthenticationFailed('X-Api-Key invalida.')

    return empresa


def get_target_from_headers(request):
    """
    Extrai e valida os headers X-Api-Key e X-User-Id.
    Retorna o Target correspondente.
    """
    empresa = get_empresa_from_headers(request)

    user_id = request.headers.get('X-User-Id')
    if not user_id:
        raise AuthenticationFailed('Header X-User-Id e obrigatorio.')

    # Busca ou cria o target (usuario nessa empresa)
    target, created = Target.objects.get_or_create(
        empresa=empresa,
        user_id=int(user_id),
    )

    return target
```

> **Por que `get_or_create`?**
>
> Se o usuario do portfolio nunca recebeu uma notificacao, o Target dele ainda nao existe. O `get_or_create` cria automaticamente o target na primeira vez que o sistema consulta. Assim nao e necessario cadastrar targets manualmente.

---

## Passo 6: Criar os Serializers

Crie o arquivo `notificacoes/serializers.py`:

```python
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'mensagem', 'is_read', 'criado_em']
        read_only_fields = ['id', 'criado_em']


class NotificationCreateSerializer(serializers.Serializer):
    """
    Serializer para criar notificacoes via API.
    Recebe user_id e mensagem. O target e resolvido automaticamente
    a partir do X-Api-Key (empresa) + user_id do body.
    """
    user_id = serializers.IntegerField()
    mensagem = serializers.CharField()
```

---

## Passo 7: Criar as Views

Abra `notificacoes/views.py`:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Notification, Target
from .serializers import NotificationSerializer, NotificationCreateSerializer
from .authentication import get_target_from_headers, get_empresa_from_headers


class NotificacoesNaoLidasCountView(APIView):
    """
    GET /api/notificacoes/nao-lidas/
    Retorna a quantidade de notificacoes nao lidas do usuario.
    """

    def get(self, request):
        target = get_target_from_headers(request)
        count = Notification.objects.filter(target=target, is_read=False).count()
        return Response({'count': count})


class NotificacoesListView(APIView):
    """
    GET /api/notificacoes/
    Retorna as notificacoes do usuario.

    Query params opcionais:
        ?is_read=true   → somente lidas
        ?is_read=false  → somente nao lidas
        (sem parametro) → todas
    """

    def get(self, request):
        target = get_target_from_headers(request)
        notificacoes = Notification.objects.filter(target=target)

        # Filtro opcional por is_read
        is_read_param = request.query_params.get('is_read')
        if is_read_param is not None:
            is_read = is_read_param.lower() in ['true', '1', 'sim']
            notificacoes = notificacoes.filter(is_read=is_read)

        serializer = NotificationSerializer(notificacoes, many=True)
        return Response(serializer.data)


class NotificacaoMarcarLidaView(APIView):
    """
    PATCH /api/notificacoes/<id>/lida/
    Marca uma notificacao como lida.
    """

    def patch(self, request, pk):
        target = get_target_from_headers(request)

        try:
            notificacao = Notification.objects.get(pk=pk, target=target)
        except Notification.DoesNotExist:
            return Response({'erro': 'Notificacao nao encontrada.'}, status=404)

        notificacao.is_read = True
        notificacao.save()

        serializer = NotificationSerializer(notificacao)
        return Response(serializer.data)


class NotificacaoCreateView(APIView):
    """
    POST /api/notificacoes/criar/
    Cria uma notificacao para um usuario.

    Esse endpoint e usado por OUTROS SISTEMAS (ou pelo admin/testes)
    para enviar notificacoes. O portfolio NAO usa esse endpoint —
    ele apenas LE as notificacoes.

    Headers: X-Api-Key (identifica a empresa)
    Body: { "user_id": 1, "mensagem": "Texto da notificacao" }
    """

    def post(self, request):
        empresa = get_empresa_from_headers(request)

        serializer = NotificationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Busca ou cria o target
        target, created = Target.objects.get_or_create(
            empresa=empresa,
            user_id=serializer.validated_data['user_id'],
        )

        # Cria a notificacao
        notificacao = Notification.objects.create(
            target=target,
            mensagem=serializer.validated_data['mensagem'],
        )

        return Response(
            NotificationSerializer(notificacao).data,
            status=status.HTTP_201_CREATED,
        )
```

### Entendendo as views

| Endpoint | Metodo | O que faz |
|----------|--------|-----------|
| `/api/notificacoes/nao-lidas/` | GET | Retorna `{"count": N}` com o total de nao lidas |
| `/api/notificacoes/` | GET | Lista notificacoes. Aceita `?is_read=true` ou `?is_read=false` |
| `/api/notificacoes/<id>/lida/` | PATCH | Marca uma notificacao especifica como lida |
| `/api/notificacoes/criar/` | POST | Cria uma notificacao (usado por outros sistemas ou para testes) |

> **Quem cria as notificacoes?**
>
> As notificacoes podem ser criadas de **duas formas**:
> 1. **Pelo Django Admin** — acesse [http://127.0.0.1:8001/admin/](http://127.0.0.1:8001/admin/) e crie manualmente. Ideal para testes.
> 2. **Pela API (POST)** — outro sistema envia uma requisicao POST. Isso simula o cenario real onde um terceiro sistema (ex: e-commerce, RH) envia notificacoes para os usuarios.
>
> O **portfolio NAO cria notificacoes** — ele apenas le e marca como lidas. Quem cria e o admin ou outros sistemas.

---

## Passo 8: Configurar as URLs

Crie o arquivo `notificacoes/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path(
        'api/notificacoes/nao-lidas/',
        views.NotificacoesNaoLidasCountView.as_view(),
        name='notificacoes-nao-lidas',
    ),
    path(
        'api/notificacoes/',
        views.NotificacoesListView.as_view(),
        name='notificacoes-list',
    ),
    path(
        'api/notificacoes/criar/',
        views.NotificacaoCreateView.as_view(),
        name='notificacao-criar',
    ),
    path(
        'api/notificacoes/<int:pk>/lida/',
        views.NotificacaoMarcarLidaView.as_view(),
        name='notificacao-marcar-lida',
    ),
]
```

Abra `notificacao_ms/urls.py` e inclua as URLs do app:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('notificacoes.urls')),
]
```

---

## Passo 9: Testar o Microservico

### 9.1 Iniciar o servidor na porta 8001

```bash
python manage.py runserver 8001
```

### 9.2 Criar dados de teste

Existem **duas formas** de criar notificacoes no microservico. Voce pode usar qualquer uma (ou as duas):

#### Opcao A: Pelo Django Admin

Acesse [http://127.0.0.1:8001/admin/](http://127.0.0.1:8001/admin/) e:

1. **Crie uma Empresa**: nome = `Portfolio UAST`. O hash sera gerado automaticamente. **Anote o hash** — voce vai precisar dele.

2. **Crie um Target**: selecione a empresa `Portfolio UAST` e coloque `user_id = 1` (ou o ID do seu usuario no portfolio — verifique no admin do portfolio em Users).

3. **Crie algumas Notificacoes** para esse target:
   - "Bem-vindo ao sistema de notificacoes!" (is_read = False)
   - "Seu perfil foi atualizado com sucesso." (is_read = False)
   - "Nova aula disponivel: Microservicos" (is_read = False)

#### Opcao B: Pela API (simulando um terceiro sistema)

Imagine que existe um **terceiro sistema** (ex: sistema de RH, e-commerce) que precisa enviar notificacoes para os usuarios. Esse sistema usaria o endpoint `POST /api/notificacoes/criar/` para isso.

Primeiro, crie a Empresa pelo admin (passo 1 acima) e anote o hash. Depois, use curl para simular o terceiro sistema enviando notificacoes:

```bash
# Criar notificacoes via API (simulando outro sistema)
# Substitua SEU_HASH_AQUI pelo hash da empresa

curl -X POST http://127.0.0.1:8001/api/notificacoes/criar/ \
     -H "X-Api-Key: SEU_HASH_AQUI" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "mensagem": "Bem-vindo ao sistema de notificacoes!"}'

curl -X POST http://127.0.0.1:8001/api/notificacoes/criar/ \
     -H "X-Api-Key: SEU_HASH_AQUI" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "mensagem": "Seu perfil foi atualizado com sucesso."}'

curl -X POST http://127.0.0.1:8001/api/notificacoes/criar/ \
     -H "X-Api-Key: SEU_HASH_AQUI" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "mensagem": "Nova aula disponivel: Microservicos"}'
```

> **Note:** no POST, o header `X-User-Id` **nao e necessario** — o `user_id` vai no **body** da requisicao. O header `X-Api-Key` identifica qual empresa esta enviando a notificacao.

### 9.3 Testar leitura com curl

Substitua `SEU_HASH_AQUI` pelo hash da empresa que voce anotou:

```bash
# 1. Contar notificacoes nao lidas
curl http://127.0.0.1:8001/api/notificacoes/nao-lidas/ \
     -H "X-Api-Key: SEU_HASH_AQUI" \
     -H "X-User-Id: 1"

# Resposta esperada: {"count": 3}

# 2. Listar todas as notificacoes
curl http://127.0.0.1:8001/api/notificacoes/ \
     -H "X-Api-Key: SEU_HASH_AQUI" \
     -H "X-User-Id: 1"

# 3. Listar somente nao lidas
curl "http://127.0.0.1:8001/api/notificacoes/?is_read=false" \
     -H "X-Api-Key: SEU_HASH_AQUI" \
     -H "X-User-Id: 1"

# 4. Marcar notificacao como lida (troque 1 pelo ID da notificacao)
curl -X PATCH http://127.0.0.1:8001/api/notificacoes/1/lida/ \
     -H "X-Api-Key: SEU_HASH_AQUI" \
     -H "X-User-Id: 1"

# 5. Criar mais uma notificacao via API (simulando outro sistema)
curl -X POST http://127.0.0.1:8001/api/notificacoes/criar/ \
     -H "X-Api-Key: SEU_HASH_AQUI" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "mensagem": "Voce tem uma nova tarefa pendente!"}'
```

Se os testes funcionaram, o microservico esta pronto. Agora vamos integrar com o portfolio.

---

# PARTE 2 — Integrar no Portfolio

Agora vamos voltar ao projeto do portfolio (porta 8000) e adicionar o **sino de notificacoes** no menu.

> **IMPORTANTE:** A partir daqui, voce deve estar trabalhando no projeto do **portfolio** (o mesmo das aulas anteriores), **nao** no microservico.

## Passo 10: Adicionar configuracoes no portfolio

Abra o `django_tutorial/settings.py` do seu projeto do portfolio e adicione no final:

```python
# ─── Microservico de Notificacao ───
NOTIFICACAO_MS_URL = 'http://127.0.0.1:8001'
NOTIFICACAO_MS_API_KEY = 'SEU_HASH_AQUI'  # Hash da empresa criada no microservico
```

> **Substitua** `SEU_HASH_AQUI` pelo hash da empresa que voce criou no Django Admin do microservico.

---

## Passo 11: Passar as configuracoes para o template

Para que o JavaScript tenha acesso a URL e a API Key do microservico, precisamos passar essas informacoes via **context processor** ou diretamente na view.

Vamos usar um **context processor** para que os dados estejam disponiveis em **todos** os templates automaticamente.

Crie o arquivo `core/context_processors.py`:

```python
from django.conf import settings


def notificacao_ms(request):
    """
    Disponibiliza as configuracoes do microservico de notificacao
    em todos os templates.
    """
    context = {
        'NOTIFICACAO_MS_URL': settings.NOTIFICACAO_MS_URL,
        'NOTIFICACAO_MS_API_KEY': settings.NOTIFICACAO_MS_API_KEY,
    }

    # Passa o user_id se o usuario estiver logado
    if request.user.is_authenticated:
        context['NOTIFICACAO_USER_ID'] = request.user.id

    return context
```

Registre o context processor no `django_tutorial/settings.py`:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.notificacao_ms',  # Adicionar esta linha
            ],
        },
    },
]
```

---

## Passo 12: Atualizar o Template Base

Agora vamos adicionar o sino de notificacoes no `base.html`. Abra `core/templates/core/base.html` e atualize a secao `<nav>` e adicione o CSS e JavaScript do sino.

Substitua o conteudo completo do `base.html`:

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Meu Portfolio{% endblock %}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f4f4;
            color: #333;
        }
        header {
            background-color: #2c3e50;
            color: white;
            padding: 20px 0;
            text-align: center;
        }
        header h1 {
            font-size: 2em;
        }
        nav {
            background-color: #34495e;
            padding: 10px 0;
            text-align: center;
            position: relative;
        }
        nav a {
            color: white;
            text-decoration: none;
            margin: 0 15px;
            font-size: 1.1em;
        }
        nav a:hover {
            text-decoration: underline;
        }
        .container {
            max-width: 960px;
            margin: 30px auto;
            padding: 0 20px;
        }
        footer {
            background-color: #2c3e50;
            color: white;
            text-align: center;
            padding: 15px 0;
            margin-top: 40px;
        }

        /* ─── Estilos do Sino de Notificacoes ─── */
        .sino-container {
            position: absolute;
            right: 30px;
            top: 50%;
            transform: translateY(-50%);
        }
        .sino-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.4em;
            cursor: pointer;
            position: relative;
        }
        .sino-badge {
            position: absolute;
            top: -8px;
            right: -10px;
            background-color: #e74c3c;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 0.65em;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        .sino-badge.sem-conexao {
            background-color: #95a5a6;
        }
        .sino-badge.sem-mensagens {
            background-color: #27ae60;
        }

        /* ─── Dropdown de Notificacoes ─── */
        .notif-dropdown {
            display: none;
            position: absolute;
            right: 0;
            top: 40px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            width: 320px;
            max-height: 400px;
            overflow-y: auto;
            z-index: 999;
        }
        .notif-dropdown.aberto {
            display: block;
        }
        .notif-dropdown-header {
            padding: 12px 15px;
            background: #2c3e50;
            color: white;
            border-radius: 8px 8px 0 0;
            font-weight: bold;
        }
        .notif-item {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            transition: background 0.2s;
        }
        .notif-item:hover {
            background: #f8f9fa;
        }
        .notif-item.nao-lida {
            border-left: 3px solid #3498db;
            background: #eef6ff;
        }
        .notif-item .notif-mensagem {
            font-size: 0.9em;
            color: #333;
        }
        .notif-item .notif-data {
            font-size: 0.75em;
            color: #999;
            margin-top: 4px;
        }
        .notif-vazio {
            padding: 20px;
            text-align: center;
            color: #999;
        }

        {% block extra_css %}{% endblock %}
    </style>
</head>
<body>
    <header>
        <h1>{% block header_title %}Portfolio do Aluno{% endblock %}</h1>
    </header>

    <nav>
        <a href="{% url 'portfolio:home' %}">Inicio</a>
        <a href="{% url 'portfolio:projetos' %}">Projetos</a>

        <!-- Sino de Notificacoes -->
        {% if user.is_authenticated %}
        <div class="sino-container">
            <button class="sino-btn" id="sino-btn" title="Notificacoes">
                &#128276;
                <span class="sino-badge sem-conexao" id="sino-badge">X</span>
            </button>
            <div class="notif-dropdown" id="notif-dropdown">
                <div class="notif-dropdown-header">Notificacoes</div>
                <div id="notif-lista">
                    <div class="notif-vazio">Carregando...</div>
                </div>
            </div>
        </div>
        {% endif %}
    </nav>

    <div class="container">
        {% block content %}{% endblock %}
    </div>

    <footer>
        <p>&copy; 2026 - Portfolio Academico | UAST</p>
    </footer>

    <!-- JavaScript do Sino de Notificacoes -->
    {% if user.is_authenticated %}
    <script>
    (function() {
        // ─── Configuracoes vindas do Django (context processor) ───
        var MS_URL = '{{ NOTIFICACAO_MS_URL }}';
        var API_KEY = '{{ NOTIFICACAO_MS_API_KEY }}';
        var USER_ID = '{{ NOTIFICACAO_USER_ID }}';

        // ─── Elementos do DOM ───
        var sinoBtn = document.getElementById('sino-btn');
        var sinoBadge = document.getElementById('sino-badge');
        var dropdown = document.getElementById('notif-dropdown');
        var notifLista = document.getElementById('notif-lista');

        // ─── Headers padrao para todas as requisicoes ───
        var headers = {
            'X-Api-Key': API_KEY,
            'X-User-Id': USER_ID,
        };

        // ─── Funcao: Buscar contagem de nao lidas ───
        function buscarContagem() {
            fetch(MS_URL + '/api/notificacoes/nao-lidas/', { headers: headers })
                .then(function(response) {
                    if (!response.ok) throw new Error('Erro na API');
                    return response.json();
                })
                .then(function(data) {
                    var count = data.count;

                    // Remove classes anteriores
                    sinoBadge.classList.remove('sem-conexao', 'sem-mensagens');

                    if (count === 0) {
                        sinoBadge.textContent = '0';
                        sinoBadge.classList.add('sem-mensagens');
                    } else {
                        sinoBadge.textContent = count;
                    }
                })
                .catch(function() {
                    // Sem conexao com o microservico
                    sinoBadge.textContent = 'X';
                    sinoBadge.classList.remove('sem-mensagens');
                    sinoBadge.classList.add('sem-conexao');
                });
        }

        // ─── Funcao: Buscar lista de notificacoes ───
        function buscarNotificacoes() {
            fetch(MS_URL + '/api/notificacoes/', { headers: headers })
                .then(function(response) {
                    if (!response.ok) throw new Error('Erro na API');
                    return response.json();
                })
                .then(function(notificacoes) {
                    if (notificacoes.length === 0) {
                        notifLista.innerHTML = '<div class="notif-vazio">Nenhuma notificacao.</div>';
                        return;
                    }

                    var html = '';
                    notificacoes.forEach(function(notif) {
                        var classe = notif.is_read ? 'notif-item' : 'notif-item nao-lida';
                        var data = new Date(notif.criado_em).toLocaleString('pt-BR');

                        html += '<div class="' + classe + '" data-id="' + notif.id + '">';
                        html += '  <div class="notif-mensagem">' + notif.mensagem + '</div>';
                        html += '  <div class="notif-data">' + data + '</div>';
                        html += '</div>';
                    });

                    notifLista.innerHTML = html;

                    // Adicionar evento de click para marcar como lida
                    var items = notifLista.querySelectorAll('.notif-item.nao-lida');
                    items.forEach(function(item) {
                        item.addEventListener('click', function() {
                            var id = this.getAttribute('data-id');
                            marcarComoLida(id, this);
                        });
                    });
                })
                .catch(function() {
                    notifLista.innerHTML = '<div class="notif-vazio">Erro ao carregar notificacoes.</div>';
                });
        }

        // ─── Funcao: Marcar notificacao como lida ───
        function marcarComoLida(id, elemento) {
            fetch(MS_URL + '/api/notificacoes/' + id + '/lida/', {
                method: 'PATCH',
                headers: headers,
            })
            .then(function(response) {
                if (!response.ok) throw new Error('Erro');
                return response.json();
            })
            .then(function() {
                // Remove o destaque visual
                elemento.classList.remove('nao-lida');
                // Atualiza a contagem
                buscarContagem();
            })
            .catch(function(erro) {
                console.error('Erro ao marcar como lida:', erro);
            });
        }

        // ─── Abrir/Fechar dropdown ───
        sinoBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            var aberto = dropdown.classList.contains('aberto');

            if (aberto) {
                dropdown.classList.remove('aberto');
            } else {
                dropdown.classList.add('aberto');
                buscarNotificacoes();
            }
        });

        // Fechar dropdown ao clicar fora
        document.addEventListener('click', function() {
            dropdown.classList.remove('aberto');
        });

        dropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });

        // ─── Polling: buscar contagem a cada 5 segundos ───
        buscarContagem();  // Primeira busca imediata
        setInterval(buscarContagem, 5000);  // Depois, a cada 5 segundos
    })();
    </script>
    {% endif %}
</body>
</html>
```

### Entendendo o JavaScript

| Funcao | O que faz |
|--------|-----------|
| `buscarContagem()` | Faz GET em `/api/notificacoes/nao-lidas/` e atualiza o badge do sino |
| `buscarNotificacoes()` | Faz GET em `/api/notificacoes/` e monta a lista no dropdown |
| `marcarComoLida(id)` | Faz PATCH em `/api/notificacoes/<id>/lida/` |
| `setInterval(buscarContagem, 5000)` | **Polling** — repete a busca a cada 5 segundos |

### Comportamento do badge

| Estado | Aparencia | Significado |
|--------|-----------|-------------|
| `X` (cinza) | Sem conexao com o microservico |
| `0` (verde) | Conectado, sem notificacoes nao lidas |
| `N` (vermelho) | N notificacoes nao lidas |

> **O que e polling?**
>
> Polling e a tecnica de ficar consultando um servidor repetidamente em intervalos regulares. A cada 5 segundos, o JavaScript do portfolio faz uma requisicao ao microservico para saber se tem notificacoes novas. Nao e a forma mais eficiente (websockets seriam melhores), mas e simples e funciona bem para nosso caso.

---

## Passo 13: Testar tudo junto

Voce vai precisar de **dois terminais** abertos ao mesmo tempo.

### Terminal 1 — Microservico (porta 8001)

```bash
cd ~/Projetos/notificacao_ms
source venv/bin/activate
python manage.py runserver 8001
```

### Terminal 2 — Portfolio (porta 8000)

```bash
cd ~/Projetos/UAST/web_2026_1/django_tutorial    # ou onde esta seu projeto
source venv/bin/activate
python manage.py runserver
```

### Testando

1. Acesse o portfolio: [http://127.0.0.1:8000/portfolio/](http://127.0.0.1:8000/portfolio/)

2. Faca login no Django Admin do portfolio ([http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)) para que `user.is_authenticated` seja `True` e o sino apareca.

3. Volte para o portfolio. O **sino** deve aparecer no menu com o numero de notificacoes nao lidas.

4. Clique no sino para ver a lista de notificacoes.

5. Clique em uma notificacao nao lida para marca-la como lida.

6. Crie uma nova notificacao — pode ser pelo **Django Admin** ([http://127.0.0.1:8001/admin/](http://127.0.0.1:8001/admin/)) ou **pela API** com curl (simulando um terceiro sistema). Em ate **5 segundos**, o badge do sino no portfolio deve atualizar automaticamente.

7. Para testar o estado **sem conexao**: pare o servidor do microservico (Ctrl+C no Terminal 1). O badge deve mudar para **X** (cinza) na proxima atualizacao.

---

## Estrutura Final

### Microservico (projeto novo)

```
notificacao_ms/
├── manage.py
├── notificacao_ms/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── notificacoes/
    ├── admin.py              ← Cadastro de Empresa, Target, Notification
    ├── authentication.py     ← Validacao dos headers X-Api-Key e X-User-Id
    ├── models.py             ← Empresa, Target, Notification
    ├── serializers.py        ← NotificationSerializer
    ├── urls.py               ← 4 endpoints da API
    └── views.py              ← Views da API
```

### Portfolio (projeto existente — alteracoes)

```
django_tutorial/
├── django_tutorial/
│   └── settings.py           ← + NOTIFICACAO_MS_URL e NOTIFICACAO_MS_API_KEY
├── core/
│   ├── context_processors.py ← NOVO: passa configs do MS para os templates
│   └── templates/
│       └── core/
│           └── base.html     ← + sino de notificacoes + JavaScript com polling
```

---

## Resumo dos conceitos praticados

| Conceito | Onde foi usado |
|----------|---------------|
| **Microservico** | Projeto separado com banco proprio, API propria |
| **Autenticacao por headers** | `X-Api-Key` + `X-User-Id` — sem JWT, sem login |
| **CORS** | `django-cors-headers` permite requisicoes cross-origin |
| **Polling** | JavaScript consulta a API a cada 5 segundos |
| **Context Processor** | Passa configuracoes do Django para todos os templates |
| **Independencia de bancos** | O MS nao conhece o banco do portfolio (`user_id` e so um numero) |
| **Hash como API Key** | `secrets.token_hex(8)` gera 16 caracteres aleatorios |
| **get_or_create** | Cria Target automaticamente na primeira consulta |

---

## Desafio extra

1. Adicione um botao **"Marcar todas como lidas"** no dropdown (dica: crie um endpoint `PATCH /api/notificacoes/marcar-todas-lidas/`)
2. Adicione um campo `titulo` no model Notification e exiba no dropdown com destaque
3. Crie uma segunda Empresa no admin (ex: "Sistema RH") com hash diferente e teste que cada empresa so ve suas proprias notificacoes — isso comprova o isolamento entre clientes do microservico
4. Crie um pequeno script Python (`enviar_notificacao.py`) que use a biblioteca `requests` para enviar notificacoes pela API, simulando um terceiro sistema automatizado
