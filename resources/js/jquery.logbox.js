(function($) {
    var state = {
            history: [],
            delay_close: false,
            hover: false,
            stick: false
        },
        settings = {
            delay: 5000,
            boxid: 'logBox'
        },
        actions = {
            init: function(options) {
                for (var k in options) {
                    if (settings.hasOwnProperty(k)) {
                        settings[k] = options[k];
                    }
                }
                var $logBox = $('<div/>', {id: settings.boxid}).css({display: 'none'}).appendTo($('body')),
                    $closeBtn = $('<a/>', {class: 'close', href: '#'}).html('&times;').appendTo($logBox),
                    $stickBtn = $('<a/>', {class: 'stick', href: '#'}).html('Stick').appendTo($logBox);
                $closeBtn.click(function(e) {
                    e.preventDefault();
                    $.logBox('stick', false);
                    $.logBox('hide', false);
                });
                $stickBtn.click(function(e) {
                    e.preventDefault();
                    $.logBox('stick');
                })
                $logBox.hover(
                    function() {
                        state.hover = true;
                    },
                    function() {
                        state.hover = false;
                        if (state.delay_close) {
                            state.delay_close = false;
                            $logBox.removeClass('closing');
                            $.logBox('hide', false);
                        }
                    });
            },
            stick: function(toggle) {
                var $logBox = this,
                    newvalue = (toggle !== undefined ? toggle : !state.stick);
                state.stick = newvalue;
                $logBox.toggleClass('sticky', state.stick);
                if (state.stick) {
                    $logBox.clearQueue();
                    smartTimeout('logbox-hide-timeout');
                    $.logBox('show', true);
                } else if (settings.delay) {
                    state.timeout = smartTimeout('logbox-hide-timeout', function() { $.logBox.call($.logBox, 'hide', true); }, settings.delay);
                }
                return newvalue;
            },
            show: function(history, cb) {
                var $logBox = this;
                for (var i = 0 ; i < arguments.length ; i++) {
                    if (typeof arguments[i] === "function") {
                        cb = arguments[i];
                        break;
                    }
                }
                if (history === true) {
                    $.each(state.history, function(i, h) { $logBox.append(h); })
                }
                if (settings.delay) {
                    state.timeout = smartTimeout('logbox-hide-timeout', function() { actions.hide.call($logBox, true); }, settings.delay);
                } else {
                    smartTimeout('logbox-hide-timeout');
                }
                $logBox.fadeIn(function() {
                    if (typeof cb === "function") {
                        cb.apply($logBox);
                    }
                })
            },
            hide: function(auto, cb) {
                var $logBox = this;
                if (state.stick) { return; }
                if (auto && state.hover) {
                    state.delay_close = true;
                    $logBox.addClass('closing');
                } else {
                    $logBox.fadeOut(function() {
                        $logBox.find('.log').each(function(i, e) {
                            state.history.push($(e).detach());
                        });
                        if (typeof cb === "function") {
                            cb.apply($logBox);
                        }
                    });
                    smartTimeout('logbox-hide-timeout');
                }
            },
            log: function() {
                var $logBox = this,
                    msg = Array.prototype.join.call(arguments, ' '),
                    $lastlog = $logBox.find('.log:first-child'),
                    lastmsg = $lastlog.find('.msg').html();
                if (lastmsg === msg) {
                    var $count = $lastlog.find('.count'),
                        count = parseInt($count.html()) + 1;
                    $count.html(count);
                    $count.removeClass('single');
                    return $lastlog;
                } else {
                    return $('<div/>', {class: 'log'})
                        .append($('<span/>', {class: 'count single'}).html(1))
                        .append($('<span/>', {class: 'msg'}).html(msg))
                        .prependTo($logBox);
                }
            }
        };
    $.logBox = function(actionname) {
        var args = Array.prototype.slice.call(arguments, 1),
            action = actions[actionname],
            $logBox = $('#' + settings.boxid);
        if (action) {
            return action.apply($logBox, args);
        }
    }

    $.log = function() {
        var args = Array.prototype.slice.call(arguments);
        args.unshift('log');
        $.logBox('show');
        return $.logBox.apply(this, args);
    }
})(jQuery);

