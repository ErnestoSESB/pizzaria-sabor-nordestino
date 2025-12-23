from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Pizza, Pedido, ItemPedido
from .carrinho import Carrinho
from .calculadora_preco import calcular_preco_pizza
from urllib.parse import quote
import json

def index(request):
	return render(request, 'pizzaria/index.html')

def cardapio(request):
    pizzas = Pizza.objects.filter(disponivel=True)
    return render(request, 'pizzaria/cardapio.html', {'pizzas': pizzas})

def contato(request):
	return render(request, 'pizzaria/contato.html')

# Escolher sabores
def escolher_sabores(request):
	pizzas = Pizza.objects.filter(disponivel=True)
	pizzas_json = json.dumps([{
		'id': p.id,
		'nome': p.nome,
		'ingredientes': p.ingredientes,
		'especial': p.especial
	} for p in pizzas])
	pizzas_especiais_json = json.dumps([p.id for p in pizzas if p.especial])
	return render(request, 'pizzaria/escolher_sabores.html', {
		'pizzas_json': pizzas_json,
		'pizzas_especiais_json': pizzas_especiais_json
	})

# Carrinho views
def carrinho_adicionar(request, pizza_id):
	carrinho = Carrinho(request)
	pizza = get_object_or_404(Pizza, id=pizza_id)
	carrinho.adicionar(pizza=pizza, quantidade=1)
	return redirect('carrinho_detalhes')

def carrinho_adicionar_pizza(request):
	if request.method == 'POST':
		carrinho = Carrinho(request)
		
		# Dados do formulário
		tamanho = request.POST.get('tamanho')
		num_sabores = int(request.POST.get('num_sabores', 1))
		borda_chocolate = request.POST.get('borda_chocolate') == 'on'
		catupiry_cima = request.POST.get('catupiry_cima', 'nao')
		catupiry_borda = request.POST.get('catupiry_borda') == 'on'
		
		# Coletar sabores
		sabores_ids = []
		sabores_nomes = []
		sabores_especiais_count = 0
		
		for i in range(1, num_sabores + 1):
			sabor_id = request.POST.get(f'sabor_{i}')
			if sabor_id:
				pizza = get_object_or_404(Pizza, id=sabor_id)
				sabores_ids.append(int(sabor_id))
				sabores_nomes.append(pizza.nome)
				if pizza.especial:
					sabores_especiais_count += 1
		
		# Calcular preço
		preco_final = calcular_preco_pizza(
			tamanho=tamanho,
			sabores_especiais_count=sabores_especiais_count,
			total_sabores=num_sabores,
			borda_chocolate=borda_chocolate,
			catupiry_cima=catupiry_cima,
			catupiry_borda=catupiry_borda
		)
		
		# Criar descrição
		tamanhos = {'P': 'Pequena', 'M': 'Média', 'G': 'Grande'}
		descricao = f"{tamanhos[tamanho]} - {' / '.join(sabores_nomes)}"
		
		# Pizza principal (primeira selecionada)
		pizza_principal = get_object_or_404(Pizza, id=sabores_ids[0])
		
		# Adiciona ao carrinho
		carrinho.adicionar(
			pizza=pizza_principal,
			quantidade=1,
			preco=float(preco_final),
			tamanho=tamanho,
			borda_chocolate=borda_chocolate,
			catupiry_cima=catupiry_cima,
			catupiry_borda=catupiry_borda,
			sabores=json.dumps({
				'num_sabores': num_sabores,
				'ids': sabores_ids,
				'nomes': sabores_nomes,
				'descricao': descricao
			})
		)
		
		return redirect('carrinho_detalhes')
	return redirect('escolher_sabores')

def carrinho_remover(request, item_id):
	carrinho = Carrinho(request)
	carrinho.remover(item_id)
	return redirect('carrinho_detalhes')

def carrinho_detalhes(request):
	carrinho = Carrinho(request)
	from .models import TaxaEntrega
	
	# Ordem personalizada dos locais
	ordem_locais = [
		'Lucrécia',
		'Lucrécia (Sítio)',
		'Três Altos (Sítio)',
		'Almino Afonso',
		'Frutuoso Gomes'
	]
	
	# Buscar taxas ativas e ordenar manualmente
	taxas_dict = {taxa.nome: taxa for taxa in TaxaEntrega.objects.filter(ativo=True)}
	taxas_entrega = [taxas_dict[nome] for nome in ordem_locais if nome in taxas_dict]
	
	# Processar sabores para o template
	itens_processados = []
	for item in carrinho:
		item_data = {
			'pizza': item['pizza'],
			'quantidade': item['quantidade'],
			'preco': item['preco'],
			'total': item['total'],
			'item_id': item['item_id'],
			'tamanho': item.get('tamanho', 'G'),
			'borda_chocolate': item.get('borda_chocolate', False),
			'catupiry_cima': item.get('catupiry_cima', 'nao'),
			'catupiry_borda': item.get('catupiry_borda', False),
			'sabores_data': None
		}
		if item.get('sabores'):
			try:
				item_data['sabores_data'] = json.loads(item['sabores'])
			except:
				pass
		itens_processados.append(item_data)
	
	return render(request, 'pizzaria/carrinho.html', {
		'carrinho': carrinho,
		'itens': itens_processados,
		'taxas_entrega': taxas_entrega
	})

def carrinho_finalizar(request):
	carrinho = Carrinho(request)
	if len(carrinho) == 0:
		return redirect('cardapio')
	
	# Obter dados do formulário
	nome = request.POST.get('nome', '')
	endereco = request.POST.get('endereco', '')
	observacoes = request.POST.get('observacoes', '')
	pagamento = request.POST.get('pagamento', '')
	troco = request.POST.get('troco', '')
	local_entrega_id = request.POST.get('local_entrega', '')
	
	# Calcular taxa de entrega
	from .models import TaxaEntrega
	taxa_entrega = 0
	local_entrega = None
	nome_local = 'Retirada no local'
	
	if local_entrega_id and local_entrega_id != 'local':
		try:
			local_entrega = TaxaEntrega.objects.get(id=local_entrega_id, ativo=True)
			taxa_entrega = local_entrega.taxa
			nome_local = local_entrega.nome
		except TaxaEntrega.DoesNotExist:
			pass
	
	subtotal = carrinho.get_total()
	total_final = subtotal + taxa_entrega
	
	# Criar pedido no banco de dados
	pedido = Pedido.objects.create(
		cliente=nome,
		endereco=endereco,
		observacao=observacoes,
		local_entrega=local_entrega,
		taxa_entrega=taxa_entrega,
		subtotal=subtotal,
		total=total_final
	)
	
	# Criar itens do pedido
	for item in carrinho:
		ItemPedido.objects.create(
			pedido=pedido,
			pizza=item['pizza'],
			quantidade=item['quantidade'],
			preco_unitario=item['preco'],
			sabores=item.get('sabores'),
			tamanho=item.get('tamanho', 'G'),
			borda_chocolate=item.get('borda_chocolate', False),
			catupiry_cima=item.get('catupiry_cima', 'nao'),
			catupiry_borda=item.get('catupiry_borda', False)
		)
	
	# Montar mensagem para WhatsApp
	mensagem = "*NOVO PEDIDO - PIZZARIA SABOR NORDESTINO*\n\n"
	mensagem += f"*Pedido #{pedido.id}*\n\n"
	
	mensagem += "*DADOS DO CLIENTE*\n"
	mensagem += f"Nome: {nome}\n"
	mensagem += f"Endereço: {endereco}\n\n"
	
	mensagem += "*PEDIDO*\n"
	for item in carrinho:
		# Descrição da pizza
		if item.get('sabores'):
			sabores_data = json.loads(item['sabores'])
			mensagem += f"• {item['quantidade']}x Pizza {sabores_data['descricao']}\n"
			mensagem += f"  Sabores: {', '.join(sabores_data['nomes'])}\n"
		else:
			mensagem += f"• {item['quantidade']}x {item['pizza'].nome}\n"
			mensagem += f"  {item['pizza'].ingredientes}\n"
		
		# Tamanho
		tamanhos = {'P': 'Pequena', 'M': 'Média', 'G': 'Grande'}
		tamanho = item.get('tamanho', 'G')
		mensagem += f"  Tamanho: {tamanhos.get(tamanho, 'Grande')}\n"
		
		# Adicionais
		adicionais = []
		if item.get('borda_chocolate'):
			adicionais.append('Borda de Chocolate')
		
		catupiry_cima = item.get('catupiry_cima', 'nao')
		if catupiry_cima == 'inteira':
			adicionais.append('Catupiry Original por Cima (Inteira)')
		elif catupiry_cima == 'metade':
			adicionais.append('Catupiry Original por Cima (Metade)')
		
		if item.get('catupiry_borda'):
			adicionais.append('Catupiry Original na Borda')
		
		if adicionais:
			mensagem += f"  Adicionais: {', '.join(adicionais)}\n"
		
		mensagem += f"  R$ {item['preco']:.2f} x {item['quantidade']} = R$ {item['total']:.2f}\n\n"
	
	mensagem += f"*Subtotal: R$ {subtotal:.2f}*\n"
	
	# Taxa de entrega
	if taxa_entrega > 0:
		mensagem += f"*Taxa de Entrega ({nome_local}): R$ {taxa_entrega:.2f}*\n"
	else:
		mensagem += f"*{nome_local}*\n"
	
	mensagem += f"*TOTAL: R$ {total_final:.2f}*\n\n"
	
	mensagem += f"*Pagamento:* {pagamento}\n"
	if pagamento == 'Dinheiro' and troco:
		mensagem += f"Troco para: R$ {troco}\n"
	
	if observacoes:
		mensagem += f"\n*Observações:*\n{observacoes}\n"
	
	mensagem += "\n*Aguardando confirmação e tempo de entrega!*"
	
	whatsapp_url = f"https://wa.me/5584999852976?text={quote(mensagem)}"
	
	# Limpar carrinho após finalizar
	carrinho.limpar()
	
	return redirect(whatsapp_url)

@login_required(login_url='/login/')
def painel(request):
	from django.db.models import Sum, Count, Q
	
	hoje = timezone.now().date()
	
	# Contadores básicos
	pizzas_total = Pizza.objects.count()
	pedidos_hoje = Pedido.objects.filter(criado_em__date=hoje).count()
	pedidos_novos = Pedido.objects.filter(status='Novo').count()
	
	# Faturamento
	faturamento_hoje = Pedido.objects.filter(criado_em__date=hoje).aggregate(total=Sum('total'))['total'] or 0
	
	sete_dias_atras = hoje - timedelta(days=7)
	faturamento_semana = Pedido.objects.filter(criado_em__date__gte=sete_dias_atras).aggregate(total=Sum('total'))['total'] or 0
	
	trinta_dias_atras = hoje - timedelta(days=30)
	faturamento_mes = Pedido.objects.filter(criado_em__date__gte=trinta_dias_atras).aggregate(total=Sum('total'))['total'] or 0
	
	# Ticket médio
	pedidos_totais = Pedido.objects.count()
	faturamento_total = Pedido.objects.aggregate(total=Sum('total'))['total'] or 0
	ticket_medio = faturamento_total / pedidos_totais if pedidos_totais > 0 else 0
	
	# Pizza mais vendida
	pizza_mais_vendida = ItemPedido.objects.values('pizza__nome').annotate(
		total=Sum('quantidade')
	).order_by('-total').first()
	
	# Tamanho mais vendido
	tamanho_mais_vendido = ItemPedido.objects.values('tamanho').annotate(
		total=Sum('quantidade')
	).order_by('-total').first()
	
	# Status dos pedidos
	status_pedidos = {
		'novos': Pedido.objects.filter(status='Novo').count(),
		'preparo': Pedido.objects.filter(status='Em preparo').count(),
		'prontos': Pedido.objects.filter(status='Pronto').count(),
		'entregues': Pedido.objects.filter(status='Entregue').count(),
	}
	
	# Pedidos por período
	pedidos_ontem = Pedido.objects.filter(criado_em__date=hoje - timedelta(days=1)).count()
	pedidos_semana = Pedido.objects.filter(criado_em__date__gte=sete_dias_atras).count()
	
	# Top 5 pizzas mais vendidas
	top_pizzas = ItemPedido.objects.values('pizza__nome').annotate(
		total=Sum('quantidade')
	).order_by('-total')[:5]
	
	context = {
		'pizzas_total': pizzas_total,
		'pedidos_hoje': pedidos_hoje,
		'pedidos_novos': pedidos_novos,
		'faturamento_hoje': faturamento_hoje,
		'faturamento_semana': faturamento_semana,
		'faturamento_mes': faturamento_mes,
		'ticket_medio': ticket_medio,
		'pizza_mais_vendida': pizza_mais_vendida,
		'tamanho_mais_vendido': tamanho_mais_vendido,
		'status_pedidos': status_pedidos,
		'pedidos_ontem': pedidos_ontem,
		'pedidos_semana': pedidos_semana,
		'top_pizzas': top_pizzas,
	}
	
	return render(request, 'pizzaria/painel.html', context)

# Gerenciar Pizzas
@login_required(login_url='/login/')
def painel_pizzas(request):
	pizzas = Pizza.objects.all().order_by('-criado_em')
	return render(request, 'pizzaria/painel_pizzas.html', {'pizzas': pizzas})

@login_required(login_url='/login/')
def pizza_adicionar(request):
	if request.method == 'POST':
		nome = request.POST.get('nome')
		ingredientes = request.POST.get('ingredientes')
		especial = request.POST.get('especial') == 'on'
		Pizza.objects.create(nome=nome, ingredientes=ingredientes, especial=especial)
		return redirect('painel_pizzas')
	return render(request, 'pizzaria/pizza_form.html')

@login_required(login_url='/login/')
def pizza_editar(request, pizza_id):
	pizza = get_object_or_404(Pizza, id=pizza_id)
	if request.method == 'POST':
		pizza.nome = request.POST.get('nome')
		pizza.ingredientes = request.POST.get('ingredientes')
		pizza.especial = request.POST.get('especial') == 'on'
		pizza.disponivel = request.POST.get('disponivel') == 'on'
		pizza.save()
		return redirect('painel_pizzas')
	return render(request, 'pizzaria/pizza_form.html', {'pizza': pizza})

@login_required(login_url='/login/')
def pizza_excluir(request, pizza_id):
	pizza = get_object_or_404(Pizza, id=pizza_id)
	pizza.delete()
	return redirect('painel_pizzas')

# Gerenciar Pedidos
@login_required(login_url='/login/')
def painel_pedidos(request):
	filtro = request.GET.get('filtro', 'hoje')
	data_especifica = request.GET.get('data', '')
	
	# Filtrar por data específica se fornecida
	if data_especifica:
		try:
			from datetime import datetime
			data_obj = datetime.strptime(data_especifica, '%Y-%m-%d').date()
			pedidos = Pedido.objects.filter(criado_em__date=data_obj)
			filtro = 'data'
		except ValueError:
			# Se a data for inválida, usar filtro padrão
			data_especifica = ''
			pedidos = Pedido.objects.filter(criado_em__date=timezone.now().date())
	else:
		# Filtrar por data padrão
		hoje = timezone.now().date()
		if filtro == 'hoje':
			pedidos = Pedido.objects.filter(criado_em__date=hoje)
		elif filtro == 'ontem':
			ontem = hoje - timedelta(days=1)
			pedidos = Pedido.objects.filter(criado_em__date=ontem)
		elif filtro == '7dias':
			sete_dias_atras = hoje - timedelta(days=7)
			pedidos = Pedido.objects.filter(criado_em__date__gte=sete_dias_atras)
		else:  # todos
			pedidos = Pedido.objects.all()
	
	pedidos = pedidos.order_by('-criado_em')
	
	# Processar sabores para cada pedido
	pedidos_processados = []
	for pedido in pedidos:
		itens_processados = []
		for item in pedido.itens.all():
			item_data = {
				'item': item,
				'sabores_lista': None
			}
			if item.sabores:
				try:
					sabores_data = json.loads(item.sabores)
					nomes = sabores_data.get('nomes', [])
					item_data['sabores_lista'] = ', '.join(nomes)
				except:
					pass
			itens_processados.append(item_data)
		pedido.itens_processados = itens_processados
		pedidos_processados.append(pedido)
	
	return render(request, 'pizzaria/painel_pedidos.html', {
		'pedidos': pedidos_processados, 
		'filtro_atual': filtro,
		'data_filtro': data_especifica
	})

@login_required(login_url='/login/')
def pedido_adicionar(request):
	if request.method == 'POST':
		cliente = request.POST.get('cliente')
		telefone = request.POST.get('telefone')
		endereco = request.POST.get('endereco', '')
		observacao = request.POST.get('observacao', '')
		
		pedido = Pedido.objects.create(
			cliente=cliente,
			telefone=telefone,
			endereco=endereco,
			observacao=observacao,
			total=0
		)
		
		# Adicionar itens ao pedido
		pizzas_ids = request.POST.getlist('pizza_id[]')
		quantidades = request.POST.getlist('quantidade[]')
		
		total = 0
		for pizza_id, quantidade in zip(pizzas_ids, quantidades):
			if pizza_id and quantidade:
				pizza = Pizza.objects.get(id=pizza_id)
				ItemPedido.objects.create(
					pedido=pedido,
					pizza=pizza,
					quantidade=int(quantidade),
					preco_unitario=pizza.preco
				)
				total += pizza.preco * int(quantidade)
		
		pedido.total = total
		pedido.save()
		return redirect('painel_pedidos')
	
	pizzas = Pizza.objects.filter(disponivel=True)
	return render(request, 'pizzaria/pedido_form.html', {'pizzas': pizzas})

@login_required(login_url='/login/')
def pedido_alterar_status(request, pedido_id):
	pedido = get_object_or_404(Pedido, id=pedido_id)
	if request.method == 'POST':
		pedido.status = request.POST.get('status')
		pedido.save()
	return redirect('painel_pedidos')

@login_required(login_url='/login/')
def pedido_imprimir(request, pedido_id):
	pedido = get_object_or_404(Pedido, id=pedido_id)
	
	# Processar itens com sabores
	itens_processados = []
	for item in pedido.itens.all():
		item_data = {
			'item': item,
			'sabores_data': None
		}
		if item.sabores:
			try:
				item_data['sabores_data'] = json.loads(item.sabores)
			except:
				pass
		itens_processados.append(item_data)
	
	return render(request, 'pizzaria/pedido_imprimir.html', {
		'pedido': pedido,
		'itens_processados': itens_processados
	})

def login_view(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('painel')
		else:
			return render(request, 'pizzaria/login.html', {'error': 'Usuário ou senha inválidos.'})
	return render(request, 'pizzaria/login.html')

def logout_view(request):
	logout(request)
	return redirect('login')

def debug_recriar_pizzas(request):
	"""View de debug para recriar pizzas"""
	from django.http import HttpResponse
	
	# Apagar todas
	count = Pizza.objects.count()
	Pizza.objects.all().delete()
	
	pizzas = [
		{'nome': 'Americana', 'ingredientes': 'Mussarela, presunto, ovo, bacon, cebola e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Bacon', 'ingredientes': 'Bacon, cebola, mussarela e azeitona', 'especial': False, 'disponivel': True},
		{'nome': 'Baiana', 'ingredientes': 'Calabresa moída, pimenta, cebola, mussarela e azeitona', 'especial': False, 'disponivel': True},
		{'nome': 'Caipira', 'ingredientes': 'Frango desfiado, milho, catupiry e azeitona', 'especial': False, 'disponivel': True},
		{'nome': 'Calabresa 1', 'ingredientes': 'Calabresa fatiada, cebola e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Calabresa 2', 'ingredientes': 'Calabresa fatiada, bacon, mussarela, cebola e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Calabresa 3', 'ingredientes': 'Mussarela por baixo, calabresa, cebola e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Calabresa 4', 'ingredientes': 'Calabresa, cheddar, mussarela, cebola, bacon e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Calacatu', 'ingredientes': 'Calabresa fatiada, catupiry, cebola e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Delícia', 'ingredientes': 'Lombinho, palmito, catupiry e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Frango Bacon 1', 'ingredientes': 'Frango, mussarela, bacon e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Frango Bacon 2', 'ingredientes': 'Frango, milho, ovo, mussarela, bacon e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Frango catupiry', 'ingredientes': 'Frango desfiado, catupiry e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Marguerita', 'ingredientes': 'Mussarela, parmesão, manjericão, tomate e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Milho', 'ingredientes': 'Mussarela e milho', 'especial': False, 'disponivel': True},
		{'nome': 'Mussarela', 'ingredientes': 'Mussarela, tomate e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Namorado', 'ingredientes': 'Palmito, catupiry, mussarela e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Napolitana', 'ingredientes': 'Mussarela, molho de tomate, parmesão e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Nordestina', 'ingredientes': 'Carne seca temperada, mussarela, cebola e azeitonas', 'especial': True, 'disponivel': True},
		{'nome': 'Portuguesa', 'ingredientes': 'Presunto, mussarela, palmito, cebola, ovo, ervilha e milho', 'especial': False, 'disponivel': True},
		{'nome': 'Toscana', 'ingredientes': 'Presunto, calabresa, ovo, mussarela, bacon e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'À moda do chefe', 'ingredientes': 'Lombo canadense, ovos, ervilha, palmito, mussarela, cebola e azeitonas', 'especial': False, 'disponivel': True},
		{'nome': 'Atum 1', 'ingredientes': 'Atum, cebola, tomate e azeitonas', 'especial': True, 'disponivel': True},
		{'nome': 'Atum 2', 'ingredientes': 'Atum, mussarela, cebola e azeitonas', 'especial': True, 'disponivel': True},
		{'nome': 'Quatro Queijos', 'ingredientes': 'Mussarela, gorgonzola, catupiry e provolone', 'especial': True, 'disponivel': True},
		{'nome': 'Chocolate 1', 'ingredientes': 'Creme de leite, chocolate, confetes e granulado', 'especial': False, 'disponivel': True},
		{'nome': 'Chocolate 2', 'ingredientes': 'Mussarela com chocolate', 'especial': False, 'disponivel': True},
	]
	
	for pizza_data in pizzas:
		Pizza.objects.create(**pizza_data)
	
	nordestina = Pizza.objects.get(nome='Nordestina')
	
	return HttpResponse(f"""
		<h1>✅ Pizzas Recriadas!</h1>
		<p>❌ {count} pizzas antigas apagadas</p>
		<p>✅ {len(pizzas)} pizzas novas criadas</p>
		<h2>🔥 Pizza Nordestina:</h2>
		<ul>
			<li>ID: {nordestina.id}</li>
			<li>Nome: {nordestina.nome}</li>
			<li>Especial: {'⭐ SIM' if nordestina.especial else '❌ NÃO'}</li>
		</ul>
		<a href="/escolher-sabores/">Ir para o site</a>
	""")
