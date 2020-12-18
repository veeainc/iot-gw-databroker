$(document).ready(function(){
    winh=$(window).height();
    headerh=$('.navbar').outerHeight();
    footerh=$('.footer').outerHeight();
    //alert(winh+" AND "+headerh+" AND "+footerh);

    containerh=winh-(headerh+footerh);
    $('.main-container').css('min-height', containerh);

    $(window).resize(function() {   
        winh=$(window).height();
        headerh=$('.navbar').outerHeight();
        footerh=$('.footer').outerHeight();
        //alert(winh+" AND "+headerh+" AND "+footerh);
    
        containerh=winh-(headerh+footerh);
        $('.main-container').css('min-height', containerh);
    });

    $(window).resize();

});

