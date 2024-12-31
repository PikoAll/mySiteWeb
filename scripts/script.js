// NAVBAR HAMBURGER
document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.getElementById('hamburger-menu'); // Bottone per aprire il menu
    const navbar = document.getElementById('navbar'); // Elemento che rappresenta il menu
    const overlay = document.getElementById('overlay'); // Overlay per il menu

    console.log('Script loaded. DOM fully loaded and parsed.');

    // Gestione click sull'hamburger menu
    hamburger.addEventListener('click', () => {
        // Aggiungi/rimuovi la classe 'active' per mostrare/nascondere il menu e l'overlay
        navbar.classList.toggle('active');
        overlay.classList.toggle('active');
    });

    // Chiudi il menu se si clicca sull'overlay
    overlay.addEventListener('click', () => {
        // Rimuovi la classe 'active' per nascondere il menu e l'overlay
        navbar.classList.remove('active');
        overlay.classList.remove('active');
    });

    // Chiudi il menu quando si torna indietro nel browser
    window.addEventListener('popstate', () => {
        console.log('Popstate event detected. Checking menu state.');
        // Controlla se il menu è aperto e chiudilo se necessario
        if (navbar.classList.contains('active') || overlay.classList.contains('active')) {
            navbar.classList.remove('active');
            overlay.classList.remove('active');
        } 
    });

     // Forza il refresh della pagina quando si torna indietro nel browser
     window.addEventListener('popstate', () => {
        console.log('Popstate event detected. Forcing page reload.');
        location.reload(); // Forza il refresh della pagina
    });

    // Resetta navbar e overlay all'avvio della pagina (per sicurezza)
    if (navbar.classList.contains('active') || overlay.classList.contains('active')) {
        navbar.classList.remove('active');
        overlay.classList.remove('active');
    }
});

// PULSANTE PER SALIRE SOPRA
document.addEventListener('DOMContentLoaded', () => {
    const scrollToTopButton = document.getElementById('scrollToTop'); // Bottone per tornare in cima alla pagina

    // Mostra o nasconde il pulsante in base allo scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            // Aggiunge la classe 'show' per mostrare il pulsante
            scrollToTopButton.classList.add('show');
        } else {
            // Rimuove la classe 'show' per nascondere il pulsante
            scrollToTopButton.classList.remove('show');
        }
    });

    // Funzione per tornare in alto
    scrollToTopButton.addEventListener('click', () => {
        // Scorri verso l'alto con un'animazione fluida
        window.scrollTo({
            top: 0,
            behavior: 'smooth',
        });
    });
});

// PER IL SOTTO MENU SERVIZI
document.addEventListener('DOMContentLoaded', () => {
    const dropdownToggle = document.getElementById('dropdown-toggle'); // Bottone per aprire il dropdown
    const dropdownMenu = document.querySelector('.dropdown-menu'); // Contenuto del dropdown

    // Gestione click sul bottone per mostrare/nascondere il dropdown
    dropdownToggle.addEventListener('click', (event) => {
        event.preventDefault(); // Impedisce il comportamento predefinito del link
        // Verifica se il menu è visibile e alterna lo stile 'display'
        if (dropdownMenu.style.display === 'block') {
            dropdownMenu.style.display = 'none';
        } else {
            dropdownMenu.style.display = 'block';
        }
    });

    // Chiudi il menu cliccando fuori dal dropdown
    document.addEventListener('click', (event) => {
        if (!dropdownToggle.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.style.display = 'none'; // Nasconde il dropdown
        }
    });
});
