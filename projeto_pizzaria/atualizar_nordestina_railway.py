#!/usr/bin/env python
"""
Script para atualizar apenas a pizza Nordestina como especial
Pode ser executado no Railway sem afetar outros dados
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pizzaria.models import Pizza

print("🔄 Atualizando pizza Nordestina...\n")

try:
    pizza = Pizza.objects.get(nome='Nordestina')
    pizza.especial = True
    pizza.save()
    print(f"✅ Pizza {pizza.nome} atualizada como ESPECIAL!")
    print(f"   Ingredientes: {pizza.ingredientes}\n")
    
    # Mostrar todas as especiais
    print("📋 Pizzas Especiais:")
    for p in Pizza.objects.filter(especial=True).order_by('nome'):
        print(f"   ⭐ {p.nome}")
    
except Pizza.DoesNotExist:
    print("❌ Pizza Nordestina não encontrada no banco!")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

print("\n✨ Atualização concluída!")
