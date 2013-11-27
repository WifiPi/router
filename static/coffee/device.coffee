
$ ->
    $(".music_activator").click ->
        mac = $(this).parent().parent().attr('id').replace('menu-', '').replace(new RegExp('-','gm'), ':')

    $(".block").click ->
        mac = $(this).parent().parent().attr('id').replace('menu-', '').replace(new RegExp('-','gm'), ':')
        $.post "/api/device/block",
            'mac': mac

    $(".unlock").click ->
        mac = $(this).parent().parent().attr('id').replace('menu-', '').replace(new RegExp('-','gm'), ':')
        $.post "/api/device/unlock", 
            'mac': mac

