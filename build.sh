#!/usr/bin/env bash
# exit on error
set -o errexit

# Instala as dependências
pip install -r requirements.txt

# Coleta os arquivos estáticos
python manage.py collectstatic --noinput

# Aplica as migrações do banco de dados
python manage.py migrate

#Cria o superusuário e || true  evita que o build quebre nos próximos deploys, quando o usuário já existir.
python manage.py createsuperuser --noinput || true
