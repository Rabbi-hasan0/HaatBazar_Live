
// For Hero Banner
var swiper = new Swiper(".banner-swiper", {
    spaceBetween: 30,
    centeredSlides: true,
    autoplay: {
        delay: 2500,
        disableOnInteraction: false,
    },
    pagination: {
        el: ".banner-swiper .swiper-pagination",
        clickable: true,
    },
    navigation: {
        nextEl: ".banner-swiper .swiper-button-next",
        prevEl: ".banner-swiper .swiper-button-prev",
    },
});


// Accents
var swiper = new Swiper(".accents-swiper", {
    slidesPerView: 5,
    spaceBetween: 30,
    freeMode: true,
    autoplay:{
        delay: 3200,
        disableOnInteraction: false,
    },
    breakpoints: {
        320: {
            spaceBetween: 20,
            slidesPerView: 1
        },
        576: {
            spaceBetween: 20,
            slidesPerView: 3
        },
        992: {
            spaceBetween: 30,
            slidesPerView: 4
        },
        1280: {
            spaceBetween: 30,
            slidesPerView: 5
        }
    },
    navigation: {
        nextEl: '.accents-swiper .swiper-button-next',
        prevEl: '.accents-swiper .swiper-button-prev'
    }
});