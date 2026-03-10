// Dados obtidos do Google Places API em 01/03/2026
// Fonte: https://console.cloud.google.com/

import dadosRaw from './telefones-raw.json';

// Função para obter categorias únicas
export const getCategorias = () => {
  const categorias = new Set(dadosRaw.map(d => d.categoria));
  return Array.from(categorias);
};

// Função para obter bairros únicos
export const getBairros = (categoria) => {
  const filtrados = dadosRaw.filter(d => d.categoria === categoria);
  const bairros = new Set(filtrados.map(d => d.bairro));
  return Array.from(bairros).sort();
};

// Função para obter subcategorias únicas
export const getSubcategorias = (categoria) => {
  const filtrados = dadosRaw.filter(d => d.categoria === categoria);
  const subs = new Set(filtrados.map(d => d.subcategoria));
  return Array.from(subs).sort();
};

// Função para filtrar dados
export const filtrarDados = (categoria, bairro = null, subcategoria = null) => {
  let filtrados = dadosRaw.filter(d => d.categoria === categoria);

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
    saude: "👨‍⚕️",
    direito: "⚖️",
    contabilidade: "💰",
    construcao: "🏗️",
    agronegocio: "🌾",
    hotelaria: "🏨",
    concessionarias: "🚗",
    clinicas: "🏥",
    industria: "🏭"
  };
  return icons[categoria] || "📱";
};

// Labels para exibição
export const getCategoriaLabel = (categoria) => {
  const labels = {
    saude: "Saúde — Médicos e Dentistas",
    direito: "Direito — Escritórios de Advocacia",
    contabilidade: "Contabilidade e Finanças",
    construcao: "Construção Civil e Incorporação",
    agronegocio: "Agronegócio",
    hotelaria: "Hotelaria, Turismo e Gastronomia",
    concessionarias: "Concessionárias e Revendas",
    clinicas: "Clínicas e Laboratórios",
    industria: "Indústria e Distribuição",
    // Legados para compatibilidade
    medico: "Médicos",
    advogado: "Advogados",
    contador: "Contadores"
  };
  return labels[categoria] || categoria;
};

// Exportar dados brutos para uso direto se necessário
export const dadosTelefones = dadosRaw;
