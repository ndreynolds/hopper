$(function() {
  $('#new-issue').tipTip({
    content: 'Submit a new issue to the tracker'
  });
  return $('#flash').click(function() {
    return $(this).hide();
  });
});