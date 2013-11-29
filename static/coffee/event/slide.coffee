$ ->
    live = () ->
        setTimeout () ->
            $.ajax("/api/event/slide/push", {complete: live, success: waiting, dataType: "json"})
        , 1000

    waiting = (data) ->
        #console.log data
        $("body").load "/admin/event/slide/preview?title="+data["title"]

    live()
