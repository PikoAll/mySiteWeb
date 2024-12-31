document.addEventListener('DOMContentLoaded', () => {
    // Codice hamburger menu
    const hamburger = document.getElementById('hamburger-menu');
    const navbar = document.getElementById('navbar');
    const overlay = document.getElementById('overlay');
    hamburger.addEventListener('click', () => {
        navbar.classList.toggle('active');
        overlay.classList.toggle('active');
    });
    overlay.addEventListener('click', () => {
        navbar.classList.remove('active');
        overlay.classList.remove('active');
    });

    // Listener popstate
    window.addEventListener('popstate', () => {
        console.log('Navigazione indietro rilevata.');
        if (navbar.classList.contains('active') || overlay.classList.contains('active')) {
            navbar.classList.remove('active');
            overlay.classList.remove('active');
        }
        location.reload();
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
