import time
import random
from django.core.management.base import BaseCommand
from django.db import connection, reset_queries
from core.models import Project, Task

class Command(BaseCommand):
    help = 'Demonstra o problema de N+1 e a solução com prefetch_related'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Preparando dados para o teste...'))
        self._setup_data()
        
        self.stdout.write(self.style.SUCCESS('\n--- INICIANDO TESTE DE PERFORMANCE ---\n'))
        
        # Teste 1: O jeito errado (N+1)
        self.stdout.write('1. Executando SEM otimização (N+1)...')
        reset_queries()
        start_time = time.time()
        self._run_nplus1_scenario()
        end_time = time.time()
        
        query_count_bad = len(connection.queries)
        time_bad = end_time - start_time
        self.stdout.write(f'   Resultado: {query_count_bad} queries executadas em {time_bad:.4f}s')

        # Teste 2: O jeito certo (prefetch_related)
        self.stdout.write('\n2. Executando COM otimização (prefetch_related)...')
        reset_queries()
        start_time = time.time()
        self._run_optimized_scenario()
        end_time = time.time()
        
        query_count_good = len(connection.queries)
        time_good = end_time - start_time
        self.stdout.write(f'   Resultado: {query_count_good} queries executadas em {time_good:.4f}s')

        # Conclusão visual
        reduction = query_count_bad - query_count_good
        self.stdout.write(self.style.SUCCESS(f'\nCONCLUSÃO: Redução de {reduction} queries no banco de dados!'))

    def _setup_data(self):
        # Limpa banco para teste limpo
        Task.objects.all().delete()
        Project.objects.all().delete()
        
        # Cria 5 projetos com 20 tarefas cada (100 tarefas total)
        projects = []
        for i in range(5):
            projects.append(Project(nome=f"Projeto {i}", descricao="Teste N+1", data_inicio="2026-01-01", data_fim="2026-12-31"))
        Project.objects.bulk_create(projects)
        
        all_projects = Project.objects.all()
        tasks = []
        for proj in all_projects:
            for j in range(20):
                tasks.append(Task(
                    projeto=proj, 
                    titulo=f"Tarefa {j}", 
                    status='PENDENTE',
                    data_entrega='2026-01-30'
                ))
        Task.objects.bulk_create(tasks)

    def _run_nplus1_scenario(self):
        # O ERRO: Iterar sobre filhos sem carregar antes
        projects = Project.objects.all()
        for project in projects:
            # A cada loop, o Django vai no banco buscar as tasks (N queries extras)
            _ = [t.titulo for t in project.tasks.all()]

    def _run_optimized_scenario(self):
        # A SOLUÇÃO: prefetch_related carrega tudo em 2 queries
        projects = Project.objects.prefetch_related('tasks').all()
        for project in projects:
            # Agora os dados já estão em memória Python
            _ = [t.titulo for t in project.tasks.all()]