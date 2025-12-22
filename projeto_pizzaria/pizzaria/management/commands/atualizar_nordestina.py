"""
Django management command para atualizar pizza Nordestina como especial
Execute: python manage.py atualizar_nordestina
"""
from django.core.management.base import BaseCommand
from pizzaria.models import Pizza

class Command(BaseCommand):
    help = 'Atualiza a pizza Nordestina como especial'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Atualizando pizza Nordestina...\n')
        
        try:
            pizza = Pizza.objects.get(nome='Nordestina')
            pizza.especial = True
            pizza.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Pizza {pizza.nome} atualizada como ESPECIAL!'))
            self.stdout.write(f'   Ingredientes: {pizza.ingredientes}\n')
            
            # Mostrar todas as especiais
            self.stdout.write('📋 Pizzas Especiais:')
            for p in Pizza.objects.filter(especial=True).order_by('nome'):
                self.stdout.write(self.style.SUCCESS(f'   ⭐ {p.nome}'))
            
        except Pizza.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Pizza Nordestina não encontrada no banco!'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro: {e}'))
            return
        
        self.stdout.write(self.style.SUCCESS('\n✨ Atualização concluída!'))
