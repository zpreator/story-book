let currentIndex = 0;
let currentSelection = {};
const questions = document.querySelectorAll('.question');
const nextButton = document.getElementById('nextButton');
const submitButton = document.getElementById('submitButton');

function showQuestion(index) {
    questions.forEach(question => {
        question.classList.remove('active');
    });
    questions[index].classList.add('active');

    // Handle button visibility
    if (currentIndex === questions.length - 1) {
        nextButton.style.display = 'none';
        submitButton.style.display = 'inline-block';
    } else {
        nextButton.style.display = 'inline-block';
        submitButton.style.display = 'none';
    }
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

function submitForm() {
    // Collect data to send
    const formData = {};
    questions.forEach(question => {
        let selected = question.querySelector('.option.selected');
        if (selected) {
            formData[question.id] = selected.getAttribute('data-value');
        }
    });

    // Send data to Flask route
    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function updateHistory() {
    let historyItem = document.createElement('li');
    historyItem.textContent = 'Selected: ' + currentSelection[questions[currentIndex - 1].id];
    document.getElementById('historyList').appendChild(historyItem);
}

// Initialize the first question
showQuestion(0);
