from decimal import Decimal
from .models import Pizza
import json

class Carrinho:
    def __init__(self, request):
        self.session = request.session
        carrinho = self.session.get('carrinho')
        if not carrinho:
            carrinho = self.session['carrinho'] = {}
        self.carrinho = carrinho
    
    def adicionar(self, pizza, quantidade=1, preco=None, tamanho='G', borda_chocolate=False, 
                  catupiry_cima='nao', catupiry_borda=False, sabores=None):
        pizza_id = str(pizza.id)
        # Gera ID único se tiver sabores (para permitir múltiplas pizzas mistas diferentes)
        if sabores:
            import time
            item_id = f"{pizza_id}_{int(time.time() * 1000)}"
        else:
            item_id = pizza_id
        
        if item_id not in self.carrinho:
            self.carrinho[item_id] = {
                'pizza_id': pizza_id,
                'quantidade': quantidade,
                'preco': str(preco if preco else pizza.get_preco(tamanho)),
                'tamanho': tamanho,
                'borda_chocolate': borda_chocolate,
                'catupiry_cima': catupiry_cima,
                'catupiry_borda': catupiry_borda,
                'sabores': sabores
            }
        else:
            self.carrinho[item_id]['quantidade'] += quantidade
        self.salvar()
    
    def remover(self, item_id):
        if item_id in self.carrinho:
            del self.carrinho[item_id]
            self.salvar()
    
    def atualizar_quantidade(self, item_id, quantidade):
        if item_id in self.carrinho:
            self.carrinho[item_id]['quantidade'] = quantidade
            self.salvar()
    
    def salvar(self):
        self.session.modified = True
    
    def limpar(self):
        del self.session['carrinho']
        self.salvar()
    
    def __iter__(self):
        pizza_ids = [item['pizza_id'] for item in self.carrinho.values()]
        pizzas = Pizza.objects.filter(id__in=pizza_ids)
        pizzas_dict = {str(p.id): p for p in pizzas}
        
        for item_id, item_data in self.carrinho.items():
            item = item_data.copy()
            item['item_id'] = item_id
            item['pizza'] = pizzas_dict.get(item['pizza_id'])
            item['preco'] = Decimal(item['preco'])
            item['total'] = item['preco'] * item['quantidade']
            yield item
    
    def __len__(self):
        return sum(item['quantidade'] for item in self.carrinho.values())
    
    def get_total(self):
        return sum(Decimal(item['preco']) * item['quantidade'] for item in self.carrinho.values())
