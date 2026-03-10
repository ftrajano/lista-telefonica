#!/usr/bin/env python3
"""
Script para buscar dados de sócios de 5.000 empresas usando OpenCNPJ.

Foco: 5.000 empresas/mês para não ultrapassar free tier.
"""

import csv
import json
import requests
from pathlib import Path
from collections import defaultdict
import time
from datetime import datetime

# Configurações
BASE_DIR = Path('/home/ftrajano/projetos/computacao/lista-telefonica')
INPUT_FILE = BASE_DIR / 'docs/empresas-5000-com-telefone.json'  # Ajustar depois da busca de telefone
OUTPUT_FILE = BASE_DIR / 'docs/empresas-5000-com-socios.json'
SOCIOS_FILE = BASE_DIR / 'docs/socios-5000.json'
INVESTIDORES_FILE = BASE_DIR / 'docs/investidores-5000.json'
PROGRESS_FILE = BASE_DIR / 'docs/progresso-5000-socios.json'

# API OpenCNPJ
API_URL = "https://api.opencnpj.org/{cnpj}"

# Headers para requisição
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def formatar_cnpj(cnpj):
    """Remove caracteres não-numéricos do CNPJ."""
    return ''.join(filter(str.isdigit, str(cnpj)))

def buscar_opencnpj(cnpj, max_tentativas=3):
    """Busca dados do CNPJ na API OpenCNPJ."""
    cnpj_formatado = formatar_cnpj(cnpj)
    url = API_URL.format(cnpj=cnpj_formatado)
    
    for tentativa in range(max_tentativas):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None  # CNPJ não encontrado
            elif response.status_code == 429:
                # Rate limit excedido, esperar
                time.sleep(2)
                continue
            else:
                return None
        except Exception as e:
            if tentativa < max_tentativas - 1:
                time.sleep(1)
                continue
            return None
    
    return None

def extrair_socios(dados_cnpj):
    """Extrai informações dos sócios dos dados do CNPJ."""
    if not dados_cnpj or 'QSA' not in dados_cnpj:
        return []
    
    socios = []
    for socio in dados_cnpj['QSA']:
        socio_info = {
            'nome': socio.get('nome_socio', ''),
            'cpf_cnpj': socio.get('cnpj_cpf_socio', ''),
            'qualificacao': socio.get('qualificacao_socio', ''),
            'data_entrada': socio.get('data_entrada_sociedade', ''),
            'tipo': socio.get('identificador_socio', '')
        }
        
        # Só adicionar se tiver nome
        if socio_info['nome']:
            socios.append(socio_info)
    
    return socios

def carregar_empresas(arquivo):
    """Carrega empresas do JSON."""
    with open(arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)

def buscar_socios_empresas(empresas):
    """Busca sócios para uma lista de empresas."""
    resultados = []
    
    print(f"\n📊 Processando {len(empresas)} empresas")
    
    # Rate limiting: 50 req/seg = 20ms entre requisições
    delay_entre_req = 0.02  # 20ms = 50 req/seg
    
    for i, empresa in enumerate(empresas, 1):
        cnpj = empresa.get('cnpj', '')
        nome = empresa.get('nome_fantasia') or empresa.get('razao_social', '')
        
        if not cnpj:
            continue
        
        # Mostrar progresso a cada 100 empresas
        if i % 100 == 0 or i == 1:
            print(f"\n[{i}/{len(empresas)}] {nome}")
            print(f"   CNPJ: {cnpj}")
        
        # Buscar dados do CNPJ
        dados_cnpj = buscar_opencnpj(cnpj)
        
        if dados_cnpj:
            # Extrair sócios
            socios = extrair_socios(dados_cnpj)
            
            if socios:
                if i % 100 == 0 or i == 1:
                    print(f"   ✓ {len(socios)} sócio(s)")
            else:
                if i % 100 == 0 or i == 1:
                    print(f"   ⚠️  Sem sócios encontrados")
            
            resultado = {
                **empresa,
                'dados_opencnpj': dados_cnpj,
                'socios': socios,
                'qtd_socios': len(socios),
                'tem_socios': len(socios) > 0
            }
            resultados.append(resultado)
        else:
            if i % 100 == 0 or i == 1:
                print(f"   ❌ CNPJ não encontrado na API")
            
            resultado = {
                **empresa,
                'dados_opencnpj': None,
                'socios': [],
                'qtd_socios': 0,
                'tem_socios': False,
                'erro_busca': True
            }
            resultados.append(resultado)
        
        # Salvar progresso a cada 500 empresas
        if i % 500 == 0:
            com_socios = sum(1 for e in resultados if e.get('tem_socios'))
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'progresso': i,
                    'total': len(empresas),
                    'com_socios': com_socios,
                    'ultima_atualizacao': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            print(f"   💾 Progresso salvo: {i}/{len(empresas)}")
        
        # Rate limiting (respeitar 50 req/seg)
        time.sleep(delay_entre_req)
    
    return resultados

def extrair_investidores(dados_enriquecidos):
    """Extrai rede de sócios identificando nomes repetidos."""
    nome_socios = defaultdict(list)
    
    for empresa in dados_enriquecidos:
        if empresa.get('socios'):
            for socio in empresa['socios']:
                nome_socio = socio.get('nome', '')
                
                if nome_socio:
                    nome_socios[nome_socio].append({
                        'empresa': empresa.get('nome_fantasia') or empresa.get('razao_social', ''),
                        'cnpj': empresa.get('cnpj', ''),
                        'grupo': empresa.get('nome_grupo', ''),
                        'atividade': empresa.get('desc_atividade', ''),
                        'telefone': empresa.get('telefone_google', '')
                    })
    
    # Identificar sócios em múltiplas empresas
    investidores = {
        nome: empresas
        for nome, empresas in nome_socios.items()
        if len(empresas) > 1
    }
    
    # Ordenar por quantidade de empresas
    investidores_ordenados = dict(
        sorted(investidores.items(), key=lambda x: len(x[1]), reverse=True)
    )
    
    return {
        'total_socios_unicos': len(nome_socios),
        'investidores_multiplas_empresas': len(investidores),
        'investidores': investidores_ordenados
    }

def salvar_dados(dados, arquivo):
    """Salva dados enriquecidos em JSON."""
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def main():
    """Função principal."""
    print("=" * 70)
    print("BUSCA DE SÓCIOS - 5.000 EMPRESAS/MÊS")
    print("=" * 70)
    
    # Verificar se arquivo de entrada existe
    if not INPUT_FILE.exists():
        print(f"\n⚠️  Arquivo não encontrado: {INPUT_FILE}")
        print(f"   Primeiro execute o script de busca de telefone!")
        print(f"   scripts/buscar-telefone-5000.py")
        return
    
    # 1. Carregar empresas
    print("\n📂 Carregando empresas...")
    empresas = carregar_empresas(INPUT_FILE)
    print(f"   ✓ {len(empresas)} empresas carregadas")
    
    # 2. Buscar sócios
    print("\n🔍 Buscando dados de sócios...")
    print("   ⏱️  Estimativa: ~2 minutos (50 req/seg)")
    
    dados_com_socios = buscar_socios_empresas(empresas)
    
    # 3. Extrair investidores
    print("\n🔗 Analisando rede de sócios...")
    rede_socios = extrair_investidores(dados_com_socios)
    
    # 4. Salvar dados completos
    print("\n💾 Salvando dados completos...")
    salvar_dados(dados_com_socios, OUTPUT_FILE)
    print(f"   ✓ {OUTPUT_FILE}")
    
    # 5. Salvar apenas os sócios
    socios_extratos = []
    for empresa in dados_com_socios:
        if empresa.get('socios'):
            for socio in empresa['socios']:
                socio_info = {
                    **socio,
                    'empresa_nome': empresa.get('nome_fantasia') or empresa.get('razao_social', ''),
                    'empresa_cnpj': empresa.get('cnpj', ''),
                    'empresa_grupo': empresa.get('nome_grupo', ''),
                    'empresa_atividade': empresa.get('desc_atividade', ''),
                    'empresa_telefone': empresa.get('telefone_google', '')
                }
                socios_extratos.append(socio_info)
    
    salvar_dados(socios_extratos, SOCIOS_FILE)
    print(f"   ✓ {SOCIOS_FILE} ({len(socios_extratos)} sócios)")
    
    # 6. Salvar investidores
    salvar_dados(rede_socios, INVESTIDORES_FILE)
    print(f"   ✓ {INVESTIDORES_FILE}")
    
    # 7. Relatório
    print("\n" + "=" * 70)
    print("📊 RELATÓRIO")
    print("=" * 70)
    
    total_empresas = len(dados_com_socios)
    com_socios = sum(1 for e in dados_com_socios if e.get('tem_socios'))
    sem_socios = total_empresas - com_socios
    
    print(f"\n📋 Total de empresas processadas: {total_empresas}")
    print(f"✅ Com sócios encontrados: {com_socios} ({com_socios/total_empresas*100:.1f}%)")
    print(f"❌ Sem sócios: {sem_socios} ({sem_socios/total_empresas*100:.1f}%)")
    
    print(f"\n🔗 Rede de sócios:")
    print(f"   Sócios únicos: {rede_socios['total_socios_unicos']}")
    print(f"   Investidores em múltiplas empresas: {rede_socios['investidores_multiplas_empresas']}")
    
    if rede_socios['investidores']:
        print(f"\n💰 TOP 20 INVESTIDORES:")
        for i, (nome, empresas) in enumerate(list(rede_socios['investidores'].items())[:20], 1):
            print(f"\n{i}. {nome}")
            print(f"   Empresas: {len(empresas)}")
            for emp in empresas[:3]:
                print(f"     - {emp['empresa']} ({emp['grupo']})")
            if len(empresas) > 3:
                print(f"     ... + {len(empresas) - 3} outras")
    
    print("\n" + "=" * 70)
    print("✅ CONCLUÍDO!")
    print("=" * 70)
    print(f"\n💾 Arquivos gerados:")
    print(f"   📄 Dados completos: {OUTPUT_FILE}")
    print(f"   👥 Sócios: {SOCIOS_FILE}")
    print(f"   💰 Investidores: {INVESTIDORES_FILE}")

if __name__ == '__main__':
    main()
