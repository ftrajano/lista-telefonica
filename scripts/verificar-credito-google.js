#!/usr/bin/env python3
"""
Script para verificar crédito disponível da API Google Places.

Não consome crédito, apenas verifica limites.
"""

# Fonte: https://developers.google.com/maps/billing/overview

# Limites da API Google Places
LIMITES = {
    'credito_mensal_usd': 200.00,
    'custo_nearby_search': 0.032,  # USD por requisição
    'custo_text_search': 0.005,    # USD por requisição
    'custo_geocoding': 0.005,      # USD por requisição
    'max_req_dia': 100000,
    'max_req_min': 100
}

def calcular_custo(quantidade_requisicoes, tipo='nearby_search'):
    """Calcula custo estimado."""
    custo_por_req = LIMITES[f'custo_{tipo}']
    return quantidade_requisicoes * custo_por_req

def verificar_custo(quantidade, tipo='nearby_search', margem_seguranca=0.8):
    """Verifica se está dentro do free tier com margem de segurança."""
    custo_estimado = calcular_custo(quantidade, tipo)
    max_gasto = LIMITES['credito_mensal_usd'] * margem_seguranca
    
    return {
        'quantidade': quantidade,
        'custo_estimado': custo_estimado,
        'max_gasto_permitido': max_gasto,
        'ultrapassa': custo_estimado > max_gasto,
        'percentagem_uso': (custo_estimado / LIMITES['credito_mensal_usd']) * 100
    }

def main():
    print("=" * 70)
    print("VERIFICAÇÃO DE CRÉDITO - API GOOGLE PLACES")
    print("=" * 70)
    
    # Cenários
    
    print("\n📊 CENÁRIOS DE USO:")
    
    # Cenário 1: 81.687 empresas
    cenario1 = verificar_custo(81687)
    print(f"\n1. 81.687 requisições (Todas as empresas filtradas)")
    print(f"   Custo estimado: ${cenario1['custo_estimado']:.2f}")
    print(f"   Limite (80%): ${cenario1['max_gasto_permitido']:.2f}")
    print(f"   Ultrapassa: {cenario1['ultrapassa']}")
    print(f"   Uso: {cenario1['percentagem_uso']:.1f}%")
    
    # Cenário 2: 50.000 empresas
    cenario2 = verificar_custo(50000)
    print(f"\n2. 50.000 requisições (Amostra)")
    print(f"   Custo estimado: ${cenario2['custo_estimado']:.2f}")
    print(f"   Limite (80%): ${cenario2['max_gasto_permitido']:.2f}")
    print(f"   Ultrapassa: {cenario2['ultrapassa']}")
    print(f"   Uso: {cenario2['percentagem_uso']:.1f}%")
    
    # Cenário 3: 10.000 empresas
    cenario3 = verificar_custo(10000)
    print(f"\n3. 10.000 requisições (Teste pequeno)")
    print(f"   Custo estimado: ${cenario3['custo_estimado']:.2f}")
    print(f"   Limite (80%): ${cenario3['max_gasto_permitido']:.2f}")
    print(f"   Ultrapassa: {cenario3['ultrapassa']}")
    print(f"   Uso: {cenario3['percentagem_uso']:.1f}%")
    
    # Recomendação
    print("\n" + "=" * 70)
    print("🎯 RECOMENDAÇÃO")
    print("=" * 70)
    print(f"""
Baseado nos limites:
- Custo por requisição: ${LIMITES['custo_nearby_search']:.3f}
- Free tier: ${LIMITES['credito_mensal_usd']:.2f}/mês
- Margem de segurança: 80% = ${LIMITES['credito_mensal_usd'] * 0.8:.2f}

✅ Seguro para executar: até 4.500 requisições/mês
⚠️  Cuidado: 4.500 - 6.250 requisições/mês
🔴 Evitar: > 6.250 requisições/mês

RECOMENDAÇÃO:
1. Processar 5.000 empresas inicialmente (teste)
   Custo: ${calcular_custo(5000):.2f}
   
2. Avaliar resultados
3. Decidir se vale a pena expandir para 81.687
   Custo: ${calcular_custo(81687):.2f}
""")

if __name__ == '__main__':
    main()
