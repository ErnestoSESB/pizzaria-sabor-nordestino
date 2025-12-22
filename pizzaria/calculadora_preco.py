from decimal import Decimal

def calcular_preco_pizza(tamanho, sabores_especiais_count, total_sabores, 
                         borda_chocolate=False, catupiry_cima='nao', catupiry_borda=False):
    """
    Calcula o preço final da pizza baseado nas regras:
    
    Preços base:
    - G: R$ 39,00
    - M: R$ 32,00
    - P: R$ 25,00
    
    Sabores especiais (atum, carne de sol, 4 queijos):
    - Metade especial: +R$ 2,00
    - Toda especial: +R$ 4,00
    
    Borda de chocolate:
    - G: +R$ 6,00
    - M: +R$ 5,00
    - P: +R$ 4,00
    
    Catupiry original por cima:
    - G: +R$ 14,00 (inteira) / +R$ 7,00 (metade)
    - M: +R$ 12,00 (inteira) / +R$ 6,00 (metade)
    - P: +R$ 10,00 (inteira) / +R$ 5,00 (metade)
    
    Catupiry original na borda:
    - G: +R$ 12,00
    - M: +R$ 10,00
    - P: +R$ 8,00
    """
    
    # Preços base
    precos_base = {'P': Decimal('25.00'), 'M': Decimal('32.00'), 'G': Decimal('39.00')}
    preco = precos_base.get(tamanho, Decimal('39.00'))
    
    # Adicional por sabores especiais
    if sabores_especiais_count > 0:
        if sabores_especiais_count == total_sabores:
            # Toda a pizza é especial
            preco += Decimal('4.00')
        else:
            # Apenas parte é especial (metade ou 1/3)
            preco += Decimal('2.00')
    
    # Borda de chocolate
    if borda_chocolate:
        bordas = {'P': Decimal('4.00'), 'M': Decimal('5.00'), 'G': Decimal('6.00')}
        preco += bordas.get(tamanho, Decimal('6.00'))
    
    # Catupiry por cima
    if catupiry_cima == 'inteira':
        catupiry_cima_precos = {'P': Decimal('10.00'), 'M': Decimal('12.00'), 'G': Decimal('14.00')}
        preco += catupiry_cima_precos.get(tamanho, Decimal('14.00'))
    elif catupiry_cima == 'metade':
        catupiry_cima_precos = {'P': Decimal('5.00'), 'M': Decimal('6.00'), 'G': Decimal('7.00')}
        preco += catupiry_cima_precos.get(tamanho, Decimal('7.00'))
    
    # Catupiry na borda
    if catupiry_borda:
        catupiry_borda_precos = {'P': Decimal('8.00'), 'M': Decimal('10.00'), 'G': Decimal('12.00')}
        preco += catupiry_borda_precos.get(tamanho, Decimal('12.00'))
    
    return preco
