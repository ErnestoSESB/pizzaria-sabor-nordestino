#!/usr/bin/env python
"""
Script de inicialização para Railway
Cria superusuário e popula dados iniciais
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from pizzaria.models import Pizza, TaxaEntrega

User = get_user_model()

def criar_superuser():
    """Cria superusuário se não existir"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            password='pizzaria2025',
            email='admin@sabornordestino.com'
        )
        print('✅ Superusuário criado: admin / pizzaria2025')
    else:
        print('ℹ️ Superusuário já existe')

def popular_taxas():
    """Cria taxas de entrega se não existirem"""
    taxas = [
        {'nome': 'Três Altos', 'taxa': 6.00},
        {'nome': 'Frutuoso Gomes', 'taxa': 6.00},
        {'nome': 'Almino Afonso', 'taxa': 6.00},
        {'nome': 'Lucrécia', 'taxa': 0.00},
        {'nome': 'Lucrécia (Sítio)', 'taxa': 0.00},
    ]
    
    for taxa_data in taxas:
        taxa, created = TaxaEntrega.objects.get_or_create(
            nome=taxa_data['nome'],
            defaults={'taxa': taxa_data['taxa']}
        )
        if created:
            print(f'✅ Taxa criada: {taxa.nome} - R$ {taxa.taxa:.2f}')
        else:
            print(f'ℹ️ Taxa já existe: {taxa.nome}')

def popular_pizzas():
    """Cria pizzas básicas se não existirem"""
    if Pizza.objects.count() == 0:
        pizzas_basicas = [
            {'nome': 'Calabresa', 'ingredientes': 'Calabresa, cebola, mussarela e azeitonas', 'especial': False},
            {'nome': 'Frango', 'ingredientes': 'Frango desfiado, mussarela, milho e azeitonas', 'especial': False},
            {'nome': 'Portuguesa', 'ingredientes': 'Presunto, mussarela, ovo, cebola, tomate e azeitonas', 'especial': False},
            {'nome': 'Nordestina', 'ingredientes': 'Carne seca temperada, mussarela, cebola e azeitonas', 'especial': True},
            {'nome': '4 Queijos', 'ingredientes': 'Mussarela, catupiry, parmesão, provolone', 'especial': True},
            {'nome': 'Atum 1', 'ingredientes': 'Atum, cebola, tomate e azeitonas', 'especial': True},
            {'nome': 'Carne de Sol', 'ingredientes': 'Carne de sol, cebola, tomate, queijo coalho', 'especial': True},
        ]
        
        for pizza_data in pizzas_basicas:
            Pizza.objects.create(**pizza_data)
            print(f'✅ Pizza criada: {pizza_data["nome"]}')
    else:
        print(f'ℹ️ Já existem {Pizza.objects.count()} pizzas cadastradas')

if __name__ == '__main__':
    print('🚀 Iniciando configuração do Railway...\n')
    criar_superuser()
    print()
    popular_taxas()
    print()
    popular_pizzas()
    print('\n✨ Configuração concluída!')
