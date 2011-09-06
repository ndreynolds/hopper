class Filter
    constructor: ->
        @types = 4
        @wrapper = '<div class="content-bar">{0}</div>'

        if $('.content-bar').length
            $('.content-bar').last().after(@types)
    remove: ->
        return @types + 2
