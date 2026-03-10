#!/usr/bin/env python3
"""
Script para filtrar empresas da Prefeitura para prospecção de assessores de investimentos.

Foco: Empresas de alto valor (não MEI, não comércio varejo)
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

# Configurações
BASE_DIR = Path('/home/ftrajano/projetos/computacao/lista-telefonica')
PREFEITURA_FILE = BASE_DIR / 'docs/empresasativender.csv'
OUTPUT_FILE = BASE_DIR / 'docs/empresas-investimento.csv'
RELATORIO_FILE = BASE_DIR / 'docs/relatorio-investimento.json'

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
        'excluidas_grupo': 0,
        'excluidas_atividade': 0,
        'excluidas_idade': 0,
        'excluidas_vigilancia': 0,
        'distribuicao_grupo': {},
        'distribuicao_bairro': {}
    }
    
    # Critérios de filtro
    grupos_prioritarios = {
        'SAUDE',
        'CONSTRUCAO CIVIL',
        'INDUSTRIA GERAL',
        'SERVICOS DE INFORMATICA',
        'TRANSPORTE E COMUNICACAO'
    }
    
    atividades_excluidas = [
        'VAREJISTA', 'ATACADISTA', 'RESTAURANTE', 'LANCHONETE', 'PADARIA',
        'MERCEARIA', 'MINIMERCADO', 'CONVENIENCIA', 'ACOUGUEIRO'
    ]
    
    with open(arquivo, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            estatisticas['total'] += 1
            
            # Apenas empresas ATIVAS
            if row.get('situacao_empresa') != 'ATIVO':
                continue
            
            estatisticas['ativas'] += 1
            
            # Critério 1: Grupo prioritário
            grupo = row.get('nome_grupo', '').upper()
            if grupo not in grupos_prioritarios:
                estatisticas['excluidas_grupo'] += 1
                continue
            
            # Critério 2: Atividade NÃO é comércio varejo/atacado/restaurante
            atividade = row.get('desc_atividade', '').upper()
            if any(excl in atividade for excl in atividades_excluidas):
                estatisticas['excluidas_atividade'] += 1
                continue
            
            # Critério 3: Idade mínima de 2 anos (empresas estáveis)
            data_abertura = parsear_data_abertura(row.get('data_abertura_empresa', ''))
            idade = calcular_idade_empresa(data_abertura)
            
            if idade < 2:
                estatisticas['excluidas_idade'] += 1
                continue
            
            # Critério 4 (Opcional): Vigilância sanitária (exige maior formalização)
            # if row.get('atividade_vig_sanitaria') == 'N':
            #     estatisticas['excluidas_vigilancia'] += 1
            #     continue
            
            # Empresa passou nos filtros!
            empresa_filtrada = {
                'razao_social': row.get('razao_social', ''),
                'nome_fantasia': row.get('nome_fantasia', ''),
                'cnpj': row.get('cnpj', ''),
                'cnae': row.get('cnae', ''),
                'desc_atividade': row.get('desc_atividade', ''),
                'nome_grupo': row.get('nome_grupo', ''),
                'data_abertura': row.get('data_abertura_empresa', ''),
                'idade_anos': idade,
                'atividade_vig_sanitaria': row.get('atividade_vig_sanitaria', ''),
                'atividade_predominante': row.get('atividade_predominante', ''),
                'endereco': f"{row.get('nome_logradouro', '')}, {row.get('bairro', '')}",
                'latitude': row.get('latitude', ''),
                'longitude': row.get('longitude', '')
            }
            
            empresas_filtradas.append(empresa_filtrada)
            
            # Estatísticas de distribuição
            if grupo not in estatisticas['distribuicao_grupo']:
                estatisticas['distribuicao_grupo'][grupo] = 0
            estatisticas['distribuicao_grupo'][grupo] += 1
            
            bairro = row.get('nome_bairro', '')
            if bairro not in estatisticas['distribuicao_bairro']:
                estatisticas['distribuicao_bairro'][bairro] = 0
            estatisticas['distribuicao_bairro'][bairro] += 1
    
    return empresas_filtradas, estatisticas

def salvar_csv(empresas, arquivo):
    """Salva empresas filtradas em CSV."""
    if not empresas:
        print("   ⚠️ Nenhuma empresa filtrada")
        return
    
    campos = [
        'razao_social', 'nome_fantasia', 'cnpj', 'cnae',
        'desc_atividade', 'nome_grupo', 'data_abertura',
        'idade_anos', 'atividade_vig_sanitaria',
        'atividade_predominante', 'endereco', 'latitude', 'longitude'
    ]
    
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
    print("   ✅ Idade: ≥ 2 anos")
    print("   ✅ Grupo: Saúde, Construção, Indústria, TI, Transporte")
    print("   ✅ Atividade: EXCLUI varejo, atacado, restaurantes, padarias")
    
    empresas_filtradas, estatisticas = filtrar_empresas(PREFEITURA_FILE)
    
    print(f"\n✅ {len(empresas_filtradas)} empresas filtradas")
    
    # 2. Salvar CSV
    print("\n💾 Salvando CSV...")
    salvar_csv(empresas_filtradas, OUTPUT_FILE)
    
    # 3. Salvar relatório
    relatorio = {
        'resumo': estatisticas,
        'empresas_top_idade': sorted(empresas_filtradas,
                                        key=lambda x: x['idade_anos'],
                                        reverse=True)[:20],
        'distribuicao_grupo': dict(sorted(estatisticas['distribuicao_grupo'].items(),
                                            key=lambda x: x[1],
                                            reverse=True)),
        'top Bairros': dict(sorted(estatisticas['distribuicao_bairro'].items(),
                                   key=lambda x: x[1],
                                   reverse=True)[:10])
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
    print(f"❌ Excluídas por grupo: {est['excluidas_grupo']:,}")
    print(f"❌ Excluídas por atividade: {est['excluidas_atividade']:,}")
    print(f"❌ Excluídas por idade: {est['excluidas_idade']:,}")
    print(f"🎯 Empresas filtradas: {len(empresas_filtradas):,}")
    
    print(f"\n📊 Distribuição por Grupo:")
    for grupo, count in list(relatorio['distribuicao_grupo'].items())[:5]:
        print(f"   {grupo}: {count:,}")
    
    print(f"\n💰 TOP 5 EMPRESAS POR IDADE (mais antigas = mais estáveis)")
    print("=" * 70)
    
    top_idade = sorted(empresas_filtradas, key=lambda x: x['idade_anos'], reverse=True)[:5]
    for i, emp in enumerate(top_idade, 1):
        print(f"\n{i}. {emp['nome_fantasia'] or emp['razao_social']}")
        print(f"   Idade: {emp['idade_anos']} anos")
        print(f"   Atividade: {emp['desc_atividade'][:60]}...")
        print(f"   CNPJ: {emp['cnpj']}")
    
    print("\n" + "=" * 70)
    print("✅ FILTRAGEM CONCLUÍDA!")
    print("=" * 70)
    print(f"\n💾 Arquivos gerados:")
    print(f"   📄 Empresas: {OUTPUT_FILE}")
    print(f"   📊 Relatório: {RELATORIO_FILE}")

if __name__ == '__main__':
    main()
