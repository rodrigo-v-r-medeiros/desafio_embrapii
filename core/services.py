from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from django.db import transaction
from .models import Task, Project
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class TaskWorkflowService:
    """
    Serviço responsável por gerenciar o ciclo de vida e regras de negócio de uma Tarefa.
    
    QUESTÃO 2 - Organização de Regras de Negócio:
    - Isolamos a lógica aqui para não poluir Views ou Models
    - Centraliza validações de fluxo e transições de estado
    - Garante rastreabilidade e auditoria
    - Facilita testes e manutenção
    
    Princípios aplicados:
    - Single Responsibility: Apenas gerencia workflow de tasks
    - DRY: Lógica centralizada, não duplicada
    - Separation of Concerns: Service Layer separado de Views/Models
    """
    
    # Matriz de transições válidas (State Machine)
    VALID_TRANSITIONS = {
        Task.StatusChoices.PENDENTE: [
            Task.StatusChoices.EM_PROGRESSO,
            Task.StatusChoices.CANCELADA
        ],
        Task.StatusChoices.EM_PROGRESSO: [
            Task.StatusChoices.CONCLUIDA,
            Task.StatusChoices.CANCELADA,
            Task.StatusChoices.PENDENTE  # Pode voltar para pendente
        ],
        Task.StatusChoices.CONCLUIDA: [],  # Estado final, não pode mudar
        Task.StatusChoices.CANCELADA: [
            Task.StatusChoices.PENDENTE  # Pode reabrir tarefa cancelada
        ]
    }

    @classmethod
    def transition_status(cls, task: Task, new_status: str, user, reason: str = None) -> Task:
        """
        Executa transição de status validando regras de negócio.
        
        Args:
            task: Instância da tarefa
            new_status: Novo status desejado
            user: Usuário executando a ação
            reason: Motivo da transição (opcional)
            
        Returns:
            Task atualizada
            
        Raises:
            ValidationError: Se a transição violar regras de negócio
            PermissionDenied: Se usuário não tiver permissão
        """
        old_status = task.status
        
        # Se status não mudou, apenas retorna
        if old_status == new_status:
            return task
        
        # 1. Validação de Transição (State Machine)
        cls._validate_transition(task, old_status, new_status)
        
        # 2. Validação de Regras de Negócio Específicas
        cls._validate_business_rules(task, new_status, user)
        
        # 3. Validação de Permissões
        cls._validate_permissions(task, new_status, user)
        
        # 4. Executa a transição com auditoria
        with transaction.atomic():
            task.status = new_status
            task.save()
            
            # Registra auditoria
            cls._audit_transition(task, old_status, new_status, user, reason)
            
            # Executa ações pós-transição
            cls._post_transition_actions(task, old_status, new_status, user)
        
        logger.info(
            f"Task {task.id} transitou de {old_status} para {new_status} "
            f"pelo usuário {user.username}"
        )
        
        return task
    
    @classmethod
    def _validate_transition(cls, task: Task, old_status: str, new_status: str) -> None:
        """
        Valida se a transição de status é permitida pela State Machine.
        
        QUESTÃO 2: Regra explícita de fluxo.
        """
        valid_next_statuses = cls.VALID_TRANSITIONS.get(old_status, [])
        
        if new_status not in valid_next_statuses:
            raise ValidationError(
                f"Transição inválida: não é possível mudar de '{old_status}' "
                f"para '{new_status}'. Estados válidos: {', '.join(valid_next_statuses)}"
            )
    
    @classmethod
    def _validate_business_rules(cls, task: Task, new_status: str, user) -> None:
        """
        Valida regras de negócio específicas de cada status.
        
        QUESTÃO 2: Regras de negócio centralizadas.
        """
        # Regra: Tarefa em progresso precisa ter responsável
        if new_status == Task.StatusChoices.EM_PROGRESSO:
            if not task.assignee:
                raise ValidationError(
                    "Não é possível iniciar uma tarefa sem um responsável (Assignee)."
                )
            
            # Regra: Data de entrega não pode estar no passado (se for date object)
            if hasattr(task.data_entrega, 'year'):  # Verifica se é date object
                if task.data_entrega < timezone.now().date():
                    raise ValidationError(
                        "Não é possível iniciar uma tarefa com data de entrega no passado."
                    )
        
        # Regra: Tarefa concluída precisa ter descrição do que foi feito
        if new_status == Task.StatusChoices.CONCLUIDA:
            if not task.descricao or len(task.descricao.strip()) < 10:
                raise ValidationError(
                    "Para concluir, é necessário preencher a descrição do que foi feito "
                    "(mínimo 10 caracteres)."
                )
            
            # Regra: Apenas o responsável pode concluir (ou staff)
            if task.assignee and task.assignee != user and not user.is_staff:
                raise ValidationError(
                    "Apenas o responsável pela tarefa ou um administrador pode concluí-la."
                )
    
    @classmethod
    def _validate_permissions(cls, task: Task, new_status: str, user) -> None:
        """
        Valida permissões do usuário para executar a transição.
        
        QUESTÃO 2: Validação dependente de ação humana/permissões.
        """
        # Exemplo: Apenas staff pode cancelar tarefas em progresso
        if new_status == Task.StatusChoices.CANCELADA:
            if task.status == Task.StatusChoices.EM_PROGRESSO and not user.is_staff:
                raise PermissionDenied(
                    "Apenas administradores podem cancelar tarefas em progresso."
                )
        
        # Exemplo: Usuários anônimos não podem alterar status
        if not user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado.")
    
    @classmethod
    def _audit_transition(cls, task: Task, old_status: str, new_status: str, 
                         user, reason: Optional[str]) -> None:
        """
        Registra auditoria da transição.
        
        QUESTÃO 2: Rastreabilidade das decisões e mudanças de status.
        
        Em um sistema real, isso seria salvo em uma tabela TaskHistory:
        - task_id
        - old_status
        - new_status  
        - changed_by (user)
        - changed_at (timestamp)
        - reason (motivo da mudança)
        - ip_address
        """
        audit_message = (
            f"[AUDIT] Task ID={task.id} | "
            f"Status: {old_status} → {new_status} | "
            f"User: {user.username} | "
            f"Timestamp: {timezone.now().isoformat()}"
        )
        
        if reason:
            audit_message += f" | Reason: {reason}"
        
        logger.info(audit_message)
        print(audit_message)  # Para demonstração no desafio
    
    @classmethod
    def _post_transition_actions(cls, task: Task, old_status: str, 
                                 new_status: str, user) -> None:
        """
        Executa ações automáticas após transição bem-sucedida.
        
        QUESTÃO 2: Validações automáticas vs ação humana.
        Estas ações ocorrem automaticamente após validações manuais.
        
        Exemplos de ações:
        - Enviar notificações
        - Atualizar métricas do projeto
        - Disparar webhooks
        - Criar tarefas dependentes
        """
        # Exemplo: Ao concluir tarefa, notificar partes interessadas
        if new_status == Task.StatusChoices.CONCLUIDA:
            # Em produção: enviar email, notificação push, etc
            logger.info(f"Task {task.id} concluída - notificações enviadas")
        
        # Exemplo: Ao iniciar tarefa, marcar data de início real
        if new_status == Task.StatusChoices.EM_PROGRESSO and old_status == Task.StatusChoices.PENDENTE:
            # Poderíamos adicionar campo data_inicio_real no model
            logger.info(f"Task {task.id} iniciada - data registrada")
    
    @classmethod
    def get_available_transitions(cls, task: Task) -> List[str]:
        """
        Retorna lista de transições disponíveis para a tarefa atual.
        
        Útil para UI dinâmica mostrando apenas ações válidas.
        """
        return cls.VALID_TRANSITIONS.get(task.status, [])
    
    @classmethod
    def can_transition_to(cls, task: Task, new_status: str) -> bool:
        """
        Verifica se é possível transitar para o novo status (sem executar).
        """
        return new_status in cls.get_available_transitions(task)


class ProjectService:
    """
    Serviço para gerenciar regras de negócio de Projetos.
    
    QUESTÃO 2: Demonstra organização de services por domínio.
    """
    
    @classmethod
    @transaction.atomic
    def create_project_with_initial_tasks(cls, project_data: Dict, 
                                         initial_tasks: List[Dict], user) -> Project:
        """
        Cria projeto e tarefas iniciais em uma transação.
        
        QUESTÃO 2: Operação complexa que envolve múltiplas entidades.
        Garante atomicidade: ou cria tudo ou nada.
        """
        # Valida dados do projeto
        if project_data['data_fim'] <= project_data['data_inicio']:
            raise ValidationError("Data de fim deve ser posterior à data de início.")
        
        # Cria projeto
        project = Project.objects.create(**project_data)
        
        # Cria tarefas iniciais
        tasks = []
        for task_data in initial_tasks:
            task_data['projeto'] = project
            tasks.append(Task(**task_data))
        
        Task.objects.bulk_create(tasks)
        
        logger.info(
            f"Projeto {project.id} criado com {len(tasks)} tarefas "
            f"pelo usuário {user.username}"
        )
        
        return project
    
    @classmethod
    def get_project_summary(cls, project: Project) -> Dict:
        """
        Retorna resumo do projeto com métricas.
        
        QUESTÃO 2: Lógica de agregação centralizada no service.
        """
        tasks = project.tasks.all()
        
        return {
            'id': project.id,
            'nome': project.nome,
            'total_tasks': tasks.count(),
            'tasks_pendentes': tasks.filter(status=Task.StatusChoices.PENDENTE).count(),
            'tasks_em_progresso': tasks.filter(status=Task.StatusChoices.EM_PROGRESSO).count(),
            'tasks_concluidas': tasks.filter(status=Task.StatusChoices.CONCLUIDA).count(),
            'tasks_canceladas': tasks.filter(status=Task.StatusChoices.CANCELADA).count(),
            'progress_percentage': cls._calculate_progress(tasks),
        }
    
    @staticmethod
    def _calculate_progress(tasks) -> float:
        """Calcula percentual de conclusão do projeto."""
        total = tasks.count()
        if total == 0:
            return 0.0
        
        concluidas = tasks.filter(status=Task.StatusChoices.CONCLUIDA).count()
        return round((concluidas / total) * 100, 2)
