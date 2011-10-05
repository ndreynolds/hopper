$(function() {
  $('input#title').HopperFocusHelper();
  return $('#issue-preview-button').click(function() {
    var converter, title;
    converter = new Showdown.converter();
    $('#markdown').html(converter.makeHtml($('textarea').val()));
    title = $('input#title').val();
    if (title === 'Issue Summary') {
      title = '';
    }
    $('span#title').html(title);
    return $('#issue-preview').dialog({
      modal: true,
      width: 800,
      resizable: false,
      position: 'top',
      open: function(event, ui) {
        return $('.ui-widget-overlay').bind('click', function() {
          return $('#issue-preview').dialog('close');
        });
      }
    });
  });
});