$ ->
    live = () ->
        setTimeout () ->
            $.ajax("/api/event/slide/push", {complete: live, success: waiting, dataType: "json"})
        , 500

    waiting = (data) ->
        #console.log data
        $.get "/api/event/slide/load?title="+encodeURI(data["title"]), (data) ->
	        $("body").html data["content"]

    live()
