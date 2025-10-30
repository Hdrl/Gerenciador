import { useState, useEffect } from 'react';
import apiClient from './api/axiosConfig';
import OrdemProducaoList from './components/OrdemProducaoList';
import OrdemProducaoForm from './components/OrdemProducaoForm';
import './App.css'; // Vamos usar o App.css mesmo

function App() {
  const [ordens, setOrdens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState(null);

  // Função para buscar os dados da API
  const fetchOrdens = () => {
    setLoading(true);
    setErro(null);

    apiClient.get('/ordemservico/') // Ajuste a URL se necessário
      .then(response => {
        setOrdens(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Erro ao buscar Ordens de Produção:', error);
        setErro('Não foi possível carregar os dados.');
        setLoading(false);
      });
  };

  // useEffect para buscar os dados quando o componente carregar
  useEffect(() => {
    fetchOrdens();
  }, []); // O array vazio [] faz rodar só uma vez

  // Função que será chamada pelo Form para atualizar a lista
  const handleOpCriada = (novaOp) => {
    // Adiciona a nova OP na lista sem precisar de outra chamada de API
    // setOrdens([novaOp, ...ordens]);
    
    // Ou, mais simples, apenas recarrega tudo
    fetchOrdens();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Sistema de Gestão de PCP</h1>
      </header>
      
      <main className="container">
        {/* Componente do Formulário */}
        <OrdemProducaoForm onOpCriada={handleOpCriada} />

        <hr />

        {/* Componente da Lista */}
        {loading && <p>Carregando Ordens de Produção...</p>}
        {erro && <p className="erro-msg">{erro}</p>}
        {!loading && !erro && (
          <OrdemProducaoList 
            ordens={ordens} 
            onAtualizarLista={fetchOrdens} 
          />
        )}
      </main>
    </div>
  );
}

export default App;