from django.contrib import admin
from .models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin para gerenciar Projetos."""
    list_display = ['nome', 'data_inicio', 'data_fim', 'get_tasks_count']
    list_filter = ['data_inicio', 'data_fim']
    search_fields = ['nome', 'descricao']
    date_hierarchy = 'data_inicio'
    
    def get_tasks_count(self, obj):
        """Retorna número de tarefas do projeto."""
        return obj.tasks.count()
    get_tasks_count.short_description = 'Tarefas'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin para gerenciar Tarefas."""
    list_display = ['titulo', 'projeto', 'status', 'assignee', 'data_entrega', 'data_criacao']
    list_filter = ['status', 'data_entrega', 'data_criacao']
    search_fields = ['titulo', 'descricao', 'projeto__nome']
    date_hierarchy = 'data_criacao'
    autocomplete_fields = ['projeto', 'assignee']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('projeto', 'titulo', 'descricao')
        }),
        ('Status e Atribuição', {
            'fields': ('status', 'assignee')
        }),
        ('Datas', {
            'fields': ('data_entrega', 'data_criacao'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['data_criacao']
