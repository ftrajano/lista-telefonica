#!/usr/bin/env python3
"""
Script para buscar dados de sócios das empresas com CNPJ.

Fontes gratuitas:
- CNPJ.ws (grátis, sem autenticação)
- Minha Receita (open source)
"""

import json
import requests
from pathlib import Path
from collections import defaultdict
import time

# Configurações
BASE_DIR = Path('/home/ftrajano/projetos/computacao/lista-telefonica')
INPUT_FILE = BASE_DIR / 'src/data/telefones-com-cnpj.json'
OUTPUT_FILE = BASE_DIR / 'src/data/telefones-com-socios.json'
SOCIOS_FILE = BASE_DIR / 'docs/dados-socios.json'

# APIs gratuitas
API_CNPJ_WS = "https://publica.cnpj.ws/cnpj/{cnpj}"

def formatar_cnpj(cnpj):
    """Remove caracteres não-numéricos do CNPJ."""
    return ''.join(filter(str.isdigit, str(cnpj)))

def buscar_cnpj_ws(cnpj):
    """Busca dados do CNPJ na API CNPJ.ws."""
    try:
        url = API_CNPJ_WS.format(cnpj=formatar_cnpj(cnpj))
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"   ⚠️  Erro {response.status_code}: {cnpj}")
            return None
    except Exception as e:
        print(f"   ❌ Erro: {e} - {cnpj}")
        return None

def extrair_socios(dados_cnpj):
    """Extrai informações dos sócios dos dados do CNPJ."""
    if not dados_cnpj or 'qsa' not in dados_cnpj:
        return []
    
    socios = []
    for socio in dados_cnpj['qsa']:
        socio_info = {
            'nome': socio.get('nome', ''),
            'qual': socio.get('qual', ''),
            'pais_origem': socio.get('pais_origem', ''),
            'nome_representante_legal': socio.get('nome_representante_legal', ''),
            'qual_representante_legal': socio.get('qual_representante_legal', '')
        }
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
        dados_cnpj = buscar_cnpj_ws(cnpj)
        
        if dados_cnpj:
            # Extrair sócios
            socios = extrair_socios(dados_cnpj)
            
            print(f"   ✓ Encontrados {len(socios)} sócio(s)")
            
            resultado = {
                **empresa,
                'dados_cnpj_completos': dados_cnpj,
                'socios': socios,
                'qtd_socios': len(socios),
                'tem_socios': len(socios) > 0
            }
            resultados.append(resultado)
        else:
            # Empresa com CNPJ mas sem dados na API
            resultado = {
                **empresa,
                'dados_cnpj_completos': None,
                'socios': [],
                'qtd_socios': 0,
                'tem_socios': False,
                'erro_busca': True
            }
            resultados.append(resultado)
        
        # Rate limiting (respeitar a API)
        time.sleep(1)
    
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
    """Extrai rede de sócios identificando CPFs repetidos."""
    cpf_socios = defaultdict(list)
    
    for empresa in dados_enriquecidos:
        if empresa.get('socios'):
            for socio in empresa['socios']:
                nome_socio = socio.get('nome', '')
                
                # Tentar extrair CPF do nome (quando incluído)
                # Nota: A API CNPJ.ws geralmente não retorna CPF completo por privacidade
                cpf_socios[nome_socio].append(empresa['nome'])
    
    # Identificar sócios em múltiplas empresas
    investidores = {
        nome: empresas
        for nome, empresas in cpf_socios.items()
        if len(empresas) > 1
    }
    
    return {
        'total_socios_unicos': len(cpf_socios),
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
    print("BUSCA DE DADOS DE SÓCIOS")
    print("=" * 70)
    
    # 1. Carregar dados
    print("\n📂 Carregando dados enriquecidos...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        empresa_data = json.load(f)
    print(f"   ✓ {len(empresa_data)} empresas carregadas")
    
    # 2. Buscar sócios
    print("\n🔍 Buscando dados de sócios...")
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
        for nome, empresas in list(rede_socios['investidores'].items())[:5]:
            print(f"   • {nome}: {len(empresas)} empresa(s)")
            for emp in empresas:
                print(f"     - {emp}")
    
    print("\n" + "=" * 70)
    print("✅ CONCLUÍDO!")
    print("=" * 70)

if __name__ == '__main__':
    main()
