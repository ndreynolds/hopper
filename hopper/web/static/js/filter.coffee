class Filter
    # Client-side issue filter representation.
    #
    # Server-side does the actual filtering, client-side
    # has to format the request.
    constructor: ->
        base = '<div class="content-bar">'
        if $('.content-bar').length
            $('.content-bar').last().after(base)
        else
            $('#content-header').after(base)

        # get the jQuery element we just inserted.
        @el = $('.content-bar').last()
        @.set()
        
        that = @
        $(@el.find('select')).live 'change', ->
            that.set that.el.find('#top option:selected').val(), that.el.find('#mid option:selected').val()

    destroy: ->
        @el.remove()

    set: (option=null, child_option=null) ->
        options = ("<option>#{field}</option>" for field, subs of @types).join('')
        select = "<select id='top'>#{options}</select>"

        if not option
            option = (field for field, subs of @types)[0]

        child_options = ("<option>#{field}</option>" for field, subs of @types[option]).join('')
        child_options = child_options.replace /_/g, ' '
        child_select = "<select id='mid'>#{child_options}</select>"

        if not child_option
            child_option = (field for field, subs of @types[option])[0]

        gchild_field = if @types[option][child_option] then "<input type='text'>" else null
        html = "#{select} #{child_select} #{gchild_field}<div class='close'>x</div>"

        @el.html html

    types: {
        updated:
            before: ['date']
            after: ['date']
            on: ['date']
            within: ['date1', 'date2']
            today: null
            this_week: null
            this_month: null
            this_year: null
        created:
            before: ['date']
            after: ['date']
            on: ['date']
            within: ['date1', 'date2']
            today: null
            this_week: null
            this_month: null
            this_year: null
        labels:
            contains: ['string']
            does_not_contain: ['string']
        title:
            matches: ['string']
            starts_with: ['string']
            ends_with: ['string']
        content:
            contains: ['string']
            does_not_contain: ['string']
    }
