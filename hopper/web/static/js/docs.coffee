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
        alert 'you clicked save'
