let currentSelection = {};

document.querySelectorAll('.option').forEach(option => {
    option.addEventListener('click', function() {
        currentSelection[this.parentElement.parentElement.id] = this.dataset.value;
        this.parentElement.querySelectorAll('.option').forEach(opt => {
            opt.classList.remove('selected');
        });
        this.classList.add('selected');
    });
});

function nextQuestion() {
    // Add logic to switch between questions and update the sidebar history
    console.log(currentSelection); // Placeholder for actual logic
    let historyItem = document.createElement('li');
    historyItem.textContent = 'Selected Genre: ' + currentSelection['genreQuestion'];
    document.getElementById('historyList').appendChild(historyItem);
}
