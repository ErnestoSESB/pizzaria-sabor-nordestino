#!/usr/bin/env python
"""
Script de inicialização para Railway
Executa migrations e cria dados iniciais
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def check_database_connection():
    """Verifica se a conexão com o banco está funcionando"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Conexão com banco de dados OK")
        return True
    except Exception as e:
        print(f"✗ Erro na conexão com banco: {e}")
        return False

def run_migrations():
    """Executa as migrations do Django"""
    try:
        print("\n=== EXECUTANDO MIGRATIONS ===")
        call_command('migrate', '--noinput', '--verbosity=2')
        print("✓ Migrations executadas com sucesso")
        return True
    except Exception as e:
        print(f"✗ Erro ao executar migrations: {e}")
        import traceback
        traceback.print_exc()
        return False

def collect_static():
    """Coleta arquivos estáticos"""
    try:
        print("\n=== COLETANDO ARQUIVOS ESTÁTICOS ===")
        call_command('collectstatic', '--noinput', '--clear')
        print("✓ Arquivos estáticos coletados")
        return True
    except Exception as e:
        print(f"✗ Erro ao coletar estáticos: {e}")
        return False

def create_initial_data():
    """Cria dados iniciais via comando init_data"""
    try:
        print("\n=== CRIANDO DADOS INICIAIS ===")
        call_command('init_data')
        print("✓ Dados iniciais criados")
        return True
    except Exception as e:
        print(f"⚠ Aviso ao criar dados iniciais: {e}")
        # Não falha se dados já existem
        return True

def main():
    print("=" * 50)
    print("RAILWAY SETUP - Pizzaria Sabor Nordestino")
    print("=" * 50)
    
    # 1. Verificar conexão
    if not check_database_connection():
        print("\n✗ Setup falhou: sem conexão com banco")
        sys.exit(1)
    
    # 2. Executar migrations
    if not run_migrations():
        print("\n✗ Setup falhou: erro nas migrations")
        sys.exit(1)
    
    # 3. Coletar estáticos
    if not collect_static():
        print("\n✗ Setup falhou: erro ao coletar estáticos")
        sys.exit(1)
    
    # 4. Criar dados iniciais
    create_initial_data()
    
    print("\n" + "=" * 50)
    print("✓ SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 50)

if __name__ == '__main__':
    main()
