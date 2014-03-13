
$ ->
    $("#wifi-mode-select").change ->
        if this.value == "join"
            $("#wan-panel").hide()
            $("#lan-panel").hide()
        else
            $("#wan-panel").show()
            $("#lan-panel").show()

    $("#wifi-secure-select").change ->
        if this.value == "none"
            $(".wifi-password-panel").hide()
        else
            $(".wifi-password-panel").show()

    $("#wifi-save").click ->
        wifi_mode = $("#wifi-mode-select").val()
        ssid = $("#ssid").val()
        if $("#wifi-secure-select").val() == "wpa2"
            ssid_password = $("#ssid_password").val()
            $.post "/api/network/wifi",
                "wifi_mode": wifi_mode
                "ssid": ssid
                "ssid_password": ssid_password
                "secure": "wpa2"
        else
            $.post "/api/network/wifi",
                "wifi_mode": wifi_mode
                "ssid": ssid
                "secure": "none"

    $("#wan-connect-type").change ->
        $(".wan-pppoe-panel").hide()
        $(".wan-dhcp-panel").hide()
        $(".wan-static-panel").hide()
        if this.value == "pppoe"
            $(".wan-pppoe-panel").show()
        else if this.value == "dhcp"
            $(".wan-dhcp-panel").show()
        else
            $(".wan-static-panel").show()

    $("#wan-pppoe-save").click ->
        pppoe_username = $("#pppoe_username").val()
        pppoe_password = $("#pppoe_password").val()
        $.post "/api/network/wan",
            "wan": "pppoe"
            "pppoe_username": pppoe_username
            "pppoe_password": pppoe_password

    $("#wan-static-save").click ->
        alert "static"

    $("#wan-dhcp-save").click ->
        $.post "/api/network/wan",
            "wan": "dhcp"


    $("#lan-ip-range").change ->
        $(".ip10").hide()
        $(".mask10").hide()
        $(".ip192").hide()
        $(".mask192").hide()

        $(".ip" + this.value).show()
        $(".mask" + this.value).show()

    $("#lan-save").click ->
        if $("#lan-ip-range").val() == "192"
            $.post "/api/network/lan",
                "router_ip": "192.168."+$("#ip192-segment-2").val()+".1"
                #"router_mask": "255.255.255.0"

        else if $("#lan-ip-range").val() == "10"
            $.post "/api/network/lan",
                "router_ip": "10."+$("#ip10-segment-1").val()+".0.1"
                #"router_mask": "255.255.0.0"
