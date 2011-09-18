$ ->
    keyup_start = false
    $('#issue-close').tipTip {
        content: 'Click to close this Issue'
        defaultPosition: 'top'
    }
    $('#issue-open').tipTip {
        content: 'Click to reopen this Issue'
        defaultPosition: 'top'
    }
    $('textarea').keyup ->
        if not keyup_start
            $('#preview-toggle').fadeIn()
            $('#preview-wrapper').fadeIn()
            $('#preview').css('min-height', '50px').height 'auto'
            keyup_start = true
        converter = new Showdown.converter()
        $('#preview').html(converter.makeHtml($(@).val()))

    $('#preview-toggle').click ->
        if $('#preview').css('display') == 'none'
            $('#preview').css('visibilty', 'hidden').slideUp()
        else 
            $('#preview').slideDown().css('visibility', 'visible')
