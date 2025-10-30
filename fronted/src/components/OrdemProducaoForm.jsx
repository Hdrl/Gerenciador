import React, { useState, useEffect } from 'react';
import apiClient from '../api/axiosConfig';

function AtividadeForm({ onAtividadeCriada }) {
    
    const [solicitante, setSolicitante] = useState('');
    const [localExecucao, setLocalExecucao] = useState('');
    const [projeto, setProjeto] = useState('');
    const [transporte, setTransporte] = useState('');
    const [transportadoraPadrao, setTransportadoraPadrao] = useState('');
    const [tecnicoResponsavel, setTecnicoResponsavel] = useState('');

    const [locaisList, setLocaisList] = useState([]);
    const [solicitantesList, setSolicitantesList] = useState([]);
    const [projetosList, setProjetosList] = useState([]);

    const [validationErrors, setValidationErrors] = useState({});
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        apiClient.get('/locais/')
            .then(res => setLocaisList(res.data))
            .catch(err => console.error("Erro ao buscar locais:", err));

        apiClient.get('/usuarios/')
            .then(res => setSolicitantesList(res.data))
            .catch(err => console.error("Erro ao buscar solicitantes:", err));
        
        apiClient.get('/projetos/')
            .then(res => setProjetosList(res.data))
            .catch(err => console.error("Erro ao buscar projetos:", err));
    }, []);

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

        apiClient.post('/atividades/', novaAtividade)
            .then(response => {
                alert('Atividade criada com sucesso!');
                setLoading(false);
                setSolicitante('');
                setLocalExecucao('');
                setProjeto('');
                setTransporte('');
                setTransportadoraPadrao('');
                setTecnicoResponsavel('');
                setValidationErrors({});

                if (onAtividadeCriada) {
                    onAtividadeCriada(response.data);
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
            <h3>Nova Atividade</h3>
            
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
                            {item.nome}
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
                            {item.nome}
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

            <button type="submit" disabled={loading}>
                {loading ? 'Salvando...' : 'Salvar Atividade'}
            </button>
        </form>
    );
}

export default AtividadeForm;