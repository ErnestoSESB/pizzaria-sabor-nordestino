from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .calculadora_preco import calcular_preco_pizza
from .models import Pedido, Pizza


class CalculadoraPrecoTests(TestCase):
	def test_calcula_preco_com_sabor_especial_metade_e_adicionais(self):
		preco = calcular_preco_pizza(
			tamanho='G',
			sabores_especiais_count=1,
			total_sabores=2,
			borda_chocolate=True,
			catupiry_cima='metade',
			catupiry_borda=False,
		)
		# 39 base + 2 especial parcial + 6 borda chocolate + 7 catupiry metade
		self.assertEqual(preco, Decimal('54.00'))


class CheckoutCarrinhoTests(TestCase):
	def setUp(self):
		self.pizza = Pizza.objects.create(
			nome='Calabresa Teste',
			ingredientes='Calabresa, cebola e azeitona',
			disponivel=True,
			especial=False,
		)

	def _popular_carrinho(self):
		session = self.client.session
		session['carrinho'] = {
			str(self.pizza.id): {
				'pizza_id': str(self.pizza.id),
				'quantidade': 1,
				'preco': '39.00',
				'tamanho': 'G',
				'borda_chocolate': False,
				'catupiry_cima': 'nao',
				'catupiry_borda': False,
				'sabores': None,
			}
		}
		session.save()

	def test_finalizar_exige_post(self):
		self._popular_carrinho()
		response = self.client.get(reverse('carrinho_finalizar'))
		self.assertEqual(response.status_code, 405)

	def test_finalizar_cria_pedido_e_redireciona_whatsapp(self):
		self._popular_carrinho()
		response = self.client.post(
			reverse('carrinho_finalizar'),
			data={
				'nome': 'Cliente Teste',
				'endereco': '',
				'observacoes': 'Sem cebola',
				'pagamento': 'PIX',
				'local_entrega': 'local',
			},
		)

		self.assertEqual(Pedido.objects.count(), 1)
		pedido = Pedido.objects.first()
		self.assertEqual(pedido.cliente, 'Cliente Teste')
		self.assertEqual(pedido.subtotal, Decimal('39.00'))
		self.assertEqual(pedido.total, Decimal('39.00'))
		self.assertTrue(response.url.startswith('https://wa.me/'))
