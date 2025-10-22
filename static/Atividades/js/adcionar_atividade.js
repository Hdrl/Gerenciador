// Trava para impedir a execução dupla do script
if (window.adcionarAtividadeScriptLoaded) {
    console.warn("Script 'adcionar_atividade.js' já carregado. Interrompendo a segunda execução.");
} else {
    window.adcionarAtividadeScriptLoaded = true; 

    document.addEventListener('DOMContentLoaded', function() {
        const audioSucesso = document.getElementById('audioSucesso');
        const audioErro = document.getElementById('audioErro');

        const form = document.getElementById('form-adcionar');
        if (!form) {
            return; 
        }

        // --- INÍCIO DA MODIFICAÇÃO (LocalStorage) ---
        // 1. Cria uma chave de armazenamento única para esta página
        const storageKey = 'activitySerialItems_' + window.location.pathname;
        // --- FIM DA MODIFICAÇÃO ---

        function inicializarAudio() {
            audioSucesso.load();
            audioErro.load();
        }
        function tocarSucesso() {
            audioErro.pause();           // Para o som de erro se estiver tocando
            audioErro.currentTime = 0;   // Reinicia o áudio de erro
            audioSucesso.currentTime = 0; // Reinicia o áudio de sucesso
            audioSucesso.play();
        }
        function tocarErro() {
            audioSucesso.pause();
            audioSucesso.currentTime = 0;
            audioErro.currentTime = 0;
            audioErro.play();
        }
        document.body.addEventListener('click', inicializarAudio, { once: true });
        document.body.addEventListener('keydown', inicializarAudio, { once: true });
        // --- Pega todos os elementos necessários ---
        const verificarEmbalagemURL = form.dataset.verificarSerialUrl; // API para 'E'
        const verificarMontagemURL = form.dataset.verificarMontagemUrl; // API para 'M'
        
        const initialSerialsData = form.dataset.initialSerials; // JSON de seriais iniciais
        
        const tipoAtividadeSelect = document.getElementById('id_tipoAtividade');
        const produtoSelect = document.getElementById('id_produto');
        const serialInput = document.getElementById('id_serial');
        const tableBody = document.getElementById('serial-table-body');
        const salvar = document.getElementById('salvar');
        // --- Gerenciamento do Input Oculto ---
        const hiddenInputId = 'id_serials_list_json';
        let hiddenInput = document.getElementById(hiddenInputId);
        
        if (!hiddenInput) {
            console.log("Criando hidden input...");
            hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'serials_list_json';
            hiddenInput.id = hiddenInputId;
            form.appendChild(hiddenInput);
        }

        // --- Array principal de itens ---
        let addedItems = [];

        // --- Função Helper para adicionar linha na tabela ---
        function addSerialToTable(item) {
            document.getElementById('tabela-vazia')?.remove();
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.produtoNome}</td>
                <td>${item.serial}</td>
                <td class="text-center">
                    <button type="button" class="btn btn-danger btn-sm btn-excluir-serial" data-serial="${item.serial}">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;
            tableBody.appendChild(tr);
        }

        // --- LÓGICA DE CARREGAMENTO INICIAL (MODIFICADA PARA LocalStorage) ---
        // 2. Tenta carregar dados do localStorage
        const storedItems = localStorage.getItem(storageKey);
        let dataToParse = initialSerialsData || '[]';

        // Se o localStorage tiver dados (ex: refresh), use-o.
        // Se não, use os dados do servidor (ex: página de editar).
        if (storedItems) {
            dataToParse = storedItems;
        }

        try {
            addedItems = JSON.parse(dataToParse);
        } catch (e) {
            console.warn("Nenhum serial inicial ou JSON inválido.", e);
            addedItems = [];
        }
        // --- FIM DA MODIFICAÇÃO ---

        // Atualiza o input oculto com os valores iniciais
        hiddenInput.value = JSON.stringify(addedItems);

        // Desenha a tabela inicial se houver itens
        if (addedItems.length > 0) {
            addedItems.forEach(item => {
                addSerialToTable(item);
            });
        }
        // --- FIM DA LÓGICA DE CARREGAMENTO INICIAL ---


        // Impede 'Enter' de submeter o form
        form.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && event.target.id !== 'id_serial'){
                event.preventDefault();
            }
        });

        // --- Listener principal para adicionar seriais (com API) ---
        serialInput.addEventListener('keydown', async function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                
                const serialValue = serialInput.value.trim().toUpperCase();
                if (serialValue === '') return;

                // Pega os valores atuais dos selects
                let produtoId = produtoSelect.value;
                let produtoNome = produtoSelect.options[produtoSelect.selectedIndex].text;
                const tipoAtividadeValue = tipoAtividadeSelect.value; // 'M', 'E', 'MA'

                // Checagem de duplicado (feita antes da API)
                if (addedItems.some(item => item.serial === serialValue)) {
                    Swal.fire('Atenção', 'Este serial já foi adicionado.', 'warning');
                    tocarErro();
                    serialInput.value = '';
                    serialInput.focus();
                    return;
                }

                // --- MODIFICADO: Lógica de API dividida ---
                if (tipoAtividadeValue === 'E') { // 'E' = Embalagem
                    
                    Swal.fire({
                        title: 'Verificando Embalagem...',
                        text: `Consultando status do serial ${serialValue}`,
                        allowOutsideClick: false,
                        didOpen: () => { Swal.showLoading(); }
                    });

                    try {
                        const response = await fetch(`${verificarEmbalagemURL}?serial=${encodeURIComponent(serialValue)}`);
                        const data = await response.json();

                        if (!response.ok) {
                            throw new Error(data.message);
                        }
                        
                        Swal.close();
                        // Atualiza o nome do produto com o que a API retornou
                        produtoNome = data.produto_nome;
                        // produtoId = data.equipamento_id; // Opcional

                    } catch (error) {
                        Swal.fire('Verificação Falhou', error.message, 'error');
                        tocarErro();
                        serialInput.focus();
                        serialInput.select();
                        return; // Para a execução
                    }
                
                } else if (tipoAtividadeValue === 'M') { // 'M' = Montagem
                    
                    Swal.fire({
                        title: 'Verificando Serial...',
                        text: `Verificando disponibilidade do serial ${serialValue}`,
                        allowOutsideClick: false,
                        didOpen: () => { Swal.showLoading(); }
                    });

                    try {
                        // Chama a NOVA API de MONTAGEM
                        const response = await fetch(`${verificarMontagemURL}?serial=${encodeURIComponent(serialValue)}`);
                        const data = await response.json();

                        if (!response.ok) {
                            // API retornou erro (serial já existe)
                            throw new Error(data.message);
                        }
                        
                        // OK, serial está disponível
                        Swal.close(); 

                    } catch (error) {
                        Swal.fire('Verificação Falhou', error.message, 'error');
                        tocarErro();
                        serialInput.focus();
                        serialInput.select();
                        return; // Para a execução
                    }
                }
                // --- FIM DA LÓGICA DE API ---
                
                
                // Se for MONTAGEM ('M'), precisa ter selecionado um produto
                if (tipoAtividadeValue === 'M' && produtoId === '') {
                    Swal.fire('Atenção', 'Selecione um Produto primeiro.', 'warning');
                    tocarErro();
                    return;
                }

                // Tudo OK, adiciona o item
                const novoItem = { produtoId: produtoId, produtoNome: produtoNome, serial: serialValue };
                addedItems.push(novoItem);
                
                // Atualiza o input oculto IMEDIATAMENTE
                hiddenInput.value = JSON.stringify(addedItems);

                // --- INÍCIO DA MODIFICAÇÃO (LocalStorage) ---
                // 3. Salva no localStorage a cada adição
                localStorage.setItem(storageKey, JSON.stringify(addedItems));
                // --- FIM DA MODIFICAÇÃO ---
                
                // Desenha na tabela
                addSerialToTable(novoItem); 
                tocarSucesso();
                serialInput.value = '';
                serialInput.focus();
            }
        });


        // --- Listener para excluir seriais ---
        tableBody.addEventListener('click', function(event) {
            
            const deleteButton = event.target.closest('.btn-excluir-serial');
            if (!deleteButton) {
                return;
            }

            event.preventDefault();
            event.stopPropagation(); 

            const serialToRemove = deleteButton.dataset.serial;
            
            // Remove do array
            addedItems = addedItems.filter(item => item.serial !== serialToRemove);

            // Atualiza o input oculto IMEDIATAMENTE
            hiddenInput.value = JSON.stringify(addedItems);

            // --- INÍCIO DA MODIFICAÇÃO (LocalStorage) ---
            // 4. Salva no localStorage a cada remoção
            localStorage.setItem(storageKey, JSON.stringify(addedItems));
            // --- FIM DA MODIFICAÇÃO ---

            // Remove da tabela
            deleteButton.closest('tr').remove();

            // Adiciona a linha "vazia" se for o caso
            if (document.querySelectorAll(".btn-excluir-serial").length === 0 && !document.getElementById('tabela-vazia')) {
                const emptyRow = document.createElement('tr');
                emptyRow.id = 'tabela-vazia';
                emptyRow.innerHTML = `
                    <td colspan="3" class="text-center text-muted">Nenhum serial adicionado.</td>
                `;
                tableBody.appendChild(emptyRow);
            }
        });
        
        
        // --- Listener para salvar (submeter o form) ---
        salvar.addEventListener('click', function(event){
            event.preventDefault();
            // Opcional: garantir que o valor está atualizado (já deve estar)
            hiddenInput.value = JSON.stringify(addedItems);

            // --- INÍCIO DA MODIFICAÇÃO (LocalStorage) ---
            // 5. Limpa o localStorage ANTES de submeter
            localStorage.removeItem(storageKey);
            // --- FIM DA MODIFICAÇÃO ---

            form.submit();
        });
    });
}