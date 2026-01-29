# Scripts de Demonstração - Desafio Técnico Embrapii

Este diretório contém scripts de demonstração para cada questão do desafio técnico.

## 📋 Lista de Scripts

### Questão 1 - Otimização ORM e N+1 Queries
**Arquivo:** `demo_nplus1.py`

Demonstra o problema de N+1 queries e sua solução com `prefetch_related()`.

```bash
python manage.py shell < scripts/demo_nplus1.py
```

**O que demonstra:**
- Problema N+1: 6 queries executadas
- Solução otimizada: 2 queries executadas
- Redução de 67% nas queries
- Ferramentas para identificar o problema

---

### Questão 2 - Service Layer e Regras de Negócio
**Arquivo:** `demo_task_workflow.py`

Demonstra o Service Layer com validações de regras de negócio.

```bash
python manage.py shell < scripts/demo_task_workflow.py
```

**O que demonstra:**
- Separação de responsabilidades (Service Layer)
- Validação de regras de negócio
- State machine para transições de status
- Auditoria e rastreabilidade

---

### Questão 4 - Validações de Backend
**Arquivo:** `demo_validacoes_api.py`

Demonstra validações em múltiplas camadas do backend.

```bash
python manage.py shell < scripts/demo_validacoes_api.py
```

**O que demonstra:**
- Validação SINTÁTICA (formato, tamanho, tipo)
- Validação SEMÂNTICA (relacionamento entre campos)
- Validação de REGRAS DE NEGÓCIO (lógica de domínio)
- Importância de não confiar apenas no frontend

---

## 🚀 Como Executar Todos os Testes

```bash
# Ative o ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Execute cada script
python manage.py shell < scripts/demo_nplus1.py
python manage.py shell < scripts/demo_task_workflow.py
python manage.py shell < scripts/demo_validacoes_api.py
```

## 📊 Estrutura de Cada Script

Todos os scripts seguem o mesmo padrão:
1. **Setup:** Prepara dados de teste
2. **Testes:** Executa cenários práticos
3. **Conclusão:** Resume os conceitos demonstrados

## 💡 Observações

- Os scripts são independentes e podem ser executados em qualquer ordem
- Cada script limpa seus próprios dados de teste
- Outputs são formatados para facilitar prints e documentação
- Código está comentado para fins didáticos
