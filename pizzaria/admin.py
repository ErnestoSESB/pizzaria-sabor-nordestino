from django.contrib import admin
from .models import Pizza, Pedido, ItemPedido, TaxaEntrega

@admin.register(TaxaEntrega)
class TaxaEntregaAdmin(admin.ModelAdmin):
	list_display = ('nome', 'taxa', 'ativo')
	list_filter = ('ativo',)
	search_fields = ('nome',)
	list_editable = ('taxa', 'ativo')

@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
	list_display = ('nome', 'especial', 'disponivel', 'criado_em')
	list_filter = ('especial', 'disponivel')
	search_fields = ('nome', 'ingredientes')
	list_editable = ('disponivel',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
	list_display = ('id', 'cliente', 'local_entrega', 'taxa_entrega', 'subtotal', 'total', 'status', 'criado_em')
	list_filter = ('status', 'criado_em', 'local_entrega')
	search_fields = ('cliente', 'endereco')
	readonly_fields = ('criado_em', 'atualizado_em')
	
@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
	list_display = ('pedido', 'pizza', 'tamanho', 'quantidade', 'preco_unitario', 'subtotal')
	list_filter = ('tamanho',)
	search_fields = ('pedido__cliente', 'pizza__nome')

