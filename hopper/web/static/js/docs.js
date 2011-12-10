$(function() {
  var mdown;
  mdown = $('.markdown').html();
  mdown = mdown.replace(/^\s*/g, '');
  $('#edit-button').click(function() {
    $('.markdown').html($('.doc').html());
    return $('.doc').html("<textarea id='edit-field'>" + mdown + "</textarea>                        <br><br>                        <div class='button gray' id='save-button'                            style='display:inline'>Save changes</div>                        <div class='button red' id='cancel-button'                            style='display:inline'>Cancel</div>                        <br><br>");
  });
  $('#cancel-button').live('click', function() {
    $('.doc').html($('.markdown').html());
    return $('.markdown').html(mdown);
  });
  return $('#save-button').live('click', function() {
    var edited;
    return edited = $('.doc').html();
  });
});