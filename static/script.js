let currentIndex = 0;
let currentSelection = {};
const questions = document.querySelectorAll('.question');

function showQuestion(index) {
    questions.forEach((question, idx) => {
        if (idx === index) {
            question.classList.add('active');
        } else {
            question.classList.remove('active');
        }
    });
}

function startOver() {
    currentIndex = 0;
    showQuestion(currentIndex);
    currentSelection = {};
    document.getElementById('historyList').innerHTML = '';
    questions.forEach(question => {
        const opts = question.querySelectorAll('.option');
        opts.forEach(opt => opt.classList.remove('selected'));
    });
}

document.querySelectorAll('.option').forEach(option => {
    option.addEventListener('click', function() {
        const questionId = this.parentElement.parentElement.id;
        currentSelection[questionId] = this.dataset.value;

        // Remove 'selected' class from all options in the same question
        this.parentElement.querySelectorAll('.option').forEach(opt => {
            opt.classList.remove('selected');
        });

        // Add 'selected' class to the clicked option
        this.classList.add('selected');
    });
});


function nextQuestion() {
    if (currentIndex < questions.length - 1) {
        currentIndex++;
        showQuestion(currentIndex);
        updateHistory();
    } else {
        // Handle the end of the questionnaire
        console.log("All questions completed");
    }
}

function prevQuestion() {
    if (currentIndex > 0) {
        currentIndex--;
        showQuestion(currentIndex);
    }
}

function updateHistory() {
    let historyItem = document.createElement('li');
    historyItem.textContent = 'Selected: ' + currentSelection[questions[currentIndex - 1].id];
    document.getElementById('historyList').appendChild(historyItem);
}

// Initialize the first question
showQuestion(0);
