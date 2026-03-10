#!/usr/bin/env python3
"""
Script para analisar a distribuição de empresas por grupo.
"""

import csv
from collections import defaultdict
from pathlib import Path

# Configurações
BASE_DIR = Path('/home/ftrajano/projetos/computacao/lista-telefonica')
PREFEITURA_FILE = BASE_DIR / 'docs/empresasativender.csv'
OUTPUT_FILE = BASE_DIR / 'docs/distribuicao-grupos.json'

def carregar_distribuicao(arquivo):
    """Carrega a distribuição de empresas por grupo."""
    grupos = defaultdict(int)
    
    with open(arquivo, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            # Apenas empresas ATIVAS
            if row.get('situacao_empresa') != 'ATIVO':
                continue
            
            grupo = row.get('nome_grupo', '')
            if grupo:
                grupos[grupo] += 1
    
    return dict(sorted(grupos.items(), key=lambda x: x[1], reverse=True))

def main():
    """Função principal."""
    print("=" * 70)
    print("DISTRIBUIÇÃO DE EMPRESAS POR GRUPO")
    print("=" * 70)
    
    # 1. Carregar distribuição
    print("\n📂 Carregando dados da Prefeitura...")
    grupos = carregar_distribuicao(PREFEITURA_FILE)
    
    total = sum(grupos.values())
    print(f"   ✓ {total:,} empresas ativas")
    print(f"   ✓ {len(grupos)} grupos diferentes")
    
    # 2. Mostrar distribuição
    print("\n" + "=" * 70)
    print("DISTRIBUIÇÃO POR GRUPO")
    print("=" * 70)
    
    for i, (grupo, count) in enumerate(grupos.items(), 1):
        porcentagem = count / total * 100
        print(f"\n{i:2d}. {grupo}")
        print(f"     {count:8,} empresas ({porcentagem:5.1f}%)")
        
        # Estimativa de 5.000 empresas
        empresas_por_grupo = min(5000, int(count))
        meses_para_5000 = 1 if empresas_por_grupo >= 5000 else int(5000 / empresas_por_grupo) + 1
        print(f"     5.000 empresas ≈ {meses_para_5000} mês(es)")
    
    # 3. Grupos mais promissores para investimentos
    print("\n" + "=" * 70)
    print("TOP 10 GRUPOS MAIS PROMISSORES PARA INVESTIMENTOS")
    print("=" * 70)
    
    grupos_promissores = [
        'CONSTRUCAO CIVIL',
        'SAUDE',
        'SERVICOS DE INFORMATICA',
        'INDUSTRIA GERAL',
        'TRANSPORTE E COMUNICACAO',
        'JURIDICO, ECONOMICO E TECNICO ADMINISTRATIVO',
        'CONTABILIDADE, CONSULTORIA E ASSESSORIA',
        'TURISMO, HOSPEDAGEM E ASSEMELHADOS',
        'INSTITUICOES FINANCEIRAS E SECURITARIAS',
        'INSTALACAO, COLOCACAO E MONTAGEM'
    ]
    
    print("\nGrupo                              | Empresas  | 5.000/mês")
    print("-" * 70)
    
    total_promissores = 0
    meses_totais = 0
    
    for grupo in grupos_promissores:
        if grupo in grupos:
            count = grupos[grupo]
            total_promissores += count
            
            meses = 1 if count >= 5000 else int(5000 / count) + 1
            meses_totais += meses
            
            print(f"{grupo:40s} | {count:8,} | {meses} mês(es)")
    
    print("-" * 70)
    print(f"{'TOTAL':<40s} | {total_promissores:8,} | {meses_totais} mês(es)")
    
    # 4. Cenários de processamento
    print("\n" + "=" * 70)
    print("CENÁRIOS DE PROCESSAMENTO")
    print("=" * 70)
    
    print("\n📊 Cenário 1: 5.000 empresas/mês (atual)")
    print(f"   Grupos: {len(grupos)}")
    print(f"   Empresas por grupo: 5.000")
    print(f"   Mês por grupo: variável")
    print(f"   Tempo total: {total // 5000 + (1 if total % 5000 else 0):,} meses")
    
    print("\n📊 Cenário 2: 10.000 empresas/mês (agressivo)")
    print(f"   Custo: $320/mês (excede free tier!)")
    print(f"   Tempo total: {total // 10000 + (1 if total % 10000 else 0):,} meses")
    
    print("\n📊 Cenário 3: 5.000 empresas/mês, TOP 10 grupos")
    print(f"   Grupos: 10")
    print(f"   Empresas: {total_promissores:,}")
    print(f"   Tempo: {meses_totais} meses")
    print(f"   Custo: ${meses_totais * 160:.2f}")
    
    print("\n" + "=" * 70)
    print("✅ CONCLUÍDO!")
    print("=" * 70)

if __name__ == '__main__':
    main()
