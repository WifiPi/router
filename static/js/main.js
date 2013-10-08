var IN_LONGPLAY_WIFI = false;

$(function(){
    if(IN_LONGPLAY_WIFI){
        $("#longplay_wifi").show();
    }

    $(".icon-play").click(function(){
        $.get("/api/play");
    })

    $(".icon-stop").click(function(){
        $.get("/api/stop");
    })
});

