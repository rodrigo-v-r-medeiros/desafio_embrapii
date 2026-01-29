from rest_framework import serializers
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError
from decimal import Decimal, InvalidOperation
from .models import Project, Task
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer para Project com validações em múltiplas camadas.
    Demonstra Questão 4: Validação Backend.
    """
    tasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'nome', 'descricao', 'data_inicio', 'data_fim', 'tasks_count']
        read_only_fields = ['id']
    
    def get_tasks_count(self, obj):
        """Método para retornar contagem de tarefas."""
        return obj.tasks.count()
    
    def validate_nome(self, value):
        """
        Validação SINTÁTICA em campo específico.
        Exemplo: tamanho mínimo, caracteres permitidos.
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "O nome do projeto deve ter no mínimo 3 caracteres."
            )
        
        # Validação: não pode conter apenas números
        if value.strip().isdigit():
            raise serializers.ValidationError(
                "O nome do projeto não pode conter apenas números."
            )
        
        return value.strip()
    
    def validate(self, data):
        """
        Validação SEMÂNTICA multi-campo.
        Valida relacionamentos e regras de negócio.
        """
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')
        
        # Regra de negócio: data fim deve ser maior que data início
        if data_inicio and data_fim:
            if data_fim <= data_inicio:
                raise serializers.ValidationError({
                    'data_fim': 'A data de fim deve ser posterior à data de início.'
                })
        
        # Regra de negócio: projeto não pode iniciar no passado (exceto em edição)
        if not self.instance and data_inicio:  # Apenas na criação
            if data_inicio < timezone.now().date():
                raise serializers.ValidationError({
                    'data_inicio': 'Não é possível criar projetos com data de início no passado.'
                })
        
        # Validação: duração mínima do projeto (exemplo: 1 dia)
        if data_inicio and data_fim:
            duracao = (data_fim - data_inicio).days
            if duracao < 1:
                raise serializers.ValidationError(
                    'O projeto deve ter duração mínima de 1 dia.'
                )
        
        return data


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer para Task com validações robustas.
    Demonstra todos os tipos de validação mencionados na Questão 4.
    """
    projeto_nome = serializers.CharField(source='projeto.nome', read_only=True)
    assignee_username = serializers.CharField(source='assignee.username', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    dias_ate_entrega = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'projeto', 'projeto_nome', 'titulo', 'descricao', 
            'status', 'status_display', 'assignee', 'assignee_username',
            'data_criacao', 'data_entrega', 'dias_ate_entrega'
        ]
        read_only_fields = ['id', 'data_criacao']
    
    def get_dias_ate_entrega(self, obj):
        """Calcula dias até a entrega."""
        if obj.data_entrega:
            delta = obj.data_entrega - timezone.now().date()
            return delta.days
        return None
    
    def validate_titulo(self, value):
        """
        Validação SINTÁTICA: formato e caracteres.
        """
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "O título deve ter no mínimo 5 caracteres."
            )
        
        # Não pode conter apenas caracteres especiais
        if not any(c.isalnum() for c in value):
            raise serializers.ValidationError(
                "O título deve conter pelo menos um caractere alfanumérico."
            )
        
        return value.strip()
    
    def validate_status(self, value):
        """
        Validação SINTÁTICA: valor deve estar nas choices.
        Django já faz isso, mas podemos adicionar lógica extra.
        """
        valid_statuses = [choice[0] for choice in Task.StatusChoices.choices]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Status inválido. Opções válidas: {', '.join(valid_statuses)}"
            )
        return value
    
    def validate_data_entrega(self, value):
        """
        Validação de data de entrega.
        """
        # Em edição, permite datas passadas (para histórico)
        # Mas em criação, deve ser futura
        if not self.instance and value < timezone.now().date():
            raise serializers.ValidationError(
                "A data de entrega deve ser futura para novas tarefas."
            )
        
        return value
    
    def validate(self, data):
        """
        Validação SEMÂNTICA e REGRAS DE NEGÓCIO.
        Valida relacionamentos entre campos e regras complexas.
        """
        projeto = data.get('projeto') or (self.instance.projeto if self.instance else None)
        data_entrega = data.get('data_entrega') or (self.instance.data_entrega if self.instance else None)
        status = data.get('status') or (self.instance.status if self.instance else None)
        assignee = data.get('assignee') or (self.instance.assignee if self.instance else None)
        descricao = data.get('descricao', '') or (self.instance.descricao if self.instance else '')
        
        # Regra de negócio: data de entrega deve estar dentro do período do projeto
        if projeto and data_entrega:
            if data_entrega < projeto.data_inicio:
                raise serializers.ValidationError({
                    'data_entrega': f'A data de entrega não pode ser anterior ao início do projeto ({projeto.data_inicio}).'
                })
            if data_entrega > projeto.data_fim:
                raise serializers.ValidationError({
                    'data_entrega': f'A data de entrega não pode ser posterior ao fim do projeto ({projeto.data_fim}).'
                })
        
        # Regra de negócio: tarefa em progresso precisa ter responsável
        if status == Task.StatusChoices.EM_PROGRESSO and not assignee:
            raise serializers.ValidationError({
                'assignee': 'Tarefas em progresso devem ter um responsável atribuído.'
            })
        
        # Regra de negócio: tarefa concluída precisa ter descrição
        if status == Task.StatusChoices.CONCLUIDA and not descricao:
            raise serializers.ValidationError({
                'descricao': 'Tarefas concluídas devem ter uma descrição do que foi realizado.'
            })
        
        # Validação de transição de status (integração com Service Layer)
        if self.instance and status != self.instance.status:
            # Não pode pular de PENDENTE para CONCLUIDA
            if self.instance.status == Task.StatusChoices.PENDENTE and status == Task.StatusChoices.CONCLUIDA:
                raise serializers.ValidationError({
                    'status': 'Não é possível marcar como concluída uma tarefa pendente. Inicie a tarefa primeiro.'
                })
            
            # Não pode voltar de CONCLUIDA para outros status
            if self.instance.status == Task.StatusChoices.CONCLUIDA and status != Task.StatusChoices.CONCLUIDA:
                raise serializers.ValidationError({
                    'status': 'Não é possível alterar o status de uma tarefa já concluída.'
                })
        
        return data
    
    def create(self, validated_data):
        """
        Sobrescreve create para adicionar lógica de negócio na criação.
        """
        # Tarefas novas sempre começam como PENDENTE
        if 'status' not in validated_data:
            validated_data['status'] = Task.StatusChoices.PENDENTE
        
        return super().create(validated_data)


class TaskCreateSerializer(serializers.Serializer):
    """
    Serializer alternativo para demonstrar validação customizada
    sem estar acoplado ao model. Útil para APIs complexas.
    """
    projeto_id = serializers.IntegerField()
    titulo = serializers.CharField(min_length=5, max_length=200)
    descricao = serializers.CharField(required=False, allow_blank=True)
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    data_entrega = serializers.DateField()
    
    def validate_projeto_id(self, value):
        """Validação: projeto deve existir."""
        try:
            Project.objects.get(id=value)
        except Project.DoesNotExist:
            raise serializers.ValidationError(f"Projeto com ID {value} não existe.")
        return value
    
    def validate_assignee_id(self, value):
        """Validação: usuário deve existir."""
        if value is not None:
            try:
                User.objects.get(id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError(f"Usuário com ID {value} não existe.")
        return value
    
    def validate(self, data):
        """Validação cruzada de campos."""
        projeto = Project.objects.get(id=data['projeto_id'])
        data_entrega = data['data_entrega']
        
        # Data de entrega dentro do período do projeto
        if data_entrega < projeto.data_inicio or data_entrega > projeto.data_fim:
            raise serializers.ValidationError(
                f"A data de entrega deve estar entre {projeto.data_inicio} e {projeto.data_fim}."
            )
        
        return data
    
    def create(self, validated_data):
        """Cria a task a partir dos dados validados."""
        return Task.objects.create(
            projeto_id=validated_data['projeto_id'],
            titulo=validated_data['titulo'],
            descricao=validated_data.get('descricao', ''),
            assignee_id=validated_data.get('assignee_id'),
            data_entrega=validated_data['data_entrega'],
            status=Task.StatusChoices.PENDENTE
        )
