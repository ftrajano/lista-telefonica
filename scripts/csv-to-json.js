#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Caminhos dos arquivos
const csvPath = path.join(__dirname, '../src/data/telefones-raw.csv');
const jsPath = path.join(__dirname, '../src/data/telefones.js');

// Lê o CSV
function parseCSV(csvText) {
  const lines = csvText.trim().split('\n');
  const headers = lines[0].split(',').map(h => h.trim());

  const dados = [];

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',');
    if (values.length !== headers.length) continue;

    const obj = {
      id: i,
      nome: values[0].trim(),
      categoria: values[1].trim().toLowerCase(),
      subcategoria: values[2].trim(),
      bairro: values[3].trim(),
      telefone: values[4].trim(),
      tipo: values[1].trim().toLowerCase() === 'medico' ? 'consultório' : 'escritório'
    };

    dados.push(obj);
  }

  return dados;
}

// Converte para o formato JavaScript
function generateJS(dados) {
  return `// Dados importados de CSV
// ${new Date().toLocaleDateString('pt-BR')}

export const dadosTelefones = ${JSON.stringify(dados, null, 2)};

// Função para obter categorias únicas
export const getCategorias = () => {
  const categorias = new Set(dadosTelefones.map(d => d.categoria));
  return Array.from(categorias);
};

// Função para obter bairros únicos
export const getBairros = (categoria) => {
  const filtrados = dadosTelefones.filter(d => d.categoria === categoria);
  const bairros = new Set(filtrados.map(d => d.bairro));
  return Array.from(bairros).sort();
};

// Função para obter subcategorias únicas
export const getSubcategorias = (categoria) => {
  const filtrados = dadosTelefones.filter(d => d.categoria === categoria);
  const subs = new Set(filtrados.map(d => d.subcategoria));
  return Array.from(subs).sort();
};

// Função para filtrar dados
export const filtrarDados = (categoria, bairro = null, subcategoria = null) => {
  let filtrados = dadosTelefones.filter(d => d.categoria === categoria);

  if (bairro) {
    filtrados = filtrados.filter(d => d.bairro === bairro);
  }

  if (subcategoria) {
    filtrados = filtrados.filter(d => d.subcategoria === subcategoria);
  }

  return filtrados;
};

// Mapa de ícones por categoria
export const getCategoriaIcon = (categoria) => {
  const icons = {
    medico: "👨‍⚕️",
    advogado: "⚖️",
    contador: "💰"
  };
  return icons[categoria] || "📱";
};

// Labels para exibição
export const getCategoriaLabel = (categoria) => {
  const labels = {
    medico: "Médicos",
    advogado: "Advogados",
    contador: "Contadores"
  };
  return labels[categoria] || categoria;
};
`;
}

// Principal
try {
  if (!fs.existsSync(csvPath)) {
    console.error('❌ Arquivo CSV não encontrado: ' + csvPath);
    console.log('ℹ️  Crie o arquivo src/data/telefones-raw.csv com seus dados');
    process.exit(1);
  }

  const csvText = fs.readFileSync(csvPath, 'utf-8');
  const dados = parseCSV(csvText);
  const jsContent = generateJS(dados);

  // Backup do arquivo original
  if (fs.existsSync(jsPath)) {
    const backupPath = jsPath + '.backup';
    fs.copyFileSync(jsPath, backupPath);
    console.log('✅ Backup criado: ' + backupPath);
  }

  // Escreve o novo arquivo
  fs.writeFileSync(jsPath, jsContent, 'utf-8');

  console.log(`✅ Sucesso! ${dados.length} registros convertidos`);
  console.log(`📄 Arquivo gerado: ${jsPath}`);
  console.log('\nRecarregue a aplicação para ver os novos dados:');

} catch (error) {
  console.error('❌ Erro:', error.message);
  process.exit(1);
}
