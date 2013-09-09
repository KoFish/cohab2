(function($) {
    $.fn.grade = function(options) {
        var settings = $.extend({
            symbols: ['!', '!!', '!!!', '!!!!'],
            colors: ['#88f', '#8f8', '#f88', '#f33']
        }, options);
        return this.each(function(i, elem) {
            var $elem = $(elem);
            $elem.hide()
            if ($elem.is('select')) {
                var $span = $('<span/>', {class: 'grade-selector'}),
                    selval = $elem.find('option:selected').val();
                for (var i = 0 ; i < settings.symbols.length && i < $elem.children().length ; i++) {
                    var color = (settings.colors.length > i) ? settings.colors[i] : settings.colors[settings.colors.length-1],
                        symbol = settings.symbols[i],
                        curval = $elem.children()[i].value,
                        span = $('<span/>', {'data-value': $elem.children()[i].value}).html(symbol.fontcolor(color)).appendTo($span);
                    if (selval === curval) { span.addClass('active'); }
                    span.click(function(e) {
                        e.preventDefault();
                        var $btn = $(this),
                            value = $btn.attr('data-value');
                        $btn.parent('span').find('.active').removeClass('active');
                        $btn.addClass('active');
                        $elem.val(value);
                    });
                }
                $elem.after($span);
            } else {
                var $span = $('<span/>', {class: 'grade-indicator'}),
                    value = parseInt($elem.html()),
                    i = (value < settings.symbols.length) ? value : settings.symbols.length-1;
                $span.html(('' + settings.symbols[i]).fontcolor(settings.colors[i]));
                $elem.after($span);
            }
        });
    }
})(jQuery);
