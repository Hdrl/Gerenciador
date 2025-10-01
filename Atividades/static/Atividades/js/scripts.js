document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.querySelector('#sidebar-toggle');
    const sidebar = document.querySelector('#sidebar');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
        });
    }
});