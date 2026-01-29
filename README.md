# Desafio Técnico Embrapii - Sistema de Gestão de Projetos

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16-red.svg)](https://www.django-rest-framework.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Sistema Django completo desenvolvido para o processo seletivo Embrapii, demonstrando domínio em otimizações ORM, arquitetura de software, validações robustas e boas práticas de desenvolvimento.**

## 🌟 Destaques

- ⚡ **67% de redução** em queries ao banco (N+1 resolvido com demonstração quantificada)
- 🏗️ **Service Layer robusto** com state machine e auditoria completa
- ✅ **Validações em 4 camadas** (Model, Serializer, Service, View)
- 📊 **3 scripts executáveis** demonstrando cada solução técnica
- 📚 **Documentação completa** com 1493+ linhas de explicações detalhadas (ver [RESPOSTAS.md](RESPOSTAS.md))

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Questões Respondidas](#questões-respondidas)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Instalação](#instalação)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Demonstrações](#demonstrações)
- [API REST](#api-rest)
- [Testes](#testes)

---

## 🎯 Sobre o Projeto

Este projeto implementa um **sistema completo de gestão de projetos e tarefas** desenvolvido como resposta ao desafio técnico Embrapii. Demonstra conhecimento avançado em Django, arquitetura de software e boas práticas de desenvolvimento.

### ✨ Funcionalidades Implementadas

- ✅ **Otimização de queries** com redução comprovada de 67% (N+1 queries resolvido)
- ✅ **Service Layer** centralizado com state machine e validações de negócio
- ✅ **Modelagem estratégica** com índices compostos e relacionamentos otimizados
- ✅ **API REST completa** com Django REST Framework
- ✅ **Validações em múltiplas camadas** (sintática, semântica, regras de negócio)
- ✅ **Sistema de auditoria** rastreando todas as transições de status
- ✅ **Admin Django** totalmente configurado
- ✅ **Scripts executáveis** demonstrando cada solução técnica

### 📖 Documentação Completa

Para respostas detalhadas das 4 questões técnicas com explicações aprofundadas, exemplos de código e justificativas de decisões arquiteturais, consulte:

**👉 [RESPOSTAS.md](RESPOSTAS.md)** - Documento técnico completo (1493 linhas)

---

## 📝 Questões Respondidas

### Questão 1: Otimização de ORM e N+1 Queries

**Implementação:** [core/management/commands/test_nplus1.py](core/management/commands/test_nplus1.py)  
**Demonstração:** [scripts/demo_nplus1.py](scripts/demo_nplus1.py)

- Prova matemática do problema N+1 (6 queries → 2 queries)
- Uso de `prefetch_related()` e `select_related()`
- Redução de 67% nas consultas ao banco

**Executar:**
```bash
python manage.py shell < scripts/demo_nplus1.py
```

### Questão 2: Service Layer e Regras de Negócio

**Implementação:** [core/services.py](core/services.py)  
**Demonstração:** [scripts/demo_task_workflow.py](scripts/demo_task_workflow.py)

- Service Layer com `TaskWorkflowService` e `ProjectService`
- State machine completa para transições de status
- Validações de regras de negócio centralizadas
- Auditoria e rastreabilidade de todas as ações
- Separação clara de responsabilidades

**Executar:**
```bash
python manage.py shell < scripts/demo_task_workflow.py
```

### Questão 3: Modelagem Django ORM

**Implementação:** [core/models.py](core/models.py)

- Models `Project` e `Task` bem estruturados
- Relacionamentos com `related_name` e índices otimizados
- StatusChoices para enum de status
- Ordenação padrão e metadados

### Questão 4: Validações de Backend

**Implementação:** [core/serializers.py](core/serializers.py) + [core/views.py](core/views.py)  
**Demonstração:** [scripts/demo_validacoes_api.py](scripts/demo_validacoes_api.py)

- Validação SINTÁTICA (formato, tamanho, tipo)
- Validação SEMÂNTICA (relacionamento entre campos)
- Validação de REGRAS DE NEGÓCIO (lógica de domínio)
- Validações em múltiplas camadas (Model, Serializer, View, Service)

**Executar:**
```bash
python manage.py shell < scripts/demo_validacoes_api.py
```

---

## 🛠 Tecnologias Utilizadas

- **Django 6.0** - Framework web Python
- **Django REST Framework 3.16** - API REST
- **Django Extensions** - Ferramentas extras para desenvolvimento
- **SQLite** - Banco de dados (desenvolvimento)
- **Black** - Formatação de código
- **Pytest** + **pytest-django** - Testes
- **IPython** - Shell interativo

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.12 ou superior
- pip (gerenciador de pacotes Python)
- Git

### Linux / Mac

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/embrappi.git
cd embrappi

# 2. Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute as migrações
python manage.py migrate

# 5. (Opcional) Crie um superusuário para acessar o admin
python manage.py createsuperuser

# 6. Execute as demonstrações (opcional, mas recomendado)
python manage.py shell < scripts/demo_nplus1.py
python manage.py shell < scripts/demo_task_workflow.py
python manage.py shell < scripts/demo_validacoes_api.py

# 7. Inicie o servidor
python manage.py runserver
```

### Windows

```powershell
# 1. Clone o repositório
git clone https://github.com/seu-usuario/embrappi.git
cd embrappi

# 2. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute as migrações
python manage.py migrate

# 5. (Opcional) Crie um superusuário para acessar o admin
python manage.py createsuperuser

# 6. Execute as demonstrações (opcional, mas recomendado)
python manage.py shell < scripts/demo_nplus1.py
python manage.py shell < scripts/demo_task_workflow.py
python manage.py shell < scripts/demo_validacoes_api.py

# 7. Inicie o servidor
python manage.py runserver
```

O projeto estará disponível em:
- **Frontend:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/
- **API:** http://127.0.0.1:8000/api/

---

## 📁 Estrutura do Projeto

```
embrappi/
├── config/                      # Configurações Django
│   ├── settings.py             # Configurações principais
│   ├── urls.py                 # URLs principais
│   └── wsgi.py                 # WSGI application
│
├── core/                        # App principal
│   ├── management/
│   │   └── commands/           # Comandos customizados
│   │       └── test_nplus1.py  # Demonstração N+1
│   ├── migrations/             # Migrações do banco
│   ├── admin.py                # Admin Django
│   ├── models.py               # Models (Project, Task)
│   ├── serializers.py          # Serializers DRF
│   ├── services.py             # Service Layer
│   ├── tests.py                # Testes unitários
│   ├── urls.py                 # URLs da API
│   └── views.py                # ViewSets da API
│
├── scripts/                     # Scripts de demonstração
│   ├── README.md               # Documentação dos scripts
│   ├── demo_nplus1.py          # Demo Questão 1
│   ├── demo_task_workflow.py   # Demo Questão 2
│   └── demo_validacoes_api.py  # Demo Questão 4
│
├── manage.py                    # Utilitário Django
├── requirements.txt             # Dependências
├── .gitignore                   # Arquivos ignorados
└── README.md                    # Este arquivo
```

---

## 🎬 Demonstrações

Todos os scripts de demonstração estão na pasta `/scripts/`. Veja [scripts/README.md](scripts/README.md) para detalhes.

### Executar Todas as Demonstrações

```bash
# Ative o ambiente virtual primeiro
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Execute cada demonstração
python manage.py shell < scripts/demo_nplus1.py
python manage.py shell < scripts/demo_task_workflow.py
python manage.py shell < scripts/demo_validacoes_api.py
```

---

## 🌐 API REST

A API REST está disponível em `/api/` com os seguintes endpoints:

### Projects

- `GET /api/projects/` - Lista todos os projetos
- `POST /api/projects/` - Cria novo projeto
- `GET /api/projects/{id}/` - Detalhes de um projeto
- `PUT/PATCH /api/projects/{id}/` - Atualiza projeto
- `DELETE /api/projects/{id}/` - Remove projeto
- `GET /api/projects/{id}/tasks/` - Lista tarefas do projeto

### Tasks

- `GET /api/tasks/` - Lista todas as tarefas
- `POST /api/tasks/` - Cria nova tarefa
- `GET /api/tasks/{id}/` - Detalhes de uma tarefa
- `PUT/PATCH /api/tasks/{id}/` - Atualiza tarefa
- `DELETE /api/tasks/{id}/` - Remove tarefa
- `POST /api/tasks/{id}/transition/` - Transição de status
- `GET /api/tasks/atrasadas/` - Lista tarefas atrasadas
- `GET /api/tasks/minhas/` - Lista tarefas do usuário

### Exemplos de Uso

```bash
# Listar projetos
curl http://127.0.0.1:8000/api/projects/

# Criar projeto
curl -X POST http://127.0.0.1:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Novo Projeto",
    "descricao": "Descrição do projeto",
    "data_inicio": "2026-02-01",
    "data_fim": "2026-12-31"
  }'

# Transição de status de task
curl -X POST http://127.0.0.1:8000/api/tasks/1/transition/ \
  -H "Content-Type: application/json" \
  -d '{"new_status": "EM_PROGRESSO"}'
```

---

## 🧪 Testes

### Executar Testes Unitários

```bash
pytest
```

### Executar Testes com Coverage

```bash
pytest --cov=core --cov-report=html
```

### Executar Comando de Teste N+1

```bash
python manage.py test_nplus1
```

---

## 🔑 Conceitos Principais Implementados

### 1. Otimização ORM
- `select_related()` para ForeignKey e OneToOne
- `prefetch_related()` para ManyToMany e reverse FK
- Uso de `annotate()` e `Count()` para agregações

### 2. Service Layer
- Regras de negócio isoladas de Views/Models
- State machine para controle de fluxo
- Auditoria e logging de todas as ações
- Transações atômicas para operações complexas

### 3. Validações Múltiplas Camadas
- **Model:** Constraints básicos (max_length, choices)
- **Serializer:** Validações sintáticas e semânticas
- **Service:** Regras de negócio complexas
- **View:** Permissões e autorização
🎓 Diferenciais Técnicos

Este projeto demonstra:

- **Performance:** Otimização comprovada com métricas reais (67% redução de queries)
- **Arquitetura:** Separação clara de responsabilidades (SOLID principles)
- **Qualidade:** Código limpo, documentado e seguindo PEP 8
- **Testabilidade:** Scripts demonstráveis e estrutura preparada para testes
- **Profissionalismo:** Documentação completa, commits organizados, estrutura escalável

## 📚 Documentação Adicional

- **[RESPOSTAS.md](RESPOSTAS.md)** - Respostas detalhadas das 4 questões técnicas
- **[scripts/README.md](scripts/README.md)** - Guia de execução dos scripts de demonstração

## 👨‍💻 Autor

Desenvolvido por **Rodrigo** como parte do Desafio Técnico Embrapii - Janeiro 2026

---

## 📝 Notas

Este projeto foi desenvolvido especificamente para demonstrar conhecimentos técnicos em:
- Otimização de ORM e resolução de N+1 queries
- Arquitetura de software com Service Layer
- Modelagem de dados estratégica
- Validações robustas em múltiplas camadas

Todas as implementações são funcionais e podem ser executadas localmente

**Rodrigo**

Desenvolvido como parte do Desafio Técnico Embrapii - Janeiro 2026

---

## 📄 Licença

Este projeto foi desenvolvido para fins de avaliação técnica.
