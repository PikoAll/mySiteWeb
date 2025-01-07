document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM completamente caricato"); // Log iniziale per verifica

    const hamburger = document.getElementById('hamburger-menu');
    const navbar = document.getElementById('navbar');
    const overlay = document.getElementById('overlay');
    const scrollToTopButton = document.getElementById('scrollToTop');
    const dropdownToggle = document.getElementById('dropdown-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    // Gestione click sul pulsante hamburger
    hamburger.addEventListener('click', (event) => {
        event.stopPropagation();
        navbar.classList.toggle('active');
        overlay.classList.toggle('active');
        console.log("EVENTO: Click sul pulsante hamburger");
    
        if (navbar.classList.contains('active')) {
            history.replaceState({ menu: 'opened' }, ''); // Modifica lo stato corrente
            console.log("EVENTO: Stato aggiornato nella cronologia");
        }
    });
    
    window.addEventListener('popstate', (event) => {
        if (event.state && event.state.menu === 'opened') {
            console.log("EVENTO: popstate, chiudo menu");
            navbar.classList.remove('active');
            overlay.classList.remove('active');
        } else {
            console.log("EVENTO: popstate, navigazione normale");
        }
    });
    

    // Gestione click sull'overlay per chiudere il menu
    overlay.addEventListener('click', () => {
        navbar.classList.remove('active');
        overlay.classList.remove('active');
        console.log("EVENTO: Click sull'overlay");
    });

   
    // Gestione scroll per mostrare o nascondere il bottone "Torna su"
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            scrollToTopButton.classList.add('show');
            console.log("EVENTO: Scorrimento, bottone 'Torna su' visibile");
        } else {
            scrollToTopButton.classList.remove('show');
            console.log("EVENTO: Scorrimento, bottone 'Torna su' nascosto");
        }
    });

    // Click sul bottone "Torna su"
    scrollToTopButton.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        console.log("EVENTO: Click sul bottone 'Torna su'");
    });

    // Gestione apertura e chiusura del dropdown menu
    dropdownToggle.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation(); // Evita conflitti con altri listener
        if (dropdownMenu.style.display === 'block') {
            dropdownMenu.style.display = 'none';
            console.log("EVENTO: Click sul dropdown, chiuso");
        } else {
            dropdownMenu.style.display = 'block';
            console.log("EVENTO: Click sul dropdown, aperto");
        }
    });

    // Click al di fuori del dropdown per chiuderlo
    document.addEventListener('click', (event) => {
        if (!dropdownToggle.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.style.display = 'none';
            console.log("EVENTO: Click fuori dal dropdown, chiuso");
            // Verifica se il menu è aperto
            if (navbar.classList.contains('active') || overlay.classList.contains('active')) {
                console.log("EVENTO: Menu aperto, chiudo simulando clic sull'hamburger");

                // Simula un clic sull'hamburger
                hamburger.click();
            }
        }
    });

    // Reset navbar e overlay all'avvio
    if (navbar.classList.contains('active') || overlay.classList.contains('active')) {
        navbar.classList.remove('active');
        overlay.classList.remove('active');
        console.log("INIZIALIZZAZIONE: Reset navbar e overlay all'avvio");
    }



    /*DISPENSE FOTOPER PAGINA CREATIVE SERVICES*/
    const slide = document.querySelector('.carousel-slide');
    const images = document.querySelectorAll('.carousel-slide img');
    let currentIndex = 0;

    // Calcola la larghezza dell'immagine dinamicamente
    const updateWidth = () => images[0].clientWidth;

    // Funzione per scorrere automaticamente
    const autoScroll = () => {
        currentIndex++;
        if (currentIndex >= images.length) {
            currentIndex = 0; // Torna alla prima immagine
        }
        slide.style.transform = `translateX(${-updateWidth() * currentIndex}px)`;
    };

    // Scorrimento automatico ogni 3 secondi
    setInterval(autoScroll, 3000);

    // Aggiorna larghezza immagine su resize
    window.addEventListener('resize', () => {
        slide.style.transition = 'none'; // Disabilita transizione durante il resize
        slide.style.transform = `translateX(${-updateWidth() * currentIndex}px)`;
        setTimeout(() => {
            slide.style.transition = 'transform 0.5s ease-in-out'; // Riabilita la transizione
        });
    });

    /*FINE DISPENE FOTO PER PAGINA CREATIVE SERVICES*/
});
