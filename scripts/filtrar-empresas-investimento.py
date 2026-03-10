#!/usr/bin/env python3
"""
Script para filtrar empresas da Prefeitura para prospecção de assessores de investimentos.

Foco: Empresas de alto valor (não MEI)
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

# Configurações
BASE_DIR = Path('/home/ftrajano/projetos/computacao/lista-telefonica')
PREFEITURA_FILE = BASE_DIR / 'docs/empresasativender.csv'
OUTPUT_FILE = BASE_DIR / 'docs/empresas-filtradas-investimento.csv'
RELATORIO_FILE = BASE_DIR / 'docs/relatorio-filtragem-investimento.json'

def parsear_capital_social(capital_str):
    """Converte string de capital social para float."""
    if not capital_str or not str(capital_str).strip():
        return 0.0
    
    # Remover formatação (pontos, vírgulas)
    capital = ''.join(filter(str.isdigit, str(capital_str)))
    
    if len(capital) < 2:
        return 0.0
    
    # Dividir por 100 (últimos 2 dígitos são centavos)
    return float(capital[:-2]) + (float(capital[-2:]) / 100)

def parsear_data_abertura(data_str):
    """Converte string de data para datetime."""
    if not data_str:
        return None
    
    try:
        return datetime.strptime(data_str, '%Y-%m-%d')
    except:
        return None

def calcular_idade_empresa(data_abertura):
    """Calcula idade da empresa em anos."""
    if not data_abertura:
        return 0
    
    hoje = datetime.now()
    idade = (hoje - data_abertura).days / 365.25
    
    return round(idade, 1)

def filtrar_empresas(arquivo):
    """Filtra empresas para prospecção de assessores de investimentos."""
    
    empresas_filtradas = []
    estatisticas = {
        'total': 0,
        'ativas': 0,
        'mei': 0,
        'capital_alto': 0,
        'capital_medio': 0,
        'idade_alta': 0,
        'idade_media': 0
    }
    
    with open(arquivo, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            estatisticas['total'] += 1
            
            # Apenas empresas ATIVAS
            if row.get('situacao_empresa') != 'ATIVO':
                continue
            
            estatisticas['ativas'] += 1
            
            # Ignorar MEI (empresário individual - código 213-5)
            # Nota: A base da prefeitura NÃO tem código de natureza jurídica
            # Vamos usar outras estratégias
            
            # Estratégia 1: Filtrar por capital social
            capital = parsear_capital_social(row.get('capital_social', '0'))
            
            if capital < 10000:  # Menos de 10 mil - provável MEI
                estatisticas['mei'] += 1
                continue
            
            # Estratégia 2: Filtrar por antiguidade
            data_abertura = parsear_data_abertura(row.get('data_inicio_empresa', ''))
            idade = calcular_idade_empresa(data_abertura)
            
            # Empresas novas podem ser MEI
            if idade < 2 and capital < 50000:
                continue
            
            # Estratégia 3: Filtrar por atividade
            # Foco em categorias de maior valor para investimentos
            atividade = row.get('desc_atividade', '').upper()
            atividade_excluida = any(excl in atividade for excl in [
                'VAREJISTA', 'ATACADISTA', 'RESTAURANTE',
                'LANCHONETE', 'PADARIA', 'MERCEARIA',
                'MINIMERCADO', 'CONVENIENCIA'
            ])
            
            if atividade_excluida:
                continue
            
            # Estratégia 4: Filtrar por grupo
            grupo = row.get('nome_grupo', '').upper()
            grupos_prioritarios = [
                'SAUDE', 'CONSTRUCAO CIVIL', 'INDUSTRIA GERAL',
                'SERVICOS DE INFORMATICA', 'TRANSPORTE E COMUNICACAO'
            ]
            
            if grupo not in grupos_prioritarios:
                continue
            
            # Empresa passou nos filtros!
            empresa_filtrada = {
                'razao_social': row.get('razao_social', ''),
                'nome_fantasia': row.get('nome_fantasia', ''),
                'cnpj': row.get('cnpj', ''),
                'cnae': row.get('cnae', ''),
                'desc_atividade': row.get('desc_atividade', ''),
                'nome_grupo': row.get('nome_grupo', ''),
                'capital_social': capital,
                'data_abertura': row.get('data_inicio_empresa', ''),
                'idade_anos': idade,
                'endereco': f"{row.get('nome_logradouro', '')}, {row.get('bairro', '')}"
            }
            
            empresas_filtradas.append(empresa_filtrada)
            
            # Estatísticas
            if capital > 500000:
                estatisticas['capital_alto'] += 1
            elif capital > 100000:
                estatisticas['capital_medio'] += 1
            
            if idade >= 10:
                estatisticas['idade_alta'] += 1
            elif idade >= 5:
                estatisticas['idade_media'] += 1
    
    return empresas_filtradas, estatisticas

def salvar_csv(empresas, arquivo):
    """Salva empresas filtradas em CSV."""
    if not empresas:
        print("   ⚠️ Nenhuma empresa filtrada")
        return
    
    campos = ['razao_social', 'nome_fantasia', 'cnpj', 'cnae', 
              'desc_atividade', 'nome_grupo', 'capital_social', 
              'data_abertura', 'idade_anos', 'endereco']
    
    with open(arquivo, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(empresas)
    
    print(f"   ✓ {len(empresas)} empresas salvas")

def main():
    """Função principal."""
    print("=" * 70)
    print("FILTRAGEM DE EMPRESAS PARA ASSESSORES DE INVESTIMENTOS")
    print("=" * 70)
    
    # 1. Filtrar empresas
    print("\n🔍 Filtrando empresas da Prefeitura...")
    print("   Critérios:")
    print("   ✅ Situação: ATIVA")
    print("   ✅ Capital social: ≥ R$ 10.000")
    print("   ✅ Idade: ≥ 2 anos OU capital ≥ R$ 50.000")
    print("   ✅ Atividade: EXCLUI varejo, atacado, restaurantes")
    print("   ✅ Grupo: Saúde, Construção, Indústria, TI, Transporte")
    
    empresas_filtradas, estatisticas = filtrar_empresas(PREFEITURA_FILE)
    
    print(f"\n✅ {len(empresas_filtradas)} empresas filtradas")
    
    # 2. Salvar CSV
    print("\n💾 Salvando CSV...")
    salvar_csv(empresas_filtradas, OUTPUT_FILE)
    
    # 3. Salvar relatório
    relatorio = {
        'resumo': estatisticas,
        'empresas_top_capital': sorted(empresas_filtradas, 
                                           key=lambda x: x['capital_social'], 
                                           reverse=True)[:20],
        'empresas_top_idade': sorted(empresas_filtradas,
                                        key=lambda x: x['idade_anos'],
                                        reverse=True)[:20]
    }
    
    with open(RELATORIO_FILE, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    print(f"   ✓ {RELATORIO_FILE}")
    
    # 4. Mostrar resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DA FILTRAGEM")
    print("=" * 70)
    
    est = estatisticas
    
    print(f"\n📋 Total de empresas na base: {est['total']:,}")
    print(f"✅ Empresas ativas: {est['ativas']:,} ({est['ativas']/est['total']*100:.1f}%)")
    print(f"❌ MEI/Pequenas (excluídas): {est['mei']:,} ({est['mei']/est['ativas']*100:.1f}%)")
    print(f"🎯 Empresas filtradas: {len(empresas_filtradas):,}")
    
    print(f"\n💰 Distribuição por capital social:")
    print(f"   Alto (> R$ 500k): {est['capital_alto']:,}")
    print(f"   Médio (> R$ 100k): {est['capital_medio']:,}")
    
    print(f"\n📅 Distribuição por antiguidade:")
    print(f"   Alta (≥10 anos): {est['idade_alta']:,}")
    print(f"   Média (≥5 anos): {est['idade_media']:,}")
    
    print("\n" + "=" * 70)
    print("💰 TOP 5 EMPRESAS POR CAPITAL SOCIAL")
    print("=" * 70)
    
    top_capital = sorted(empresas_filtradas, key=lambda x: x['capital_social'], reverse=True)[:5]
    for i, emp in enumerate(top_capital, 1):
        print(f"\n{i}. {emp['nome_fantasia'] or emp['razao_social']}")
        print(f"   Capital: R$ {emp['capital_social']:,.2f}")
        print(f"   Idade: {emp['idade_anos']} anos")
        print(f"   Atividade: {emp['desc_atividade'][:50]}...")
    
    print("\n" + "=" * 70)
    print("✅ FILTRAGEM CONCLUÍDA!")
    print("=" * 70)

if __name__ == '__main__':
    main()
