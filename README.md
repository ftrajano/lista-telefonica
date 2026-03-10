# 📞 Lista Telefônica por Bairro - Recife

Aplicação React para exibir telefones de médicos, advogados e contadores separados por bairro do Recife. Os dados são obtidos em tempo real do **Google Places API**.

## 🚀 Como Usar

### Iniciar o servidor de desenvolvimento:
```bash
npm start
```

A aplicação estará disponível em `http://localhost:3000`

### Atualizar os dados do Google Maps:
```bash
node scripts/fetch-google-places.js
```

⚠️ **Importante:** Cada busca completa consome cerca de $1.92 (60 requisições). O crédito gratuito é de $200/mês, então dá para rodar ~100 buscas por mês sem pagar nada!

### Build para produção:
```bash
npm run build
```

## 📊 Dados Atuais

- **Total de registros:** 922
- **Médicos:** 239
- **Hospitais:** 464
- **Advogados:** 228
- **Contadores:** 230

**Custo:** $1.92 (Google Places API)
**Última atualização:** 01/03/2026

## 📂 Estrutura do Projeto

```
lista-telefonica/
├── src/
│   ├── data/
│   │   ├── telefones.js          # Módulo com funções de filtro
│   │   ├── telefones-raw.json   # Dados brutos do Google Places
│   │   └── estatisticas.json   # Estatísticas dos dados
│   ├── App.js                   # Componente principal
│   └── App.css                  # Estilos
├── scripts/
│   └── fetch-google-places.js   # Script para buscar dados do Google
├── .env.local                 # Chave da API do Google
└── README.md
```

## 🗺️ Bairros Incluídos

O script busca dados nos seguintes bairros do Recife:

- Boa Viagem
- Graças
- Madalena
- Ibura
- Boa Vista
- Santo Antônio
- São José
- Santo Amaro
- Encruzilhada
- Aflitos
- Piedade
- Imbiribeira

## 🔧 Como Atualizar a Lista de Bairros

Edite o arquivo `scripts/fetch-google-places.js` e adicione/remova bairros no objeto `bairros`:

```javascript
const bairros = {
  'Novo Bairro': { lat: -8.1234, lng: -34.5678, radius: 2000 },
  // ...
};
```

**Dica:** Use o Google Maps para pegar as coordenadas exatas (lat/lng) de cada bairro.

## 🎯 Como Adicionar Mais Categorias

Edite o array `categorias` em `scripts/fetch-google-places.js`:

```javascript
const categorias = [
  { tipo: 'doctor', label: 'medico', subcategoria: 'Médicos' },
  { tipo: 'lawyer', label: 'advogado', subcategoria: 'Advogados' },
  { tipo: 'accounting', label: 'contador', subcategoria: 'Contadores' },
  // Adicione novas categorias aqui
  { tipo: 'dentist', label: 'dentista', subcategoria: 'Dentistas' },
];
```

**Lista completa de tipos do Google Places:** https://developers.google.com/maps/documentation/places/web-service/place-types

## ✨ Funcionalidades

- ✅ Filtrar por categoria (médicos, advogados, contadores)
- ✅ Filtrar por subcategoria (Médicos, Hospitais, etc.)
- ✅ Filtrar por bairro
- ✅ Mostrar avaliações e notas do Google
- ✅ Contagem de resultados por bairro
- ✅ Design responsivo (funciona em celular)
- ✅ Interface moderna e intuitiva
- ✅ Dados reais do Google Places API

## 🎨 Personalização

### Mudar cores:
Edite `src/App.css` e modifique os gradientes:
- Background: `background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);`
- Cards: `background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);`

### Mudar o raio de busca:
Ajuste o valor `radius` (em metros) em `scripts/fetch-google-places.js`:
```javascript
'Boa Viagem': { lat: -8.1813, lng: -34.9128, radius: 2500 }, // 2.5km
```

## 📦 Tecnologias

- React 18
- Google Places API (New v1)
- CSS3 com Flexbox e Grid
- JavaScript ES6+
- Node.js (para scripts de coleta de dados)

## 💰 Custos do Google Places API

- **Grátis:** $200 de crédito/mês
- **Custo por busca:** $0.032 por requisição
- **Busca completa (12 bairros × 5 categorias):** 60 requisições = $1.92
- **Buscas grátis por mês:** ~100 buscas completas

Ou seja: você pode atualizar os dados 2-3 vezes por dia e ainda não pagar nada!

## 🔒 Google Maps API Key

A API Key está salva em `.env.local`:

```env
REACT_APP_GOOGLE_MAPS_API_KEY=sua-chave-aqui
```

**Importante:** Nunca commite o `.env.local` no Git (já está no `.gitignore`).

## 🚨 Solução de Problemas

### Erro: "Places API (New) has not been used"
- Acesse: https://console.cloud.google.com/apis/api/places.googleapis.com/overview
- Clique em "Enable"
- Aguarde 2-5 minutos para propagar
- Rode o script novamente

### Erro: "FieldMask is a required parameter"
- O script já está configurado com o FieldMask correto
- Verifique se está usando a versão mais recente do script

### Nenhum resultado encontrado
- Tente aumentar o raio de busca (`radius`)
- Verifique se as coordenadas do bairro estão corretas
- Confirme se o tipo de estabelecimento existe no Google Places

## 🔄 Atualizações Futuras

- [ ] Busca por nome/texto
- [ ] Ordenar por avaliação
- [ ] Exportar lista para CSV/PDF
- [ ] Favoritar contatos (usando localStorage)
- [ ] Ver no Google Maps (link direto)
- [ ] Adicionar filtros avançados (só com telefone, só com avaliação, etc.)

## 📝 Fonte dos Dados

Todos os dados são obtidos do **Google Places API**, que fornece informações de estabelecimentos cadastrados no Google Maps. Os dados são atualizados periodicamente para manter a base de dados fresca.

---

**Criado por:** Lumen ✨
**Data:** 1º de março de 2026
**Versão:** 1.0.0
