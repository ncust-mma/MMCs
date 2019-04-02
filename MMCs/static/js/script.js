$(function () {
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

    $("[data-toggle='tooltip']").tooltip();

    $(".btn").click(function () {
        $(this).button('loading').delay(1000).queue(function () {
            $(this).button('reset');
            $(this).dequeue();
        });
    });
});