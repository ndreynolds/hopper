$ ->
    mdown = $('.markdown').html()
    mdown = mdown.replace(/^\s*/g, '')

    $('#edit-button').click ->
        $('.markdown').html($('.doc').html())
        $('.doc').html("<textarea id='edit-field'>#{mdown}</textarea>
                        <br><br>
                        <div class='button gray' id='save-button'
                            style='display:inline'>Save changes</div>
                        <div class='button red' id='cancel-button'
                            style='display:inline'>Cancel</div>
                        <br><br>")

    $('#cancel-button').live 'click', ->
        $('.doc').html($('.markdown').html())
        $('.markdown').html(mdown)

    $('#save-button').live 'click', ->
        $doc = $('.doc')
        $markdown = $('.markdown')
        edited = $('#edit-field').val()
        name = $doc.attr('name')
        converter = new Showdown.converter()
        $.ajax 
            type: 'POST'
            url: "/api/docs/#{name}/edit"
            data: 
                edited: edited
            dataType: 'json'
            success: (data) ->
                if data.success
                    $markdown.html edited
                    $doc.html converter.makeHtml edited
                else
                    alert 'An error occurred, please try again.'
                    $doc.html $markdown.html
                    $markdown.html edited
