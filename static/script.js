
let currentSlide = 0;
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');
const slideInterval = 2000; // 1 second interval

function showSlide(index) {
    slides.forEach((slide, i) => {
        slide.style.display = i === index ? 'block' : 'none';
    });
    dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === index);
    });
}

function nextSlide() {
    currentSlide = (currentSlide < slides.length - 1) ? currentSlide + 1 : 0;
    showSlide(currentSlide);
}

function prevSlide() {
    currentSlide = (currentSlide > 0) ? currentSlide - 1 : slides.length - 1;
    showSlide(currentSlide);
}

document.querySelector('.prev').addEventListener('click', () => {
    prevSlide();
    resetAutoSlide();
});

document.querySelector('.next').addEventListener('click', () => {
    nextSlide();
    resetAutoSlide();
});

dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
        currentSlide = index;
        showSlide(currentSlide);
        resetAutoSlide();
    });
});

function autoSlide() {
    nextSlide();
}

let autoSlideInterval = setInterval(autoSlide, slideInterval);

function resetAutoSlide() {
    clearInterval(autoSlideInterval);
    autoSlideInterval = setInterval(autoSlide, slideInterval);
}

showSlide(currentSlide);

let slide2Index = 0;
const slides2 = document.querySelector('.slides2');
const slide2Count = document.querySelectorAll('.slide2').length;

document.querySelector('.prev2').addEventListener('click', function() {
    moveSlide(-1);
});

document.querySelector('.next2').addEventListener('click', function() {
    moveSlide(1);
});

function moveSlide(n) {
    slide2Index += n;
    if (slide2Index < 0) {
        slide2Index = slide2Count - 1;
    }
    if (slide2Index >= slide2Count) {
        slide2Index = 0;
    }
    slides2.style.transform = 'translateX(' + (-slide2Index * 33.33) + '%)';
}

function shopNow() {
    window.location.href = '/menu';  // Replace with the correct URL for your menu page
}


    // Show the popup after a delay (e.g., 3 seconds)
    setTimeout(() => {
        document.getElementById('popup').style.display = 'block';
    }, 1000);

// Close the popup when the close button is clicked
    document.getElementById('close-popup').addEventListener('click', () => {
        document.getElementById('popup').style.display = 'none';
    });

document.addEventListener("DOMContentLoaded", () => {
    const reviewForms = document.querySelectorAll(".review-form");

    reviewForms.forEach(form => {
        form.addEventListener("submit", event => {
            event.preventDefault();

            const formData = new FormData(form);
            const itemId = formData.get("item_id");

            fetch("/submit_review", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams(formData)
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    document.getElementById(`average-rating-${itemId}`).textContent = data.average_rating.toFixed(1);
                    form.reset();
                })
                .catch(error => console.error("Error:", error));
        });
    });
});