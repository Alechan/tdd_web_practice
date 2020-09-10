function getErrorElement() {
    return document.querySelectorAll('.has-error')[0];
}

function isVisible(elem) {
    return !!(elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length);
}

function triggerEvent(eventType, element) {
    const event = document.createEvent('HTMLEvents');
    event.initEvent(eventType, true, false);
    element.dispatchEvent(event);
}

function getInputElement() {
    return document.querySelectorAll('input[name="text"]')[0];
}
