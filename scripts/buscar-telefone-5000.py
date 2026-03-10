#!/usr/bin/env python3
"""
Script para buscar telefone de 5.000 empresas no Google Maps.

Limitação: 5.000 empresas/mês para não ultrapassar free tier ($160 = 80%)
"""

import csv
import json
import requests
from pathlib import Path
import time
import random
from datetime import datetime

# Configurações
BASE_DIR = Path('/home/ftrajano/projetos/computacao/lista-telefonica')
INPUT_FILE = BASE_DIR / 'docs/empresas-investimento.csv'
OUTPUT_FILE = BASE_DIR / 'docs/empresas-5000-com-telefone.json'
PROGRESS_FILE = BASE_DIR / 'docs/progresso-5000.json'

# API Google Places
API_KEY = "SUA_CHAVE_AQUI"  # Você precisa configurar
NEARBY_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# Configurações de limite
MAX_EMPRESAS = 5000
CUSTO_POR_REQ = 0.032  # USD
ORCAMENTO_MENSAL = 200 * 0.8  # 80% de segurança = $160
MAX_REQS = int(ORCAMENTO_MENSAL / CUSTO_POR_REQ)  # 5.000 req

# Headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def carregar_empresas(arquivo, max_empresas=None):
    """Carrega empresas do CSV filtrado."""
    empresas = []
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            empresas.append(row)
            
            if max_empresas and len(empresas) >= max_empresas:
                break
    
    return empresas

def criar_query_google(empresa):
    """Cria query para buscar no Google Maps."""
    nome = empresa.get('nome_fantasia') or empresa.get('razao_social', '')
    endereco = empresa.get('endereco', '')
    bairro = empresa.get('nome_bairro', '')
    
    # Query: "Nome da empresa + Endereço + Recife"
    query = f"{nome} {endereco} Recife PE"
    
    return query, nome

def buscar_telefone_google(query, nome):
    """Busca telefone no Google Maps."""
    url = f"{NEARBY_SEARCH_URL}?location=-8.0476,-34.8770&radius=50000&key={API_KEY}"
    
    params = {
        'keyword': query,
        'type': 'establishment'
    }
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                primeiro_resultado = data['results'][0]
                
                return {
                    'nome_google': primeiro_resultado.get('name', ''),
                    'endereco_google': primeiro_resultado.get('vicinity', ''),
                    'telefone': primeiro_resultado.get('formatted_phone_number', ''),
                    'avaliacao': primeiro_resultado.get('rating', 0),
                    'total_avaliacoes': primeiro_resultado.get('user_ratings_total', 0),
                    'google_place_id': primeiro_resultado.get('place_id', ''),
                    'query_usada': query
                }
        return None
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None

def main():
    """Função principal."""
    print("=" * 70)
    print("BUSCA DE TELEFONE - 5.000 EMPRESAS/MÊS")
    print("=" * 70)
    
    # 1. Carregar empresas
    print(f"\n📂 Carregando empresas...")
    empresas = carregar_empresas(INPUT_FILE, max_empresas=MAX_EMPRESAS)
    print(f"   ✓ {len(empresas)} empresas carregadas")
    
    # 2. Calcular orçamento
    print(f"\n💰 Orçamento estimado:")
    print(f"   Requisições: {len(empresas)}")
    print(f"   Custo: ${len(empresas) * CUSTO_POR_REQ:.2f}")
    print(f"   Orçamento: ${ORCAMENTO_MENSAL:.2f} (80% do free tier)")
    print(f"   Seguro: {len(empresas) * CUSTO_POR_REQ <= ORCAMENTO_MENSAL}")
    
    if len(empresas) * CUSTO_POR_REQ > ORCAMENTO_MENSAL:
        print(f"\n⚠️  ATENÇÃO: Custo ultrapassa orçamento!")
        print(f"   Reduzindo para {MAX_REQS} empresas...")
        empresas = empresas[:MAX_REQS]
    
    # 3. Buscar telefones
    print(f"\n🔍 Buscando telefones...")
    
    resultados = []
    com_telefone = 0
    sem_telefone = 0
    erros = 0
    
    delay_entre_req = 0.2  # 200ms = 5 req/seg (respita rate limit)
    
    for i, empresa in enumerate(empresas, 1):
        query, nome = criar_query_google(empresa)
        
        # Mostrar progresso a cada 100
        if i % 100 == 0 or i == 1:
            print(f"\n[{i}/{len(empresas)}] Buscando: {nome}")
            print(f"   Query: {query}")
        
        # Buscar telefone
        resultado_google = buscar_telefone_google(query, nome)
        
        if resultado_google:
            if resultado_google['telefone']:
                com_telefone += 1
                print(f"   ✓ Telefone: {resultado_google['telefone']}")
            else:
                sem_telefone += 1
                print(f"   ⚠️  Sem telefone")
            
            resultado = {
                **empresa,
                'telefone_google': resultado_google['telefone'],
                'avaliacao': resultado_google['avaliacao'],
                'total_avaliacoes': resultado_google['total_avaliacoes'],
                'google_place_id': resultado_google['google_place_id'],
                'query_google': resultado_google['query_usada'],
                'tem_telefone': bool(resultado_google['telefone'])
            }
            resultados.append(resultado)
        else:
            erros += 1
            print(f"   ❌ Erro na busca")
            resultado = {
                **empresa,
                'telefone_google': '',
                'avaliacao': 0,
                'total_avaliacoes': 0,
                'google_place_id': '',
                'query_google': query,
                'tem_telefone': False,
                'erro_busca': True
            }
            resultados.append(resultado)
        
        # Salvar progresso a cada 500 empresas
        if i % 500 == 0:
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'progresso': i,
                    'total': len(empresas),
                    'com_telefone': com_telefone,
                    'sem_telefone': sem_telefone,
                    'erros': erros,
                    'ultima_atualizacao': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            print(f"   💾 Progresso salvo: {i}/{len(empresas)}")
        
        # Rate limiting
        time.sleep(delay_entre_req + random.uniform(0, 0.1))
    
    # 4. Salvar resultados
    print(f"\n💾 Salvando resultados...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"   ✓ {OUTPUT_FILE}")
    
    # 5. Relatório
    print(f"\n" + "=" * 70)
    print(f"📊 RELATÓRIO FINAL")
    print(f"=" * 70)
    
    total = len(resultados)
    
    print(f"\n📋 Total de empresas processadas: {total}")
    print(f"✅ Com telefone: {com_telefone} ({com_telefone/total*100:.1f}%)")
    print(f"❌ Sem telefone: {sem_telefone} ({sem_telefone/total*100:.1f}%)")
    print(f"❌ Erros: {erros} ({erros/total*100:.1f}%)")
    
    print(f"\n💰 Custo total:")
    custo_real = total * CUSTO_POR_REQ
    print(f"   ${custo_real:.2f}")
    print(f"   Orçamento: ${ORCAMENTO_MENSAL:.2f}")
    print(f"   Diferença: ${ORCAMENTO_MENSAL - custo_real:.2f}")
    
    print(f"\n" + "=" * 70)
    print(f"✅ CONCLUÍDO!")
    print(f"=" * 70)
    print(f"\n📝 Próximo passo:")
    print(f"   1. Verificar se API_KEY está configurada")
    print(f"   2. Executar o script")
    print(f"   3. Após 5.000 empresas, expandir para mais 5.000")

if __name__ == '__main__':
    main()
