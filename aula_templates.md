# Aula: Templates no Django — Portfólio do Aluno

## Objetivo

Nesta aula vamos aprender como funciona o sistema de **templates** do Django. Vamos criar um portfólio pessoal do aluno usando:

- Um app `core` com o template **base** (layout compartilhado)
- Um app `portfolio` que **herda** do template base usando `{% block %}`

**Não vamos usar modelos (models) nesta aula.** O foco é exclusivamente em templates.

---

## 1. O que são Templates?

Templates são arquivos HTML que o Django usa para gerar as páginas que o usuário vê no navegador. Eles permitem:

- **Separar a lógica (Python)** da **apresentação (HTML)**
- **Reutilizar código HTML** entre várias páginas (herança de templates)
- **Inserir dados dinâmicos** usando a linguagem de template do Django

### Principais tags de template

| Tag | Descrição |
|-----|-----------|
| `{{ variavel }}` | Exibe o valor de uma variável |
| `{% block nome %}` | Define um bloco que pode ser sobrescrito |
| `{% extends "arquivo.html" %}` | Herda de outro template |
| `{% url 'nome' %}` | Gera a URL a partir do nome da rota |
| `{% load static %}` | Carrega arquivos estáticos (CSS, JS, imagens) |

### Como funciona a herança de templates?

```
base.html (template pai)
├── Define a estrutura geral: header, nav, footer
├── Define blocos: {% block title %}, {% block content %}
│
├── home.html (template filho)
│   └── {% extends "base.html" %} + sobrescreve os blocos
│
└── projetos.html (template filho)
    └── {% extends "base.html" %} + sobrescreve os blocos
```

O template **pai** (`base.html`) define a estrutura e os **blocos**. Os templates **filhos** usam `{% extends %}` para herdar essa estrutura e sobrescrevem apenas os blocos que precisam mudar.

---

## 2. Criar o App `core`

O app `core` vai conter o template base que será compartilhado por todos os outros apps.

### 2.1 Criar o app

```bash
python manage.py startapp core
```

### 2.2 Registrar o app no `settings.py`

Abra o arquivo `django_tutorial/settings.py` e adicione `'core'` na lista `INSTALLED_APPS`:

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
]
```

### 2.3 Criar a pasta de templates

O Django procura templates dentro de cada app, na pasta `templates/<nome_do_app>/`. Crie a seguinte estrutura:

```
core/
└── templates/
    └── core/
        └── base.html
```

No terminal:

```bash
mkdir -p core/templates/core
```

> **Por que a pasta duplicada `core/templates/core/`?**
>
> O Django junta todos os diretórios `templates/` de todos os apps em um único espaço. Se dois apps tiverem um arquivo chamado `base.html`, o Django pode confundir qual é qual. Usando `core/templates/core/base.html`, garantimos que o caminho completo é `core/base.html`, evitando conflitos.

### 2.4 Criar o template base

Crie o arquivo `core/templates/core/base.html`:

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Meu Portfólio{% endblock %}</title>
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
        {% block extra_css %}{% endblock %}
    </style>
</head>
<body>
    <header>
        <h1>{% block header_title %}Portfólio do Aluno{% endblock %}</h1>
    </header>

    <nav>
        <a href="{% url 'portfolio:home' %}">Início</a>
        <a href="{% url 'portfolio:projetos' %}">Projetos</a>
    </nav>

    <div class="container">
        {% block content %}{% endblock %}
    </div>

    <footer>
        <p>&copy; 2026 - Portfólio Acadêmico | UAST</p>
    </footer>
</body>
</html>
```

### Entendendo os blocos do template base

| Bloco | Finalidade |
|-------|-----------|
| `{% block title %}` | Título da aba do navegador |
| `{% block header_title %}` | Texto do cabeçalho da página |
| `{% block extra_css %}` | CSS adicional específico de cada página |
| `{% block content %}` | Conteúdo principal da página |

Cada página filha pode **sobrescrever** qualquer um desses blocos. Se não sobrescrever, o valor padrão definido no `base.html` será usado.

---

## 3. Criar o App `portfolio`

Agora vamos criar o app que vai conter as páginas do portfólio.

### 3.1 Criar o app

```bash
python manage.py startapp portfolio
```

### 3.2 Registrar no `settings.py`

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
]
```

### 3.3 Criar a pasta de templates

```bash
mkdir -p portfolio/templates/portfolio
```

---

## 4. Criar os Templates do Portfólio

### 4.1 Página Inicial — `home.html`

Crie o arquivo `portfolio/templates/portfolio/home.html`:

```html
{% extends "core/base.html" %}

{% block title %}Início - Meu Portfólio{% endblock %}

{% block header_title %}João da Silva{% endblock %}

{% block extra_css %}
.perfil {
    text-align: center;
    margin-bottom: 30px;
}
.perfil img {
    width: 180px;
    height: 180px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #2c3e50;
    margin-bottom: 15px;
}
.perfil h2 {
    margin-bottom: 5px;
}
.perfil p {
    color: #666;
}
.secao {
    background: white;
    padding: 25px;
    margin-bottom: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.secao h3 {
    color: #2c3e50;
    margin-bottom: 15px;
    border-bottom: 2px solid #3498db;
    padding-bottom: 8px;
}
.secao ul {
    list-style: none;
    padding: 0;
}
.secao ul li {
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}
.secao ul li:last-child {
    border-bottom: none;
}
{% endblock %}

{% block content %}
<div class="perfil">
    <img src="https://via.placeholder.com/180" alt="Foto do Aluno">
    <h2>João da Silva</h2>
    <p>Estudante de Sistemas de Informação - UAST/UFRPE</p>
</div>

<div class="secao">
    <h3>Sobre Mim</h3>
    <p>
        Olá! Sou estudante de Sistemas de Informação na UAST/UFRPE.
        Tenho interesse em desenvolvimento web, ciência de dados e
        inteligência artificial. Busco sempre aprender novas tecnologias
        e contribuir com projetos open source.
    </p>
</div>

<div class="secao">
    <h3>Dados Pessoais</h3>
    <ul>
        <li><strong>Nome:</strong> João da Silva</li>
        <li><strong>Curso:</strong> Bacharelado em Sistemas de Informação</li>
        <li><strong>Período:</strong> 5º</li>
        <li><strong>E-mail:</strong> joao.silva@ufrpe.br</li>
        <li><strong>GitHub:</strong> github.com/joaosilva</li>
        <li><strong>LinkedIn:</strong> linkedin.com/in/joaosilva</li>
    </ul>
</div>

<div class="secao">
    <h3>Cursos e Certificados</h3>
    <ul>
        <li>Python para Data Science - Coursera (2025)</li>
        <li>Django para Iniciantes - Udemy (2025)</li>
        <li>Git e GitHub Essencial - DIO (2024)</li>
        <li>Introdução ao Machine Learning - Stanford Online (2024)</li>
    </ul>
</div>
{% endblock %}
```

**O que está acontecendo aqui?**

1. `{% extends "core/base.html" %}` — herda toda a estrutura do template base
2. `{% block title %}` — muda o título da aba para "Início - Meu Portfólio"
3. `{% block header_title %}` — muda o cabeçalho para o nome do aluno
4. `{% block extra_css %}` — adiciona CSS específico desta página
5. `{% block content %}` — insere o conteúdo principal: foto, dados, cursos

### 4.2 Página de Projetos — `projetos.html`

Crie o arquivo `portfolio/templates/portfolio/projetos.html`:

```html
{% extends "core/base.html" %}

{% block title %}Projetos - Meu Portfólio{% endblock %}

{% block header_title %}Meus Projetos{% endblock %}

{% block extra_css %}
.projeto-card {
    background: white;
    padding: 25px;
    margin-bottom: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid #3498db;
}
.projeto-card h3 {
    color: #2c3e50;
    margin-bottom: 10px;
}
.projeto-card p {
    color: #555;
    margin-bottom: 10px;
}
.projeto-card .tipo {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.85em;
    color: white;
    margin-bottom: 10px;
}
.tipo-pessoal {
    background-color: #27ae60;
}
.tipo-disciplina {
    background-color: #e67e22;
}
.projeto-card a {
    color: #3498db;
    text-decoration: none;
}
.projeto-card a:hover {
    text-decoration: underline;
}
{% endblock %}

{% block content %}
<div class="projeto-card">
    <span class="tipo tipo-pessoal">Projeto Pessoal</span>
    <h3>To-Do List em Django</h3>
    <p>
        Aplicação web para gerenciamento de tarefas pessoais, desenvolvida
        com Django e Bootstrap. Possui autenticação de usuários e CRUD completo.
    </p>
    <a href="#">github.com/joaosilva/todo-django</a>
</div>

<div class="projeto-card">
    <span class="tipo tipo-disciplina">Projeto de Disciplina</span>
    <h3>Sistema de Enquetes (Polls)</h3>
    <p>
        Sistema de enquetes desenvolvido na disciplina de Programação Web,
        seguindo o tutorial oficial do Django. Permite criar perguntas
        e registrar votos.
    </p>
    <a href="#">github.com/joaosilva/django-polls</a>
</div>

<div class="projeto-card">
    <span class="tipo tipo-pessoal">Projeto Pessoal</span>
    <h3>API de Clima</h3>
    <p>
        API REST desenvolvida com Django REST Framework que consulta
        dados climáticos e retorna previsões para cidades brasileiras.
    </p>
    <a href="#">github.com/joaosilva/clima-api</a>
</div>

<div class="projeto-card">
    <span class="tipo tipo-disciplina">Projeto de Disciplina</span>
    <h3>Dashboard de Vendas</h3>
    <p>
        Dashboard interativo para análise de dados de vendas,
        desenvolvido na disciplina de Banco de Dados com Python e Pandas.
    </p>
    <a href="#">github.com/joaosilva/dashboard-vendas</a>
</div>
{% endblock %}
```

---

## 5. Criar as Views

Abra o arquivo `portfolio/views.py` e substitua o conteúdo por:

```python
from django.shortcuts import render


def home(request):
    return render(request, 'portfolio/home.html')


def projetos(request):
    return render(request, 'portfolio/projetos.html')
```

**Entendendo o `render()`:**

- `request` — o objeto da requisição HTTP
- `'portfolio/home.html'` — caminho do template (dentro de `templates/`)
- O Django encontra o template, processa as tags `{% %}` e `{{ }}`, e retorna o HTML final para o navegador

---

## 6. Criar as URLs

### 6.1 URLs do app `portfolio`

Crie o arquivo `portfolio/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.home, name='home'),
    path('projetos/', views.projetos, name='projetos'),
]
```

> **O que é `app_name`?**
>
> O `app_name` define um **namespace** para as URLs do app. Isso permite usar `{% url 'portfolio:home' %}` nos templates, evitando conflito com URLs de outros apps que também possam ter uma rota chamada `home`.

### 6.2 URLs do projeto

Abra o arquivo `django_tutorial/urls.py` e adicione a rota do portfólio:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('polls/', include('polls.urls')),
    path('portfolio/', include('portfolio.urls')),
]
```

---

## 7. Testar

Inicie o servidor:

```bash
python manage.py runserver
```

Acesse no navegador:

- **Página inicial:** [http://127.0.0.1:8000/portfolio/](http://127.0.0.1:8000/portfolio/)
- **Projetos:** [http://127.0.0.1:8000/portfolio/projetos/](http://127.0.0.1:8000/portfolio/projetos/)

Verifique que:

1. O **header**, **nav** e **footer** são os mesmos nas duas páginas (vêm do `base.html`)
2. O **conteúdo** muda conforme a página (cada template filho sobrescreve o `{% block content %}`)
3. O **título da aba** do navegador muda em cada página
4. Os **links de navegação** funcionam entre as páginas

---

## 8. Estrutura Final do Projeto

```
django_tutorial/
├── manage.py
├── django_tutorial/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── polls/
│   └── ...
├── core/
│   ├── __init__.py
│   ├── apps.py
│   └── templates/
│       └── core/
│           └── base.html        ← Template base (pai)
└── portfolio/
    ├── __init__.py
    ├── apps.py
    ├── views.py
    ├── urls.py
    └── templates/
        └── portfolio/
            ├── home.html        ← Herda de base.html
            └── projetos.html    ← Herda de base.html
```

---

## 9. Resumo dos Conceitos

| Conceito | O que faz |
|----------|-----------|
| `{% extends "..." %}` | Herda a estrutura de outro template |
| `{% block nome %}...{% endblock %}` | Define/sobrescreve um bloco de conteúdo |
| `{% url 'app:nome' %}` | Gera URL a partir do nome da rota |
| `app_name` no `urls.py` | Define o namespace do app para as URLs |
| `render(request, template)` | Renderiza o template e retorna como resposta HTTP |
| `APP_DIRS: True` no `settings.py` | Django busca templates em `app/templates/` automaticamente |

---

## 10. Exercício

Agora é com você! Personalize o portfólio com **seus dados reais**:

1. Troque o nome, curso, período e contatos
2. Adicione uma foto sua (pode usar um placeholder por enquanto)
3. Liste seus cursos e certificados reais
4. Adicione seus projetos pessoais e de disciplinas com os links do GitHub
5. **Desafio:** Crie uma terceira página (ex: `contato.html`) que também herde do `base.html` e adicione o link na navegação
6. No app core criar um banco Pessoal  
   6.1 nome;  
   6.2 descricao;  
   6.3 curso;  
   6.4 Periodo;  
   6.5 email;  
   6.6 git;  
   6.7 linked;
   6.8 url de uma imagem  
7. No app portfolia criar dois modelos  
  7.1 Certificado (Somente uma coluna com Descriacao)  
  7.2 Projeto
    - tipo (Pessoal ou Disciplia)
    - Nome
    - descricao
    - link do git

8. Substituir os templates para usar esses modelos. Registrar os modelos no django-admin para criar e editar registros.



