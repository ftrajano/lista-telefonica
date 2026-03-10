#!/usr/bin/env python3
"""
Script rápido para cruzar dados do Google Maps com Prefeitura do Recife.

Foca em match perfeito por nome para maior eficiência.
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

# Configurações
BASE_DIR = Path('/home/ftrajano/projetos/computacao/lista-telefonica')
GOOGLE_MAPS_FILE = BASE_DIR / 'src/data/telefones-raw.json'
PREFEITURA_FILE = BASE_DIR / 'docs/empresasativender.csv'
OUTPUT_FILE = BASE_DIR / 'src/data/telefones-com-cnpj.json'
REPORT_FILE = BASE_DIR / 'docs/relatorio-cruzamento.json'

def normalizar_nome(nome):
    """Remove espaços extras e converte para maiúsculas."""
    if not nome:
        return ''
    return ' '.join(nome.strip().upper().split())

def carregar_google_maps(arquivo):
    """Carrega dados do Google Maps."""
    with open(arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)

def carregar_indice_prefeitura(arquivo):
    """Carrega apenas índice por nome da Prefeitura."""
    indice = {}
    
    with open(arquivo, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            # Apenas empresas ATIVAS
            if row.get('situacao_empresa') != 'ATIVO':
                continue
            
            cnpj = row.get('cnpj', '').strip()
            
            # Indexar por nome fantasia
            nome_fantasia = normalizar_nome(row.get('nome_fantasia', ''))
            if nome_fantasia and cnpj:
                if nome_fantasia not in indice:
                    indice[nome_fantasia] = row
                # Se já existe, manter o primeiro (match mais antigo)
            
            # Indexar por razão social
            razao_social = normalizar_nome(row.get('razao_social', ''))
            if razao_social and cnpj:
                if razao_social not in indice:
                    indice[razao_social] = row
    
    return indice

def cruzar_match_perfeito(google_data, indice_prefeitura):
    """Cruza usando apenas match perfeito por nome."""
    matches = []
    sem_match = []
    
    for item in google_data:
        google_nome = normalizar_nome(item['nome'])
        
        # Buscar match perfeito
        if google_nome in indice_prefeitura:
            pref_data = indice_prefeitura[google_nome]
            matches.append({
                'google': item,
                'prefeitura': pref_data,
                'tipo': 'PERFEITO'
            })
        else:
            sem_match.append(item)
    
    return matches, sem_match

def main():
    """Função principal."""
    print("=" * 70)
    print("CRUZAMENTO RÁPIDO GOOGLE MAPS × PREFEITURA")
    print("=" * 70)
    
    # 1. Carregar Google Maps
    print("\n📂 Google Maps...")
    google_data = carregar_google_maps(GOOGLE_MAPS_FILE)
    print(f"   ✓ {len(google_data)} empresas")
    
    # 2. Carregar índice da Prefeitura
    print("\n📂 Prefeitura (criando índice)...")
    indice_prefeitura = carregar_indice_prefeitura(PREFEITURA_FILE)
    print(f"   ✓ {len(indice_prefeitura)} empresas indexadas")
    
    # 3. Cruzar (match perfeito)
    print("\n🔍 Cruzando (match perfeito)...")
    matches, sem_match = cruzar_match_perfeito(google_data, indice_prefeitura)
    print(f"   ✓ Matches: {len(matches)}")
    print(f"   ✓ Sem match: {len(sem_match)}")
    
    # 4. Criar dados enriquecidos
    print("\n💾 Criando dados enriquecidos...")
    dados_enriquecidos = []
    
    for match in matches:
        google = match['google']
        pref = match['prefeitura']
        
        dado = {
            **google,
            'cnpj': pref.get('cnpj', ''),
            'razao_social': pref.get('razao_social', ''),
            'data_abertura': pref.get('data_inicio_empresa', ''),
            'cnae': pref.get('cnae', ''),
            'desc_atividade': pref.get('desc_atividade', ''),
            'nome_grupo': pref.get('nome_grupo', ''),
            'has_cnpj': True
        }
        dados_enriquecidos.append(dado)
    
    # Para empresas sem match, marcar como sem CNPJ
    for item in sem_match:
        dado = {
            **item,
            'cnpj': '',
            'razao_social': '',
            'data_abertura': '',
            'cnae': '',
            'desc_atividade': '',
            'nome_grupo': '',
            'has_cnpj': False
        }
        dados_enriquecidos.append(dado)
    
    print(f"   ✓ {len(dados_enriquecidos)} empresas processadas")
    
    # 5. Salvar
    print("\n💾 Salvando...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados_enriquecidos, f, ensure_ascii=False, indent=2)
    print(f"   ✓ {OUTPUT_FILE}")
    
    # 6. Relatório
    relatorio = {
        'resumo': {
            'total_google': len(google_data),
            'total_prefeitura_indexada': len(indice_prefeitura),
            'matches_perfeitos': len(matches),
            'sem_match': len(sem_match),
            'taxa_match': len(matches) / len(google_data) * 100
        },
        'exemplos_matches': matches[:5],
        'exemplos_sem_match': sem_match[:5]
    }
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    print(f"   ✓ {REPORT_FILE}")
    
    # 7. Mostrar resumo
    print("\n" + "=" * 70)
    print("📊 RESULTADO")
    print("=" * 70)
    print(f"\n📋 Google Maps: {relatorio['resumo']['total_google']} empresas")
    print(f"✅ Matches perfeitos: {relatorio['resumo']['matches_perfeitos']} ({relatorio['resumo']['taxa_match']:.1f}%)")
    print(f"❌ Sem match: {relatorio['resumo']['sem_match']} ({100-relatorio['resumo']['taxa_match']:.1f}%)")
    print(f"\n🎯 Empresas com CNPJ: {len(matches)}")
    print(f"📄 Empresas sem CNPJ: {len(sem_match)}")
    
    print("\n" + "=" * 70)
    print("✅ CONCLUÍDO!")
    print("=" * 70)

if __name__ == '__main__':
    main()
