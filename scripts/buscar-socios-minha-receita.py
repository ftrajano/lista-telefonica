#!/usr/bin/env python3
"""
Script para buscar dados de sócios usando Minha Receita (API open source).
Mais lenta, mas sem rate limiting.
"""

import json
import requests
from pathlib import Path
from collections import defaultdict
import time
import random

# Configurações
BASE_DIR = Path('/home/ftrajano/projetos/computacao/lista-telefonica')
INPUT_FILE = BASE_DIR / 'src/data/telefones-com-cnpj.json'
OUTPUT_FILE = BASE_DIR / 'src/data/telefones-com-socios.json'
SOCIOS_FILE = BASE_DIR / 'docs/dados-socios.json'

# API Minha Receita (repositórios GitHub espelhados)
APIS = [
    "https://minhareceita.org/{cnpj}",
    "https://receitaws.com.br/v1/cnpj/{cnpj}",
    "https://brasilapi.com.br/api/cnpj/v1/{cnpj}",
]

def formatar_cnpj(cnpj):
    """Remove caracteres não-numéricos do CNPJ."""
    return ''.join(filter(str.isdigit, str(cnpj)))

def buscar_cnpj_aleatorio(cnpj, max_tentativas=3):
    """Tenta buscar CNPJ em APIs aleatórias."""
    cnpj_formatado = formatar_cnpj(cnpj)
    
    for tentativa in range(max_tentativas):
        api_url = random.choice(APIS).format(cnpj=cnpj_formatado)
        
        try:
            response = requests.get(api_url, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limiting, esperar mais
                time.sleep(5 + random.uniform(0, 2))
                continue
            else:
                return None
        except Exception as e:
            if tentativa < max_tentativas - 1:
                time.sleep(1 + random.uniform(0, 1))
                continue
            return None
    
    return None

def extrair_socios(dados_cnpj):
    """Extrai informações dos sócios dos dados do CNPJ."""
    if not dados_cnpj:
        return []
    
    socios = []
    
    # Tentar diferentes campos de sócios dependendo da API
    campos_socios = ['qsa', 'socios', 'quadro_societario']
    
    campo_socios = None
    for campo in campos_socios:
        if campo in dados_cnpj:
            campo_socios = campo
            break
    
    if campo_socios and dados_cnpj[campo_socios]:
        for socio in dados_cnpj[campo_socios]:
            socio_info = {
                'nome': socio.get('nome_socio', socio.get('nome', socio.get('nome_razao_social', ''))),
                'qual': socio.get('qual', socio.get('qualificacao_socio', '')),
                'tipo_socio': socio.get('tipo', socio.get('tipo_socio', '')),
                'cargo': socio.get('cargo', socio.get('cargo_socio', '')),
            }
            socio_info = {k: v for k, v in socio_info.items() if v}
            if socio_info.get('nome'):
                socios.append(socio_info)
    
    return socios

def buscar_socios_empresas(empresa_data):
    """Busca sócios para uma lista de empresas."""
    resultados = []
    
    # Filtrar apenas empresas com CNPJ
    empresas_com_cnpj = [e for e in empresa_data if e.get('cnpj')]
    
    print(f"\n📊 Encontradas {len(empresas_com_cnpj)} empresas com CNPJ")
    
    for i, empresa in enumerate(empresas_com_cnpj, 1):
        cnpj = empresa['cnpj']
        nome = empresa['nome']
        
        print(f"\n[{i}/{len(empresas_com_cnpj)}] Buscando: {nome}")
        print(f"   CNPJ: {cnpj}")
        
        # Buscar dados do CNPJ
        dados_cnpj = buscar_cnpj_aleatorio(cnpj, max_tentativas=2)
        
        if dados_cnpj:
            # Extrair sócios
            socios = extrair_socios(dados_cnpj)
            
            if socios:
                print(f"   ✓ Encontrados {len(socios)} sócio(s)")
                for socio in socios[:3]:
                    print(f"     - {socio.get('nome', 'N/A')}")
            else:
                print(f"   ⚠️  Sem sócios encontrados")
            
            resultado = {
                **empresa,
                'dados_cnpj_completos': dados_cnpj,
                'socios': socios,
                'qtd_socios': len(socios),
                'tem_socios': len(socios) > 0
            }
            resultados.append(resultado)
        else:
            print(f"   ❌ CNPJ não encontrado na API")
            
            resultado = {
                **empresa,
                'dados_cnpj_completos': None,
                'socios': [],
                'qtd_socios': 0,
                'tem_socios': False,
                'erro_busca': True
            }
            resultados.append(resultado)
        
        # Rate limiting mais agressivo
        time.sleep(2 + random.uniform(0, 2))
    
    # Para empresas sem CNPJ, manter dados originais
    empresas_sem_cnpj = [e for e in empresa_data if not e.get('cnpj')]
    
    for empresa in empresas_sem_cnpj:
        resultado = {
            **empresa,
            'dados_cnpj_completos': None,
            'socios': [],
            'qtd_socios': 0,
            'tem_socios': False,
            'motivo_sem_socios': 'sem_cnpj'
        }
        resultados.append(resultado)
    
    return resultados

def extrair_rede_socios(dados_enriquecidos):
    """Extrai rede de sócios identificando nomes repetidos."""
    nome_socios = defaultdict(list)
    
    for empresa in dados_enriquecidos:
        if empresa.get('socios'):
            for socio in empresa['socios']:
                nome_socio = socio.get('nome', '')
                
                if nome_socio:
                    nome_socios[nome_socio].append(empresa['nome'])
    
    # Identificar sócios em múltiplas empresas
    investidores = {
        nome: empresas
        for nome, empresas in nome_socios.items()
        if len(empresas) > 1
    }
    
    return {
        'total_socios_unicos': len(nome_socios),
        'investidores_multiplas_empresas': len(investidores),
        'investidores': investidores
    }

def salvar_dados(dados, arquivo):
    """Salva dados enriquecidos em JSON."""
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def main():
    """Função principal."""
    print("=" * 70)
    print("BUSCA DE DADOS DE SÓCIOS (MINHA RECEITA)")
    print("=" * 70)
    
    # 1. Carregar dados
    print("\n📂 Carregando dados enriquecidos...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        empresa_data = json.load(f)
    print(f"   ✓ {len(empresa_data)} empresas carregadas")
    
    # 2. Buscar sócios
    print("\n🔍 Buscando dados de sócios...")
    print("   (Processo lento: ~5-10 segundos por CNPJ)")
    
    dados_com_socios = buscar_socios_empresas(empresa_data)
    
    # 3. Analisar rede de sócios
    print("\n🔗 Analisando rede de sócios...")
    rede_socios = extrair_rede_socios(dados_com_socios)
    
    # 4. Salvar dados completos
    print("\n💾 Salvando dados completos...")
    salvar_dados(dados_com_socios, OUTPUT_FILE)
    print(f"   ✓ {OUTPUT_FILE}")
    
    # 5. Salvar dados apenas dos sócios
    socios_extratos = []
    for empresa in dados_com_socios:
        if empresa.get('socios'):
            for socio in empresa['socios']:
                socio_info = {
                    **socio,
                    'empresa_nome': empresa['nome'],
                    'empresa_cnpj': empresa['cnpj'],
                    'empresa_bairro': empresa['bairro'],
                    'empresa_categoria': empresa['categoria']
                }
                socios_extratos.append(socio_info)
    
    salvar_dados(socios_extratos, SOCIOS_FILE)
    print(f"   ✓ {SOCIOS_FILE} ({len(socios_extratos)} sócios)")
    
    # 6. Relatório
    print("\n" + "=" * 70)
    print("📊 RELATÓRIO")
    print("=" * 70)
    
    total_empresas = len(dados_com_socios)
    com_socios = sum(1 for e in dados_com_socios if e.get('tem_socios'))
    sem_socios = total_empresas - com_socios
    
    print(f"\n📋 Total de empresas: {total_empresas}")
    print(f"✅ Com sócios encontrados: {com_socios} ({com_socios/total_empresas*100:.1f}%)")
    print(f"❌ Sem sócios: {sem_socios} ({sem_socios/total_empresas*100:.1f}%)")
    
    print(f"\n🔗 Rede de sócios:")
    print(f"   Sócios únicos: {rede_socios['total_socios_unicos']}")
    print(f"   Investidores em múltiplas empresas: {rede_socios['investidores_multiplas_empresas']}")
    
    if rede_socios['investidores']:
        print(f"\n💰 Investidores identificados:")
        for nome, empresas in list(rede_socios['investidores'].items())[:10]:
            print(f"   • {nome}: {len(empresas)} empresa(s)")
    
    print("\n" + "=" * 70)
    print("✅ CONCLUÍDO!")
    print("=" * 70)

if __name__ == '__main__':
    main()
