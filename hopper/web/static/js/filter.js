var Filter;
Filter = (function() {
  function Filter() {
    this.types = 4;
    this.wrapper = '<div class="content-bar">{0}</div>';
    if ($('.content-bar').length) {
      $('.content-bar').last().after(this.types);
    }
  }
  Filter.prototype.remove = function() {
    return this.types + 2;
  };
  return Filter;
})();