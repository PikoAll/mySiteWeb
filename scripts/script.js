// NAVBAR HAMBURGHER
document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.getElementById('hamburger-menu');
    const navbar = document.getElementById('navbar');
    const overlay = document.getElementById('overlay');

    console.log('Script loaded. DOM fully loaded and parsed.');

    // Gestione click sull'hamburger menu
    hamburger.addEventListener('click', () => {
        navbar.classList.toggle('active'); // Mostra/nascondi il menu
        overlay.classList.toggle('active'); // Mostra/nascondi l'overlay
        console.log('Hamburger menu clicked. Navbar active:', navbar.classList.contains('active'));
    });

    // Chiudi il menu se si clicca sull'overlay
    overlay.addEventListener('click', () => {
        navbar.classList.remove('active');
        overlay.classList.remove('active');
        console.log('Overlay clicked. Navbar and overlay deactivated.');
    });

    // Chiudi il menu quando si torna indietro
    window.addEventListener('popstate', () => {
        console.log('Popstate event detected.');
        if (navbar.classList.contains('active') || overlay.classList.contains('active')) {
            navbar.classList.remove('active');
            overlay.classList.remove('active');
            console.log('Navbar and overlay state reset due to popstate.');
        } else {
            console.log('Navbar is already closed.');
        }
    });

    // Reset navbar e overlay all'avvio della pagina (per sicurezza)
    if (navbar.classList.contains('active') || overlay.classList.contains('active')) {
        navbar.classList.remove('active');
        overlay.classList.remove('active');
        console.log('Navbar and overlay reset on page load.');
    }
});

// PULSANTE PER SALIRE SOPRA
document.addEventListener('DOMContentLoaded', () => {
    const scrollToTopButton = document.getElementById('scrollToTop');

    // Mostra o nasconde il pulsante in base allo scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            scrollToTopButton.classList.add('show');
        } else {
            scrollToTopButton.classList.remove('show');
        }
    });

    // Funzione per tornare in alto
    scrollToTopButton.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth',
        });
    });
});

// PER IL SOTTO MENU SERVIZI
document.addEventListener('DOMContentLoaded', () => {
    const dropdownToggle = document.getElementById('dropdown-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    dropdownToggle.addEventListener('click', (event) => {
        event.preventDefault(); // Impedisce il comportamento predefinito del link
        // Verifica se il menu è visibile e alterna lo stile 'display'
        if (dropdownMenu.style.display === 'block') {
            dropdownMenu.style.display = 'none';
        } else {
            dropdownMenu.style.display = 'block';
        }
        console.log('Dropdown menu toggled. Visible:', dropdownMenu.style.display === 'block');
    });

    // Chiudi il menu cliccando fuori dal dropdown
    document.addEventListener('click', (event) => {
        if (!dropdownToggle.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.style.display = 'none';
            console.log('Clicked outside dropdown. Dropdown menu closed.');
        }
    });
});