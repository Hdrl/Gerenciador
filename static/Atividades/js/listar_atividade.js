document.addEventListener('DOMContentLoaded', function() {
    const excluirButton = document.getElementById('excluir');
    const editarButton = document.getElementById('editar');
    const atividadeLinks = document.querySelectorAll('.registro');

    const editarUrlTemplate = editarButton.getAttribute('data-url-template');
    const excluirUrlTemplate = excluirButton.getAttribute('data-url-template');

    atividadeLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            // Remove a classe 'selected' de todos os links
            atividadeLinks.forEach(function(l) {
                l.classList.remove('table-primary');
            });
            // Adiciona a classe 'selected' ao link clicado
            this.classList.add('table-primary');
        });
    });

    excluirButton.addEventListener('click', function(event) {
        event.preventDefault(); // Evita o comportamento padrão do link
        selecionado = document.querySelector('.table-primary');
        if (selecionado) {
            const atividadeId = selecionado.getAttribute('data-atividade-id');
            Swal.fire({
                title: 'Excluir Atividade',
                text: 'Tem certeza que deseja excluir esta atividade?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sim, excluir',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    const excluirUrl = excluirUrlTemplate.replace('0', atividadeId);
                    window.location.href = excluirUrl;
                }
            });
            return;
        }else{
            console.log("ERROR", selecionado)
            Swal.fire({
                title: 'Excluir Atividade',
                text: 'Selecionar uma atividade primeiro',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    });

    editarButton.addEventListener('click', function(event) {
        event.preventDefault(); // Evita o comportamento padrão do link
        selecionado = document.querySelector('.table-primary');
        if (selecionado) {
            const atividadeId = selecionado.getAttribute('data-atividade-id');
            const editarUrl = editarUrlTemplate.replace('0', atividadeId);
            window.location.href = editarUrl;
            return;
        }else{
            console.log("ERROR", selecionado)
            Swal.fire({
                title: 'Editar Atividade',
                text: 'Selecionar uma atividade primeiro',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    });
}); 