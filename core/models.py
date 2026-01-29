from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    """Modelo para gerenciar projetos."""
    
    nome = models.CharField(max_length=200, verbose_name="Nome")
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Fim")
    
    class Meta:
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"
        ordering = ["-data_inicio"]
    
    def __str__(self):
        return self.nome


class Task(models.Model):
    """Modelo para gerenciar tarefas vinculadas a projetos."""
    
    class StatusChoices(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        EM_PROGRESSO = "EM_PROGRESSO", "Em Progresso"
        CONCLUIDA = "CONCLUIDA", "Concluída"
        CANCELADA = "CANCELADA", "Cancelada"
    
    projeto = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Projeto"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDENTE,
        db_index=True,
        verbose_name="Status"
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Responsável"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_entrega = models.DateField(db_index=True, verbose_name="Data de Entrega")
    
    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ["-data_criacao"]
    
    def __str__(self):
        return f"{self.titulo} - {self.projeto.nome}"
