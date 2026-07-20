// --- Sticky Header Logic ---
var sticky_menu = document.getElementById("header_sticky");

$(window).scroll(function() {
    // এখানে চেক করা হচ্ছে sticky_menu আসলে পেজে আছে কি না
    if (sticky_menu) {
        const scrollTop = $(window).scrollTop();
        if (scrollTop > 300) {
            sticky_menu.classList.add('sticky');
        } else if (scrollTop < 100) {
            sticky_menu.classList.remove('sticky');
        }
    }
});

// --- Click Outside to Close Logic ---
document.addEventListener('click', function (event) {
    const pocketBox = document.getElementById('cart-pocket-box');
    const pocketContainer = document.getElementById('pocket-container');
    const cartButtons = document.querySelectorAll('.cart-qty-box');

    // এলিমেন্টগুলো না থাকলে এই লজিক কাজ করবে না (Error Prevented)
    if (!pocketBox || !pocketContainer) return;

    const clickedOutsideCurrencyButtons = !Array.from(cartButtons).some((button) => button.contains(event.target));
    if (!pocketContainer.contains(event.target) && clickedOutsideCurrencyButtons) {
        pocketBox.style.display = 'none';
        document.body.classList.remove('item-modal-open');
    }
});

// --- Pocket/Cart Open Logic ---
function cart_open() {
    document.body.classList.remove('modal-open');

    // currency-box চেক (Error Prevented)
    const currencyBox = document.getElementById('currency-box');
    if (currencyBox) {
        currencyBox.style.display = 'none';
    }

    const pocketBox = document.getElementById('cart-pocket-box');
    const pocketContainer = document.getElementById('pocket-container');
    
    // কনসোল লগ চেক করার জন্য রাখতে পারেন
    console.log("Pocket Elements Found:", !!pocketBox, !!pocketContainer);
    
    if (!pocketBox || !pocketContainer) {
        console.warn('Cart elements (pocketBox/pocketContainer) missing on this page.');
        return;
    }

    if (pocketBox.style.display === 'block') {
        pocketBox.style.display = 'none';
        document.body.classList.remove('item-modal-open');
    } else {
        pocketBox.style.display = 'block';
        document.body.classList.add('item-modal-open');
    }
}

// --- Cart Popup Close ---
function closeCartPopup() {
    const pocketBox = document.getElementById('cart-pocket-box');
    if (pocketBox) {
        document.body.classList.remove('item-modal-open');
        pocketBox.style.display = 'none';
    }
}

// --- Message & Error Alerts Hide Logic ---
setTimeout(function() {
    const messageElement = document.querySelector(".messages");
    if (messageElement) {
        messageElement.style.display = "none";
    }
}, 3000);

const errorElements = document.querySelectorAll('.error');
errorElements.forEach((element) => {
    setTimeout(() => {
        if (element) element.style.display = 'none';
    }, 3000);
});

// --- Search Box Logic ---
function search_box() {
    const searchBox = document.getElementById('search-box');
    if (searchBox) {
        searchBox.classList.add('active');
    }
}

$(document).click(function (event) {
    if (!$(event.target).closest('#search-box').length) {
        $('#search-box').removeClass('active');
    }
});