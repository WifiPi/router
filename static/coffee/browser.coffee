$ ->
    parent_folder_template = _.template($('#parent-folder-template').html())
    folder_template = _.template($('#folder-template').html())
    file_template = _.template($('#file-template').html())

    load_folder = (folder, ele) ->
        if folder
            param = "?folder="+encodeURIComponent(folder)
        else
            param = ""

        if ele
            ele.css("background-color", "#cfc")

        $.getJSON "/api/file/list"+param, (data) ->
            $("#picker").empty()
            if ele
                ele.css("background-color", "")

            $("#current_folder").text(data["current"])

            if folder != "/" and folder != ""
                parent_folder_html = $(parent_folder_template({"path": data["parent"]}))
                $("#picker").append(parent_folder_html)

            for i in data["folders"]
                folder_html = $(folder_template({"path": folder+"/"+i, "display": i}))
                $("#picker").append(folder_html)

            if not _.isEmpty(data["files"])
                for i in data["files"]
                    file = $(file_template({"path": i, "display": i}))
                    $("#picker").append(file)
    load_folder(CURRENT_FOLDER)

    load_file = (path, rev, ele) ->

    #$("#picker").on "click", ".folder", (e) ->
    #    load_folder($(this).attr("path"), $(this))

    $("#picker").on "click", ".file", (e) ->
        console.log $(this)
        #load_file($(this).attr("path"), $(this).attr("rev"), $(this))

    #$("#reload").click () ->
    #    load_folder($(this).find("#current_folder").text(), $(this))
