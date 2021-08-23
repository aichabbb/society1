
$(document).ready(function () {
    "use strict";

    var window_width = $(window).width(),
        window_height = window.innerHeight,
        header_height = $(".default-header").height(),
        header_height_static = $(".site-header.static").outerHeight(),
        fitscreen = window_height - header_height;


    $(".fullscreen").css("height", window_height)
    $(".fitscreen").css("height", fitscreen);


    // -------   Active Mobile Menu-----//

    $(".menu-bar").on('click', function (e) {
        e.preventDefault();
        $("nav").toggleClass('hide');
        $("span", this).toggleClass("lnr-menu lnr-cross");
        $(".main-menu").addClass('mobile-menu');
    });

    $('select').niceSelect();
    $('.img-pop-up').magnificPopup({
        type: 'image',
        gallery: {
            enabled: true
        }
    });

    //  Counter Js

    $('.counter').counterUp({
        delay: 10,
        time: 2000
    });

    $(document).ready(function () {
        $('#mc_embed_signup').find('form').ajaxChimp();
    });

    // OWL Slider
    $("#owl-slider").owlCarousel({

        autoPlay: 3000,
        stopOnHover: true,
        navigation: true,
        paginationSpeed: 1000,
        goToFirstSpeed: 2000,
        singleItem: true,
        autoHeight: true,
        transitionStyle: "fade"

    });

    var $mas = $('.knowWrap .js-kw').masonry({
        // options
        itemSelector: '.know',
        columnWidth: 1
        //percentPosition: true
    });


    for (var i = 1; i <= $('.knowWrap .know').length; i++) {
        $('.knowWrap .know:nth-child(' + i + ')').attr('data-index', i);
    }

    $('.category__nav-class a').click(function (e) {
        e.preventDefault();

        if ($(this).hasClass('checked') && $('.category__nav-class a.checked').length == 1) {
            $(this).removeClass('checked');
            $('.know').removeClass('show').show();
            $mas.masonry();
        } else if (!$(this).hasClass('checked') && $('.category__nav-class a').hasClass('checked')) {
            $(this).addClass('checked');
            $('.know:not(.show).' + $(this).attr('data-target') + '').addClass('show').show();
            $mas.masonry();
        } else if ($(this).hasClass('checked') && $('.category__nav-class a.checked').length >= 2) {
            $(this).removeClass('checked');
            $('.know.' + $(this).attr('data-target') + '').removeClass('show').hide();
            $mas.masonry();
        } else {
            $('.know').hide();
            $('.know.' + $(this).attr('data-target') + '').addClass('show').show();
            $mas.masonry();
            $('.know:not(.' + $(this).attr('data-target') + ')').css('top', 0).css('left', 0).css('transform', '');
            $('.category__nav-class a').removeClass('checked');
            $(this).addClass('checked');
        }

    });

    // Check if element is scrolled into view
    function isScrolledIntoView(elem) {
        var docViewTop = $(window).scrollTop();
        var docViewBottom = docViewTop + $(window).height();

        var elemTop = $(elem).offset().top;
        var elemBottom = elemTop + $(elem).height();

        return ((elemBottom <= docViewBottom) && (elemTop >= docViewTop));
    }
    // If element is scrolled into view, fade it in
    $(window).scroll(function () {
        $('.scroll-animations .goRight').each(function () {
            if (isScrolledIntoView(this) === true) {
                $(this).addClass('animated fadeInLeft');
                $(this).removeClass('hide');
            }
        });

        $('.scroll-animations .goLeft').each(function () {
            if (isScrolledIntoView(this) === true) {
                $(this).addClass('animated fadeInRight');
                $(this).removeClass('hide');
            }
        });

        $('.scroll-animations .goDown').each(function () {
            if (isScrolledIntoView(this) === true) {
                $(this).addClass('animated bounceInDown');
                $(this).removeClass('hide');
            }
        });
    });

    $(".owl-carousel-clients").owlCarousel({
        items: 4,
        loop: true,
        margin: 80,
        autoplay: true,
        autoplayTimeout: 3000,
        autoWidth: true,
        autoplayHoverPause: true
    });

    $('.content').waypoint(function() {
        $(".main-navigation").toggleClass('fixed');
        $(".banner-contact").hide();
    });

});
