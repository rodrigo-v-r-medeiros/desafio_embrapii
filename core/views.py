from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count, Prefetch
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from .services import TaskWorkflowService
from django.core.exceptions import ValidationError as DjangoValidationError


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Projetos.
    
    Endpoints:
    - GET /api/projects/ - Lista todos os projetos
    - POST /api/projects/ - Cria novo projeto
    - GET /api/projects/{id}/ - Detalhes de um projeto
    - PUT/PATCH /api/projects/{id}/ - Atualiza projeto
    - DELETE /api/projects/{id}/ - Remove projeto
    - GET /api/projects/{id}/tasks/ - Lista tarefas do projeto (otimizado)
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    def get_queryset(self):
        """
        Otimização: Sempre retorna queryset otimizado.
        Evita N+1 queries ao carregar relacionamentos.
        """
        queryset = Project.objects.annotate(
            tasks_total=Count('tasks')
        ).prefetch_related('tasks')
        
        # Filtros opcionais via query params
        nome = self.request.query_params.get('nome', None)
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        
        return queryset.order_by('-data_inicio')
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """
        Custom action: retorna tarefas de um projeto específico.
        Demonstra otimização com prefetch_related.
        
        GET /api/projects/{id}/tasks/
        """
        project = self.get_object()
        
        # Otimização: prefetch assignee para evitar N+1
        tasks = project.tasks.select_related('assignee').all()
        
        # Filtro opcional por status
        status_filter = request.query_params.get('status', None)
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Tarefas.
    Demonstra validações em múltiplas camadas (Questão 4).
    
    Endpoints:
    - GET /api/tasks/ - Lista todas as tarefas
    - POST /api/tasks/ - Cria nova tarefa (com validações)
    - GET /api/tasks/{id}/ - Detalhes de uma tarefa
    - PUT/PATCH /api/tasks/{id}/ - Atualiza tarefa (com validações)
    - DELETE /api/tasks/{id}/ - Remove tarefa
    - POST /api/tasks/{id}/transition/ - Transição de status (Service Layer)
    - GET /api/tasks/atrasadas/ - Lista tarefas atrasadas
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        """
        Otimização: Sempre usa select_related para evitar N+1.
        """
        queryset = Task.objects.select_related('projeto', 'assignee').all()
        
        # Filtros via query params
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        projeto_id = self.request.query_params.get('projeto', None)
        if projeto_id:
            queryset = queryset.filter(projeto_id=projeto_id)
        
        assignee_id = self.request.query_params.get('assignee', None)
        if assignee_id:
            queryset = queryset.filter(assignee_id=assignee_id)
        
        return queryset.order_by('-data_criacao')
    
    def create(self, request, *args, **kwargs):
        """
        Sobrescreve create para adicionar validações extras.
        Demonstra validação em VIEW (camada mais externa).
        """
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            return Response(
                {
                    'message': 'Tarefa criada com sucesso.',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Erro ao criar tarefa.',
                    'details': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        """
        Custom action: transição de status usando Service Layer.
        Demonstra separação de responsabilidades (Questão 2).
        
        POST /api/tasks/{id}/transition/
        Body: {"new_status": "EM_PROGRESSO"}
        """
        task = self.get_object()
        new_status = request.data.get('new_status')
        
        if not new_status:
            return Response(
                {'error': 'Campo "new_status" é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validação: status deve existir nas choices
        valid_statuses = [choice[0] for choice in Task.StatusChoices.choices]
        if new_status not in valid_statuses:
            return Response(
                {
                    'error': f'Status inválido. Opções: {", ".join(valid_statuses)}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Usa o Service Layer para validar regras de negócio
            updated_task = TaskWorkflowService.transition_status(
                task, 
                new_status, 
                request.user
            )
            
            serializer = self.get_serializer(updated_task)
            return Response({
                'message': f'Status alterado para {new_status}.',
                'data': serializer.data
            })
        
        except DjangoValidationError as e:
            return Response(
                {'error': str(e.message) if hasattr(e, 'message') else str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Erro ao alterar status: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def atrasadas(self, request):
        """
        Custom action: lista tarefas atrasadas.
        Demonstra query complexa e regra de negócio.
        
        GET /api/tasks/atrasadas/
        """
        hoje = timezone.now().date()
        
        # Tarefas atrasadas: data_entrega no passado e status != CONCLUIDA/CANCELADA
        tasks_atrasadas = self.get_queryset().filter(
            data_entrega__lt=hoje
        ).exclude(
            status__in=[Task.StatusChoices.CONCLUIDA, Task.StatusChoices.CANCELADA]
        )
        
        serializer = self.get_serializer(tasks_atrasadas, many=True)
        
        return Response({
            'count': tasks_atrasadas.count(),
            'tasks': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def minhas(self, request):
        """
        Custom action: lista tarefas do usuário logado.
        
        GET /api/tasks/minhas/
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Autenticação necessária.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        tasks = self.get_queryset().filter(assignee=request.user)
        serializer = self.get_serializer(tasks, many=True)
        
        return Response({
            'count': tasks.count(),
            'tasks': serializer.data
        })
