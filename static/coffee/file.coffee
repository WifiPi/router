$ ->
    UPLOAD_BLOCK_SIZE = 1024*1024*10
    logged_in = false
    uploading = false

    file_lists = []

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

    $("#picker").on "click", ".folder", (e) ->
        load_folder($(this).attr("path"), $(this))

    $("#picker").on "click", ".file", (e) ->
        console.log $(this)
        #load_file($(this).attr("path"), $(this).attr("rev"), $(this))

    #$("#reload").click () ->
    #    load_folder($(this).find("#current_folder").text(), $(this))


    if window.File and window.FileList and window.FileReader and window.Blob and window.Worker
        handleFileSelect = (evt) ->
            evt.stopPropagation()
            evt.preventDefault()

            $("#upload_files").hide()
            $("#uploading_files").show()
            #$("#upload").removeClass("on_drag")

            #if not logged_in
            #    alert "You need to login"
            #    return

            files = null
            if evt.target.files
                files = evt.target.files
            else
                files = evt.dataTransfer.files

            file_lists.push(files)
            file_index = 0
            startingByte = 0
            endingByte = 0

            uploadFile = (file) ->
                t =  if file.type then file.type else 'n/a'
                reader = new FileReader()
                tempfile = null
                startingByte = 0

                xhrProvider = () ->
                    xhr = jQuery.ajaxSettings.xhr()
                    if xhr.upload
                        xhr.upload.addEventListener('progress', updateProgress, false)
                    return xhr

                updateProgress = (evt) ->
                    #console.log startingByte, file.size, evt.loaded, evt.total
                    $("#uploading_files").text("Uploading file #{file_index+1} of #{files.length} at #{(startingByte + (endingByte-startingByte)*evt.loaded/evt.total)/file.size*100}%")

                uploadNextFile = () ->
                    #console.log files, file_index
                    file_index++
                    if file_index < files.length
                        uploadFile(files[file_index])
                    else
                        file_lists.shift()
                        if file_lists.length > 0
                            file_index = 0
                            files = file_lists[0]
                            uploadFile(files[file_index])

                uploadFilePart = (data) ->
                    reader.onload = (evt) ->
                        content = evt.target.result.slice evt.target.result.indexOf("base64,")+7
                        bin = atob content

                        $.ajax
                            type: 'POST',
                            dataType: 'json',
                            url: '/api/file/upload_html5_slice',
                            data:
                                "tempfile": tempfile,
                                "name": file.name,
                                "content": content,
                                "start": startingByte,
                                "size": file.size,
                            xhr: xhrProvider,
                            success: uploadFilePart

                     if data["result"] == "success"
                        $("#uploading_files").text("File uploading successed!")
                        $('#list').append("<li><strong>#{ file.name }</strong> (#{ t }) - #{ file.size } bytes</li>")

                        $("#list li").slice(0, -10).slideUp () ->
                            $("#list li").slice(0, -10).remove()

                        uploadNextFile()
                        return

                    else if data["result"] == "uploading"
                        tempfile = data["tempfile"]
                        startingByte = data["uploaded_size"]
                        endingByte = if startingByte + UPLOAD_BLOCK_SIZE < file.size then startingByte + UPLOAD_BLOCK_SIZE else file.size

                    else if data["result"] == "error"
                        uploadFile(files[file_index])
                        return

                    if file.slice
                        blob = file.slice startingByte, endingByte
                    else if file.webkitSlice
                        blob = file.webkitSlice startingByte, endingByte
                    else if file.mozSlice
                        blob = file.mozSlice startingByte, endingByte
                    else
                        alert "Not support slice API"
                    reader.readAsDataURL(blob)

                uploadFilePart({"result": "not found"})

            if file_lists.length == 1
                uploadFile(files[file_index])


        handleDragEnter = (evt) ->
            $("#upload").addClass("on_drag")

        handleDragLeave = (evt) ->
            $("#upload").removeClass("on_drag")

        handleDragOver = (evt) ->
            evt.stopPropagation()
            evt.preventDefault()

        wrapper = document.getElementById('upload')
        if wrapper
            wrapper.addEventListener('dragenter', handleDragEnter, false)
            wrapper.addEventListener('dragover', handleDragOver, false)
            wrapper.addEventListener('drop', handleFileSelect, false)
        container = document.getElementsByClassName("container")[0]
        container.addEventListener('dragleave', handleDragLeave, false)

    else
        $('section').text('Require Chrome, Firefox, Safari 6 or IE 10')
