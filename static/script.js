let currentSelection = {};

function nextQuestion() {
    // Logic to move to next question or save the current selection
    console.log(currentSelection); // Debugging output to see selections
    // Move to next question logic here
}

document.querySelectorAll('.option').forEach(option => {
    option.addEventListener('click', function() {
        currentSelection[this.parentElement.parentElement.id] = this.dataset.value;
        this.parentElement.querySelectorAll('.option').forEach(opt => {
            opt.classList.remove('selected');
        });
        this.classList.add('selected');
    });
});
