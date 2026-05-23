from rest_framework.decorators import api_view
from rest_framework.response import Response  # Substitui o HttpResponse / render()
from rest_framework import status             # Codigos HTTP (200, 201, 400...)
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