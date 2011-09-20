$(function() {
  $('#new-issue').tipTip({
    content: 'Submit a new issue to the tracker'
  });
  $('#search input').HopperFocusHelper();
  return $('#flash').click(function() {
    return $(this).hide();
  });
});