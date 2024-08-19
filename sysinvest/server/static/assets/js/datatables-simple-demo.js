window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki
    const datatablesSimple = document.getElementById('dashboard');
    if ( datatablesSimple )
    {
        instance = new simpleDatatables.DataTable( datatablesSimple );
        return;
    }
});


window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki

    const datatablesSimple = document.getElementById('hosts');
    if ( datatablesSimple )
    {
        instance = new simpleDatatables.DataTable( datatablesSimple );
    }
});