import React from 'react';
import apiClient from '../api/axiosConfig';

// 'ordens' e 'onAtualizarLista' são passados pelo App.jsx
function OrdemProducaoList({ ordens, onAtualizarLista }) {

    // Função para "Liberar" a OP (Update/PATCH)
    // No Django, isso deve chamar o método "liberar_producao"
    // Vamos supor que você criou uma "action" no ViewSet
    const handleLiberar = (id) => {
        // A melhor forma de fazer isso é com uma "action" no ViewSet
        // Ex: /api/ordens/{id}/liberar_producao/
        apiClient.post(`/ordemservico/${id}/liberar_producao/`)
            .then(response => {
                alert(`OP ${response.data.codigo_op} liberada!`);
                onAtualizarLista(); // Recarrega a lista
            })
            .catch(error => {
                console.error('Erro ao liberar OP:', error);
                alert('Erro ao liberar OP.');
            });
    };
    
    // Função para "Concluir" a OP (Update/PATCH)
    const handleConcluir = (id) => {
        // Simulando a conclusão com uma quantidade
        const qtd = prompt("Qual a quantidade produzida?");
        if (!qtd || isNaN(qtd) || parseInt(qtd) <= 0) {
            alert("Quantidade inválida.");
            return;
        }

        apiClient.post(`/ordemservico/${id}/concluir_producao/`, { quantidade_boa: parseInt(qtd) })
            .then(response => {
                alert(`OP ${response.data.codigo_op} concluída!`);
                onAtualizarLista(); // Recarrega a lista
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
                        <th>Data Emissão</th>
                        <th>Data Prevista</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {ordens.map(op => (
                        <tr key={op.id}>
                            <td>{op.codigo_op}</td>
                            <td>{op.status}</td>
                            <td>{op.produto}</td> {/* Idealmente seria op.produto.codigo */}
                            <td>{op.quantidade_planejada}</td>
                            <td>{new Date(op.data_emissao).toLocaleDateString()}</td>
                            <td>{new Date(op.data_prevista_conclusao).toLocaleDateString()}</td>
                            <td className="acoes">
                                {/* Mostra o botão certo dependendo do status */}
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
                                {/* Você pode adicionar outros botões (Iniciar, Cancelar, etc.) */}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default OrdemProducaoList;