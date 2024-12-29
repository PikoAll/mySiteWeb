//NAVBAR HAMBURGHER
document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.getElementById('hamburger-menu');
    const navbar = document.getElementById('navbar');
    const overlay = document.getElementById('overlay');

    hamburger.addEventListener('click', () => {
        navbar.classList.toggle('active'); // Mostra/nascondi il menu
        overlay.classList.toggle('active'); // Mostra/nascondi l'overlay
    });

    // Chiudi il menu se si clicca sull'overlay
    overlay.addEventListener('click', () => {
        navbar.classList.remove('active');
        overlay.classList.remove('active');
    });
});


//PULSANTE PER SALIRE SOPRA
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
