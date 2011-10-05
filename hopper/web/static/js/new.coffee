$ ->
    $('input#title').HopperFocusHelper()
    $('#issue-preview-button').click ->
        converter = new Showdown.converter()
        $('#markdown').html(converter.makeHtml($('textarea').val()))
        title = $('input#title').val()
        if title == 'Issue Summary'
            title = ''
        $('span#title').html(title)
        $('#issue-preview').dialog({
            modal: true
            width: 800
            resizable: false
            position: 'top'
            open: (event, ui) ->
                $('.ui-widget-overlay').bind 'click', ->
                    $('#issue-preview').dialog('close')
        })
