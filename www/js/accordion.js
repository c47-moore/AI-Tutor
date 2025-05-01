function accordionToggle(el) {
    const activeElements = document.getElementsByClassName("active");
    if (activeElements.length > 0) {
        activeElements[0].classList.remove("active");
    }
    document.getElementById('q' + el).classList.add("active");
    document.getElementById('a' + el).focus();
}
