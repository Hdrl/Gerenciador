import React from 'react';
import apiClient from '../api/apiClient';

// Recebe as novas funções 'onEditarClick' e 'onRemoverClick' do App.jsx
function OrdemProducaoList({ ordens, onAtualizarLista, onEditarClick, onRemoverClick }) {

    // Funções de status (Liberar, Concluir) permanecem as mesmas
    const handleLiberar = (id) => {
        apiClient.post(`/ordemservico/${id}/liberar_producao/`)
            .then(response => {
                alert(`OP ${response.data.codigo_op} liberada!`);
                onAtualizarLista(); 
            })
            .catch(error => {
                console.error('Erro ao liberar OP:', error);
                alert('Erro ao liberar OP.');
            });
    };
    
    const handleConcluir = (id) => {
        const qtd = prompt("Qual a quantidade produzida?");
        if (!qtd || isNaN(qtd) || parseInt(qtd) <= 0) {
            alert("Quantidade inválida.");
            return;
        }

        apiClient.post(`/ordemservico/${id}/concluir_producao/`, { quantidade_boa: parseInt(qtd) })
            .then(response => {
                alert(`OP ${response.data.codigo_op} concluída!`);
                onAtualizarLista();
            })
            .catch(error => {
                console.error('Erro ao concluir OP:', error);
                alert('Erro ao concluir OP.');
            });
    };


    if (ordens.length === 0) {
        return <p>Nenhuma Ordem de Produção encontrada.</p>;
    }

    return (
        <div className="table-container">
            <h3>Ordens de Produção Atuais</h3>
            <table>
                <thead>
                    <tr>
                        <th>Cód. OP</th>
                        <th>Status</th>
                        <th>Produto (ID)</th>
                        <th>Qtd. Planej.</th>
                        <th>Data Prevista</th>
                        {/* NOVA COLUNA DE AÇÕES (EDITAR/REMOVER) */}
                        <th>Ações CRUD</th>
                        {/* Coluna para ações de status */}
                        <th>Ações de Status</th>
                    </tr>
                </thead>
                <tbody>
                    {ordens.map(op => (
                        <tr key={op.id}>
                            <td>{op.codigo_op}</td>
                            <td>{op.status}</td>
                            <td>{op.produto}</td>
                            <td>{op.quantidade_planejada}</td>
                            <td>{new Date(op.data_prevista_conclusao).toLocaleDateString()}</td>
                            
                            {/* NOVOS BOTÕES DE EDITAR E REMOVER */}
                            <td className="acoes-crud">
                                <button 
                                    className="btn-editar"
                                    onClick={() => onEditarClick(op)}
                                >
                                    Editar
                                </button>
                                <button 
                                    className="btn-remover"
                                    onClick={() => onRemoverClick(op.id)}
                                >
                                    Remover
                                </button>
                            </td>

                            {/* Botões de Ação de Status (Liberar, Concluir) */}
                            <td className="acoes-status">
                                {op.status === 'PLANEJADA' && (
                                    <button 
                                        className="btn-liberar" 
                                        onClick={() => handleLiberar(op.id)}
                                    >
                                        Liberar
                                    </button>
                                )}
                                {op.status === 'EM_PRODUCAO' && (
                                    <button 
                                        className="btn-concluir"
                                        onClick={() => handleConcluir(op.id)}
                                    >
                                        Concluir
                                    </button>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default OrdemProducaoList;