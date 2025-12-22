"""
Script para criar as taxas de entrega iniciais
Execute: python criar_taxas.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pizzaria.models import TaxaEntrega

# Criar as taxas de entrega
locais = [
    {'nome': 'Três Altos (Sítio)', 'taxa': 6.00},
    {'nome': 'Frutuoso Gomes', 'taxa': 6.00},
    {'nome': 'Almino Afonso', 'taxa': 6.00},
    {'nome': 'Lucrécia', 'taxa': 0.00},
    {'nome': 'Lucrécia (Sítio)', 'taxa': 0.00},
]

for local in locais:
    taxa, criado = TaxaEntrega.objects.update_or_create(
        nome=local['nome'],
        defaults={'taxa': local['taxa'], 'ativo': True}
    )
    if criado:
        print(f"✅ Taxa criada: {taxa.nome} - R$ {taxa.taxa:.2f}")
    else:
        print(f"ℹ️ Taxa já existe: {taxa.nome} - R$ {taxa.taxa:.2f}")

print("\n🎉 Concluído! Agora você pode:")
print("1. Editar os valores das taxas no admin Django (/admin/)")
print("2. Ou executar este script novamente com os valores corretos")
