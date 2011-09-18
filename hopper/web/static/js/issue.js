$(function() {
  var keyup_start;
  keyup_start = false;
  $('#issue-close').tipTip({
    content: 'Click to close this Issue',
    defaultPosition: 'top'
  });
  $('#issue-open').tipTip({
    content: 'Click to reopen this Issue',
    defaultPosition: 'top'
  });
  $('textarea').keyup(function() {
    var converter;
    if (!keyup_start) {
      $('#preview-toggle').fadeIn();
      $('#preview-wrapper').fadeIn();
      $('#preview').css('min-height', '50px').height('auto');
      keyup_start = true;
    }
    converter = new Showdown.converter();
    return $('#preview').html(converter.makeHtml($(this).val()));
  });
  return $('#preview-toggle').click(function() {
    if ($('#preview').css('display') === 'none') {
      return $('#preview').css('visibilty', 'hidden').slideUp();
    } else {
      return $('#preview').slideDown().css('visibility', 'visible');
    }
  });
});