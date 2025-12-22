from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cardapio/', views.cardapio, name='cardapio'),
    path('contato/', views.contato, name='contato'),
    path('escolher-sabores/', views.escolher_sabores, name='escolher_sabores'),
    path('carrinho/', views.carrinho_detalhes, name='carrinho_detalhes'),
    path('carrinho/adicionar/<int:pizza_id>/', views.carrinho_adicionar, name='carrinho_adicionar'),
    path('carrinho/adicionar-pizza/', views.carrinho_adicionar_pizza, name='carrinho_adicionar_pizza'),
    path('carrinho/remover/<str:item_id>/', views.carrinho_remover, name='carrinho_remover'),
    path('carrinho/finalizar/', views.carrinho_finalizar, name='carrinho_finalizar'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Painel Admin
    path('painel/', views.painel, name='painel'),
    path('painel/pizzas/', views.painel_pizzas, name='painel_pizzas'),
    path('painel/pizzas/adicionar/', views.pizza_adicionar, name='pizza_adicionar'),
    path('painel/pizzas/editar/<int:pizza_id>/', views.pizza_editar, name='pizza_editar'),
    path('painel/pizzas/excluir/<int:pizza_id>/', views.pizza_excluir, name='pizza_excluir'),
    path('painel/pedidos/', views.painel_pedidos, name='painel_pedidos'),
    path('painel/pedidos/adicionar/', views.pedido_adicionar, name='pedido_adicionar'),
    path('painel/pedidos/status/<int:pedido_id>/', views.pedido_alterar_status, name='pedido_alterar_status'),
    path('painel/pedidos/imprimir/<int:pedido_id>/', views.pedido_imprimir, name='pedido_imprimir'),
]
