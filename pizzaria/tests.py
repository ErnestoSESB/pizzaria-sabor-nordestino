from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .calculadora_preco import calcular_preco_pizza
from .models import Bebida, Pedido, Pizza


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

	def test_finalizar_cria_pedido_no_app(self):
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
		self.assertRedirects(response, reverse('carrinho_detalhes'))


class PainelBebidasTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username='admin', password='123456')

	def test_bebida_pode_ter_imagem(self):
		bebida = Bebida.objects.create(
			nome='Refrigerante Teste',
			descricao='Lata 350ml',
			preco='8.50',
			disponivel=True,
			imagem=SimpleUploadedFile('refrigerante.png', b'fake-image-content', content_type='image/png'),
		)
		self.assertTrue(bebida.imagem)
		self.assertTrue(bebida.imagem.name.endswith('.png'))

	def test_pedido_finalizado_inclui_bebida_selecionada(self):
		pizza = Pizza.objects.create(
			nome='Calabresa',
			ingredientes='Calabresa',
			disponivel=True,
			especial=False,
		)
		bebida = Bebida.objects.create(
			nome='Coca-Cola',
			descricao='Lata 350ml',
			preco='8.50',
			disponivel=True,
		)
		response = self.client.post(
			reverse('carrinho_adicionar_pizza'),
			data={
				'acao': 'pedido',
				'tamanho': 'G',
				'num_sabores': '1',
				'sabor_1': str(pizza.id),
				'quer_bebida': 'sim',
				'bebida_id': str(bebida.id),
				'catupiry_cima': 'nao',
			},
			follow=True,
		)
		self.assertEqual(response.status_code, 200)
		carrinho = self.client.session.get('carrinho', {})
		self.assertGreater(len(carrinho), 1)
		self.assertTrue(any(item.get('bebida_id') == str(bebida.id) for item in carrinho.values()))

	def test_painel_bebidas_exige_login(self):
		response = self.client.get(reverse('painel_bebidas'))
		self.assertEqual(response.status_code, 302)

	def test_painel_bebidas_exibe_lista_para_admin(self):
		self.client.login(username='admin', password='123456')
		response = self.client.get(reverse('painel_bebidas'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Gerenciar Bebidas')
