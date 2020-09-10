window.Superlists = {};

window.Superlists.initialize = function () {
    const events_that_hide = ["click", "keypress"]
    events_that_hide.forEach(event => hideErrorMessageOnEvent(event));
};

function hide_error_message() {
    document.querySelectorAll('.has-error')[0].style.display = "none";
}

function hideErrorMessageOnEvent(event) {
    document
        .querySelectorAll('input[name="text"]')[0]
        .addEventListener(event, hide_error_message);
}

