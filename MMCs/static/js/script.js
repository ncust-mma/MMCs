$(function () {
    var default_error_message = 'Server error, please try again later.';

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrf_token);
            }
        }
    });

    $(document).ajaxError(function (event, request, settings) {
        var message = null;
        if (request.responseJSON && request.responseJSON.hasOwnProperty('message')) {
            message = request.responseJSON.message;
        } else if (request.responseText) {
            var IS_JSON = true;
            try {
                var data = JSON.parse(request.responseText);
            } catch (err) {
                IS_JSON = false;
            }
            if (IS_JSON && data !== undefined && data.hasOwnProperty('message')) {
                message = JSON.parse(request.responseText).message;
            } else {
                message = default_error_message;
            }
        } else {
            message = default_error_message;
        }
        toast(message, 'error');
    });

    var flash = null;

    function toast(body, category) {
        clearTimeout(flash);
        var $toast = $('#toast');
        if (category === 'error') {
            $toast.css('background-color', 'red')
        } else {
            $toast.css('background-color', '#333')
        }
        $toast.text(body).fadeIn();
        flash = setTimeout(function () {
            $toast.fadeOut();
        }, 3000);
    }

    // delete confirm modal
    $('#confirm-delete').on('show.bs.modal', function (e) {
        $('.delete-form').attr('action', $(e.relatedTarget).data('href'));
    });
    // random confirm modal
    $('#confirm-random').on('show.bs.modal', function (e) {
        $('.random-form').attr('action', $(e.relatedTarget).data('href'));
    });
    // start confirm modal
    $('#confirm-start').on('show.bs.modal', function (e) {
        $('.start-form').attr('action', $(e.relatedTarget).data('href'));
    });
    // stop confirm modal
    $('#confirm-stop').on('show.bs.modal', function (e) {
        $('.stop-form').attr('action', $(e.relatedTarget).data('href'));
    });
    // continue confirm modal
    $('#confirm-continue').on('show.bs.modal', function (e) {
        $('.continue-form').attr('action', $(e.relatedTarget).data('href'));
    });

    if (is_authenticated) {
        setInterval(update_notifications_count, 30000);
    }

});