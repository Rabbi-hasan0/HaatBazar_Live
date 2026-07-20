

// Sticky header
var sticky_menu = document.getElementById("sticky");
$(window).scroll(function() {
    const scrollTop = $(window).scrollTop();
    
    if (scrollTop > 300) {
        sticky_menu.classList.add('sticky');
    } else {
        sticky_menu.classList.remove('sticky');
    }

});

