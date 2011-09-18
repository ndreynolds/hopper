var Filter;
Filter = (function() {
  function Filter() {
    var base, that;
    base = '<div class="content-bar">';
    if ($('.content-bar').length) {
      $('.content-bar').last().after(base);
    } else {
      $('#content-header').after(base);
    }
    this.el = $('.content-bar').last();
    this.set();
    that = this;
    $(this.el.find('select')).live('change', function() {
      return that.set(that.el.find('#top option:selected').val(), that.el.find('#mid option:selected').val());
    });
  }
  Filter.prototype.destroy = function() {
    return this.el.remove();
  };
  Filter.prototype.set = function(option, child_option) {
    var child_options, child_select, field, gchild_field, html, options, select, subs;
    if (option == null) {
      option = null;
    }
    if (child_option == null) {
      child_option = null;
    }
    options = ((function() {
      var _ref, _results;
      _ref = this.types;
      _results = [];
      for (field in _ref) {
        subs = _ref[field];
        _results.push("<option>" + field + "</option>");
      }
      return _results;
    }).call(this)).join('');
    select = "<select id='top'>" + options + "</select>";
    if (!option) {
      option = ((function() {
        var _ref, _results;
        _ref = this.types;
        _results = [];
        for (field in _ref) {
          subs = _ref[field];
          _results.push(field);
        }
        return _results;
      }).call(this))[0];
    }
    child_options = ((function() {
      var _ref, _results;
      _ref = this.types[option];
      _results = [];
      for (field in _ref) {
        subs = _ref[field];
        _results.push("<option>" + field + "</option>");
      }
      return _results;
    }).call(this)).join('');
    child_options = child_options.replace(/_/g, ' ');
    child_select = "<select id='mid'>" + child_options + "</select>";
    if (!child_option) {
      child_option = ((function() {
        var _ref, _results;
        _ref = this.types[option];
        _results = [];
        for (field in _ref) {
          subs = _ref[field];
          _results.push(field);
        }
        return _results;
      }).call(this))[0];
    }
    gchild_field = this.types[option][child_option] ? "<input type='text'>" : null;
    html = "" + select + " " + child_select + " " + gchild_field + "<div class='close'>x</div>";
    return this.el.html(html);
  };
  Filter.prototype.types = {
    updated: {
      before: ['date'],
      after: ['date'],
      on: ['date'],
      within: ['date1', 'date2'],
      today: null,
      this_week: null,
      this_month: null,
      this_year: null
    },
    created: {
      before: ['date'],
      after: ['date'],
      on: ['date'],
      within: ['date1', 'date2'],
      today: null,
      this_week: null,
      this_month: null,
      this_year: null
    },
    labels: {
      contains: ['string'],
      does_not_contain: ['string']
    },
    title: {
      matches: ['string'],
      starts_with: ['string'],
      ends_with: ['string']
    },
    content: {
      contains: ['string'],
      does_not_contain: ['string']
    }
  };
  return Filter;
})();