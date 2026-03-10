const https = require('https');

// API Key
const API_KEY = 'AIzaSyCd_JNSDNtIe2hBzsKPQrEE5fn9h1gIOWc';

// Coordenadas dos bairros do Recife (lat, lng, raio em metros)
const bairros = {
  'Boa Viagem': { lat: -8.1813, lng: -34.9128, radius: 2500 },
  'Graças': { lat: -8.0406, lng: -34.8979, radius: 1500 },
  'Madalena': { lat: -8.0494, lng: -34.9022, radius: 1500 },
  'Ibura': { lat: -8.1369, lng: -34.9458, radius: 2000 },
  'Boa Vista': { lat: -8.0489, lng: -34.8875, radius: 1500 },
  'Santo Antônio': { lat: -8.0614, lng: -34.8711, radius: 1500 },
  'São José': { lat: -8.0661, lng: -34.8822, radius: 1200 },
  'Santo Amaro': { lat: -8.0542, lng: -34.9139, radius: 1500 },
  'Encruzilhada': { lat: -8.0344, lng: -34.9219, radius: 1500 },
  'Aflitos': { lat: -8.0369, lng: -34.9094, radius: 1200 },
  'Piedade': { lat: -8.1833, lng: -34.9086, radius: 2000 },
  'Imbiribeira': { lat: -8.1597, lng: -34.9239, radius: 2000 },
};

// Categorias para buscar
const categorias = [
  { tipo: 'doctor', label: 'medico', subcategoria: 'Médicos' },
  { tipo: 'hospital', label: 'medico', subcategoria: 'Hospitais' },
  { tipo: 'clinic', label: 'medico', subcategoria: 'Clínicas' },
  { tipo: 'lawyer', label: 'advogado', subcategoria: 'Advogados' },
  { tipo: 'accounting', label: 'contador', subcategoria: 'Contadores' },
];

// FieldMask para pedir os campos que precisamos
const FIELD_MASK = 'places.displayName,places.nationalPhoneNumber,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.id';

// Função para fazer requisição HTTPS POST
function httpsRequest(url, data, headers = {}) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify(data);

    const options = {
      hostname: 'places.googleapis.com',
      path: url,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': API_KEY,
        'X-Goog-FieldMask': FIELD_MASK,
        'Content-Length': Buffer.byteLength(postData),
        ...headers
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

// Função para extrair o bairro do endereço
function extrairBairro(address) {
  if (!address) return null;

  // Lista de bairros para buscar no endereço
  const bairrosList = Object.keys(bairros);

  // Tenta encontrar o bairro no endereço
  for (const bairro of bairrosList) {
    if (address.includes(bairro)) {
      return bairro;
    }
  }

  return null;
}

// Função para buscar places com a nova API v1
async function buscarPlaces(tipo, lat, lng, radius, bairroNome) {
  const url = '/v1/places:searchNearby';

  const requestData = {
    includedTypes: [tipo],
    maxResultCount: 20,
    locationRestriction: {
      circle: {
        center: {
          latitude: lat,
          longitude: lng
        },
        radius: radius
      }
    },
    rankPreference: 'DISTANCE',
    languageCode: 'pt-BR',
    regionCode: 'BR'
  };

  try {
    const data = await httpsRequest(url, requestData);

    if (data.error) {
      console.error(`    ❌ Erro na API: ${data.error.message || JSON.stringify(data.error)}`);
      return [];
    }

    return data.places || [];
  } catch (error) {
    console.error(`    ❌ Erro ao buscar ${tipo}:`, error.message);
    return [];
  }
}

// Função principal
async function main() {
  console.log('🔍 Buscando dados do Google Places API (New)...\n');

  const todosDados = [];
  let totalRequests = 0;

  for (const { tipo, label, subcategoria } of categorias) {
    console.log(`📋 Buscando: ${subcategoria} (${tipo})`);

    for (const [bairroNome, coords] of Object.entries(bairros)) {
      process.stdout.write(`  📍 ${bairroNome}... `);

      const places = await buscarPlaces(tipo, coords.lat, coords.lng, coords.radius, bairroNome);
      totalRequests++;

      console.log(`encontrados: ${places.length}`);

      for (const place of places) {
        const bairroEncontrado = extrairBairro(place.formattedAddress) || bairroNome;

        const dado = {
          id: todosDados.length + 1,
          nome: place.displayName?.text || place.name || 'Sem nome',
          categoria: label,
          subcategoria: subcategoria,
          bairro: bairroEncontrado,
          telefone: place.nationalPhoneNumber || null,
          endereco: place.formattedAddress || 'Sem endereço',
          latitude: place.location?.latitude,
          longitude: place.location?.longitude,
          avaliacao: place.rating || null,
          totalAvaliacoes: place.userRatingCount || null,
          googlePlaceId: place.id || null,
        };

        todosDados.push(dado);
      }

      // Aguarda um pouco para não exceder o rate limit
      await new Promise(resolve => setTimeout(resolve, 200));
    }

    const encontrados = todosDados.filter(d => d.categoria === label).length;
    console.log(`  ✅ Total ${subcategoria}: ${encontrados}\n`);
  }

  console.log(`📊 Total de requisições: ${totalRequests}`);
  console.log(`📊 Total de registros encontrados: ${todosDados.length}`);
  console.log(`💰 Custo estimado: $${(totalRequests * 0.032).toFixed(2)}`);
  console.log(`💰 Crédito gratuito: $200.00\n`);

  // Salva os dados
  const fs = require('fs');
  const path = require('path');

  const dadosJSON = JSON.stringify(todosDados, null, 2);
  const outputPath = path.join(__dirname, '../src/data/telefones-raw.json');

  fs.writeFileSync(outputPath, dadosJSON, 'utf-8');
  console.log(`✅ Dados salvos em: ${outputPath}`);

  // Cria arquivo com estatísticas
  const stats = {
    totalPorCategoria: {},
    totalPorBairro: {},
    totalPorSubcategoria: {},
    dataGeracao: new Date().toISOString(),
  };

  for (const dado of todosDados) {
    // Por categoria
    if (!stats.totalPorCategoria[dado.categoria]) {
      stats.totalPorCategoria[dado.categoria] = 0;
    }
    stats.totalPorCategoria[dado.categoria]++;

    // Por subcategoria
    if (!stats.totalPorSubcategoria[dado.subcategoria]) {
      stats.totalPorSubcategoria[dado.subcategoria] = 0;
    }
    stats.totalPorSubcategoria[dado.subcategoria]++;

    // Por bairro
    if (!stats.totalPorBairro[dado.bairro]) {
      stats.totalPorBairro[dado.bairro] = 0;
    }
    stats.totalPorBairro[dado.bairro]++;
  }

  const statsPath = path.join(__dirname, '../src/data/estatisticas.json');
  fs.writeFileSync(statsPath, JSON.stringify(stats, null, 2), 'utf-8');
  console.log(`✅ Estatísticas salvas em: ${statsPath}\n`);

  console.log('🎉 Concluído com sucesso!');
}

main().catch(console.error);
