"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Executar setup na primeira inicialização
import django
django.setup()

# Executar migrations automaticamente (apenas em produção)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:  # Se estiver no Railway
    from django.core.management import call_command
    from django.db import connection
    from django.db.utils import OperationalError, ProgrammingError
    
    try:
        # Verificar se as tabelas existem
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'pizzaria_pizza'
            """)
            table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            print("🔧 Tabelas não encontradas. Executando migrations...")
            call_command('migrate', '--noinput')
            print("✅ Migrations executadas!")
            
            # Criar dados iniciais
            try:
                call_command('init_data')
                print("✅ Dados iniciais criados!")
            except Exception as e:
                print(f"⚠️ Aviso ao criar dados: {e}")
    except Exception as e:
        print(f"⚠️ Erro no auto-setup: {e}")

application = get_wsgi_application()
