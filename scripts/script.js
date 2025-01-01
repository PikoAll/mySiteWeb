document.addEventListener('DOMContentLoaded', () => {
    // Codice hamburger menu
    const hamburger = document.getElementById('hamburger-menu');
    const navbar = document.getElementById('navbar');
    const overlay = document.getElementById('overlay');
    // Gestione click sull'hamburger
    hamburger.addEventListener('click', () => {
        navbar.classList.toggle('active');
        overlay.classList.toggle('active');
    });

    // Chiudi il menu quando si clicca sull'overlay
    overlay.addEventListener('click', () => {
        navbar.classList.remove('active');
        overlay.classList.remove('active');
    });

    // Listener popstate per chiudere il menu quando si torna indietro
    window.addEventListener('popstate', () => {
        if (navbar.classList.contains('active') || overlay.classList.contains('active')) {
            console.log('Chiudo il menu aperto al ritorno indietro.');
            navbar.classList.remove('active');
            overlay.classList.remove('active');
        }
    });

    // Aggiungi uno stato alla cronologia quando il menu viene aperto
    hamburger.addEventListener('click', () => {
        if (!navbar.classList.contains('active')) {
            history.pushState({ menu: 'opened' }, ''); // Aggiungi stato alla cronologia
        }
    });
    // Codice scrollToTop
    const scrollToTopButton = document.getElementById('scrollToTop');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            scrollToTopButton.classList.add('show');
        } else {
            scrollToTopButton.classList.remove('show');
        }
    });
    scrollToTopButton.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Codice dropdown menu
    const dropdownToggle = document.getElementById('dropdown-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    dropdownToggle.addEventListener('click', (event) => {
        event.preventDefault();
        if (dropdownMenu.style.display === 'block') {
            dropdownMenu.style.display = 'none';
        } else {
            dropdownMenu.style.display = 'block';
        }
    });
    document.addEventListener('click', (event) => {
        if (!dropdownToggle.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.style.display = 'none';
        }
    });

    // Resetta navbar e overlay all'avvio della pagina
    if (navbar.classList.contains('active') || overlay.classList.contains('active')) {
        navbar.classList.remove('active');
        overlay.classList.remove('active');
    }
});
