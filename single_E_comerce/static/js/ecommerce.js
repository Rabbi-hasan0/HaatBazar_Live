

$(document).ready(function () {
    // console.log("ecomerece.js LOADED");
    // sidebar menu
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar ul li').forEach(li => {
        li.classList.remove('active');
    });

    document.querySelectorAll('.sidebar ul li a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
        link.parentElement.classList.add('active');
        }
    });
    // sidebar menu


    $('.more').click(function (e) {
        e.stopPropagation();
        const parentMenu = $(this).closest('.more-menu');
        $('.more-menu ul').not(parentMenu.find('ul')).slideUp('fast');
        parentMenu.find('ul').stop(true, true).slideToggle('fast');
    });
    $(document).click(function () {
        $('.more-menu ul').slideUp('fast');
    });
    $('.more-menu ul').click(function (e) {
        e.stopPropagation();
    });

    $('.dropdown-toggle').on('click', function (e) {
        const parent = $(this).closest('.dropdown');
        const menu = $(this).next('.dropdown-menu');

        if (parent.hasClass('show')) {
            parent.removeClass('show');
            menu.stop(true, true).slideUp('slow');
        } else {
            $('.dropdown').removeClass('show').find('.dropdown-menu').slideUp('slow');
            parent.addClass('show');
            menu.stop(true, true).slideDown('slow');
        }
    });

    $(document).on('click', function (e) {
        if (!$(e.target).closest('.dropdown').length) {
            $('.dropdown').removeClass('show');
            $('.dropdown-menu').slideUp('slow');
        }
    });
});

