# Exercicio: Perfil do Aluno via API REST

## Contexto

Este exercicio e a **continuacao do exercicio da aula de Templates**. Na aula anterior, voce:

- Criou o model `Pessoal` no app `core` (nome, descricao, curso, periodo, email, git, linked, url_imagem)
- Registrou o model no Django Admin
- Atualizou os templates para exibir os dados do model

Na **aula de DRF**, voce aprendeu a criar APIs REST com Django REST Framework, usando serializers, views e autenticacao JWT.

Agora vamos **juntar tudo**: a pagina do portfolio (Templates) vai ganhar um botao **"Editar"** que permite atualizar os dados do perfil **via API**, usando JavaScript + JWT.

---

## O que vamos fazer

1. Vincular o model `Pessoal` ao usuario do Django (`ForeignKey → User`)
2. Criar um **Serializer** para o model `Pessoal`
3. Criar **views DRF** (Generic Views) para consultar e atualizar o perfil
4. Configurar as **URLs** da API do perfil
5. Atualizar o **template** `home.html` com um botao "Editar" e um formulario
6. Escrever o **JavaScript** que: faz login (obtem JWT) → chama a API → atualiza os dados na pagina

### Fluxo final

```
Pagina do Portfolio (Template Django)
        │
        │  Clica em "Editar"
        ▼
Modal pede username + password
        │
        │  JavaScript faz POST /api/token/
        ▼
Recebe JWT → salva no localStorage
        │
        │  JavaScript faz GET /api/perfil/
        ▼
Preenche formulario com dados atuais
        │
        │  Aluno edita e clica "Salvar"
        ▼
JavaScript faz PUT /api/perfil/
        │
        │  Resposta 200 OK
        ▼
Atualiza os dados na pagina (sem recarregar)
```

---

## Pre-requisitos

- Ter completado o exercicio da aula de Templates (models Pessoal, Certificado, Projeto)
- Ter completado a aula de DRF (DRF instalado, JWT configurado no `settings.py`)
- Ter um superusuario criado (`python manage.py createsuperuser`)
- Ter pelo menos um registro de `Pessoal` criado pelo Django Admin

---

## Passo 1: Vincular o Model `Pessoal` ao Usuario

Abra `core/models.py` e adicione um `ForeignKey` para o usuario:

```python
from django.db import models
from django.conf import settings


class Pessoal(models.Model):
    # Vincula o perfil a um usuario do Django
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
        null=True,
        blank=True,
    )

    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    curso = models.CharField(max_length=200)
    periodo = models.CharField(max_length=50)
    email = models.EmailField()
    git = models.URLField(blank=True)
    linked = models.URLField(blank=True)
    url_imagem = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Perfil Pessoal'
        verbose_name_plural = 'Perfis Pessoais'

    def __str__(self):
        return self.nome
```

> **Por que `OneToOneField`?**
>
> Cada usuario tem **um unico perfil**, e cada perfil pertence a **um unico usuario**. O `OneToOneField` garante essa relacao 1:1. Com isso, podemos acessar `user.perfil` diretamente.

Aplique a migracao:

```bash
python manage.py makemigrations core
python manage.py migrate
```

Depois, va ao Django Admin e **vincule** o registro de `Pessoal` existente ao seu usuario (selecione o usuario no campo "usuario").

---

## Passo 2: Criar o Serializer

Crie o arquivo `core/serializers.py`:

```python
from rest_framework import serializers
from .models import Pessoal


class PessoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pessoal
        fields = [
            'id', 'nome', 'descricao', 'curso',
            'periodo', 'email', 'git', 'linked', 'url_imagem',
        ]
```

> **Note:** o campo `usuario` nao aparece nos `fields`. Assim como na aula de DRF (campo `responsavel`), o usuario e preenchido automaticamente via `request.user`. O cliente nao deve poder escolher a qual usuario o perfil pertence.

---

## Passo 3: Criar as Views

Abra `core/views.py` e adicione as views da API:

```python
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Pessoal
from .serializers import PessoalSerializer


# ─── Views de Templates (ja existentes) ───

def home(request):
    # Se voce ja alterou essa view no exercicio anterior, mantenha como esta
    return render(request, 'portfolio/home.html')


# ─── Views da API (novas) ───

class PerfilDetail(generics.RetrieveUpdateAPIView):
    """
    GET   /api/perfil/ → Retorna o perfil do usuario logado
    PUT   /api/perfil/ → Atualiza o perfil completo
    PATCH /api/perfil/ → Atualiza parcialmente
    """

    serializer_class = PessoalSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Em vez de buscar pelo pk da URL, busca pelo usuario logado.
        Se o perfil nao existir, cria um vazio automaticamente.
        """
        perfil, created = Pessoal.objects.get_or_create(
            usuario=self.request.user,
            defaults={'nome': self.request.user.username},
        )
        return perfil
```

### Entendendo a view

| Conceito | Explicacao |
|----------|-----------|
| `RetrieveUpdateAPIView` | Permite GET (ver) + PUT/PATCH (atualizar). Nao permite DELETE nem listagem. |
| `get_object()` | Sobrescrevemos para buscar pelo `request.user` em vez do `pk` da URL. |
| `get_or_create()` | Se o usuario ainda nao tem perfil, cria um automaticamente com o username como nome. |
| `permission_classes` | Exige autenticacao JWT para acessar. |

> **Por que nao usamos `RetrieveUpdateDestroyAPIView`?**
>
> Porque nao faz sentido deletar o proprio perfil. Queremos apenas ver e editar.

---

## Passo 4: Configurar as URLs

Crie (ou edite) o arquivo `core/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # API do perfil
    path('api/perfil/', views.PerfilDetail.as_view(), name='perfil-api'),
]
```

Abra `django_tutorial/urls.py` e inclua as URLs do core:

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

    # API de Tarefas (da aula DRF)
    path('api/tarefas/', include('tarefas.urls')),

    # API do Perfil
    path('', include('core.urls')),

    # Autenticacao JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

### Testar com curl

Antes de mexer no template, vamos confirmar que a API funciona:

```bash
# 1. Obter token
curl -X POST http://127.0.0.1:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "sua_senha_aqui"}'

# 2. Salvar o token
TOKEN="cole_o_access_token_aqui"

# 3. Ver o perfil
curl http://127.0.0.1:8000/api/perfil/ \
     -H "Authorization: Bearer $TOKEN"

# 4. Atualizar o perfil
curl -X PATCH http://127.0.0.1:8000/api/perfil/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"nome": "Meu Nome Atualizado", "periodo": "6"}'
```

Se os testes funcionaram, a API esta pronta. Agora vamos integrar com o template.

---

## Passo 5: Atualizar o Template

Agora vamos adicionar ao template `home.html` um botao "Editar" que abre um modal com login e formulario de edicao.

Abra `portfolio/templates/portfolio/home.html` e adicione o botao de editar e o modal. Insira dentro do `{% block content %}`, **apos** as secoes existentes:

```html
<!-- Botao Editar Perfil -->
<div style="text-align: center; margin: 30px 0;">
    <button id="btn-editar" style="
        background-color: #3498db;
        color: white;
        border: none;
        padding: 12px 30px;
        font-size: 1.1em;
        border-radius: 5px;
        cursor: pointer;
    ">Editar Perfil</button>
</div>

<!-- Modal de Login -->
<div id="modal-login" style="
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 1000;
">
    <div style="
        background: white;
        max-width: 400px;
        margin: 100px auto;
        padding: 30px;
        border-radius: 8px;
    ">
        <h3 style="margin-bottom: 20px; color: #2c3e50;">Login para Editar</h3>
        <div style="margin-bottom: 15px;">
            <label>Username:</label><br>
            <input type="text" id="login-username" style="width: 100%; padding: 8px; margin-top: 5px;">
        </div>
        <div style="margin-bottom: 15px;">
            <label>Password:</label><br>
            <input type="password" id="login-password" style="width: 100%; padding: 8px; margin-top: 5px;">
        </div>
        <p id="login-erro" style="color: red; display: none;"></p>
        <button id="btn-login" style="
            background-color: #27ae60;
            color: white;
            border: none;
            padding: 10px 25px;
            border-radius: 5px;
            cursor: pointer;
        ">Entrar</button>
        <button id="btn-cancelar-login" style="
            background-color: #95a5a6;
            color: white;
            border: none;
            padding: 10px 25px;
            border-radius: 5px;
            cursor: pointer;
            margin-left: 10px;
        ">Cancelar</button>
    </div>
</div>

<!-- Modal de Edicao do Perfil -->
<div id="modal-editar" style="
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 1000;
    overflow-y: auto;
">
    <div style="
        background: white;
        max-width: 500px;
        margin: 50px auto;
        padding: 30px;
        border-radius: 8px;
    ">
        <h3 style="margin-bottom: 20px; color: #2c3e50;">Editar Perfil</h3>

        <div style="margin-bottom: 12px;">
            <label>Nome:</label><br>
            <input type="text" id="edit-nome" style="width: 100%; padding: 8px; margin-top: 5px;">
        </div>

        <div style="margin-bottom: 12px;">
            <label>Descricao:</label><br>
            <textarea id="edit-descricao" rows="3" style="width: 100%; padding: 8px; margin-top: 5px;"></textarea>
        </div>

        <div style="margin-bottom: 12px;">
            <label>Curso:</label><br>
            <input type="text" id="edit-curso" style="width: 100%; padding: 8px; margin-top: 5px;">
        </div>

        <div style="margin-bottom: 12px;">
            <label>Periodo:</label><br>
            <input type="text" id="edit-periodo" style="width: 100%; padding: 8px; margin-top: 5px;">
        </div>

        <div style="margin-bottom: 12px;">
            <label>E-mail:</label><br>
            <input type="email" id="edit-email" style="width: 100%; padding: 8px; margin-top: 5px;">
        </div>

        <div style="margin-bottom: 12px;">
            <label>GitHub:</label><br>
            <input type="url" id="edit-git" style="width: 100%; padding: 8px; margin-top: 5px;">
        </div>

        <div style="margin-bottom: 12px;">
            <label>LinkedIn:</label><br>
            <input type="url" id="edit-linked" style="width: 100%; padding: 8px; margin-top: 5px;">
        </div>

        <div style="margin-bottom: 12px;">
            <label>URL da Imagem:</label><br>
            <input type="url" id="edit-url_imagem" style="width: 100%; padding: 8px; margin-top: 5px;">
        </div>

        <p id="edit-sucesso" style="color: green; display: none;">Perfil atualizado!</p>
        <p id="edit-erro" style="color: red; display: none;"></p>

        <button id="btn-salvar" style="
            background-color: #27ae60;
            color: white;
            border: none;
            padding: 10px 25px;
            border-radius: 5px;
            cursor: pointer;
        ">Salvar</button>
        <button id="btn-cancelar-editar" style="
            background-color: #95a5a6;
            color: white;
            border: none;
            padding: 10px 25px;
            border-radius: 5px;
            cursor: pointer;
            margin-left: 10px;
        ">Cancelar</button>
    </div>
</div>
```

---

## Passo 6: Escrever o JavaScript

Ainda no `home.html`, adicione o seguinte `<script>` **antes** do fechamento do `{% endblock content %}`:

```html
<script>
// ─── Elementos do DOM ───

const btnEditar = document.getElementById('btn-editar');
const modalLogin = document.getElementById('modal-login');
const modalEditar = document.getElementById('modal-editar');

const btnLogin = document.getElementById('btn-login');
const btnCancelarLogin = document.getElementById('btn-cancelar-login');
const btnSalvar = document.getElementById('btn-salvar');
const btnCancelarEditar = document.getElementById('btn-cancelar-editar');

const loginErro = document.getElementById('login-erro');
const editSucesso = document.getElementById('edit-sucesso');
const editErro = document.getElementById('edit-erro');

// URL base da API
const API_BASE = 'http://127.0.0.1:8000';

// ─── Passo 1: Clicar em "Editar" ───

btnEditar.addEventListener('click', function() {
    // Verifica se ja tem um token salvo
    const token = localStorage.getItem('access_token');
    if (token) {
        // Ja esta logado, vai direto para o formulario
        carregarPerfil(token);
    } else {
        // Precisa fazer login primeiro
        modalLogin.style.display = 'block';
    }
});

// ─── Passo 2: Fazer Login (obter JWT) ───

btnLogin.addEventListener('click', function() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    // Esconde mensagem de erro anterior
    loginErro.style.display = 'none';

    // POST /api/token/ → obter access e refresh tokens
    fetch(API_BASE + '/api/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username, password: password }),
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Username ou senha incorretos');
        }
        return response.json();
    })
    .then(function(data) {
        // Salva os tokens no localStorage
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);

        // Fecha o modal de login
        modalLogin.style.display = 'none';

        // Carrega os dados do perfil e abre o formulario de edicao
        carregarPerfil(data.access);
    })
    .catch(function(erro) {
        loginErro.textContent = erro.message;
        loginErro.style.display = 'block';
    });
});

// ─── Passo 3: Carregar dados do perfil (GET /api/perfil/) ───

function carregarPerfil(token) {
    fetch(API_BASE + '/api/perfil/', {
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + token },
    })
    .then(function(response) {
        if (!response.ok) {
            // Token expirou ou invalido
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            modalLogin.style.display = 'block';
            throw new Error('Token expirado. Faca login novamente.');
        }
        return response.json();
    })
    .then(function(perfil) {
        // Preenche o formulario com os dados atuais
        document.getElementById('edit-nome').value = perfil.nome || '';
        document.getElementById('edit-descricao').value = perfil.descricao || '';
        document.getElementById('edit-curso').value = perfil.curso || '';
        document.getElementById('edit-periodo').value = perfil.periodo || '';
        document.getElementById('edit-email').value = perfil.email || '';
        document.getElementById('edit-git').value = perfil.git || '';
        document.getElementById('edit-linked').value = perfil.linked || '';
        document.getElementById('edit-url_imagem').value = perfil.url_imagem || '';

        // Abre o modal de edicao
        editSucesso.style.display = 'none';
        editErro.style.display = 'none';
        modalEditar.style.display = 'block';
    })
    .catch(function(erro) {
        console.error(erro);
    });
}

// ─── Passo 4: Salvar alteracoes (PUT /api/perfil/) ───

btnSalvar.addEventListener('click', function() {
    const token = localStorage.getItem('access_token');

    // Monta o objeto com os dados do formulario
    const dados = {
        nome: document.getElementById('edit-nome').value,
        descricao: document.getElementById('edit-descricao').value,
        curso: document.getElementById('edit-curso').value,
        periodo: document.getElementById('edit-periodo').value,
        email: document.getElementById('edit-email').value,
        git: document.getElementById('edit-git').value,
        linked: document.getElementById('edit-linked').value,
        url_imagem: document.getElementById('edit-url_imagem').value,
    };

    // PUT /api/perfil/ → atualiza o perfil completo
    fetch(API_BASE + '/api/perfil/', {
        method: 'PUT',
        headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dados),
    })
    .then(function(response) {
        if (!response.ok) {
            return response.json().then(function(erros) {
                throw new Error(JSON.stringify(erros));
            });
        }
        return response.json();
    })
    .then(function(perfil) {
        // Mostra mensagem de sucesso
        editSucesso.style.display = 'block';
        editErro.style.display = 'none';

        // Atualiza os dados na pagina (sem recarregar)
        atualizarPagina(perfil);
    })
    .catch(function(erro) {
        editErro.textContent = 'Erro ao salvar: ' + erro.message;
        editErro.style.display = 'block';
        editSucesso.style.display = 'none';
    });
});

// ─── Passo 5: Atualizar a pagina com os novos dados ───

function atualizarPagina(perfil) {
    // Atualiza os elementos HTML com os dados retornados pela API
    // Ajuste os seletores conforme a estrutura do seu template

    // Exemplo: se voce tem elementos com essas classes/ids
    const secaoDados = document.querySelector('.secao ul');
    if (secaoDados) {
        secaoDados.innerHTML =
            '<li><strong>Nome:</strong> ' + perfil.nome + '</li>' +
            '<li><strong>Curso:</strong> ' + perfil.curso + '</li>' +
            '<li><strong>Periodo:</strong> ' + perfil.periodo + '</li>' +
            '<li><strong>E-mail:</strong> ' + perfil.email + '</li>' +
            '<li><strong>GitHub:</strong> ' + perfil.git + '</li>' +
            '<li><strong>LinkedIn:</strong> ' + perfil.linked + '</li>';
    }

    // Atualiza o nome no perfil
    const perfilNome = document.querySelector('.perfil h2');
    if (perfilNome) {
        perfilNome.textContent = perfil.nome;
    }

    // Atualiza a descricao
    const secaoSobre = document.querySelectorAll('.secao')[0];
    if (secaoSobre) {
        const paragrafo = secaoSobre.querySelector('p');
        if (paragrafo) {
            paragrafo.textContent = perfil.descricao;
        }
    }

    // Atualiza a imagem
    const perfilImg = document.querySelector('.perfil img');
    if (perfilImg && perfil.url_imagem) {
        perfilImg.src = perfil.url_imagem;
    }
}

// ─── Botoes de cancelar ───

btnCancelarLogin.addEventListener('click', function() {
    modalLogin.style.display = 'none';
});

btnCancelarEditar.addEventListener('click', function() {
    modalEditar.style.display = 'none';
});
</script>
```

---

## Passo 7: Testar

1. Inicie o servidor:

```bash
python manage.py runserver
```

2. Acesse [http://127.0.0.1:8000/portfolio/](http://127.0.0.1:8000/portfolio/)

3. Clique em **"Editar Perfil"**

4. Faca login com seu usuario e senha

5. O formulario deve aparecer **preenchido** com os dados atuais do perfil

6. Altere alguns campos e clique em **"Salvar"**

7. Os dados na pagina devem atualizar **sem recarregar**

### O que esta acontecendo por baixo

```
[Clique em Editar]
        │
        ▼
[Modal Login]  ──POST /api/token/──→  [Django: SimpleJWT]
        │                                      │
        │              ←── { access, refresh } ─┘
        │
        │  localStorage.setItem('access_token', ...)
        │
        ▼
[GET /api/perfil/]  ──Bearer token──→  [Django: PerfilDetail.get_object()]
        │                                      │
        │         ←── { nome, curso, ... } ────┘
        │
        │  Preenche formulario
        │
        ▼
[Clique em Salvar]
        │
        ▼
[PUT /api/perfil/]  ──Bearer token──→  [Django: PerfilDetail.update()]
        │                                      │
        │         ←── { nome, curso, ... } ────┘
        │
        │  atualizarPagina(perfil)
        ▼
[Pagina atualizada sem recarregar!]
```

---

## Resumo dos conceitos praticados

| Conceito | Onde foi usado |
|----------|---------------|
| `ModelSerializer` | `core/serializers.py` — converte Pessoal ↔ JSON |
| `RetrieveUpdateAPIView` | `core/views.py` — GET + PUT/PATCH do perfil |
| `get_object()` | Busca o perfil pelo `request.user` (nao pelo pk da URL) |
| `get_or_create()` | Cria o perfil automaticamente se nao existir |
| `IsAuthenticated` | Exige JWT para acessar o endpoint |
| `fetch()` | JavaScript faz chamadas HTTP para a API |
| `localStorage` | Armazena o token JWT no navegador |
| `Authorization: Bearer` | Header que envia o token em cada requisicao |

---

## Desafio extra

1. Quando o usuario ja tem token salvo no `localStorage`, pular o login e ir direto para o formulario de edicao (ja implementado no codigo!)
2. Adicionar um botao **"Sair"** que remove o token do `localStorage`
3. Ao fechar o modal de edicao apos salvar, **recarregar a pagina** para que os dados do template Django tambem atualizem (dica: `location.reload()`)
