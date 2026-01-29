# Desafio Embrapii

Sistema Django desenvolvido para o desafio Embrapii.

## Requisitos

- Python 3.12+
- Django 6.0+

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd embrappi
```

2. Crie e ative um ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute as migrações:
```bash
python manage.py migrate
```

5. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

O projeto estará disponível em `http://127.0.0.1:8000/`

## Estrutura do Projeto

- `config/` - Configurações do Django
- `core/` - App principal da aplicação
- `requirements.txt` - Dependências do projeto

## Tecnologias Utilizadas

- Django 6.0
- Django REST Framework
- Django Extensions
- Black (formatação de código)
- Pytest (testes)
