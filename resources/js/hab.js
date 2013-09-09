jQuery(document).ready(function() {
    $.logBox('init', {delay: 10000});
});

(function($) {
    var state = {};
    function fetch_messages() {
        $.get('/get/messages/')
            .done(function(data) {
                if (data.status === 'success' && 'messages' in data) {
                    $(data.messages).each(function(i, d) {
                        $.message(d.message, 'Message', d.extra_tags);
                        $.log(arguments);
                    })
                }
            })
        state.fetch_message_timeout = setTimeout(fetch_messages, 5000);
    }
    $(document).ready(function() {
        fetch_messages();
    }); 
    $.update_messages = function() {
        if (state.fetch_message_timeout) {
            clearTimeout(state.fetch_message_timeout);
        }
        fetch_messages();
    };
    $.message = function(body, title, level) {
        var $not, msg = {text: body};
        level = level || 'info';
        msg['title'] = title || 'Message';
        $not = $.pnotify(msg)
        $.each(level.split(' '), function(i, l) {
            $not.addClass('alert-' + l);
        })
    };
})(jQuery);

(function($) {
    $.reload = function(url) {
        url = url || window.location.href;
        $.get(url + (url.indexOf('?') >= 0 ? '&' : '?') + 'strip')
            .done(function (data) {
                $('#main').html(data).basic_setup();
            })
        $.fetch_verbs();
        $.update_messages();
    }
    $.fetch_verbs = function () {
        var template = _.template($('#task-link').html()),
            $sidebar = $('#sidebar > ul');
        $.get('/get/verbs')
        .done(function(data) {
            if ('verbs' in data) {
                $.each(data.verbs, function(i, verb) {
                    var link = $sidebar.find('#task-link-'+slugify(verb[0]));
                    if (link.size() > 0) {
                        link.replaceWith(template({'verb': verb[0], 'count': verb[1]}));
                    } else {
                        $sidebar.append(template({'verb': verb[0], 'count': verb[1]}));
                    }
                });
            }
        });
    };
    $.fn.create_assignment_setup = function($modal) {
        return $(this).each(function() {
            var $this = $(this);

            $this
                .find('.grade').grade().end()
                .find('#id_repeat').change(function() {
                    var checked = $(this).prop("checked");
                    $('#id_repeat_delay').prop("disabled", !checked);
                    $('#id_allowed_owners').prop("disabled", !checked);
                    $('#assign-repeat').toggleClass('disabled', !checked);
                }).end()
                .find('#id_repeat_delay').prop("disabled", !$('#id_repeat').prop('checked')).end()
                .find('#id_allowed_owners').prop("disabled", !$('#id_repeat').prop('checked')).end()
                .find('button[type=submit]').click(function(e) {
                    e.preventDefault();
                    var $form = $(this).closest('form');
                    $form.find('.form-group.has-error').removeClass('has-error').end()
                         .find('.help-block.error').remove().end();
                    $.post($form.attr('action'), $form.serialize())
                        .done(function(data) {
                            if (data.status === 'success') {
                                var verb = $form.find('#id_verb').val()

                                var url = window.location.href,
                                    start = url.indexOf('?q=') >= 0 ? url.indexOf('?q=') : url.indexOf('&q='),
                                    end = url.indexOf('&', start);

                                $modal.find('.modal-body').html('');
                                $modal.modal('hide');

                                $.log(url, start, end);
                                if (start >= 0) {
                                    url = url.substring(0, start) + (end > 0 ? url.slice(end) : '')
                                    $.log(url)
                                    window.location.href = url;
                                } else {
                                    $.reload();
                                }
                            } else if (data.status === 'failed') {
                                for (var key in data.errors) {
                                    var $field = $('#id_' + key);
                                    $field.closest('.form-group').addClass('has-error');
                                    $.each(data.errors[key], (function() {
                                        $('<p/>', {'class': 'help-block error'}).html(this).insertAfter($field);
                                    }));
                                }
                            } else {
                                $.log('Did not get a proper from the server.', data);
                            }
                        }
                    );
                }).end()
                .find('button[type=reset]').click(function(e) {
                    $modal.modal('hide');
                }).end()
                .find('#id_verb').typeahead({
                    name: 'verbs',
                    prefetch: {url: '/get/verbs/?nocount',
                               filter: function(resp) { return resp.verbs; }},
                    remote: {url: '/get/verbs/?nocount&q=%QUERY',
                             filter: function(resp) { return resp.verbs; }}
                })

        })
    };

    $.fn.setup_assignment = function() {
        return $(this).each(function() {
            var $ass = $(this),
                id = $ass.data('id');
            $ass.find('header').click(function() {
                $ass.find('.details').toggleClass('hide');
            });
            $ass.find('.controls button.finish').click(function() {
                    $.get('/task/'+id+'/complete')
                        .done(function(data) {
                            if (data.status === "success") { $.reload(); }
                            else { $.message('Could not complete the task' + (data.message ? ': '+data.message : ''), 'Failed', 'warning'); }
                        })
                    }).end()
                .find('.controls button.clear').click(function() {
                    $.get('/task/'+id+'/clear')
                        .done(function(data) {
                            if (data.status === "success") { $.reload(); }
                            else { $.message('Could not clear the task' + (data.message ? ': '+data.message : ''), 'Failed', 'warning'); }
                        })
                    });
            $ass.find('.details button.reopen').click(function() {
                $.get('/task/' + id + '/reopen')
                    .done(function(data) {
                        if (data.status === 'success') { $.reload(); }
                        else { $.message(data.message, 'Could not reopen task', 'warning'); }
                    });
            });
            $ass.find('.details .assign-task').change(function() {
                var $select = $(this);
                $select.find('option:selected').each(function() {
                    var $sel = $(this),
                        value = $sel.attr('value');
                    if (value) {
                        $.get('/task/' + id + '/assign' + (value === 'no' ? '' : ('?to='+value)))
                        .done(function(data) {
                            if (data.status === 'success') {
                                $sel.closest('.details').find('.assignee').text(value === 'no' ? '' : value);
                            } else {
                                $.message(data.message, 'Failed assigning task!', 'warning');
                            }
                        });
                    }
                })
            });
            $ass.find('.details .suspend-task').change(function() {
                var $select = $(this);
                $select.find('option:selected').each(function() {
                    var $sel = $(this),
                        value = $sel.attr('value');
                    if (value && value != '0') {
                        $.get('/task/' + id + '/suspend?days=' + value)
                        .done(function(data) {
                            $select.val(0);
                            if (data.status === 'success') {
                                $sel.closest('.details').find('.deadline').text(data.deadline);
                                $ass.find('header h4 small').html(data.days_left);
                            } else {
                                $.message(data.message, 'Failed suspend task!: ', 'warning');
                            }
                        });
                    }
                })
            });
        });
    }

    $.fn.basic_setup = function() {
        return $(this).each(function() {
            var $this = $(this);
            $this.find('.grade').grade().end()
                 .find('#add-assignment')
                     .click(function() {
                        var $modal = $("#createAssignmentModal");
                        $.get('/add/task/')
                            .done(function(data) {
                                $modal.find('.modal-body')
                                        .html(data).end()
                                    .create_assignment_setup($modal)
                                    .modal({
                                        'backdrop': true,
                                        'keyboard': true,
                                        'show': false
                                    }).modal('show');

                            })
                        return false;
                     })
                     .end()
                 .find('#add-view-assignment')
                    .click(function() {
                        var $modal = $('#createViewAssignmentModal'),
                            $btn = $(this);
                        $.get($btn.attr('href'))
                            .done(function(data) {
                                $modal.find('.modal-body')
                                        .html(data).end()
                                    .create_assignment_setup($modal)
                                    .modal({
                                        backdrop: true,
                                        keyboard: true,
                                        show: false
                                    }).modal('show');
                            });
                    }).end()
                 .find('#auth-box').each(function() {
                    var $box = $(this),
                        $modal = $('#login-modal');
                    $box.find('button.login').click(function() {
                        $.get('/login')
                            .done(function(data) {
                                $modal.find('.modal-body').html(data);
                                $modal.modal({
                                    backdrop: true,
                                    keyboard: true,
                                    show: false
                                });
                                $modal.find('.modal-body')
                                    .find('button[type=submit]').click(function() {
                                        var $form = $(this).closest('form');
                                        $.post($form.attr('action'), $form.serialize())
                                            .done(function(data) {
                                                if (data.status === 'success') {
                                                    window.location.reload();
                                                }
                                            });
                                    });
                                $modal.modal('show');
                            })
                    }).end()
                    .find('button.logout').click(function() {
                        window.location = '/logout'
                    });
                 }).end()
                 .find('.assignment').each(function() {
                    $(this).setup_assignment();
                 }).end()
                 .find('.template').each(function() {
                    var $template = $(this),
                        id = $template.data('id');
                    $template.find('header').click(function() {
                        $template.find('.details').toggleClass('hide');
                    }).end()
                    .find('.controls')
                        .find('button.add').click(function() {
                            $.post('/template/'+id+'/instanciate')
                                .done(function(data) {
                                    if (data.status === "success") {
                                        $.reload();
                                    } else {
                                        $.message(data.message, 'Failed', 'warning');
                                    }
                                })

                        }).end()
                        .find('button.remove').click(function() {
                            $.post('/template/'+id+'/remove')
                                .done(function(data) {
                                    if (data.status === "success") {
                                        $.reload();
                                    } else {
                                        $.message(data.message, 'Failed', 'warning');
                                    }
                                })
                        });
                 })
        });
    };
}(jQuery));

$(document).ready(function() {
    $('body').basic_setup()
    $.fetch_verbs();
});