
$ ->
    $("#lan-ip-range").change ->
        $(".ip10").hide()
        $(".mask10").hide()
        $(".ip192").hide()
        $(".mask192").hide()

        $(".ip" + this.value).show()
        $(".mask" + this.value).show()
        