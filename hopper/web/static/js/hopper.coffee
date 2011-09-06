# jQuery functions

$ = jQuery

$.fn.HopperFocusHelper = () -> 
    # Clears and replaces the input value (hint) for the matched elements.
    # Will only replace the hint if the input is blank.
    
    original = $(@).val()
    $(@).live 'focus', (event) ->
        if $(@).val() == original 
            $(@).val('')
            $(@).removeClass('unfocused')

    $(@).live 'blur', (event) ->
        if $(@).val() == '' 
            $(@).val(original)
            $(@).addClass('unfocused')
    
