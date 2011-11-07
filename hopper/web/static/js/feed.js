$(function() {
  var offset;
  offset = 20;
  return $('#load-stories').click(function() {
    return $.getJSON("?offset=" + offset, function(data) {
      var html, s, stories, _i, _len;
      stories = data;
      for (_i = 0, _len = stories.length; _i < _len; _i++) {
        s = stories[_i];
        html = "<li>                    <span id='author'>" + s.user.name + "</span>                    (" + s.user.email + ")&nbsp;";
        if (s.link) {
          html += "<a class='action-link' href='" + s.link + "'                        >" + s.message + "</a>&nbsp;&nbsp;";
          html += "<a class='fancy-monospace' href='" + s.link + "'                        >" + s.button + "</a>";
        } else {
          html += "<span id='author'>" + s.message + "</span>";
        }
        html += "&nbsp; <span id='time'>" + s.time + " ↲</span>";
        if (s.snippet) {
          html += "<div class='snippet'>";
          if (s.title) {
            html += "<span id='title'>" + s.title + "</span><br>";
          }
          html += s.snippet;
        }
        html += "</li>";
        $('#feed ul').append(html);
      }
      if (stories.length < 20) {
        $('#load-stories').remove();
      }
      return offset += 20;
    });
  });
});