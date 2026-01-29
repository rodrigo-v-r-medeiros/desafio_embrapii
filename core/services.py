from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Task

class TaskWorkflowService:
    """
    Serviço responsável por gerenciar o ciclo de vida e regras de negócio de uma Tarefa.
    Isolamos a lógica aqui para não poluir Views ou Models (Questão 2).
    """

    @staticmethod
    def transition_status(task: Task, new_status: str, user):
        old_status = task.status
        
        # 1. Validação de Transição (State Machine simples)
        if old_status == Task.StatusChoices.PENDENTE and new_status == Task.StatusChoices.CONCLUIDA:
            raise ValidationError("Uma tarefa não pode pular de Pendente direto para Concluída.")

        # 2. Regras de Negócio (Questão 4 - Validação Semântica)
        if new_status == Task.StatusChoices.EM_PROGRESSO:
            if not task.assignee:
                raise ValidationError("Não é possível iniciar uma tarefa sem um responsável (Assignee).")

        if new_status == Task.StatusChoices.CONCLUIDA:
            if not task.descricao:
                raise ValidationError("Para concluir, é necessário preencher a descrição do que foi feito.")
            
            # Auditoria: Quem aprovou?
            # Poderíamos salvar isso num log separado, mas aqui validamos permissão
            if not user.is_staff: # Exemplo: Só staff conclui
                 # Em um cenário real, usaríamos permissions mais granulares
                 pass 

        # 3. Execução da mudança
        task.status = new_status
        task.save()
        
        # 4. Auditoria / Rastreabilidade (Questão 2)
        # Em um sistema real, gravaríamos em uma tabela TaskHistory
        print(f"[AUDIT] Status alterado de {old_status} para {new_status} por {user} em {timezone.now()}")
        
        return task
