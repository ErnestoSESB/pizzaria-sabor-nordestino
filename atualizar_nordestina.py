#!/usr/bin/env python
"""
Script para marcar a pizza Nordestina como especial
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pizzaria.models import Pizza

def atualizar_nordestina():
    """Marca a pizza Nordestina como especial"""
    try:
        nordestina = Pizza.objects.get(nome='Nordestina')
        if not nordestina.especial:
            nordestina.especial = True
            nordestina.save()
            print('✅ Pizza Nordestina atualizada para especial!')
            print(f'   Nome: {nordestina.nome}')
            print(f'   Ingredientes: {nordestina.ingredientes}')
            print(f'   Especial: {nordestina.especial}')
        else:
            print('ℹ️ Pizza Nordestina já está marcada como especial')
    except Pizza.DoesNotExist:
        print('❌ Pizza Nordestina não encontrada no banco de dados')
    except Exception as e:
        print(f'❌ Erro ao atualizar: {e}')

if __name__ == '__main__':
    print('🔧 Atualizando pizza Nordestina...\n')
    atualizar_nordestina()
    print('\n✨ Concluído!')
