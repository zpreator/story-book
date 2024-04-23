document.getElementById('quizForm').addEventListener('submit', function(event) {
    event.preventDefault();

    let historyList = document.getElementById('historyList');
    let favoriteColor = document.querySelector('input[name="favoriteColor"]:checked')?.value;
    let customColor = document.getElementById('customColor').value;

    let text = 'Favorite Color: ' + (favoriteColor || customColor || 'None specified');
    let newItem = document.createElement('li');
    newItem.textContent = text;
    historyList.appendChild(newItem);

    document.getElementById('customColor').value = ''; // Reset custom color input
});
