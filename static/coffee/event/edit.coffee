$ ->
    option_template = _.template("<option value='<%= title %>' <%= df %>><%= title %></option>")
    current_title = ""

    $("#markdown-edit").keyup (event) ->
        title = $("#slide-list").val() or ""
        $.post "/admin/event/slide/preview",
                "title": title,
                "content": $("#markdown-edit").val()
                () ->
                    document.getElementById('laptop').contentWindow.location.reload()
                    document.getElementById('mobile').contentWindow.location.reload()

    $("#slide-push").click () ->
        title = $("#slide-list").val() or ""
        console.log title
        $.post "/api/event/slide/push", {"title": title}, () ->

    reload_list = () ->
        $.get "/api/event/slide/list", (data) ->
            $("#slide-list").empty()
            $("#slide-list").append("<option value=''>New Title</option>")
            for i in data["list"]
                df = if i == current_title then "selected" else ""
                #alert current_title
                $("#slide-list").append(option_template({"title":i, "df": df}))
    reload_list()

    $("#slide-list").change () ->
        title = $("#slide-list").val() or ""
        $.get "/api/event/slide/load?title="+title, (data) ->
            current_title = title
            $("#markdown-edit").val(data["content"])
            $("#markdown-edit").keyup()

    #$("#slide-load").click () ->

    $("#slide-save").click () ->
        title = $("#slide-list").val()
        if not title
            title = prompt("Title")

        $.post "/api/event/slide/save",
            "title": title,
            "content": $("#markdown-edit").val(),
            () ->
                #alert "Saved!"
                current_title = title
                reload_list()


    $("#slide-delete").click () ->
        $.post "/api/event/slide/delete",
            "title": title,
            () ->
                #alert "Saved!"
