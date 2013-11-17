$ ->
    parent_folder_template = _.template($('#parent-folder-template').html())
    folder_template = _.template($('#folder-template').html())
    file_template = _.template($('#file-template').html())

    load_folder = (folder, ele) ->
        if folder
            folder = "?folder="+encodeURIComponent(folder)
        else
            folder = ""

        if ele
            ele.css("background-color", "#cfc")

        $.getJSON "/api/file/list"+folder, (data) ->
            $("#picker").empty()
            if ele
                ele.css("background-color", "")

            $("#current_folder").text(data["current"])

            if data["current"] != "/"
                folder = $(parent_folder_template({"path": data["parent"]}))
                $("#picker").append(folder)

            for i in data["folders"]
                folder = $(folder_template({"path": i, "display": i}))
                $("#picker").append(folder)

            if not _.isEmpty(data["files"])
                for i in data["files"]
                    file = $(file_template({"path": i, "display": i}))
                    $("#picker").append(file)
    load_folder()

    load_file = (path, rev, ele) ->

    $("#picker").on "click", ".folder", (e) ->
        load_folder($(this).attr("path"), $(this))

    $("#picker").on "click", ".file", (e) ->
        console.log $(this)
        #load_file($(this).attr("path"), $(this).attr("rev"), $(this))

    $("#reload").click () ->
        load_folder($(this).find("#current_folder").text(), $(this))
