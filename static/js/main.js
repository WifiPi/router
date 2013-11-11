var IN_WIFIPI_WIFI = false;

$(function(){
    if(IN_WIFIPI_WIFI){
        $("#wifipi_wifi").show();
    }

    $(".icon-play").click(function(){
        $.get("/api/play");
    })

    $(".icon-stop").click(function(){
        $.get("/api/stop");
    })

    $(".music-play").click(function(){
        $.get("/api/play");
    })

    $(".music-stop").click(function(){
        $.get("/api/stop");
    })
});

