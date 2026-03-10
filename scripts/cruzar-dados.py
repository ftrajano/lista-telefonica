#!/usr/bin/env python3
"""
Script para cruzar dados do Google Maps com a base de empresas da Prefeitura do Recife.

Objetivo: Enricher os dados do Google Maps com CNPJ oficial da prefeitura.
"""

import csv
import json
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

# Configurações
BASE_DIR = Path('/home/ftrajano/projetos/computacao/lista-telefonica')
GOOGLE_MAPS_FILE = BASE_DIR / 'src/data/telefones-raw.json'
PREFEITURA_FILE = BASE_DIR / 'docs/empresasativender.csv'
OUTPUT_FILE = BASE_DIR / 'src/data/telefones-enriquecidos.json'
REPORT_FILE = BASE_DIR / 'docs/relatorio-cruzamento.json'

def similaridade(str1, str2):
    """Calcula similaridade entre duas strings (0 a 1)."""
    return SequenceMatcher(None, str1, str2).ratio()

def normalizar_nome(nome):
    """Remove espaços extras e converte para maiúsculas."""
    if not nome:
        return ''
    return ' '.join(nome.strip().upper().split())

def carregar_google_maps(arquivo):
    """Carrega dados do Google Maps."""
    with open(arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)

def carregar_prefeitura(arquivo):
    """Carrega dados da Prefeitura e cria índices."""
    dados = []
    indice_nome = defaultdict(list)
    indice_endereco = defaultdict(list)
    
    with open(arquivo, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            # Apenas empresas ATIVAS
            if row.get('situacao_empresa') != 'ATIVO':
                continue
            
            dados.append(row)
            
            # Indexar por nome fantasia
            nome_fantasia = normalizar_nome(row.get('nome_fantasia', ''))
            razao_social = normalizar_nome(row.get('razao_social', ''))
            
            if nome_fantasia:
                indice_nome[nome_fantasia].append(row)
            if razao_social:
                indice_nome[razao_social].append(row)
            
            # Indexar por endereço + bairro
            endereco = f"{normalizar_nome(row.get('nome_logradouro', ''))} {normalizar_nome(row.get('nome_bairro', ''))}"
            if endereco:
                indice_endereco[endereco].append(row)
    
    return dados, indice_nome, indice_endereco

def buscar_match_perfeito(nome, indice_nome):
    """Busca match perfeito por nome."""
    nome_norm = normalizar_nome(nome)
    return indice_nome.get(nome_norm, [])

def buscar_match_parcial(nome, indice_nome, threshold=0.7):
    """Busca match parcial usando similaridade."""
    nome_norm = normalizar_nome(nome)
    matches = []
    
    for chave, itens in indice_nome.items():
        similaridade_nomes = similaridade(nome_norm, chave)
        if similaridade_nomes >= threshold:
            matches.append((itens[0], similaridade_nomes))
    
    # Retornar apenas o melhor match
    if matches:
        return sorted(matches, key=lambda x: x[1], reverse=True)[0][0]
    return None

def cruzar_dados(google_data, indice_nome, indice_endereco):
    """Cruza dados do Google Maps com Prefeitura."""
    resultados = {
        'match_perfeito': [],
        'match_parcial': [],
        'match_endereco': [],
        'sem_match': []
    }
    
    for item in google_data:
        google_nome = item['nome']
        google_bairro = item['bairro']
        
        # 1. Tentar match perfeito por nome
        matches_perfeitos = buscar_match_perfeito(google_nome, indice_nome)
        if matches_perfeitos:
            # Usar o primeiro match
            pref_data = matches_perfeitos[0]
            resultados['match_perfeito'].append({
                'google': item,
                'prefeitura': pref_data,
                'tipo_match': 'PERFEITO',
                'similaridade': 1.0
            })
            continue
        
        # 2. Tentar match parcial por nome
        match_parcial = buscar_match_parcial(google_nome, indice_nome, threshold=0.7)
        if match_parcial:
            resultados['match_parcial'].append({
                'google': item,
                'prefeitura': match_parcial,
                'tipo_match': 'PARCIAL',
                'similaridade': similaridade(google_nome, match_parcial.get('nome_fantasia', ''))
            })
            continue
        
        # 3. Tentar match por endereço
        endereco_google = f"{google_bairro}"
        # (Simplificado - poderia usar endereço completo)
        
        if endereco_google in indice_endereco:
            pref_data = indice_endereco[endereco_google][0]
            resultados['match_endereco'].append({
                'google': item,
                'prefeitura': pref_data,
                'tipo_match': 'ENDERECO',
                'similaridade': 0.5
            })
            continue
        
        # 4. Sem match
        resultados['sem_match'].append(item)
    
    return resultados

def enriquecer_dados(resultados_cruzamento):
    """Cria base de dados enriquecida."""
    dados_enriquecidos = []
    
    for tipo, itens in resultados_cruzamento.items():
        for item in itens:
            if isinstance(item, dict) and 'google' in item and 'prefeitura' in item:
                google = item['google']
                pref = item['prefeitura']
                
                dado_enriquecido = {
                    **google,
                    'cnpj': pref.get('cnpj', ''),
                    'razao_social': pref.get('razao_social', ''),
                    'data_abertura': pref.get('data_inicio_empresa', ''),
                    'cnae': pref.get('cnae', ''),
                    'desc_atividade': pref.get('desc_atividade', ''),
                    'nome_grupo': pref.get('nome_grupo', ''),
                    'latitude_prefeitura': pref.get('latitude', ''),
                    'longitude_prefeitura': pref.get('longitude', ''),
                    'match_tipo': item['tipo_match'],
                    'similaridade': item['similaridade']
                }
                dados_enriquecidos.append(dado_enriquecido)
    
    return dados_enriquecidos

def gerar_relatorio(resultados_cruzamento, total_google, total_prefeitura):
    """Gera relatório estatístico do cruzamento."""
    relatorio = {
        'resumo': {
            'total_google_maps': total_google,
            'total_prefeitura': total_prefeitura,
            'match_perfeito': len(resultados_cruzamento['match_perfeito']),
            'match_parcial': len(resultados_cruzamento['match_parcial']),
            'match_endereco': len(resultados_cruzamento['match_endereco']),
            'total_matches': (len(resultados_cruzamento['match_perfeito']) +
                            len(resultados_cruzamento['match_parcial']) +
                            len(resultados_cruzamento['match_endereco'])),
            'sem_match': len(resultados_cruzamento['sem_match'])
        },
        'porcentagem_match': {
            'match_perfeito': len(resultados_cruzamento['match_perfeito']) / total_google * 100,
            'match_parcial': len(resultados_cruzamento['match_parcial']) / total_google * 100,
            'match_endereco': len(resultados_cruzamento['match_endereco']) / total_google * 100,
            'sem_match': len(resultados_cruzamento['sem_match']) / total_google * 100
        },
        'exemplos_match_perfeito': resultados_cruzamento['match_perfeito'][:10],
        'exemplos_match_parcial': resultados_cruzamento['match_parcial'][:10],
        'exemplos_sem_match': resultados_cruzamento['sem_match'][:10]
    }
    
    return relatorio

def salvar_dados(dados_enriquecidos, arquivo):
    """Salva dados enriquecidos em JSON."""
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados_enriquecidos, f, ensure_ascii=False, indent=2)

def salvar_relatorio(relatorio, arquivo):
    """Salva relatório em JSON."""
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

def main():
    """Função principal."""
    print("=" * 70)
    print("CRUZAMENTO GOOGLE MAPS × PREFEITURA DO RECIFE")
    print("=" * 70)
    
    # 1. Carregar dados
    print("\n📂 Carregando dados do Google Maps...")
    google_data = carregar_google_maps(GOOGLE_MAPS_FILE)
    print(f"   ✓ {len(google_data)} empresas carregadas")
    
    print("\n📂 Carregando dados da Prefeitura...")
    prefeitura_data, indice_nome, indice_endereco = carregar_prefeitura(PREFEITURA_FILE)
    print(f"   ✓ {len(prefeitura_data)} empresas carregadas")
    print(f"   ✓ {len(indice_nome)} nomes indexados")
    print(f"   ✓ {len(indice_endereco)} endereços indexados")
    
    # 2. Cruzar dados
    print("\n🔍 Cruzando dados...")
    resultados_cruzamento = cruzar_dados(google_data, indice_nome, indice_endereco)
    print(f"   ✓ Match perfeito: {len(resultados_cruzamento['match_perfeito'])}")
    print(f"   ✓ Match parcial: {len(resultados_cruzamento['match_parcial'])}")
    print(f"   ✓ Match endereço: {len(resultados_cruzamento['match_endereco'])}")
    print(f"   ✓ Sem match: {len(resultados_cruzamento['sem_match'])}")
    
    # 3. Enriquecer dados
    print("\n💾 Enriquecendo dados...")
    dados_enriquecidos = enriquecer_dados(resultados_cruzamento)
    print(f"   ✓ {len(dados_enriquecidos)} empresas enriquecidas")
    
    # 4. Gerar relatório
    print("\n📊 Gerando relatório...")
    relatorio = gerar_relatorio(resultados_cruzamento, len(google_data), len(prefeitura_data))
    
    # 5. Salvar arquivos
    print("\n💾 Salvando arquivos...")
    salvar_dados(dados_enriquecidos, OUTPUT_FILE)
    print(f"   ✓ Dados enriquecidos: {OUTPUT_FILE}")
    
    salvar_relatorio(relatorio, REPORT_FILE)
    print(f"   ✓ Relatório: {REPORT_FILE}")
    
    # 6. Mostrar resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DO CRUZAMENTO")
    print("=" * 70)
    resumo = relatorio['resumo']
    porcentagem = relatorio['porcentagem_match']
    
    print(f"\n📋 Google Maps: {resumo['total_google_maps']} empresas")
    print(f"🏛️  Prefeitura: {resumo['total_prefeitura']} empresas")
    
    print(f"\n✅ Match Perfeito: {resumo['match_perfeito']} ({porcentagem['match_perfeito']:.1f}%)")
    print(f"⚠️  Match Parcial: {resumo['match_parcial']} ({porcentagem['match_parcial']:.1f}%)")
    print(f"📍 Match Endereço: {resumo['match_endereco']} ({porcentagem['match_endereco']:.1f}%)")
    print(f"📊 Total Matches: {resumo['total_matches']} ({(resumo['total_matches']/resumo['total_google_maps']*100):.1f}%)")
    print(f"❌ Sem Match: {resumo['sem_match']} ({porcentagem['sem_match']:.1f}%)")
    
    print(f"\n🎯 Empresas com CNPJ disponível: {resumo['total_matches']}")
    print(f"💼 Empresas sem CNPJ: {resumo['sem_match']}")
    
    print("\n" + "=" * 70)
    print("✅ CRUZAMENTO CONCLUÍDO!")
    print("=" * 70)

if __name__ == '__main__':
    main()
