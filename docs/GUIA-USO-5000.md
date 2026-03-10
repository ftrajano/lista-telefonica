# 🔢 Guia de Uso - 5.000 Empresas/mês

## 📋 Scripts Disponíveis

| Script | Função | Custo | Tempo |
|--------|---------|-------|-------|
| `verificar-credito-google.js` | Verifica limites da API | $0 | Instantâneo |
| `buscar-telefone-5000.py` | Busca 5.000 telefones | $160 | ~1.5h |
| `buscar-socios-5000.py` | Busca sócios de 5.000 empresas | $0 | ~2h |

---

## 💰 Custos

```
Mês 1:
- Google Places (5.000 req): $160 (80% do free tier)
- OpenCNPJ (5.000 req): $0 (grátis)
Total: $160 (~R$800)

Mês 2-16:
- Mesmo custo: $160/mês
- Total em 16 meses: $2.560 (~R$12.800)
```

---

## 🚀 Como Usar

### Passo 1: Configurar API Key do Google

1. Vá em: https://console.cloud.google.com/apis/credentials
2. Criar API Key para Google Places API
3. Substituir `SUA_CHAVE_AQUI` no script

### Passo 2: Buscar Telefones (5.000 empresas)

```bash
python3 scripts/buscar-telefone-5000.py
```

**Saída:**
- `docs/empresas-5000-com-telefone.json` (5.000 empresas)
- `docs/progresso-5000.json` (progresso em tempo real)

**Estatísticas esperadas:**
- Com telefone: ~3.500 (70%)
- Sem telefone: ~1.500 (30%)

### Passo 3: Buscar Sócios (5.000 empresas)

```bash
python3 scripts/buscar-socios-5000.py
```

**Saída:**
- `docs/empresas-5000-com-socios.json` (5.000 empresas)
- `docs/socios-5000.json` (todos os sócios)
- `docs/investidores-5000.json` (investidores identificados)

**Estatísticas esperadas:**
- Com sócios: ~4.000 (80%)
- Investidores em múltiplas empresas: ~200-300

---

## 📊 Cronograma

```
Dia 1:
- Manhã: Buscar 5.000 telefones (~1.5h)
- Tarde: Buscar 5.000 sócios (~2h)
- Noite: Analisar resultados

Dia 2-30:
- Prospecção usando os 5.000 leads
- Identificar investidores (200-300)
- Contatar prospects

Mês 2:
- Repetir para mais 5.000 empresas
- Total acumulado: 10.000 leads

Mês 16:
- Total: 80.000 leads (81.687 empresas)
- Investidores: ~3.000-4.000 identificados
```

---

## 🎯 Estratégia de Priorização (Mês 1)

**Para as 5.000 empresas do Mês 1:**

### Critérios de Prioridade:
1. **Idade:** ≥ 10 anos (mais estáveis)
2. **Grupo:** Saúde > Construção > TI > Transporte > Indústria
3. **Bairro:** Boa Viagem > Derby > Casa Forte > Madalena > Outros
4. **Telefone:** Priorizar empresas com telefone do Google Maps
5. **Sócios:** Priorizar empresas com sócios (para identificar investidores)

### Classificação:
- 🔴 **Classe A (top 500):** Todos os critérios acima
- 🟡 **Classe B (1.500):** 4 de 5 critérios
- 🟢 **Classe C (3.000):** 3 de 5 critérios

---

## 📁 Estrutura de Arquivos

```
docs/
├── empresas-investimento.csv (81.687 empresas)
├── empresas-5000-com-telefone.json (5.000 empresas)
├── empresas-5000-com-socios.json (5.000 empresas com sócios)
├── socios-5000.json (todos os sócios)
├── investidores-5000.json (investidores em múltiplas empresas)
└── progresso-5000.json (progresso em tempo real)
```

---

## ⚠️ Importante

**Rate Limiting:**
- Google Places: 5 req/seg (respeite para não ser bloqueado)
- OpenCNPJ: 50 req/seg (já configurado)

**Monitore:**
- Verifique `progresso-5000.json` para acompanhar o progresso
- Se o script parar, verifique se ainda tem empresas restantes

**Backup:**
- Faça backup dos arquivos JSON após cada mês
- Guarde em local seguro (Google Drive, etc.)

---

## ✅ Pronto para Começar?

1. Configure a API Key do Google
2. Execute `buscar-telefone-5000.py`
3. Execute `buscar-socios-5000.py`
4. Analise os resultados
5. Comece a prospecção!

---

**Dúvidas?** Pergunte! 🤔
