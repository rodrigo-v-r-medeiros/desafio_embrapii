"""
Script de demonstração para o Desafio Técnico Embrapii - Questão 1
Demonstra o problema de N+1 queries e sua solução

Como executar:
    python manage.py shell < scripts/demo_nplus1.py
"""
import time
from django.db import connection, reset_queries
from core.models import Project, Task

print("=" * 70)
print("DEMONSTRAÇÃO: Problema N+1 Queries e Solução (Questão 1)")
print("=" * 70)

# Preparação dos dados
print("\n[SETUP] Preparando dados para o teste...")
Task.objects.all().delete()
Project.objects.all().delete()

# Cria 5 projetos com 20 tarefas cada (100 tarefas total)
projects = []
for i in range(5):
    projects.append(Project(
        nome=f"Projeto {i+1}",
        descricao=f"Descrição do projeto {i+1}",
        data_inicio="2026-01-01",
        data_fim="2026-12-31"
    ))
Project.objects.bulk_create(projects)

all_projects = Project.objects.all()
tasks = []
for proj in all_projects:
    for j in range(20):
        tasks.append(Task(
            projeto=proj,
            titulo=f"Tarefa {j+1} do {proj.nome}",
            status='PENDENTE',
            data_entrega='2026-06-30'
        ))
Task.objects.bulk_create(tasks)

print(f"✓ Criados {all_projects.count()} projetos")
print(f"✓ Criadas {Task.objects.count()} tarefas")

# =============================================================================
# TESTE 1: O PROBLEMA - N+1 Queries
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 1] EXECUÇÃO SEM OTIMIZAÇÃO (Problema N+1)")
print("=" * 70)

reset_queries()
start_time = time.time()

# O ERRO: Busca projetos e depois itera acessando tasks
projects = Project.objects.all()
for project in projects:
    # A cada iteração, Django executa uma nova query para buscar tasks!
    # Isso é o problema N+1: 1 query inicial + N queries (uma por projeto)
    tasks_list = [t.titulo for t in project.tasks.all()]

end_time = time.time()
query_count_bad = len(connection.queries)
time_bad = end_time - start_time

print(f"\n📊 Resultados:")
print(f"   Queries executadas: {query_count_bad}")
print(f"   Tempo de execução: {time_bad:.4f}s")
print(f"\n💡 O que aconteceu:")
print(f"   - 1 query para buscar os 5 projetos")
print(f"   - 5 queries adicionais (uma para cada projeto buscar suas tasks)")
print(f"   - Total: {query_count_bad} queries ao banco de dados")

# =============================================================================
# TESTE 2: A SOLUÇÃO - prefetch_related()
# =============================================================================
print("\n" + "=" * 70)
print("[TESTE 2] EXECUÇÃO COM OTIMIZAÇÃO (prefetch_related)")
print("=" * 70)

reset_queries()
start_time = time.time()

# A SOLUÇÃO: Usa prefetch_related para carregar tudo de uma vez
projects = Project.objects.prefetch_related('tasks').all()
for project in projects:
    # Agora as tasks já estão em memória, não há queries adicionais!
    tasks_list = [t.titulo for t in project.tasks.all()]

end_time = time.time()
query_count_good = len(connection.queries)
time_good = end_time - start_time

print(f"\n📊 Resultados:")
print(f"   Queries executadas: {query_count_good}")
print(f"   Tempo de execução: {time_good:.4f}s")
print(f"\n💡 O que aconteceu:")
print(f"   - 1 query para buscar os 5 projetos")
print(f"   - 1 query adicional para buscar TODAS as tasks de uma vez")
print(f"   - Total: {query_count_good} queries ao banco de dados")

# =============================================================================
# COMPARAÇÃO E CONCLUSÃO
# =============================================================================
print("\n" + "=" * 70)
print("COMPARAÇÃO E IMPACTO")
print("=" * 70)

reduction = query_count_bad - query_count_good
percentage = ((query_count_bad - query_count_good) / query_count_bad) * 100
time_improvement = ((time_bad - time_good) / time_bad) * 100

print(f"\n📈 Redução de queries: {reduction} queries ({percentage:.1f}%)")
print(f"⚡ Melhoria de performance: {time_improvement:.1f}%")

print(f"\n" + "=" * 70)
print("CONCLUSÃO - Questão 1")
print("=" * 70)
print("""
O QUE É N+1 QUERIES?
- Padrão onde você executa 1 query inicial + N queries adicionais
- Acontece ao iterar sobre objetos e acessar relacionamentos
- Exemplo: buscar projetos e depois buscar tasks de cada projeto

COMO IDENTIFICAR?
- django-debug-toolbar: mostra número de queries na tela
- Logging: LOGGING com 'django.db.backends' para ver SQL
- connection.queries: inspeciona queries em desenvolvimento
- Django Silk: ferramenta de profiling para produção

COMO RESOLVER?
- select_related(): para ForeignKey e OneToOne (JOIN)
- prefetch_related(): para ManyToMany e reverse ForeignKey
- Prefetch(): para controle fino de prefetching
- annotate() + Count(): para agregações

IMPACTO REAL:
Com 5 projetos: 6 queries → 2 queries (redução de 67%)
Com 100 projetos: 101 queries → 2 queries (redução de 98%)
Em produção com milhares de registros, a diferença é GIGANTE!
""")
print("=" * 70)
