#!/usr/bin/env python3
"""
Script para atualizar as categorias do dados para o novo sistema de 9 categorias.
"""
import json
from pathlib import Path

# Mapeamento de subcategorias antigas para novas categorias e subcategorias
MAPEAMENTO = {
    # Saúde
    "Hospitais": {"categoria": "saude", "subcategoria": "hospital particular"},
    "Médicos": {
        "categoria": "saude",
        "subcategoria": "clínica médica"  # Genérico, pode ser ajustado depois
    },
    # Direito
    "Advogados": {
        "categoria": "direito",
        "subcategoria": "escritório de advocacia"
    },
    # Contabilidade
    "Contadores": {
        "categoria": "contabilidade",
        "subcategoria": "escritório de contabilidade"
    },
}

def atualizar_dados(input_file, output_file):
    """Atualiza as categorias no arquivo JSON."""

    with open(input_file, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    atualizados = 0
    for item in dados:
        cat_antiga = item['categoria']
        sub_antiga = item['subcategoria']

        if sub_antiga in MAPEAMENTO:
            mapeamento = MAPEAMENTO[sub_antiga]
            item['categoria'] = mapeamento['categoria']
            item['subcategoria'] = mapeamento['subcategoria']
            atualizados += 1
            print(f"Atualizado: {item['nome']}")
            print(f"  {cat_antiga} → {mapeamento['categoria']}")
            print(f"  {sub_antiga} → {mapeamento['subcategoria']}\n")

    print(f"\n✅ Total atualizado: {atualizados} de {len(dados)} registros")

    # Backup do arquivo original
    backup_file = str(input_file).replace('.json', '.json.backup')
    Path(backup_file).write_text(
        Path(input_file).read_text(encoding='utf-8'),
        encoding='utf-8'
    )
    print(f"📦 Backup criado: {backup_file}")

    # Salvar dados atualizados
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"💾 Dados atualizados salvos em: {output_file}")

if __name__ == '__main__':
    base_path = Path('/home/ftrajano/projetos/computacao/lista-telefonica/src/data')
    input_file = base_path / 'telefones-raw.json'
    output_file = base_path / 'telefones-raw.json'

    print("🔄 Atualizando categorias...\n")
    atualizar_dados(input_file, output_file)
