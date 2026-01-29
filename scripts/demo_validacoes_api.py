"""
Script de demonstração para o Desafio Técnico Embrapii - Questão 4
Demonstra validações de backend em múltiplas camadas

Como executar:
    python manage.py shell < scripts/demo_validacoes_api.py
"""
from core.models import Task, Project
from core.serializers import ProjectSerializer, TaskSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

print("=" * 70)
print("DEMONSTRAÇÃO: Validações de Backend - Múltiplas Camadas (Questão 4)")
print("=" * 70)

# Limpa dados de teste anteriores
print("\n[SETUP] Limpando dados de teste...")
Task.objects.filter(projeto__nome__startswith='Teste').delete()
Project.objects.filter(nome__startswith='Teste').delete()
User.objects.filter(username='testuser').delete()

# Cria usuário de teste
user = User.objects.create(username='testuser', email='test@example.com')
print(f"✓ Usuário criado: {user.username}")

# =============================================================================
# TESTE 1: Validação SINTÁTICA - Campo específico
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 1] VALIDAÇÃO SINTÁTICA - Nome do projeto")
print("=" * 70)

print("\n1.1 - Tentando criar projeto com nome muito curto (< 3 caracteres)...")
serializer = ProjectSerializer(data={
    'nome': 'AB',
    'descricao': 'Teste',
    'data_inicio': '2026-02-01',
    'data_fim': '2026-03-01'
})
if not serializer.is_valid():
    print(f"✓ VALIDAÇÃO BLOQUEOU: {serializer.errors['nome'][0]}")

print("\n1.2 - Tentando criar projeto com apenas números...")
serializer = ProjectSerializer(data={
    'nome': '12345',
    'descricao': 'Teste',
    'data_inicio': '2026-02-01',
    'data_fim': '2026-03-01'
})
if not serializer.is_valid():
    print(f"✓ VALIDAÇÃO BLOQUEOU: {serializer.errors['nome'][0]}")

# =============================================================================
# TESTE 2: Validação SEMÂNTICA - Relacionamento entre campos
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 2] VALIDAÇÃO SEMÂNTICA - Datas do projeto")
print("=" * 70)

print("\n2.1 - Tentando criar projeto com data_fim antes de data_inicio...")
serializer = ProjectSerializer(data={
    'nome': 'Teste Projeto',
    'descricao': 'Teste',
    'data_inicio': '2026-03-01',
    'data_fim': '2026-02-01'  # Antes do início!
})
if not serializer.is_valid():
    print(f"✓ VALIDAÇÃO BLOQUEOU: {serializer.errors['data_fim'][0]}")

print("\n2.2 - Tentando criar projeto com data_inicio no passado...")
ontem = (timezone.now() - timedelta(days=1)).date()
serializer = ProjectSerializer(data={
    'nome': 'Teste Projeto',
    'descricao': 'Teste',
    'data_inicio': str(ontem),
    'data_fim': '2026-12-31'
})
if not serializer.is_valid():
    print(f"✓ VALIDAÇÃO BLOQUEOU: {serializer.errors['data_inicio'][0]}")

# =============================================================================
# TESTE 3: Criação bem-sucedida de projeto
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 3] Criando projeto VÁLIDO")
print("=" * 70)

serializer = ProjectSerializer(data={
    'nome': 'Teste Projeto API',
    'descricao': 'Projeto válido para testes',
    'data_inicio': '2026-02-01',
    'data_fim': '2026-12-31'
})
if serializer.is_valid():
    project = serializer.save()
    print(f"✓ SUCESSO: Projeto '{project.nome}' criado com ID {project.id}")
else:
    print(f"✗ ERRO: {serializer.errors}")

# =============================================================================
# TESTE 4: Validação de Task - Múltiplas camadas
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 4] VALIDAÇÃO DE TASK - Título")
print("=" * 70)

print("\n4.1 - Tentando criar task com título muito curto...")
serializer = TaskSerializer(data={
    'projeto': project.id,
    'titulo': 'abc',  # < 5 caracteres
    'data_entrega': '2026-03-01'
})
if not serializer.is_valid():
    print(f"✓ VALIDAÇÃO BLOQUEOU: {serializer.errors['titulo'][0]}")

print("\n4.2 - Tentando criar task com título apenas caracteres especiais...")
serializer = TaskSerializer(data={
    'projeto': project.id,
    'titulo': '!@#$%',
    'data_entrega': '2026-03-01'
})
if not serializer.is_valid():
    print(f"✓ VALIDAÇÃO BLOQUEOU: {serializer.errors['titulo'][0]}")

# =============================================================================
# TESTE 5: Validação SEMÂNTICA - Data de entrega vs período do projeto
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 5] REGRA DE NEGÓCIO - Data de entrega dentro do projeto")
print("=" * 70)

print("\n5.1 - Tentando criar task com entrega ANTES do início do projeto...")
serializer = TaskSerializer(data={
    'projeto': project.id,
    'titulo': 'Task Teste',
    'data_entrega': '2026-01-15'  # Antes de 2026-02-01
})
if not serializer.is_valid():
    print(f"✓ VALIDAÇÃO BLOQUEOU: {serializer.errors['data_entrega'][0]}")

print("\n5.2 - Tentando criar task com entrega DEPOIS do fim do projeto...")
serializer = TaskSerializer(data={
    'projeto': project.id,
    'titulo': 'Task Teste',
    'data_entrega': '2027-01-15'  # Depois de 2026-12-31
})
if not serializer.is_valid():
    print(f"✓ VALIDAÇÃO BLOQUEOU: {serializer.errors['data_entrega'][0]}")

# =============================================================================
# TESTE 6: Validação de REGRA DE NEGÓCIO - Status e Assignee
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 6] REGRA DE NEGÓCIO - Status EM_PROGRESSO requer assignee")
print("=" * 70)

print("\n6.1 - Tentando criar task EM_PROGRESSO sem responsável...")
serializer = TaskSerializer(data={
    'projeto': project.id,
    'titulo': 'Task sem responsável',
    'status': 'EM_PROGRESSO',
    'data_entrega': '2026-03-01'
})
if not serializer.is_valid():
    print(f"✓ VALIDAÇÃO BLOQUEOU: {serializer.errors['assignee'][0]}")

# =============================================================================
# TESTE 7: Validação de TRANSIÇÃO DE STATUS
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 7] REGRA DE NEGÓCIO - Transições de status inválidas")
print("=" * 70)

# Cria uma task PENDENTE
task = Task.objects.create(
    projeto=project,
    titulo='Task para teste de transição',
    status='PENDENTE',
    data_entrega='2026-03-01'
)
print(f"\n✓ Task criada com status: {task.status}")

print("\n7.1 - Tentando pular de PENDENTE direto para CONCLUIDA...")
serializer = TaskSerializer(task, data={
    'projeto': project.id,
    'titulo': task.titulo,
    'status': 'CONCLUIDA',
    'descricao': 'Descrição completa',
    'data_entrega': '2026-03-01'
}, partial=False)
if not serializer.is_valid():
    print(f"✓ VALIDAÇÃO BLOQUEOU: {serializer.errors['status'][0]}")

# =============================================================================
# TESTE 8: Criação bem-sucedida de Task
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 8] Criando task VÁLIDA")
print("=" * 70)

serializer = TaskSerializer(data={
    'projeto': project.id,
    'titulo': 'Task Válida para Teste',
    'descricao': 'Descrição completa da tarefa',
    'status': 'PENDENTE',
    'assignee': user.id,
    'data_entrega': '2026-06-15'
})
if serializer.is_valid():
    task = serializer.save()
    print(f"✓ SUCESSO: Task '{task.titulo}' criada com ID {task.id}")
    print(f"  - Projeto: {task.projeto.nome}")
    print(f"  - Status: {task.get_status_display()}")
    print(f"  - Responsável: {task.assignee.username}")
    print(f"  - Entrega: {task.data_entrega}")
else:
    print(f"✗ ERRO: {serializer.errors}")

# =============================================================================
# CONCLUSÃO
# =============================================================================
print("\n" + "=" * 70)
print("CONCLUSÃO - Camadas de Validação Demonstradas:")
print("=" * 70)
print("""
1. VALIDAÇÃO SINTÁTICA (Serializer - campo específico):
   ✓ Formato de dados (tamanho, tipo, caracteres)
   ✓ Aplicada em validate_<campo>() do serializer

2. VALIDAÇÃO SEMÂNTICA (Serializer - múltiplos campos):
   ✓ Relacionamento entre campos (datas, valores)
   ✓ Aplicada em validate() do serializer

3. VALIDAÇÃO DE REGRAS DE NEGÓCIO (Serializer + Service):
   ✓ Regras complexas do domínio
   ✓ Transições de estado (state machine)
   ✓ Aplicada em validate() e Service Layer

4. VALIDAÇÃO NA VIEW (último nível):
   ✓ Permissões e autorização
   ✓ Contexto da requisição
   ✓ Tratamento de erros e respostas

IMPORTÂNCIA: Backend NUNCA deve confiar apenas no frontend!
- Frontend pode ser contornado (Postman, curl, etc)
- Validações protegem integridade dos dados
- Previnem estados inconsistentes no banco
""")
print("=" * 70)
