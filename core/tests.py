import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from core.models import Task, Project
from core.services import TaskWorkflowService

User = get_user_model()


@pytest.mark.django_db
class TestTaskWorkflowService:
    """Testes para o serviço de workflow de tarefas."""
    
    def test_transition_to_em_progresso_without_assignee_should_fail(self):
        """Tarefa não pode iniciar sem responsável."""
        user = User.objects.create(username='testuser')
        project = Project.objects.create(
            nome='Projeto Teste',
            data_inicio='2026-01-01',
            data_fim='2026-12-31'
        )
        task = Task.objects.create(
            projeto=project,
            titulo='Tarefa Teste',
            status=Task.StatusChoices.PENDENTE,
            data_entrega='2026-02-01'
        )
        
        with pytest.raises(ValidationError, match="sem um responsável"):
            TaskWorkflowService.transition_status(task, Task.StatusChoices.EM_PROGRESSO, user)
    
    def test_transition_to_em_progresso_with_assignee_should_succeed(self):
        """Tarefa pode iniciar quando tem responsável."""
        user = User.objects.create(username='testuser')
        project = Project.objects.create(
            nome='Projeto Teste',
            data_inicio='2026-01-01',
            data_fim='2026-12-31'
        )
        task = Task.objects.create(
            projeto=project,
            titulo='Tarefa Teste',
            status=Task.StatusChoices.PENDENTE,
            data_entrega='2026-02-01',
            assignee=user
        )
        
        result = TaskWorkflowService.transition_status(task, Task.StatusChoices.EM_PROGRESSO, user)
        
        assert result.status == Task.StatusChoices.EM_PROGRESSO
    
    def test_transition_pendente_to_concluida_should_fail(self):
        """Tarefa não pode pular de Pendente para Concluída."""
        user = User.objects.create(username='testuser')
        project = Project.objects.create(
            nome='Projeto Teste',
            data_inicio='2026-01-01',
            data_fim='2026-12-31'
        )
        task = Task.objects.create(
            projeto=project,
            titulo='Tarefa Teste',
            status=Task.StatusChoices.PENDENTE,
            data_entrega='2026-02-01',
            assignee=user,
            descricao='Descrição completa'
        )
        
        with pytest.raises(ValidationError, match="não pode pular de Pendente"):
            TaskWorkflowService.transition_status(task, Task.StatusChoices.CONCLUIDA, user)
    
    def test_transition_to_concluida_without_description_should_fail(self):
        """Tarefa não pode ser concluída sem descrição."""
        user = User.objects.create(username='testuser')
        project = Project.objects.create(
            nome='Projeto Teste',
            data_inicio='2026-01-01',
            data_fim='2026-12-31'
        )
        task = Task.objects.create(
            projeto=project,
            titulo='Tarefa Teste',
            status=Task.StatusChoices.EM_PROGRESSO,
            data_entrega='2026-02-01',
            assignee=user
        )
        
        with pytest.raises(ValidationError, match="preencher a descrição"):
            TaskWorkflowService.transition_status(task, Task.StatusChoices.CONCLUIDA, user)
