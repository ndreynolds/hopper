$ ->
    $('#new-issue').tipTip {
        content: 'Submit a new issue to the tracker'
    }

    $('#search input').HopperFocusHelper()
    
    $('#flash').click ->
        $(@).hide()
