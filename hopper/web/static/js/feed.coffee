$ ->
    # Want the next 20 stories
    offset = 20
    $('#load-stories').click ->
        $.getJSON "?offset=#{offset}", (data) ->
            stories = data
            for s in stories
                html = "<li>
                    <span id='author'>#{s.user.name}</span>
                    (#{s.user.email})&nbsp;"
                if s.link
                    html += "<a class='action-link' href='#{s.link}'
                        >#{s.message}</a>&nbsp;&nbsp;"
                    html += "<a class='fancy-monospace' href='#{s.link}'
                        >#{s.button}</a>"
                else
                    html += "<span id='author'>#{s.message}</span>"
                html += "&nbsp; <span id='time'>#{s.time} ↲</span>"
                if s.snippet
                    html += "<div class='snippet'>"
                    if s.title
                        html += "<span id='title'>#{s.title}</span><br>"
                    html += s.snippet
                html += "</li>"
                $('#feed ul').append html

            # remove button if no more.
            if stories.length < 20
                $('#load-stories').remove()
            # increment the offset.
            offset += 20
