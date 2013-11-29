$ ->
    $("#markdown-edit").keyup (event) ->
        $.post "/api/event/slide/preview",
                "title": "",
                "content": $("#markdown-edit").val()
                () ->
                    document.getElementById('laptop').contentWindow.location.reload()
                    document.getElementById('mobile').contentWindow.location.reload()

