import React, { useState, useEffect } from 'react';
import apiClient from '../api/apiClient';

// 1. Props atualizadas para suportar Edição
function AtividadeForm({ onAtividadeSalva, itemParaEditar, onCancelEdit }) {
    
    // Estados do formulário (sem alteração)
    const [solicitante, setSolicitante] = useState('');
    const [localExecucao, setLocalExecucao] = useState('');
    const [projeto, setProjeto] = useState('');
    const [transporte, setTransporte] = useState('');
    const [transportadoraPadrao, setTransportadoraPadrao] = useState('');
    const [tecnicoResponsavel, setTecnicoResponsavel] = useState('');

    // Estados dos dropdowns (sem alteração)
    const [locaisList, setLocaisList] = useState([]);
    const [solicitantesList, setSolicitantesList] = useState([]);
    const [projetosList, setProjetosList] = useState([]);

    const [validationErrors, setValidationErrors] = useState({});
    const [loading, setLoading] = useState(false);

    // 2. Define se estamos em modo de Edição
const isEditMode = !!itemParaEditar;
    // useEffect para buscar dados dos dropdowns (sem alteração)
    useEffect(() => {
        apiClient.get('/locais/')
            .then(res => setLocaisList(res.data))
            .catch(err => console.error("Erro ao buscar locais:", err));

        // Corrigido de /solicitantes/ para /usuarios/ (como no seu código)
        apiClient.get('/usuarios/') 
            .then(res => setSolicitantesList(res.data))
            .catch(err => console.error("Erro ao buscar solicitantes:", err));
        
        apiClient.get('/projetos/')
            .then(res => setProjetosList(res.data))
            .catch(err => console.error("Erro ao buscar projetos:", err));
    }, []);

    // 3. NOVO: useEffect para preencher o formulário ao editar
    useEffect(() => {
        if (isEditMode) {
            // Preenche os campos com os dados do item
            setSolicitante(itemParaEditar.solicitante || '');
            setLocalExecucao(itemParaEditar.local_execucao || '');
            setProjeto(itemParaEditar.projeto || '');
            setTransporte(itemParaEditar.transporte || '');
            setTransportadoraPadrao(itemParaEditar.transportadora_padrao || '');
            // Pega o primeiro técnico da lista (se houver)
            setTecnicoResponsavel(itemParaEditar.tecnico_responsavel[0] || ''); 
            setValidationErrors({}); // Limpa erros antigos
        } else {
            // Limpa o formulário se sairmos do modo de edição
            setSolicitante('');
            setLocalExecucao('');
            setProjeto('');
            setTransporte('');
            setTransportadoraPadrao('');
            setTecnicoResponsavel('');
            setValidationErrors({});
        }
    }, [itemParaEditar]); // Roda sempre que 'itemParaEditar' mudar

    // 4. ATUALIZADO: handleSubmit agora faz POST ou PUT
    const handleSubmit = (e) => {
        e.preventDefault();
        setLoading(true);
        setValidationErrors({});

        const novaAtividade = {
            solicitante: solicitante ? parseInt(solicitante) : null,
            local_execucao: localExecucao ? parseInt(localExecucao) : null,
            projeto: projeto ? parseInt(projeto) : null,
            transporte: transporte ? parseInt(transporte) : null,
            transportadora_padrao: transportadoraPadrao ? parseInt(transportadoraPadrao) : null,
            tecnico_responsavel: tecnicoResponsavel ? [parseInt(tecnicoResponsavel)] : [],
        };

        // Decide a requisição: PUT (Atualizar) ou POST (Criar)
        const request = isEditMode
            ? apiClient.put(`/ordemservico/${itemParaEditar.id}/`, novaAtividade)
            : apiClient.post('/ordemservico/', novaAtividade);

        request
            .then(response => {
                alert(isEditMode ? 'Atividade atualizada com sucesso!' : 'Atividade criada com sucesso!');
                setLoading(false);
                // Limpa o formulário (só se for modo de criação, pois no modo de edição o App.jsx vai limpar)
                if (!isEditMode) {
                    setSolicitante('');
                    setLocalExecucao('');
                    setProjeto('');
                    setTransporte('');
                    setTransportadoraPadrao('');
                    setTecnicoResponsavel('');
                }
                setValidationErrors({});

                // Chama a função principal do App.jsx para recarregar a lista
                if (onAtividadeSalva) {
                    onAtividadeSalva(response.data);
                }
            })
            .catch(error => {
                setLoading(false);
                if (error.response && error.response.status === 400) {
                    setValidationErrors(error.response.data);
                } else {
                    setValidationErrors({ global: 'Ocorreu um erro de rede ou servidor. Tente novamente.' });
                }
            });
    };

    return (
        <form onSubmit={handleSubmit} className="form-container">
            {/* 5. Título dinâmico */}
            <h3>{isEditMode ? `Editando Atividade #${itemParaEditar.id}` : 'Nova Atividade'}</h3>
            
            {validationErrors.global && <p className="error-text-global">{validationErrors.global}</p>}
            {validationErrors.non_field_errors && <p className="error-text-global">{validationErrors.non_field_errors[0]}</p>}

            <div>
                <label>Solicitante:</label>
                <select 
                    value={solicitante}
                    onChange={e => setSolicitante(e.target.value)}
                    className={validationErrors.solicitante ? 'input-error' : ''}
                >
                    <option value="">Selecione um solicitante...</option>
                    {solicitantesList.map(item => (
                        <option key={item.id} value={item.id}>
                            {/* 6. CORREÇÃO DE BUG: 
                                O modelo User padrão tem 'username' ou 'first_name', não '.nome'
                            */}
                            {item.username} 
                        </option>
                    ))}
                </select>
                {validationErrors.solicitante && (
                    <span className="error-text">{validationErrors.solicitante[0]}</span>
                )}
            </div>

            <div>
                <label>Local de Execução:</label>
                <select 
                    value={localExecucao}
                onChange={e => setLocalExecucao(e.target.value)}
                    className={validationErrors.local_execucao ? 'input-error' : ''}
                >
                    <option value="">Selecione um local...</option>
                    {locaisList.map(item => (
                        <option key={item.id} value={item.id}>
                            {item.apelido_endereco}
                        </option>
                    ))}
                </select>
                {validationErrors.local_execucao && (
                    <span className="error-text">{validationErrors.local_execucao[0]}</span>
                )}
            </div>

            <div>
                <label>Projeto:</label>
                <select 
                    value={projeto}
                    onChange={e => setProjeto(e.target.value)}
                    className={validationErrors.projeto ? 'input-error' : ''}
                >
                    <option value="">Selecione um projeto...</option>
                    {projetosList.map(item => (
                        <option key={item.id} value={item.id}>
                            {item.nome}
                        </option>
                    ))}
                </select>
                {validationErrors.projeto && (
                    <span className="error-text">{validationErrors.projeto[0]}</span>
                )}
            </div>

            <div>
                <label>Transporte (ID):</label>
                <input 
                    type="number"
                    value={transporte}
                    onChange={e => setTransporte(e.target.value)}
                    className={validationErrors.transporte ? 'input-error' : ''}
                />
                {validationErrors.transporte && (
                    <span className="error-text">{validationErrors.transporte[0]}</span>
                )}
            </div>

            <div>
                <label>Transportadora Padrão (ID):</label>
                <input 
                    type="number"
                    value={transportadoraPadrao}
                    onChange={e => setTransportadoraPadrao(e.target.value)}
                    className={validationErrors.transportadora_padrao ? 'input-error' : ''}
                />
                {validationErrors.transportadora_padrao && (
                    <span className="error-text">{validationErrors.transportadora_padrao[0]}</span>
                )}
            </div>

            <div>
                <label>Técnico Responsável (ID):</label>
                <input 
                    type="number"
                    value={tecnicoResponsavel}
                    onChange={e => setTecnicoResponsavel(e.target.value)}
                    className={validationErrors.tecnico_responsavel ? 'input-error' : ''}
                />
                {validationErrors.tecnico_responsavel && (
                    <span className="error-text">{validationErrors.tecnico_responsavel[0]}</span>
                )}
            </div>

            {/* 7. Botões Dinâmicos */}
            <div className="form-actions">
                <button type="submit" disabled={loading}>
                    {loading ? 'Salvando...' : (isEditMode ? 'Atualizar Atividade' : 'Salvar Atividade')}
                </button>
                
                {/* Botão de Cancelar Edição */}
                {isEditMode && (
                    <button type="button" onClick={onCancelEdit} className="btn-cancelar">
                        Cancelar Edição
                    </button>
                )}
            </div>
        </form>
    );
}

// 8. O nome do component/export foi mantido como 'AtividadeForm'
export default AtividadeForm;