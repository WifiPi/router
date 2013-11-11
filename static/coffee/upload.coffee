$ ->
    UPLOAD_BLOCK_SIZE = 1024*512
    logged_in = false
    uploading = false

    #music_template = _.template($('#music-template').html())

    if window.File and window.FileList and window.FileReader and window.Blob and window.Worker
        handleFileSelect = (evt) ->
            evt.stopPropagation()
            evt.preventDefault()

            $("#upload_files").hide()
            $("#uploading_files").show()
            $(".container").hide()

            if not logged_in
                alert "You need to login"
                return

            if uploading
                alert "You need to wait for uploading finished"
                return
            uploading = true

            if evt.target.files
                files = evt.target.files
            else
                files = evt.dataTransfer.files

            if files.length == 0
                return

            file_index = 0
            startingByte = 0
            endingByte = 0

            uploadFile = (file) ->
                file = file
                t =  if file.type then file.type else 'n/a'
                reader = new FileReader()

                xhr_provider = () ->
                    xhr = jQuery.ajaxSettings.xhr()
                    if xhr.upload
                        xhr.upload.addEventListener('progress', updateProgress, false)
                    return xhr

                updateProgress = (evt) ->
                    console.log startingByte, file.size, evt.loaded, evt.total
                    $("#uploading_files").text("Uploading file #{file_index+1} of #{files.length} at #{(startingByte + (endingByte-startingByte)*evt.loaded/evt.total)/file.size*100}%")

                if t == "audio/mp3" or t == "audio/mpeg"
                    reader.onload = (evt) ->
                        content = evt.target.result.slice evt.target.result.indexOf("base64,")+7
                        bin = atob content
                        $("#uploading_files").text("Check file #{file_index+1} of #{files.length} existing on server?")

                        worker = new Worker "/static/js/md5.js"
                        worker.onmessage = (event) ->
                            md5 = event.data

                            $.getJSON "/api/upload_mp3_html5_slice?filehash=#{md5}", (data) ->
                                uploadFilePart = (data) ->
                                    reader.onload = (evt) ->
                                        content = evt.target.result.slice evt.target.result.indexOf("base64,")+7
                                        bin = atob content

                                        if data["result"] == "success"
                                            $("#uploading_files").text("File uploading successed!")
                                            $('#list').append("<li><strong>#{ file.name }</strong> (#{ t }) - #{ file.size } bytes</li>")

                                            $("#list li").slice(0, -10).slideUp () ->
                                                $("#list li").slice(0, -10).remove()

                                            file_index++
                                            if file_index < files.length
                                                uploadFile(files[file_index])
                                            else
                                                uploading = false
                                            return

                                        else if data["result"] == "filehash verify failed"
                                            $("#uploading_files").text("File uploading failed! Try again.")
                                            uploadFile(files[file_index])
                                            return

                                        else if data["result"] == "not found"
                                            startingByte = 0
                                            endingByte = UPLOAD_BLOCK_SIZE

                                        else if data["result"] == "uploading"
                                            startingByte = data["uploaded_size"]
                                            endingByte = if startingByte + UPLOAD_BLOCK_SIZE < file.size then startingByte + UPLOAD_BLOCK_SIZE else file.size

                                        $.ajax
                                            type: 'POST',
                                            dataType: 'json',
                                            url: '/api/upload_mp3_html5_slice',
                                            data:
                                                "filehash": md5,
                                                "name": file.name,
                                                "content": content,
                                                "start": startingByte,
                                                "size": file.size,
                                            xhr: xhr_provider,
                                            success: uploadFilePart

                                    if data["result"] == "exists"
                                        $("#uploading_files").text("File #{file_index+1} of #{files.length} exists.")
                                        file_index++
                                        if file_index < files.length
                                            uploadFile(files[file_index])
                                        else
                                            uploading = false
                                        return

                                    else if data["result"] == "not found"
                                        startingByte = 0
                                        endingByte = UPLOAD_BLOCK_SIZE

                                    else if data["result"] == "uploading"
                                        startingByte = data["uploaded_size"]
                                        endingByte = if startingByte + UPLOAD_BLOCK_SIZE < file.size then startingByte + UPLOAD_BLOCK_SIZE else file.size

                                    if file.slice
                                        blob = file.slice startingByte, endingByte
                                    else if file.webkitSlice
                                        blob = file.webkitSlice startingByte, endingByte
                                    else if file.mozSlice
                                        blob = file.mozSlice startingByte, endingByte
                                    else
                                        alert "Not support slice API"
                                    reader.readAsDataURL(blob)


                                if data["result"] == "exists"
                                    $("#uploading_files").text("File #{file_index+1} of #{files.length} exists.")

                                    $.post "/api/add_mp3_by_filehash", "filehash": md5, () ->
                                        file_index++
                                        if file_index < files.length
                                            uploadFile(files[file_index])
                                        else
                                            uploading = false
                                    return
                                else
                                    uploadFilePart(data)

                        worker.postMessage bin

                    reader.readAsDataURL(file)
                else
                    $("#list").append("<li><strong>#{ file.name }</strong> (#{ t }) - Not a MP3</li>")

            uploadFile(files[file_index])

        handleDragEnter = (evt) ->
            if logged_in
                $(".container").show()
            else
                alert "You need to login"

        handleDragLeave = (evt) -> $(".container").hide()

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

    #$("#auth_to .digital0").keyup (e) -> $("#auth_to .digital1").focus()
    #$("#auth_to .digital1").keyup (e) -> $("#auth_to .digital2").focus()
    #$("#auth_to .digital2").keyup (e) -> $("#auth_to .digital3").focus()
    #$("#auth_to .digital3").keyup (e) ->
    #    token = $("#auth_to .digital0").val()+$("#auth_to .digital1").val()+$("#auth_to .digital2").val()+$("#auth_to .digital3").val()
    #    $.get "/api/auth_token_valid?token=#{ token }", () ->
    #        window.location.reload()
    #        return

    #request_token = () ->
    #    $.get "/api/auth_token_request", (data) ->
    #        $("#auth_token .digital0").val data["token"][0]
    #        $("#auth_token .digital1").val data["token"][1]
    #        $("#auth_token .digital2").val data["token"][2]
    #        $("#auth_token .digital3").val data["token"][3]

    #        $.getJSON "/api/auth_token_waiting?token=#{ data['token'] }", (result) ->
    #            if result["result"] == "fail"
    #                request_token()
    #            else if result["result"] == "success"
    #                window.location.reload()
    #            return

    #$("#user,#password").keyup () ->
    #    user = $("#user").val()
    #    password = $("#password").val()
    #    if user and password
    #        #$("#email_verify").text("good")
    #        $.getJSON "/api/login?login="+encodeURIComponent(user), (data) ->
    #            if _.has(data, "error")
    #                $("#login").addClass "disabled"
    #            else
    #                $("#login").removeClass "disabled"
    #    else
    #        #$("#email_verify").text("bad")
    #        $("#login").addClass "disabled"

    #$("#login").click () ->
    #    user = $("#user").val()
    #    password = $("#password").val()
    #    $.post "/api/login", {"login": user, "password": password}, () ->
    #        window.location.reload()
    #        return
    #    .error () ->
    #        alert "Wrong Password!"

    #$('#logout').click () ->
    #    $.get "/logout", () ->
    #        window.location.reload()

    #$('#signup').click () ->
    #    email = $('#email').val()
    #    password1 = $('#password1').val()
    #    password2 = $('#password2').val()
    #    if password1 == password2
    #        $.post "/api/signup", {"email": email, "password": password1}, () ->
                #alert ""
    #            return

    #$('#password_create').click () ->
    #    password1 = $('#password1').val()
    #    password2 = $('#password2').val()
    #    if password1 == password2
    #        $.post "/api/create_password", {"password": password1}, () ->
                #alert ""
    #            window.location.reload()
    #            return

    #$('#email_login').click () ->
    #    email = $('#email_email').val()
    #    $.getJSON "/api/signup", {"email": email}, (data) ->
    #        if not _.has(data, "error")
    #            $.post "/api/signup_with_email", {"email": email}, () ->
                    #alert ""
    #                window.location.reload()
    #                return

    #$('#resend_verify_email').click () ->
    #    $.post "/api/resend_verify_email", {}, (data) ->
            #alert ""
    #        return

    #$('#forget_submit').click () ->
    #    email = $('#forget_email').val()
    #    $.post "/api/reset_password_email", {"email": email}, (data) ->
    #        alert "Reset Password Email Sent!"
    #        return

    #$('#files').on "change", handleFileSelect

    #$.getJSON "/api/profile", (data) ->
    #    logged_in = true
    #    $("#user_email").text data["email"]
    #    if data["email_verified"]
    #        $("#email_not_verify").hide()
    #        if not data["has_password"]
    #            $("#password_panel").show()
    #    else
    #        $("#email_not_verify").show()
    #        $("#password_panel").hide()
    #    request_token()

    #$('body').pageScroller
    #    HTML5mode: false,
    #    keyboardControl: true,
    #    antimationSpeed: 2500,
    #    deepLink: false,
    #    onChange: (e) ->
    #        return

    #$("#main").sombrero
    #    navigation: true

    arrow_hint_timer = window.setTimeout () ->
        $("#arrow_hint").fadeIn()
    , 1000

    $(document).bind 'keyup', (event) ->
        keycode = event.keyCode
        if keycode >= 37 and keycode <= 40
            $("#arrow_hint").fadeOut () ->
                window.clearInterval arrow_hint_timer
                arrow_hint_timer = window.setTimeout () ->
                    $("#arrow_hint").fadeIn()
                , 1000


    #load_shuffle = (files) ->
    #    if files
    #        params = "?files="+files.join()+"&num="+(10-$(".music").length).toString()
    #    else
    #        params = "?num="+(10-$(".music").length).toString()

    #    $.getJSON "/api/shuffle"+params, (data) ->
    #        if not _.isEmpty data["next"]
    #            $("#player_title").show()
    #            for i in data["next"]
                    #music = $(music_template(i))
    #                $("#player_list").append(music)

    #load_shuffle([])

    load_music = (hash, ele) ->
        $(".music").removeClass("playing")
        ele.addClass("playing")

        #$("#jquery_jplayer_1").jPlayer("setMedia", {mp3: "/static/cache/"+hash+".mp3"})
        #$("#jquery_jplayer_1").jPlayer("play")

        if $(".music").length <= 10
            files = _.map $(".music"), (ele) ->
                return $(ele).attr("hash")
            ele.prevAll().remove()
            load_shuffle(files)

    #$("#player_list").on "click", ".music", (e) ->
    #    load_music($(this).attr("hash"), $(this))

    $(".jp-next").click (e) ->
        $(".playing").remove()
        next_song = $(_.first($(".music")))
        if not _.isEmpty(next_song)
            load_music(next_song.attr("hash"), next_song)

    #$("#jquery_jplayer_1").jPlayer
    #    ready: () ->
            #$(this).jPlayer "setMedia"
            #    m4a: "/static/cache/51ef9cf467d75a619649f3eda9d3afb4.mp3"
            $("#jp_container_1").fadeIn()
    #    ended: () ->
    #        $(".playing").remove()
    #        next_song = $(_.first($(".music")))
    #        if not _.isEmpty(next_song)
    #            load_music(next_song.attr("hash"), next_song)
    #    error: () ->
    #        $(".playing").remove()
    #        next_song = $(_.first($(".music")))
    #        if not _.isEmpty(next_song)
    #            load_music(next_song.attr("hash"), next_song)
    #    supplied: "mp3"
        #supplied: "m4a, oga"
    #    swfPath: "/static/js/Jplayer.swf"
    #    wmode: "window"
