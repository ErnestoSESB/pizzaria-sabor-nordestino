"""
Django management command para popular dados iniciais
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pizzaria.models import Pizza, TaxaEntrega

User = get_user_model()

class Command(BaseCommand):
    help = 'Popula dados iniciais no banco de dados'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando configuração...\n')
        
        # Criar superusuário
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                password='pizzaria2025',
                email='admin@sabornordestino.com'
            )
            self.stdout.write(self.style.SUCCESS('✅ Superusuário criado: admin / pizzaria2025'))
        else:
            self.stdout.write('ℹ️ Superusuário já existe')
        
        # Criar taxas de entrega
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
                self.stdout.write(self.style.SUCCESS(f'✅ Taxa criada: {taxa.nome} - R$ {taxa.taxa:.2f}'))
        
        # Criar pizzas básicas
        if Pizza.objects.count() == 0:
            pizzas_basicas = [
                {'nome': 'Calabresa', 'ingredientes': 'Calabresa, cebola, mussarela e azeitonas', 'especial': False, 'disponivel': True},
                {'nome': 'Frango', 'ingredientes': 'Frango desfiado, mussarela, milho e azeitonas', 'especial': False, 'disponivel': True},
                {'nome': 'Portuguesa', 'ingredientes': 'Presunto, mussarela, ovo, cebola, tomate e azeitonas', 'especial': False, 'disponivel': True},
                {'nome': '4 Queijos', 'ingredientes': 'Mussarela, catupiry, parmesão, provolone', 'especial': True, 'disponivel': True},
                {'nome': 'Atum', 'ingredientes': 'Atum, cebola, tomate e azeitonas', 'especial': True, 'disponivel': True},
                {'nome': 'Carne de Sol', 'ingredientes': 'Carne de sol, cebola, tomate, queijo coalho', 'especial': True, 'disponivel': True},
            ]
            
            for pizza_data in pizzas_basicas:
                Pizza.objects.create(**pizza_data)
                self.stdout.write(self.style.SUCCESS(f'✅ Pizza criada: {pizza_data["nome"]}'))
        else:
            self.stdout.write(f'ℹ️ Já existem {Pizza.objects.count()} pizzas cadastradas')
        
        self.stdout.write(self.style.SUCCESS('\n✨ Configuração concluída!'))
