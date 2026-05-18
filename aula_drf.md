# Aula: API REST com Django REST Framework

## Objetivo

Nesta aula vamos aprender como criar uma **API REST** usando o **Django REST Framework (DRF)**. Vamos construir uma API completa de gerenciamento de tarefas com:

- Um app `tarefas` com model, serializer e views
- Tres estilos diferentes de views (Function-Based, Class-Based e Generic Views)
- Autenticacao com JWT (JSON Web Token)
- Testes com `curl` e a API navegavel do DRF

**Pre-requisito:** Ter completado a aula de templates e ter o projeto Django funcionando.

---

## Recapitulando: O que ja aprendemos?

Nas aulas anteriores com **Django Templates**, aprendemos o fluxo basico:

```
URL  →  View  →  Form (validacao)  →  Template HTML  →  Pagina no navegador
```

- Criamos **URLs** que apontam para **Views**
- As Views processam dados e renderizam **Templates HTML**
- Usamos **Forms** para validar dados de formularios
- O resultado final e uma **pagina HTML** completa

**Mas e se o cliente nao for um navegador?** E se for um app mobile, ou um frontend React?

Nesse caso, nao queremos retornar HTML — queremos retornar **dados puros (JSON)** que qualquer aplicacao consiga entender. E ai que entra a **API REST**.

---

## 1. O que e REST?

**REST** (Representational State Transfer) e uma **interface** — um conjunto de regras que define **como** cliente e servidor se comunicam. Nao importa a linguagem, o framework ou o banco de dados: se seguir as regras REST, qualquer sistema consegue conversar com outro.

### Por que precisamos de APIs REST?

Imagine que voce criou um sistema web com Django. Agora voce quer que:

- Um **aplicativo mobile** (Android/iOS) acesse os mesmos dados
- Uma **Single Page Application** (SPA) em React ou Vue.js consuma os dados
- Outro **sistema externo** (microservico) se integre ao seu

Com templates do Django, voce retorna **HTML** — que so o navegador entende. Com uma API REST, voce retorna **JSON** — que qualquer aplicacao entende.

### Como funciona a comunicacao?

```
┌─────────────┐         Requisicao HTTP          ┌─────────────┐
│             │  ─────────────────────────────>   │             │
│   CLIENTE   │    GET /api/tarefas/              │  SERVIDOR   │
│             │    Authorization: Bearer token     │  (Django)   │
│  (Browser,  │                                   │             │
│   Mobile,   │  <─────────────────────────────   │  Processa   │
│   React)    │    Resposta JSON                  │  e retorna  │
│             │    [{"id": 1, "titulo": "..."}]   │  dados      │
└─────────────┘                                   └─────────────┘
```

O **cliente** faz uma requisicao HTTP para o **servidor**. O servidor processa e retorna os dados em formato **JSON**.

### Metodos HTTP

Cada metodo HTTP representa uma **acao** diferente sobre os dados (recurso):

| Metodo | Acao | Exemplo | Descricao |
|--------|------|---------|-----------|
| `GET` | Ler | `GET /api/tarefas/` | Lista todas as tarefas |
| `GET` | Ler | `GET /api/tarefas/1/` | Retorna a tarefa com id=1 |
| `POST` | Criar | `POST /api/tarefas/` | Cria uma nova tarefa |
| `PUT` | Atualizar (completo) | `PUT /api/tarefas/1/` | Atualiza todos os campos da tarefa 1 |
| `PATCH` | Atualizar (parcial) | `PATCH /api/tarefas/1/` | Atualiza apenas alguns campos |
| `DELETE` | Excluir | `DELETE /api/tarefas/1/` | Exclui a tarefa 1 |

### Codigos de Status HTTP

O servidor responde com um **codigo de status** que indica o resultado:

| Codigo | Significado | Quando acontece |
|--------|------------|-----------------|
| `200 OK` | Sucesso | GET, PUT, PATCH bem-sucedidos |
| `201 Created` | Criado | POST bem-sucedido |
| `204 No Content` | Sem conteudo | DELETE bem-sucedido |
| `400 Bad Request` | Dados invalidos | Enviou dados errados no POST/PUT |
| `401 Unauthorized` | Nao autenticado | Faltou o token de autenticacao |
| `403 Forbidden` | Sem permissao | Token valido, mas sem permissao |
| `404 Not Found` | Nao encontrado | Recurso nao existe |

### Contexto do mundo real

APIs REST estao em todo lugar:

- **Instagram/Twitter:** O app mobile consome uma API REST para exibir posts
- **iFood/Uber:** Comunicacao entre app, servidor e restaurantes via APIs
- **Microservicos:** Grandes empresas dividem sistemas em servicos menores que se comunicam via REST
- **Integracoes:** Login com Google, pagamento com Stripe, mapas com Google Maps — tudo via APIs REST

---

## 2. O que e o Django REST Framework?

O **Django REST Framework (DRF)** e uma biblioteca poderosa que facilita a criacao de APIs REST com Django. Ele adiciona:

- **Serializers** — convertem objetos Django (models) em JSON e vice-versa
- **Views especializadas** — classes prontas para CRUD (criar, ler, atualizar, deletar)
- **Autenticacao integrada** — suporte a tokens, JWT, sessao, etc.
- **API navegavel** — interface web para testar a API no navegador
- **Paginacao, filtros, permissoes** — tudo pronto para usar

### Por que usar DRF em vez de views Django puras?

Voce **poderia** criar uma API com Django puro usando `JsonResponse`:

```python
# SEM DRF - Trabalhoso e repetitivo
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def lista_tarefas(request):
    if request.method == 'GET':
        tarefas = Tarefa.objects.all()
        dados = [{'id': t.id, 'titulo': t.titulo} for t in tarefas]
        return JsonResponse(dados, safe=False)
    elif request.method == 'POST':
        dados = json.loads(request.body)
        # validacao manual...
        # criacao manual...
        return JsonResponse({'id': tarefa.id}, status=201)
```

Com DRF, o mesmo resultado fica **muito mais simples, seguro e organizado**:

```python
# COM DRF - Limpo e poderoso
from rest_framework import generics
from .models import Tarefa
from .serializers import TarefaSerializer

class TarefaListCreate(generics.ListCreateAPIView):
    queryset = Tarefa.objects.all()
    serializer_class = TarefaSerializer
```

O DRF cuida da validacao, serializacao, tratamento de erros, autenticacao e muito mais.

### O que ja conhecemos vs o que vamos usar

| Conceito | Django Templates | Django REST Framework |
|----------|-----------------|----------------------|
| **View** | View (retorna HTML) | **APIView / GenericView** (retorna JSON) |
| **Validacao** | Form / ModelForm | **Serializer / ModelSerializer** |
| **Saida** | Template HTML | **JSON (Response)** |
| **URL** | `path()` → `view` | `path()` → `view.as_view()` |
| **Quem consome** | Navegador | **Qualquer cliente** (app, SPA, outro servidor) |

> **A logica e a mesma!** Muda o formato de saida (HTML → JSON) e a validacao (Form → Serializer).

---

## 3. Instalacao e Configuracao

### 3.1 Instalar os pacotes

Com o ambiente virtual ativado, instale o DRF e o SimpleJWT:

```bash
pip install djangorestframework djangorestframework-simplejwt
```

> **O que estamos instalando?**
> - `djangorestframework` — o framework principal para criar APIs
> - `djangorestframework-simplejwt` — autenticacao com JWT (JSON Web Tokens)

### 3.2 Adicionar ao `INSTALLED_APPS`

Abra o arquivo `django_tutorial/settings.py` e adicione `'rest_framework'` na lista `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'polls',
    'core',
    'portfolio',
    'rest_framework',  # Django REST Framework
]
```

### 3.3 Configurar o DRF no `settings.py`

Adicione ao final do arquivo `django_tutorial/settings.py` as configuracoes do DRF:

```python
# ─── Configuracoes do Django REST Framework ───

REST_FRAMEWORK = {
    # Define que, por padrao, todas as views exigem autenticacao
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT (principal)
        'rest_framework.authentication.SessionAuthentication',  # Sessao (para API navegavel)
    ],
    # Define que, por padrao, apenas usuarios autenticados podem acessar
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# ─── Configuracoes do SimpleJWT ───

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),   # Token de acesso vale 30 minutos
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),       # Token de refresh vale 1 dia
}
```

> **O que cada configuracao faz?**
>
> - `DEFAULT_AUTHENTICATION_CLASSES` — define como o DRF verifica quem e o usuario (JWT + sessao)
> - `DEFAULT_PERMISSION_CLASSES` — define que apenas usuarios autenticados acessam os endpoints
> - `ACCESS_TOKEN_LIFETIME` — tempo que o token de acesso fica valido
> - `REFRESH_TOKEN_LIFETIME` — tempo que o token de refresh fica valido (usado para renovar o access token)

### Comparacao de fluxos: Templates vs DRF

Antes de criar nosso app, veja como os fluxos se comparam:

```
Django Templates (o que ja fizemos):
  urls.py  →  views.py  →  forms.py  →  template.html  →  Pagina HTML (navegador)

Django REST Framework (o que vamos fazer):
  urls.py  →  views.py  →  serializers.py  →  Response JSON (qualquer cliente)
```

Perceba: **a estrutura e quase identica!**
- `forms.py` vira `serializers.py`
- `Template HTML` vira `Response JSON`
- Nao precisamos de templates!

---

## 4. Criando o App e Model

### 4.1 Criar o app `tarefas`

```bash
python manage.py startapp tarefas
```

### 4.2 Registrar o app no `settings.py`

Adicione `'tarefas'` ao `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'polls',
    'core',
    'portfolio',
    'rest_framework',
    'tarefas',  # Nosso app de tarefas
]
```

### 4.3 Criar o Model `Tarefa`

Abra `tarefas/models.py` e substitua o conteudo por:

```python
from django.db import models


class Tarefa(models.Model):
    """
    Modelo que representa uma tarefa.
    Cada tarefa tem um titulo, descricao, status de conclusao
    e a data em que foi criada.
    """

    # Campo de texto curto (max 200 caracteres) — obrigatorio
    titulo = models.CharField(max_length=200)

    # Campo de texto longo — opcional (blank=True permite vazio no formulario)
    descricao = models.TextField(blank=True)

    # Campo booleano — por padrao, a tarefa nao esta concluida
    concluida = models.BooleanField(default=False)

    # Data e hora automatica — preenchido automaticamente ao criar
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ordena por data de criacao (mais recente primeiro)
        ordering = ['-criado_em']

    def __str__(self):
        # Representacao em texto da tarefa (aparece no admin)
        return self.titulo
```

### 4.4 Criar e aplicar a migracao

```bash
python manage.py makemigrations tarefas
python manage.py migrate
```

> **O que aconteceu?**
> - `makemigrations` — criou um arquivo de migracao descrevendo a tabela a ser criada
> - `migrate` — executou a migracao e criou a tabela no banco de dados

### 4.5 Registrar no Admin (opcional, mas recomendado)

Abra `tarefas/admin.py` e adicione:

```python
from django.contrib import admin
from .models import Tarefa


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    # Colunas exibidas na listagem
    list_display = ['titulo', 'concluida', 'criado_em']

    # Filtro lateral por status
    list_filter = ['concluida']

    # Campo de busca
    search_fields = ['titulo', 'descricao']
```

### 4.6 Criar o Serializer

Serializers sao o "tradutor" entre objetos Django e JSON. Eles fazem duas coisas:

1. **Serializacao:** converte um objeto Python (model) em JSON (para enviar ao cliente)
2. **Desserializacao:** converte JSON recebido do cliente em um objeto Python (para salvar no banco)

Crie o arquivo `tarefas/serializers.py`:

```python
from rest_framework import serializers
from .models import Tarefa


class TarefaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Tarefa.
    ModelSerializer gera automaticamente os campos
    com base no modelo, incluindo validacao.
    """

    class Meta:
        # Qual modelo este serializer representa
        model = Tarefa

        # Quais campos incluir na API
        # '__all__' inclui todos, mas e melhor ser explicito:
        fields = ['id', 'titulo', 'descricao', 'concluida', 'criado_em']

        # Campos que so podem ser lidos (nao aceitar no POST/PUT)
        read_only_fields = ['id', 'criado_em']
```

> **Por que usar `ModelSerializer` em vez de `Serializer`?**
>
> O `ModelSerializer` lê o modelo e gera automaticamente:
> - Os campos com os tipos corretos
> - As validacoes (CharField com max_length, BooleanField, etc.)
> - Os metodos `create()` e `update()`
>
> Com `Serializer` puro, voce teria que definir tudo manualmente.

---

## 5. Criando Views — Evolucao dos Estilos

Agora vamos implementar a **mesma funcionalidade** (listar e criar tarefas) de **tres formas diferentes**, para que voce entenda a evolucao dos estilos no DRF.

### 5.1 Function-Based Views (`@api_view`)

Este e o estilo mais simples e parecido com Django puro. Usa funcoes decoradas com `@api_view`.

Abra `tarefas/views.py` e adicione:

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response  # Substitui o HttpResponse / render()
from rest_framework import status             # Codigos HTTP (200, 201, 400...)
from .models import Tarefa
from .serializers import TarefaSerializer


# ─── Estilo 1: Function-Based Views (@api_view) ───

# URL: path('v1/', views.tarefa_list_create_fbv)

@api_view(['GET', 'POST'])  # Define quais metodos HTTP sao aceitos
def tarefa_list_create_fbv(request):
    """
    GET  /api/tarefas/v1/ → Lista todas as tarefas
    POST /api/tarefas/v1/ → Cria uma nova tarefa
    """

    if request.method == 'GET':
        tarefas = Tarefa.objects.all()
        serializer = TarefaSerializer(tarefas, many=True)
        # Response() = substitui o render() do Django
        # Em vez de HTML, retorna JSON automaticamente!
        return Response(serializer.data)             # ---> JSON com lista de tarefas

    elif request.method == 'POST':
        # request.data = corpo JSON enviado pelo cliente (substitui request.POST)
        serializer = TarefaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)   # ---> 201
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # ---> 400


# URL: path('v1/<int:pk>/', views.tarefa_detail_fbv)

@api_view(['GET', 'PUT', 'DELETE'])
def tarefa_detail_fbv(request, pk):
    """
    GET    /api/tarefas/v1/<pk>/ → Retorna uma tarefa especifica
    PUT    /api/tarefas/v1/<pk>/ → Atualiza uma tarefa
    DELETE /api/tarefas/v1/<pk>/ → Exclui uma tarefa
    """

    try:
        tarefa = Tarefa.objects.get(pk=pk)
    except Tarefa.DoesNotExist:
        return Response(
            {'erro': 'Tarefa nao encontrada'},
            status=status.HTTP_404_NOT_FOUND          # ---> 404
        )

    if request.method == 'GET':
        serializer = TarefaSerializer(tarefa)
        return Response(serializer.data)               # ---> JSON do objeto

    elif request.method == 'PUT':
        serializer = TarefaSerializer(tarefa, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)            # ---> JSON atualizado
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        tarefa.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  # ---> sem corpo, so status
```

> **O que e o `Response()`?**
>
> O `Response` do DRF substitui o `render()` ou `HttpResponse()` do Django. Em vez de retornar HTML, ele retorna **JSON automaticamente**. Tambem aceita um parametro `status` para definir o codigo HTTP da resposta.

**Vantagens:**
- Facil de entender para quem vem do Django puro
- Controle total sobre o que acontece

**Desvantagens:**
- Muito codigo repetitivo (boilerplate)
- Precisa tratar cada metodo HTTP manualmente
- Precisa buscar o objeto manualmente (try/except)

---

### 5.2 Class-Based Views (`APIView`)

O mesmo codigo, agora organizado em classes. Cada metodo HTTP vira um metodo da classe.

Adicione ao `tarefas/views.py`:

```python
from rest_framework.views import APIView


# ─── Estilo 2: Class-Based Views (APIView) ───

# URL: path('v2/', views.TarefaListCreateAPIView.as_view())

class TarefaListCreateAPIView(APIView):
    """
    GET  /api/tarefas/v2/ → Lista todas as tarefas
    POST /api/tarefas/v2/ → Cria uma nova tarefa
    """

    def get(self, request):                          # GET /api/tarefas/v2/
        tarefas = Tarefa.objects.all()
        serializer = TarefaSerializer(tarefas, many=True)
        return Response(serializer.data)             # ---> JSON lista

    def post(self, request):                         # POST /api/tarefas/v2/
        serializer = TarefaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# URL: path('v2/<int:pk>/', views.TarefaDetailAPIView.as_view())

class TarefaDetailAPIView(APIView):
    """
    GET    /api/tarefas/v2/<pk>/ → Retorna uma tarefa
    PUT    /api/tarefas/v2/<pk>/ → Atualiza uma tarefa
    DELETE /api/tarefas/v2/<pk>/ → Exclui uma tarefa
    """

    def get_object(self, pk):
        try:
            return Tarefa.objects.get(pk=pk)
        except Tarefa.DoesNotExist:
            return None

    def get(self, request, pk):                      # GET /api/tarefas/v2/1/
        tarefa = self.get_object(pk)
        if tarefa is None:
            return Response(
                {'erro': 'Tarefa nao encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TarefaSerializer(tarefa)
        return Response(serializer.data)

    def put(self, request, pk):                      # PUT /api/tarefas/v2/1/
        tarefa = self.get_object(pk)
        if tarefa is None:
            return Response(
                {'erro': 'Tarefa nao encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TarefaSerializer(tarefa, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):                   # DELETE /api/tarefas/v2/1/
        tarefa = self.get_object(pk)
        if tarefa is None:
            return Response(
                {'erro': 'Tarefa nao encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        tarefa.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

**Vantagens:**
- Mais organizado que funcoes — cada metodo HTTP e um metodo da classe
- Facil de adicionar metodos extras
- `get_object` evita repeticao dentro da mesma classe

**Desvantagens:**
- Ainda e bastante codigo manual
- O padrao CRUD se repete em todo app — nao aproveita o que o DRF oferece

---

### 5.3 Generic Views (`generics`) — RECOMENDADO

Este e o estilo **recomendado** para a maioria dos casos. O DRF ja tem classes prontas para as operacoes CRUD mais comuns. Voce so precisa informar o **model** e o **serializer**.

Adicione ao `tarefas/views.py`:

```python
from rest_framework import generics


# ─── Estilo 3: Generic Views (RECOMENDADO) ───

# URL: path('v3/', views.TarefaListCreate.as_view())

class TarefaListCreate(generics.ListCreateAPIView):
    """
    GET  /api/tarefas/v3/ → Lista todas as tarefas
    POST /api/tarefas/v3/ → Cria uma nova tarefa

    ListCreateAPIView combina:
    - ListModelMixin (GET → listar)
    - CreateModelMixin (POST → criar)
    """

    queryset = Tarefa.objects.all()       # de onde vem os dados
    serializer_class = TarefaSerializer   # como traduzir para JSON


# URL: path('v3/<int:pk>/', views.TarefaDetail.as_view())

class TarefaDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/tarefas/v3/<pk>/ → Retorna uma tarefa
    PUT    /api/tarefas/v3/<pk>/ → Atualiza uma tarefa (completo)
    PATCH  /api/tarefas/v3/<pk>/ → Atualiza uma tarefa (parcial)
    DELETE /api/tarefas/v3/<pk>/ → Exclui uma tarefa

    RetrieveUpdateDestroyAPIView combina:
    - RetrieveModelMixin (GET → detalhe)
    - UpdateModelMixin (PUT/PATCH → atualizar)
    - DestroyModelMixin (DELETE → excluir)
    """

    queryset = Tarefa.objects.all()
    serializer_class = TarefaSerializer
```

**Perceba a diferenca!** Apenas **4 linhas de codigo** em cada classe (sem contar comentarios) e temos o CRUD completo. O DRF cuida de:

- Buscar o objeto pelo `pk`
- Retornar 404 se nao encontrar
- Serializar/desserializar os dados
- Validar os dados
- Retornar os codigos de status corretos

**Vantagens:**
- Codigo minimo — principio DRY (Don't Repeat Yourself)
- Menos bugs — menos codigo manual significa menos chance de erro
- Padronizado — todo desenvolvedor DRF reconhece esse padrao

**Desvantagens:**
- Precisa conhecer as classes disponiveis (curva de aprendizado)
- Para logica muito customizada, pode ser necessario sobrescrever metodos

### Como funciona por dentro?

As Generic Views sao construidas com **Mixins**. Cada Mixin adiciona uma funcionalidade:

| Mixin | Metodo | Acao |
|-------|--------|------|
| `ListModelMixin` | `.list()` | Lista objetos (GET) |
| `CreateModelMixin` | `.create()` | Cria objeto (POST) |
| `RetrieveModelMixin` | `.retrieve()` | Retorna um objeto (GET com pk) |
| `UpdateModelMixin` | `.update()` | Atualiza objeto (PUT/PATCH) |
| `DestroyModelMixin` | `.destroy()` | Exclui objeto (DELETE) |

As classes como `ListCreateAPIView` simplesmente **combinam** esses Mixins:

```python
# Internamente, ListCreateAPIView e assim:
class ListCreateAPIView(ListModelMixin, CreateModelMixin, GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
```

### Classes Generic disponiveis

| Classe | Metodos HTTP | Uso |
|--------|-------------|-----|
| `ListAPIView` | GET | Apenas listar |
| `CreateAPIView` | POST | Apenas criar |
| `RetrieveAPIView` | GET (com pk) | Apenas detalhe |
| `UpdateAPIView` | PUT, PATCH | Apenas atualizar |
| `DestroyAPIView` | DELETE | Apenas excluir |
| `ListCreateAPIView` | GET, POST | Listar + Criar |
| `RetrieveUpdateAPIView` | GET, PUT, PATCH | Detalhe + Atualizar |
| `RetrieveDestroyAPIView` | GET, DELETE | Detalhe + Excluir |
| `RetrieveUpdateDestroyAPIView` | GET, PUT, PATCH, DELETE | Detalhe + Atualizar + Excluir |

---

### 5.4 Breve mencao a ViewSets e Routers

Existe um nivel ainda mais alto de abstracao: **ViewSets** combinados com **Routers**.

```python
# Exemplo conceitual — NAO vamos usar neste tutorial
from rest_framework import viewsets

class TarefaViewSet(viewsets.ModelViewSet):
    queryset = Tarefa.objects.all()
    serializer_class = TarefaSerializer

# No urls.py:
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('tarefas', TarefaViewSet)
# Gera automaticamente TODAS as URLs (list, create, retrieve, update, delete)
```

Com ViewSets + Routers, **uma unica classe** gera todas as rotas automaticamente. Porem:

- Voce perde visibilidade sobre quais URLs existem
- Customizacoes ficam menos obvias
- Para quem esta aprendendo, e mais dificil entender o que acontece

**Neste curso, vamos usar Generic Views** porque oferecem um bom equilibrio entre simplicidade e controle. Voce sabe exatamente quais endpoints existem e pode customizar cada um facilmente.

---

## 6. Configurando URLs

### 6.1 URLs do app `tarefas`

Crie o arquivo `tarefas/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'tarefas'

urlpatterns = [
    # ─── Estilo 1: Function-Based Views ───
    path(
        'v1/',
        views.tarefa_list_create_fbv,
        name='lista-fbv',
    ),
    path(
        'v1/<int:pk>/',
        views.tarefa_detail_fbv,
        name='detalhe-fbv',
    ),

    # ─── Estilo 2: Class-Based Views (APIView) ───
    path(
        'v2/',
        views.TarefaListCreateAPIView.as_view(),
        name='lista-cbv',
    ),
    path(
        'v2/<int:pk>/',
        views.TarefaDetailAPIView.as_view(),
        name='detalhe-cbv',
    ),

    # ─── Estilo 3: Generic Views (RECOMENDADO) ───
    path(
        'v3/',
        views.TarefaListCreate.as_view(),
        name='lista-generic',
    ),
    path(
        'v3/<int:pk>/',
        views.TarefaDetail.as_view(),
        name='detalhe-generic',
    ),
]
```

> **Por que v1, v2, v3?**
>
> E apenas para fins didaticos — para que os tres estilos coexistam no mesmo projeto e voce possa comparar. Em um projeto real, voce escolheria **um unico estilo** (de preferencia Generic Views).

### 6.2 Incluir no `urls.py` principal

Abra `django_tutorial/urls.py` e adicione as rotas de tarefas e JWT:

```python
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('polls/', include('polls.urls')),
    path('portfolio/', include('portfolio.urls')),

    # ─── API de Tarefas ───
    path('api/tarefas/', include('tarefas.urls')),

    # ─── Autenticacao JWT ───
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

---

## 7. Autenticacao com Token

### 7.1 TokenAuthentication (DRF nativo)

O DRF possui um sistema de autenticacao por token embutido (`rest_framework.authtoken`). Funciona assim:

- Cada usuario recebe **um unico token fixo**
- O token e enviado no header: `Authorization: Token abc123...`
- Simples de configurar, bom para casos basicos

Porem, esse token **nao expira** (a menos que voce implemente manualmente) e nao tem mecanismo de renovacao. Para aplicacoes reais, o **JWT** e mais seguro e flexivel.

### 7.2 SimpleJWT (Padrao de mercado)

O **SimpleJWT** e o que vamos usar. Ele implementa o padrao **JSON Web Token**, que e amplamente utilizado na industria.

#### Como funciona o JWT?

```
1. LOGIN (obter tokens)
   POST /api/token/
   {"username": "admin", "password": "senha123"}
        │
        ▼
   Resposta:
   {
     "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",   ← Token de ACESSO (curta duracao)
     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."   ← Token de REFRESH (longa duracao)
   }

2. USAR A API (com access token)
   GET /api/tarefas/v3/
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi...
        │
        ▼
   Resposta: lista de tarefas (200 OK)

3. TOKEN EXPIROU? (renovar com refresh token)
   POST /api/token/refresh/
   {"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."}
        │
        ▼
   Resposta:
   {"access": "eyJ0eXAiOiJKV1QiLCJhbG..."}  ← Novo token de acesso
```

#### Access Token vs Refresh Token

| | Access Token | Refresh Token |
|---|---|---|
| **Para que serve** | Acessar endpoints protegidos | Obter um novo access token |
| **Duracao** | Curta (30 min no nosso caso) | Longa (1 dia no nosso caso) |
| **Enviado em** | Toda requisicao a API | Apenas para renovar o access token |
| **Se vazar** | Risco menor (expira rapido) | Risco maior (permite gerar novos tokens) |

A configuracao do SimpleJWT ja foi feita no passo 3.3 (no `settings.py`). As URLs de token ja foram configuradas no passo 6.2.

---

## 8. GenericView Autenticada — Pegando o Usuario da Request

Agora que temos autenticacao configurada, vamos ver como **usar o usuario logado dentro da GenericView**. Isso e essencial para:

- Salvar **quem criou** a tarefa
- Filtrar para que cada usuario veja **apenas suas proprias tarefas**

### 8.1 Adicionar campo `responsavel` no Model

Abra `tarefas/models.py` e adicione o campo `responsavel`:

```python
from django.db import models
from django.conf import settings  # Para referenciar o modelo de usuario


class Tarefa(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    concluida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    # Novo campo: quem criou a tarefa
    # null=True e blank=True para nao quebrar tarefas ja existentes
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,       # Referencia o modelo User do Django
        on_delete=models.CASCADE,       # Se o usuario for excluido, exclui as tarefas dele
        related_name='tarefas',         # Permite acessar: user.tarefas.all()
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo
```

Aplique a migracao:

```bash
python manage.py makemigrations tarefas
python manage.py migrate
```

### 8.2 Atualizar o Serializer

Abra `tarefas/serializers.py` e atualize:

```python
from rest_framework import serializers
from .models import Tarefa


class TarefaSerializer(serializers.ModelSerializer):
    # Exibe o username do responsavel (somente leitura)
    responsavel = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Tarefa
        fields = ['id', 'titulo', 'descricao', 'concluida', 'criado_em', 'responsavel']
        read_only_fields = ['id', 'criado_em', 'responsavel']
```

> **Por que `responsavel` e `read_only`?**
>
> Porque o responsavel nao vem do JSON enviado pelo cliente. Ele e preenchido **automaticamente** com o usuario logado (via `request.user`). O cliente nao deve poder escolher o responsavel.

### 8.3 Atualizar a GenericView — `perform_create` e `get_queryset`

Aqui esta a parte mais importante. Abra `tarefas/views.py` e atualize as Generic Views:

```python
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Tarefa
from .serializers import TarefaSerializer


# ─── Generic Views com autenticacao (VERSAO FINAL) ───

# URL: path('v3/', views.TarefaListCreate.as_view())

class TarefaListCreate(generics.ListCreateAPIView):
    """
    GET  /api/tarefas/v3/ → Lista as tarefas do usuario logado
    POST /api/tarefas/v3/ → Cria uma tarefa vinculada ao usuario logado
    """

    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtra as tarefas para retornar APENAS as do usuario logado.
        request.user contem o usuario autenticado pelo JWT.
        """
        return Tarefa.objects.filter(responsavel=self.request.user)

    def perform_create(self, serializer):
        """
        Ao criar uma tarefa, preenche automaticamente o campo 'responsavel'
        com o usuario que esta fazendo a requisicao (request.user).
        """
        serializer.save(responsavel=self.request.user)


# URL: path('v3/<int:pk>/', views.TarefaDetail.as_view())

class TarefaDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/tarefas/v3/<pk>/ → Retorna uma tarefa do usuario
    PUT    /api/tarefas/v3/<pk>/ → Atualiza uma tarefa do usuario
    PATCH  /api/tarefas/v3/<pk>/ → Atualiza parcialmente
    DELETE /api/tarefas/v3/<pk>/ → Exclui uma tarefa do usuario
    """

    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Garante que o usuario so pode ver/editar/excluir SUAS tarefas.
        Se tentar acessar a tarefa de outro usuario, retorna 404.
        """
        return Tarefa.objects.filter(responsavel=self.request.user)
```

### O que mudou?

| Metodo | O que faz | Quando e chamado |
|--------|-----------|-----------------|
| `get_queryset()` | Filtra os dados — retorna so as tarefas do `request.user` | Em TODAS as operacoes (GET, PUT, DELETE...) |
| `perform_create()` | Preenche o `responsavel` automaticamente com `request.user` | Apenas no POST (criacao) |
| `request.user` | O usuario autenticado pelo JWT | Disponivel em qualquer view autenticada |

> **Importante:** `request.user` so funciona porque configuramos o `JWTAuthentication` no `settings.py`. O DRF decodifica o token JWT e preenche `request.user` automaticamente.

### 8.4 Testando com curl

```bash
# Login — obter token
curl -X POST http://127.0.0.1:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "sua_senha_aqui"}'

# Salvar o token
TOKEN="cole_o_access_token_aqui"

# Criar tarefa (o responsavel e preenchido automaticamente!)
curl -X POST http://127.0.0.1:8000/api/tarefas/v3/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"titulo": "Minha primeira tarefa autenticada"}'

# Resposta — note o campo "responsavel"!
# {
#     "id": 1,
#     "titulo": "Minha primeira tarefa autenticada",
#     "descricao": "",
#     "concluida": false,
#     "criado_em": "2026-04-27T15:00:00.000000Z",
#     "responsavel": "admin"
# }

# Listar — so mostra as tarefas do usuario logado
curl http://127.0.0.1:8000/api/tarefas/v3/ \
     -H "Authorization: Bearer $TOKEN"
```

> **Teste extra:** Crie outro usuario no admin, faca login com ele e veja que cada usuario so ve suas proprias tarefas!

---

## 9. Exemplo Pratico: Login + Endpoint Protegido (passo a passo)

### 8.1 Criar um superusuario

Se voce ainda nao tem um superusuario, crie agora:

```bash
python manage.py createsuperuser
```

Preencha:
- **Username:** admin
- **Email:** admin@uast.edu.br
- **Password:** (escolha uma senha)

### 8.2 Iniciar o servidor

```bash
python manage.py runserver
```

### 8.3 Testar sem autenticacao (deve falhar)

Abra outro terminal e tente acessar a API sem token:

```bash
curl http://127.0.0.1:8000/api/tarefas/v3/
```

**Resposta esperada (401 Unauthorized):**

```json
{
    "detail": "Authentication credentials were not provided."
}
```

Isso confirma que a API esta protegida. Sem autenticacao, ninguem acessa.

### 8.4 Fazer login e obter o token JWT

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "sua_senha_aqui"}'
```

**Resposta esperada (200 OK):**

```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

> **Importante:** Copie o valor do campo `access`. Voce vai usar nas proximas requisicoes.

### 8.5 Acessar endpoint protegido com o token

Agora use o access token para acessar a API. Substitua `SEU_TOKEN_AQUI` pelo token copiado:

```bash
curl http://127.0.0.1:8000/api/tarefas/v3/ \
     -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

**Resposta esperada (200 OK):**

```json
[]
```

A lista esta vazia porque ainda nao criamos nenhuma tarefa. Mas o importante e que agora temos acesso.

### 8.6 Usando a API Navegavel do DRF

O DRF oferece uma **interface web** para testar a API diretamente no navegador. Para usa-la:

1. Acesse [http://127.0.0.1:8000/api/tarefas/v3/](http://127.0.0.1:8000/api/tarefas/v3/) no navegador
2. Faca login pelo Django Admin primeiro: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
3. Volte para a URL da API — agora voce vera a interface do DRF

A API navegavel permite:
- Ver os dados formatados
- Enviar requisicoes POST usando um formulario
- Testar diferentes metodos HTTP
- Ver os headers da resposta

> **Nota:** A API navegavel funciona porque configuramos `SessionAuthentication` junto com o JWT no `settings.py`. A sessao do admin e usada quando voce acessa pelo navegador.

---

## 10. Testando a API

Vamos testar todas as operacoes CRUD usando `curl`. Em todos os comandos abaixo, substitua `SEU_TOKEN_AQUI` pelo seu access token.

> **Dica:** Para facilitar, salve o token em uma variavel do terminal:
> ```bash
> TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
> ```
> E use `$TOKEN` nos comandos.

### 9.1 CRIAR uma tarefa (POST)

```bash
curl -X POST http://127.0.0.1:8000/api/tarefas/v3/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
           "titulo": "Estudar Django REST Framework",
           "descricao": "Completar o tutorial de DRF da aula de Programacao Web"
         }'
```

**Resposta esperada (201 Created):**

```json
{
    "id": 1,
    "titulo": "Estudar Django REST Framework",
    "descricao": "Completar o tutorial de DRF da aula de Programacao Web",
    "concluida": false,
    "criado_em": "2026-04-27T14:30:00.000000Z"
}
```

Crie mais algumas tarefas para testar:

```bash
curl -X POST http://127.0.0.1:8000/api/tarefas/v3/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"titulo": "Fazer exercicio de API", "descricao": "Criar endpoints para o portfolio"}'

curl -X POST http://127.0.0.1:8000/api/tarefas/v3/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"titulo": "Revisar para a prova", "descricao": "Estudar REST, HTTP e autenticacao"}'
```

### 9.2 LISTAR todas as tarefas (GET)

```bash
curl http://127.0.0.1:8000/api/tarefas/v3/ \
     -H "Authorization: Bearer $TOKEN"
```

**Resposta esperada (200 OK):**

```json
[
    {
        "id": 3,
        "titulo": "Revisar para a prova",
        "descricao": "Estudar REST, HTTP e autenticacao",
        "concluida": false,
        "criado_em": "2026-04-27T14:32:00.000000Z"
    },
    {
        "id": 2,
        "titulo": "Fazer exercicio de API",
        "descricao": "Criar endpoints para o portfolio",
        "concluida": false,
        "criado_em": "2026-04-27T14:31:00.000000Z"
    },
    {
        "id": 1,
        "titulo": "Estudar Django REST Framework",
        "descricao": "Completar o tutorial de DRF da aula de Programacao Web",
        "concluida": false,
        "criado_em": "2026-04-27T14:30:00.000000Z"
    }
]
```

> Note que as tarefas vem ordenadas pela mais recente primeiro (por causa do `ordering = ['-criado_em']` no model).

### 9.3 VER uma tarefa especifica (GET com pk)

```bash
curl http://127.0.0.1:8000/api/tarefas/v3/1/ \
     -H "Authorization: Bearer $TOKEN"
```

**Resposta esperada (200 OK):**

```json
{
    "id": 1,
    "titulo": "Estudar Django REST Framework",
    "descricao": "Completar o tutorial de DRF da aula de Programacao Web",
    "concluida": false,
    "criado_em": "2026-04-27T14:30:00.000000Z"
}
```

### 9.4 ATUALIZAR uma tarefa completa (PUT)

O PUT substitui **todos** os campos. Voce precisa enviar todos os campos obrigatorios:

```bash
curl -X PUT http://127.0.0.1:8000/api/tarefas/v3/1/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
           "titulo": "Estudar Django REST Framework",
           "descricao": "Tutorial completo! Agora fazer os exercicios.",
           "concluida": true
         }'
```

**Resposta esperada (200 OK):**

```json
{
    "id": 1,
    "titulo": "Estudar Django REST Framework",
    "descricao": "Tutorial completo! Agora fazer os exercicios.",
    "concluida": true,
    "criado_em": "2026-04-27T14:30:00.000000Z"
}
```

### 9.5 ATUALIZAR parcialmente (PATCH)

O PATCH atualiza **apenas** os campos enviados:

```bash
curl -X PATCH http://127.0.0.1:8000/api/tarefas/v3/2/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"concluida": true}'
```

**Resposta esperada (200 OK):**

```json
{
    "id": 2,
    "titulo": "Fazer exercicio de API",
    "descricao": "Criar endpoints para o portfolio",
    "concluida": true,
    "criado_em": "2026-04-27T14:31:00.000000Z"
}
```

> Note que apenas o campo `concluida` mudou. Os demais campos permaneceram iguais.

### 9.6 EXCLUIR uma tarefa (DELETE)

```bash
curl -X DELETE http://127.0.0.1:8000/api/tarefas/v3/3/ \
     -H "Authorization: Bearer $TOKEN"
```

**Resposta esperada (204 No Content):**

Nenhum corpo na resposta — apenas o status 204 indicando que foi excluido com sucesso.

Confirme listando novamente:

```bash
curl http://127.0.0.1:8000/api/tarefas/v3/ \
     -H "Authorization: Bearer $TOKEN"
```

A tarefa 3 nao aparece mais na lista.

### 9.7 Testar com token expirado ou invalido

```bash
curl http://127.0.0.1:8000/api/tarefas/v3/ \
     -H "Authorization: Bearer token_invalido_qualquer"
```

**Resposta esperada (401 Unauthorized):**

```json
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is invalid or expired"
        }
    ]
}
```

### 9.8 Renovar o token (quando o access token expirar)

Quando o access token expirar (apos 30 minutos), use o refresh token para obter um novo:

```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
     -H "Content-Type: application/json" \
     -d '{"refresh": "SEU_REFRESH_TOKEN_AQUI"}'
```

**Resposta esperada (200 OK):**

```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

Use o novo access token para continuar fazendo requisicoes.

---

## 11. Resumo

### Comparacao dos 3 estilos de views

| Caracteristica | Function-Based (`@api_view`) | Class-Based (`APIView`) | Generic Views (`generics`) |
|---|---|---|---|
| **Complexidade** | Baixa | Media | Baixa (apos aprender) |
| **Quantidade de codigo** | Alta | Media | Muito baixa |
| **Controle** | Total | Total | Alto (pode sobrescrever metodos) |
| **Repeticao de codigo** | Muita | Alguma | Quase nenhuma |
| **Curva de aprendizado** | Facil | Facil | Precisa conhecer as classes |
| **Recomendado para** | Scripts rapidos, endpoints simples | Logica muito customizada | Maioria dos casos (padrao) |

### Quando usar cada estilo?

- **`@api_view`** — Endpoints muito simples ou que nao seguem o padrao CRUD (ex: um endpoint que retorna estatisticas)
- **`APIView`** — Quando voce precisa de controle total sobre a logica e nao se encaixa nos padroes do DRF
- **`generics` (GenericViews)** — Para 90% dos casos. CRUD padrao com pouco codigo. **Este e o estilo recomendado.**
- **`ViewSets + Routers`** — Quando voce quer o maximo de automacao e nao precisa de controle fino sobre as URLs

### Resumo da autenticacao

| Tipo | Como funciona | Quando usar |
|---|---|---|
| **SessionAuthentication** | Usa cookies de sessao do Django | API navegavel no browser, apps Django tradicionais |
| **TokenAuthentication** | Token fixo por usuario | APIs simples, scripts internos |
| **JWT (SimpleJWT)** | Dois tokens (access + refresh), com expiracao | **Padrao de mercado** — apps mobile, SPAs, microservicos |

### Estrutura final do app `tarefas`

```
tarefas/
├── __init__.py
├── admin.py            ← Registro do model no admin
├── apps.py
├── migrations/
│   └── 0001_initial.py ← Migracao do banco
├── models.py           ← Model Tarefa
├── serializers.py      ← TarefaSerializer (converte model ↔ JSON)
├── urls.py             ← Rotas da API (v1, v2, v3)
├── views.py            ← Views nos 3 estilos
└── tests.py
```

### URLs configuradas

| URL | Metodo | Descricao |
|-----|--------|-----------|
| `/api/token/` | POST | Login — obter access e refresh tokens |
| `/api/token/refresh/` | POST | Renovar o access token |
| `/api/tarefas/v3/` | GET | Listar todas as tarefas |
| `/api/tarefas/v3/` | POST | Criar uma nova tarefa |
| `/api/tarefas/v3/<id>/` | GET | Ver uma tarefa especifica |
| `/api/tarefas/v3/<id>/` | PUT | Atualizar tarefa (todos os campos) |
| `/api/tarefas/v3/<id>/` | PATCH | Atualizar tarefa (parcial) |
| `/api/tarefas/v3/<id>/` | DELETE | Excluir uma tarefa |

