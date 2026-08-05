const slides = document.querySelectorAll(".slide");

let currentSlide = 0;

// Pehle sab hide karo
slides.forEach((slide, index) => {
    slide.style.display = "none";
});

// First image dikhao
slides[currentSlide].style.display = "block";

function showSlides() {

    slides[currentSlide].style.display = "none";

    currentSlide++;

    if (currentSlide >= slides.length) {
        currentSlide = 0;
    }

    slides[currentSlide].style.display = "block";
}


setInterval(showSlides, 2000);