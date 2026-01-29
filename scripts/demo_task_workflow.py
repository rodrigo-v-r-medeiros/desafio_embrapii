"""
Script de demonstração para o Desafio Técnico Embrapii
Demonstra as validações de regras de negócio do TaskWorkflowService

Como executar:
    python manage.py shell < scripts/demo_task_workflow.py
"""
from core.models import Task, Project
from core.services import TaskWorkflowService
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

print("=" * 60)
print("DEMONSTRAÇÃO: TaskWorkflowService - Regras de Negócio")
print("=" * 60)

# Setup
u = User.objects.create(username='dev')
p = Project.objects.create(nome='Proj Teste', data_inicio='2026-01-01', data_fim='2026-12-31')
t = Task.objects.create(projeto=p, titulo='Task Sem Dono', status='PENDENTE', data_entrega='2026-02-01')

# Teste 1: Tentar iniciar sem dono (Deve falhar)
print("\n[TESTE 1] Tentando iniciar tarefa SEM responsável...")
try:
    TaskWorkflowService.transition_status(t, 'EM_PROGRESSO', u)
except ValidationError as e:
    print(f"✓ ERRO ESPERADO: {e}")

# Teste 2: Corrigir e tentar de novo (Deve passar)
print("\n[TESTE 2] Atribuindo responsável e iniciando tarefa...")
t.assignee = u
t.save()
TaskWorkflowService.transition_status(t, 'EM_PROGRESSO', u)
print(f"✓ SUCESSO: Status atual é {t.status}")

print("\n" + "=" * 60)
print("Demonstração concluída!")
print("=" * 60)
