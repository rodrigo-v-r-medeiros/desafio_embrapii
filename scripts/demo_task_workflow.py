"""
Script de demonstração para o Desafio Técnico Embrapii - Questão 2
Demonstra Service Layer, regras de negócio e organização de fluxo

Como executar:
    python manage.py shell < scripts/demo_task_workflow.py
"""
from core.models import Task, Project
from core.services import TaskWorkflowService, ProjectService
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied

User = get_user_model()

print("=" * 70)
print("DEMONSTRAÇÃO: Service Layer e Fluxo de Negócio (Questão 2)")
print("=" * 70)

# Limpa dados anteriores
Task.objects.filter(projeto__nome__contains='Workflow').delete()
Project.objects.filter(nome__contains='Workflow').delete()
User.objects.filter(username__in=['dev1', 'dev2', 'admin_user']).delete()

# Setup
print("\n[SETUP] Criando dados de teste...")
user_dev = User.objects.create(username='dev1', email='dev1@example.com')
user_admin = User.objects.create(username='admin_user', email='admin@example.com', is_staff=True)
projeto = Project.objects.create(
    nome='Projeto Workflow Test',
    data_inicio='2026-02-01',
    data_fim='2026-12-31'
)
print(f"✓ Usuários criados: {user_dev.username}, {user_admin.username}")
print(f"✓ Projeto criado: {projeto.nome}")

# =============================================================================
# TESTE 1: State Machine - Transições Válidas
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 1] STATE MACHINE - Validação de Transições")
print("=" * 70)

task = Task.objects.create(
    projeto=projeto,
    titulo='Task para teste de transições',
    status='PENDENTE',
    data_entrega='2026-03-01'
)
print(f"\n✓ Task criada com status: {task.status}")

print("\n1.1 - Tentando pular de PENDENTE direto para CONCLUIDA...")
try:
    TaskWorkflowService.transition_status(task, 'CONCLUIDA', user_dev)
except ValidationError as e:
    print(f"✓ BLOQUEADO (State Machine): {e}")

print("\n1.2 - Verificando transições disponíveis...")
available = TaskWorkflowService.get_available_transitions(task)
print(f"✓ Transições válidas de PENDENTE: {available}")

# =============================================================================
# TESTE 2: Regras de Negócio - Assignee Obrigatório
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 2] REGRA DE NEGÓCIO - Tarefa precisa ter responsável")
print("=" * 70)

print("\n2.1 - Tentando iniciar tarefa SEM assignee...")
try:
    TaskWorkflowService.transition_status(task, 'EM_PROGRESSO', user_dev)
except ValidationError as e:
    print(f"✓ BLOQUEADO (Regra de Negócio): {e}")

print("\n2.2 - Atribuindo responsável e iniciando...")
task.assignee = user_dev
task.save()
TaskWorkflowService.transition_status(task, 'EM_PROGRESSO', user_dev)
print(f"✓ SUCESSO: Task agora está {task.status}")

# =============================================================================
# TESTE 3: Regras de Negócio - Descrição para Concluir
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 3] REGRA DE NEGÓCIO - Descrição obrigatória para concluir")
print("=" * 70)

print("\n3.1 - Tentando concluir SEM descrição...")
try:
    TaskWorkflowService.transition_status(task, 'CONCLUIDA', user_dev)
except ValidationError as e:
    print(f"✓ BLOQUEADO (Regra de Negócio): {e}")

print("\n3.2 - Adicionando descrição e concluindo...")
task.descricao = "Tarefa concluída com sucesso. Todos os requisitos foram atendidos."
task.save()
TaskWorkflowService.transition_status(task, 'CONCLUIDA', user_dev)
print(f"✓ SUCESSO: Task agora está {task.status}")

# =============================================================================
# TESTE 4: Validação de Permissões
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 4] VALIDAÇÃO DE PERMISSÕES")
print("=" * 70)

task2 = Task.objects.create(
    projeto=projeto,
    titulo='Task para teste de permissões',
    status='PENDENTE',
    assignee=user_dev,
    data_entrega='2026-04-01'
)

print("\n4.1 - Iniciando task (usuário comum)...")
TaskWorkflowService.transition_status(task2, 'EM_PROGRESSO', user_dev)
print(f"✓ Task iniciada: {task2.status}")

print("\n4.2 - Tentando cancelar task EM_PROGRESSO (usuário comum)...")
try:
    TaskWorkflowService.transition_status(task2, 'CANCELADA', user_dev)
except PermissionDenied as e:
    print(f"✓ BLOQUEADO (Permissão): {e}")

print("\n4.3 - Cancelando task EM_PROGRESSO (administrador)...")
TaskWorkflowService.transition_status(task2, 'CANCELADA', user_admin)
print(f"✓ SUCESSO (admin): Task agora está {task2.status}")

# =============================================================================
# TESTE 5: Rastreabilidade e Auditoria
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 5] RASTREABILIDADE - Auditoria de mudanças")
print("=" * 70)

task3 = Task.objects.create(
    projeto=projeto,
    titulo='Task com auditoria',
    status='PENDENTE',
    assignee=user_dev,
    data_entrega='2026-05-01'
)

print("\n5.1 - Executando transição com motivo...")
TaskWorkflowService.transition_status(
    task3, 
    'EM_PROGRESSO', 
    user_dev,
    reason="Iniciando trabalho conforme planejamento"
)
print("✓ Transição registrada com auditoria")

# =============================================================================
# TESTE 6: ProjectService - Operações Complexas
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 6] PROJECT SERVICE - Criação com tarefas iniciais")
print("=" * 70)

print("\n6.1 - Criando projeto com tarefas em uma transação...")
try:
    projeto2 = ProjectService.create_project_with_initial_tasks(
        project_data={
            'nome': 'Projeto Workflow Completo',
            'descricao': 'Projeto criado via service',
            'data_inicio': '2026-03-01',
            'data_fim': '2026-09-30'
        },
        initial_tasks=[
            {'titulo': 'Tarefa 1', 'status': 'PENDENTE', 'data_entrega': '2026-04-01'},
            {'titulo': 'Tarefa 2', 'status': 'PENDENTE', 'data_entrega': '2026-05-01'},
            {'titulo': 'Tarefa 3', 'status': 'PENDENTE', 'data_entrega': '2026-06-01'},
        ],
        user=user_admin
    )
    print(f"✓ Projeto criado: {projeto2.nome}")
    print(f"✓ Tarefas criadas: {projeto2.tasks.count()}")
except Exception as e:
    print(f"✗ Erro: {e}")

# =============================================================================
# TESTE 7: Métricas e Resumo
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 7] MÉTRICAS - Resumo do projeto")
print("=" * 70)

print("\n7.1 - Gerando resumo do projeto...")
summary = ProjectService.get_project_summary(projeto)
print(f"✓ Projeto: {summary['nome']}")
print(f"  - Total de tarefas: {summary['total_tasks']}")
print(f"  - Pendentes: {summary['tasks_pendentes']}")
print(f"  - Em Progresso: {summary['tasks_em_progresso']}")
print(f"  - Concluídas: {summary['tasks_concluidas']}")
print(f"  - Canceladas: {summary['tasks_canceladas']}")
print(f"  - Progresso: {summary['progress_percentage']}%")

# =============================================================================
# CONCLUSÃO
# =============================================================================
print("\n" + "=" * 70)
print("CONCLUSÃO - Questão 2: Organização de Regras de Negócio")
print("=" * 70)
print("""
COMO ORGANIZAMOS AS REGRAS NO DJANGO:

1. MODELS (models.py):
   ✓ Estrutura de dados e constraints básicos
   ✓ Relacionamentos entre entidades
   ✓ Validações de campo (max_length, choices, etc)
   
2. SERVICES (services.py):
   ✓ Regras de negócio complexas
   ✓ Validações de fluxo (state machine)
   ✓ Lógica que envolve múltiplas entidades
   ✓ Auditoria e rastreabilidade
   
3. SERIALIZERS (serializers.py):
   ✓ Validações de API (formato, sintaxe)
   ✓ Validações semânticas (relacionamento entre campos)
   ✓ Transformação de dados (input/output)
   
4. VIEWS (views.py):
   ✓ Validações de permissão e autorização
   ✓ Orquestração (chama services)
   ✓ Tratamento de erros e respostas

GARANTIAS IMPLEMENTADAS:

✅ Fluxo NÃO está espalhado: Service Layer centraliza lógica
✅ Rastreabilidade: Todas transições são auditadas
✅ Validações automáticas: State machine, regras de negócio
✅ Validações manuais: Permissões, aprovações humanas
✅ Atomicidade: Transações garantem consistência

PONTOS CRÍTICOS IDENTIFICADOS:

⚠️  Transições de status (validar com negócio)
⚠️  Permissões e autorização (quem pode fazer o quê)
⚠️  Dados obrigatórios por status (validar campos)
⚠️  Auditoria e histórico (rastreabilidade total)
⚠️  Notificações e ações automáticas (após validações)
""")
print("=" * 70)
