window.Superlists = {};
window.Superlists.initialize = function () {
    $('input[name="text"]').on('keypress click', function () {
        $('.has-error').hide();
    });
};
