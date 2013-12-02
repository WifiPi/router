$ ->
    live = () ->
        setTimeout () ->
            $.ajax("/api/event/slide/push", {complete: live, success: waiting, dataType: "json"})
        , 500

    waiting = (data) ->
        #console.log data
        $("body").load "/admin/event/slide/preview?title="+encodeURI(data["title"])

    live()
