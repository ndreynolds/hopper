var $;
$ = jQuery;
$.fn.HopperFocusHelper = function() {
  var original;
  original = $(this).val();
  $(this).live('focus', function(event) {
    if ($(this).val() === original) {
      $(this).val('');
      return $(this).removeClass('unfocused');
    }
  });
  return $(this).live('blur', function(event) {
    if ($(this).val() === '') {
      $(this).val(original);
      return $(this).addClass('unfocused');
    }
  });
};