#!/usr/bin/env python3
"""
Script para buscar CNPJ externamente para empresas sem match.

Estratégias:
1. Busca Google: "NOME EMPRESA CNPJ CIDADE"
2. Se falhar: apenas "NOME EMPRESA CNPJ"
3. Extrair CNPJ da página usando regex
"""

import json
import requests
import re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time
import random

# Configurações
BASE_DIR = Path('/home/ftrajano/projetos/computacao/lista-telefonica')
INPUT_FILE = BASE_DIR / 'src/data/telefones-com-cnpj.json'
OUTPUT_FILE = BASE_DIR / 'src/data/telefones-final.json'
REPORT_FILE = BASE_DIR / 'docs/relatorio-busca-cnpj.json'

# Regex para CNPJ
REGEX_CNPJ = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{14}'

def criar_url_google(empresa):
    """Cria URL de busca do Google para a empresa."""
    nome = empresa.get('nome', '')
    bairro = empresa.get('bairro', '')
    
    # Estratégia 1: Nome + bairro + CNPJ
    if bairro:
        query = f"{nome} {bairro} Recife CNPJ"
    else:
        query = f"{nome} Recife CNPJ"
    
    return f"https://www.google.com/search?q={quote_plus(query)}&num=5", query

def buscar_google(query_url):
    """Busca no Google e retorna HTML."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(query_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception as e:
        return None

def extrair_cnpj(html_content):
    """Extrai CNPJ de uma página HTML usando regex."""
    if not html_content:
        return None
    
    # Buscar CNPJ formatado (00.000.000/0000-00)
    cnpj_formatado = re.search(REGEX_CNPJ, html_content)
    
    if cnpj_formatado:
        cnpj = cnpj_formatado.group(0)
        # Remover formatação
        cnpj_limpo = re.sub(r'[^\d]', '', cnpj)
        return cnpj_limpo
    
    return None

def buscar_cnpj_empresa(empresa):
    """Busca CNPJ para uma empresa usando múltiplas estratégias."""
    
    # Estratégia 1: Nome + bairro + Recife CNPJ
    url1, query1 = criar_url_google(empresa)
    html1 = buscar_google(url1)
    
    cnpj1 = extrair_cnpj(html1) if html1 else None
    
    if cnpj1:
        return {
            'cnpj': cnpj1,
            'fonte': 'google_nome_bairro',
            'query': query1
        }
    
    # Estratégia 2: Apenas nome + CNPJ
    nome = empresa.get('nome', '')
    url2 = f"https://www.google.com/search?q={quote_plus(nome + ' CNPJ')}&num=5"
    html2 = buscar_google(url2)
    
    cnpj2 = extrair_cnpj(html2) if html2 else None
    
    if cnpj2:
        return {
            'cnpj': cnpj2,
            'fonte': 'google_nome_simples',
            'query': nome + ' CNPJ'
        }
    
    # Estratégia 3: Tentar usar nome fantasia para buscar em sites de CNPJ
    # (Simplificado para esta versão)
    
    return {
        'cnpj': None,
        'fonte': None,
        'query': query1
    }

def buscar_cnpjs_lote(empresas_sem_cnpj, max_empresas=50):
    """Busca CNPJ para um lote de empresas."""
    resultados = []
    
    # Limitar para não demorar demais
    empresas_processar = empresas_sem_cnpj[:max_empresas]
    
    print(f"\n📊 Processando {len(empresas_processar)} empresas (limitado)")
    
    for i, empresa in enumerate(empresas_processar, 1):
        nome = empresa.get('nome', '')
        
        print(f"\n[{i}/{len(empresas_processar)}] Buscando: {nome}")
        
        # Buscar CNPJ
        resultado_busca = buscar_cnpj_empresa(empresa)
        
        dado_atualizado = {
            **empresa,
            'cnpj_encontrado': resultado_busca['cnpj'],
            'cnpj_fonte': resultado_busca['fonte'],
            'cnpj_query': resultado_busca['query']
        }
        
        if resultado_busca['cnpj']:
            print(f"   ✓ CNPJ encontrado: {resultado_busca['cnpj']}")
        else:
            print(f"   ❌ CNPJ não encontrado")
        
        resultados.append(dado_atualizado)
        
        # Rate limiting (respeitar o Google)
        time.sleep(2 + random.uniform(0, 2))
    
    # Adicionar empresas restantes sem processamento
    empresas_restantes = empresas_sem_cnpj[max_empresas:]
    
    for empresa in empresas_restantes:
        resultado = {
            **empresa,
            'cnpj_encontrado': None,
            'cnpj_fonte': None,
            'cnpj_query': None,
            'nao_processado': True
        }
        resultados.append(resultado)
    
    return resultados

def main():
    """Função principal."""
    print("=" * 70)
    print("BUSCA DE CNPJ EXTERNO")
    print("=" * 70)
    
    # 1. Carregar dados
    print("\n📂 Carregando dados...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    print(f"   ✓ {len(dados)} empresas carregadas")
    
    # 2. Filtrar empresas sem CNPJ
    empresas_sem_cnpj = [e for e in dados if not e.get('cnpj')]
    print(f"\n📊 Empresas sem CNPJ: {len(empresas_sem_cnpj)}")
    
    # 3. Buscar CNPJ (limitado para demonstração)
    print("\n🔍 Buscando CNPJ externamente...")
    print("   ⏱️  Estimativa: ~2-3 minutos para 50 empresas")
    
    resultados_finais = buscar_cnpjs_lote(empresas_sem_cnpj, max_empresas=50)
    
    # 4. Estatísticas
    cnpjs_encontrados = sum(1 for e in resultados_finais if e.get('cnpj_encontrado'))
    ainda_sem_cnpj = sum(1 for e in resultados_finais if not e.get('cnpj_encontrado') and not e.get('nao_processado'))
    nao_processados = sum(1 for e in resultados_finais if e.get('nao_processado'))
    
    print(f"\n" + "=" * 70)
    print("📊 RESULTADO")
    print("=" * 70)
    print(f"\n📊 Empresas processadas: {len(resultados_finais) - nao_processados}")
    print(f"✅ CNPJs encontrados: {cnpjs_encontrados}")
    print(f"❌ Ainda sem CNPJ: {ainda_sem_cnpj}")
    print(f"⏭️  Não processados (limite): {nao_processados}")
    
    # 5. Relatório
    relatorio = {
        'resumo': {
            'total_empresas': len(dados),
            'sem_cnpj_inicial': len(empresas_sem_cnpj),
            'processadas': len(resultados_finais) - nao_processados,
            'cnpjs_encontrados': cnpjs_encontrados,
            'taxa_sucesso': cnpjs_encontrados / (len(resultados_finais) - nao_processados) * 100 if (len(resultados_finais) - nao_processados) > 0 else 0
        },
        'exemplos_encontrados': [e for e in resultados_finais if e.get('cnpj_encontrado')][:10],
        'exemplos_nao_encontrados': [e for e in resultados_finais if not e.get('cnpj_encontrado') and not e.get('nao_processado')][:10]
    }
    
    # 6. Salvar
    print("\n💾 Salvando dados...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(resultados_finais, f, ensure_ascii=False, indent=2)
    print(f"   ✓ {OUTPUT_FILE}")
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    print(f"   ✓ {REPORT_FILE}")
    
    print("\n" + "=" * 70)
    print("✅ CONCLUÍDO!")
    print("=" * 70)

if __name__ == '__main__':
    main()
