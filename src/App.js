import React, { useState } from 'react';
import './App.css';
import { dadosTelefones, getBairros, filtrarDados, getCategoriaIcon, getCategoriaLabel, getSubcategorias } from './data/telefones';

function App() {
  const [categoriaSelecionada, setCategoriaSelecionada] = useState('saude');
  const [bairroSelecionado, setBairroSelecionado] = useState(null);
  const [subcategoriaSelecionada, setSubcategoriaSelecionada] = useState(null);

  const categorias = ['saude', 'direito', 'contabilidade', 'construcao', 'agronegocio', 'hotelaria', 'concessionarias', 'clinicas', 'industria'];
  const bairros = getBairros(categoriaSelecionada);
  const subcategorias = getSubcategorias(categoriaSelecionada);

  let dadosFiltrados = filtrarDados(categoriaSelecionada, bairroSelecionado, subcategoriaSelecionada);

  // Função para formatar telefone
  const formatarTelefone = (telefone) => {
    if (!telefone) return 'Não informado';
    return telefone;
  };

  // Função para renderizar avaliação em estrelas
  const renderizarAvaliacao = (avaliacao, total) => {
    if (!avaliacao || !total) return null;

    const estrelas = Math.round(avaliacao);
    return (
      <div className="avaliacao">
        <span className="estrelas">{'★'.repeat(estrelas)}{'☆'.repeat(5 - estrelas)}</span>
        <span className="nota">{avaliacao.toFixed(1)}</span>
        <span className="total">({total} avaliações)</span>
      </div>
    );
  };

  const handleCategoriaChange = (categoria) => {
    setCategoriaSelecionada(categoria);
    setBairroSelecionado(null);
    setSubcategoriaSelecionada(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>📞 Lista Telefônica Recife</h1>
        <p>Saúde, Direito, Finanças, Construção, Agronegócio, Hotelaria, Veículos, Clínicas e Indústria - Dados do Google Maps</p>
      </header>

      <main className="App-main">
        {/* Seleção de Categoria */}
        <div className="categoria-selector">
          <h2>Selecione uma Categoria:</h2>
          <div className="categoria-buttons">
            {categorias.map(categoria => (
              <button
                key={categoria}
                className={`categoria-btn ${categoriaSelecionada === categoria ? 'active' : ''}`}
                onClick={() => handleCategoriaChange(categoria)}
              >
                <span className="categoria-icon">{getCategoriaIcon(categoria)}</span>
                <span className="categoria-label">{getCategoriaLabel(categoria)}</span>
                <span className="categoria-count">({filtrarDados(categoria).length})</span>
              </button>
            ))}
          </div>
        </div>

        {/* Seleção de Subcategoria */}
        {subcategorias.length > 1 && (
          <div className="subcategoria-selector">
            <h2>Subcategoria:</h2>
            <button
              className={`subcategoria-btn ${!subcategoriaSelecionada ? 'active' : ''}`}
              onClick={() => setSubcategoriaSelecionada(null)}
            >
              Todas
            </button>
            {subcategorias.map(sub => (
              <button
                key={sub}
                className={`subcategoria-btn ${subcategoriaSelecionada === sub ? 'active' : ''}`}
                onClick={() => setSubcategoriaSelecionada(sub)}
              >
                {sub}
              </button>
            ))}
          </div>
        )}

        {/* Seleção de Bairro */}
        <div className="bairro-selector">
          <h2>Selecione um Bairro:</h2>
          <button
            className={`bairro-btn ${bairroSelecionado === null ? 'active' : ''}`}
            onClick={() => setBairroSelecionado(null)}
          >
            Todos os Bairros ({dadosFiltrados.length})
          </button>
          {bairros.map(bairro => (
            <button
              key={bairro}
              className={`bairro-btn ${bairroSelecionado === bairro ? 'active' : ''}`}
              onClick={() => setBairroSelecionado(bairro)}
            >
              {bairro} ({filtrarDados(categoriaSelecionada, bairro, subcategoriaSelecionada).length})
            </button>
          ))}
        </div>

        {/* Lista de Resultados */}
        <div className="resultados-container">
          <h2>
            {getCategoriaLabel(categoriaSelecionada)}
            {subcategoriaSelecionada && ` - ${subcategoriaSelecionada}`}
            {bairroSelecionado && ` - ${bairroSelecionado}`}
          </h2>
          <p className="resultados-count">Exibindo {dadosFiltrados.length} resultado(s)</p>

          {dadosFiltrados.length > 0 ? (
            <table className="resultados-table">
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Subcategoria</th>
                  <th>Bairro</th>
                  <th>Telefone</th>
                  <th>Avaliação</th>
                </tr>
              </thead>
              <tbody>
                {dadosFiltrados.map(dado => (
                  <tr key={dado.id} className="resultado-row">
                    <td className="nome-cell" data-label="Nome">
                      <strong>{dado.nome}</strong>
                      {dado.endereco && <small>{dado.endereco}</small>}
                    </td>
                    <td data-label="Subcategoria">{dado.subcategoria}</td>
                    <td data-label="Bairro">{dado.bairro}</td>
                    <td className="telefone-cell" data-label="Telefone">{formatarTelefone(dado.telefone)}</td>
                    <td data-label="Avaliação">{renderizarAvaliacao(dado.avaliacao, dado.totalAvaliacoes)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="no-results">
              <p>Nenhum resultado encontrado para os filtros selecionados.</p>
            </div>
          )}
        </div>
      </main>

      <footer className="App-footer">
        <p>📊 {dadosTelefones.length} registros • 💰 Custo: $1.92 (Google Places API)</p>
        <p>📅 Atualizado em: 01/03/2026</p>
      </footer>
    </div>
  );
}

export default App;
