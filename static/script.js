let currentQuestionIndex = 0;
let currentSelection = {};
let pages;
let currentPageIndex = 0;
const questions = document.querySelectorAll('.question');
const nextButton = document.getElementById('nextButton');
const backButton = document.getElementById("backButton");
const submitButton = document.getElementById('submitButton');
const historyList = document.getElementById('historyList');

function showQuestion(index) {
    questions.forEach(question => {
        question.classList.remove('active');
    });
    questions[index].classList.add('active');

    // Handle button visibility
    submitButton.style.display = 'inline-block';
    nextButton.style.display = 'inline-block';
    backButton.style.display = 'inline-block';
    if (currentQuestionIndex === 0){
        backButton.style.display = "none";
        submitButton.style.display = 'none';
    } else if (currentQuestionIndex === questions.length - 1) {
        nextButton.style.display = 'none';
    } else {
        submitButton.style.display = 'none';
    }
}

function startOver() {
    document.getElementById("pages").style.display = "none";
    document.getElementById("storyComplete").style.display = "none";
    document.getElementById("imagesComplete").style.display = "none";
    document.getElementById("chapters").style.display = "none";
    document.getElementById("questions").style.display = "block";
    document.getElementById("questionsButtons").style.display = "block";
    document.getElementById("navigation").style.display = "block";
    currentQuestionIndex = 0;
    showQuestion(currentQuestionIndex);
    currentSelection = {};
    document.getElementById('historyList').innerHTML = '';
    document.getElementById("summary").innerHTML = '';
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
    if (currentQuestionIndex < questions.length - 1) {
        currentQuestionIndex++;
        showQuestion(currentQuestionIndex);
        updateHistory();
    } else {
        // Handle the end of the questionnaire
        console.log("All questions completed");
    }
}

function prevQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        showQuestion(currentQuestionIndex);
    }
}

function submitForm() {
    hideQuestions();
    document.getElementById("spinner1").style.display = "block";
    const formData = {};
    questions.forEach(question => {
        let selected = question.querySelector('.option.selected');
        if (selected) {
            formData[question.id] = selected.getAttribute('data-value');
        }
    });

    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // window.location.href = data.redirect_url; // Redirect to the new URL
            getStory();
        } else {
            console.error('Error:', data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    })
    .finally(() => {
        document.getElementById("spinner1").style.display = "none";
        document.getElementById("storyComplete").style.display = "block";
    });
}

function getStory() {
    document.getElementById("spinner2").style.display = "block";
    fetch('/story', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // window.location.href = data.redirect_url; // Redirect to the new URL
            pages = data.pages;
            renderPages();
            showChapterButtons();
        } else {
            console.error('Error:', data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    })
    .finally(() => {
        document.getElementById("spinner2").style.display = "none";
        document.getElementById("imagesComplete").style.display = "block";
    });
}

function updateHistory() {
    const currentQuestion = questions[currentQuestionIndex - 1];
    const selection = currentSelection[questions[currentQuestionIndex - 1].id];
    const category = currentQuestion.getAttribute('data-value');
    const value = category + ": " + selection;
    
    let newOption;
    const options = currentQuestion.querySelectorAll('.option');
    options.forEach(option => {
        if (option.getAttribute('data-value') === selection) {
            newOption = option.cloneNode(true);
        }
    });

    newOption.setAttribute("id", "question-" + currentQuestion.id);
    newOption.classList.remove("selected");
    
    let summaryDiv = document.getElementById("summary");

    // Check if there's already an entry for this question
    let existingEntry = historyList.querySelector(`li[data-question-id="${currentQuestion.id}"]`);
    if (existingEntry) {
        existingEntry.textContent = value; // Update existing entry
        existingOption = document.getElementById("question-" + currentQuestion.id)
        if (existingOption){
            summaryDiv.removeChild(existingOption);
        }
        summaryDiv.appendChild(newOption);
    } else {
        // Create new entry if not already there
        let historyItem = document.createElement('li');
        historyItem.setAttribute('data-question-id', currentQuestion.id); // Set an attribute to identify the question
        historyItem.textContent = value;
        historyList.appendChild(historyItem);

        // Add entry to the summaries
        summaryDiv.appendChild(newOption);
    }
}

function hideQuestions() {
    questions.forEach(question => {
        question.classList.remove('active');
    });

    document.getElementById("questionsButtons").style.display = "none";
    document.getElementById("navigation").style.display = "none";
}

function showChapterButtons(){
    const chaptersElement = document.getElementById("chapters");
    for (let i = 0; i < pages.length; i++){
        let existingElement = document.getElementById("chapter-" + i.toString());
        if (!existingElement){
            const chapterElement = document.createElement("div");
            chapterElement.id = "chapter-" + i.toString();
            const chapterLink = document.createElement("button");
            chapterLink.innerText = "Chapter " + (i+1).toString();
            chapterLink.onclick = function() {
                navigateTo(i);
            };
            chapterElement.appendChild(chapterLink);
            chaptersElement.appendChild(chapterElement);
        }
    }
}

function renderPages() {
    document.getElementById("backPageButton").style.display = "inline-block";
    document.getElementById("nextPageButton").style.display = "inline-block";
    if (currentPageIndex == 0) {
        document.getElementById("backPageButton").style.display = "none";
    } else if (currentPageIndex == pages.length - 1){
        document.getElementById("nextPageButton").style.display = "none";
    } 
    document.getElementById("questions").style.display = "none";
    document.getElementById("pages").style.display = "block";
    document.getElementById("chapters").style.display = "block";
    const container = document.getElementById('bookContainer');
    container.innerHTML = ''; // Clear existing content
    const startIndex = currentPageIndex; // Show two pages at a time
    const endIndex = startIndex + 1;

    for (let i = startIndex; i < endIndex && i < pages.length; i++) {
        const page = pages[i];
        const pageElement = document.createElement('div');
        pageElement.className = 'page';
        pageElement.innerHTML = `
            <img src="${page.image}" alt="${page.description}">
            <div class="text" id="textInput">${page.text}</div>
            <audio id="audioPlayer" style="text-align:center;" controls hidden></audio>`;
        pageElement.style.textAlign = "center";
        container.appendChild(pageElement);
    }
    convertTextToSpeech();
}

function navigate(direction) {
    currentPageIndex += direction;
    if (currentPageIndex < 0) {
        currentPageIndex = 0; // Prevent going before the first page
    } else if (currentPageIndex > pages.length - 1) {
        currentPageIndex = pages.length - 1; // Prevent going past the last page
    }
    renderPages();
}

function navigateTo(index){
    currentPageIndex = index;
    renderPages();
}

function convertTextToSpeech() {
    const text = document.getElementById('textInput').innerText;
    const formData = new FormData();
    formData.append('text', text);

    fetch('/tts', {
        method: 'POST',
        body: formData
    }).then(response => response.blob())
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const audioPlayer = document.getElementById('audioPlayer');
            audioPlayer.src = url;
            audioPlayer.hidden = false;
            // audioPlayer.play();
        }).catch(error => console.error('Error:', error));
}

function exportVideo() {
    document.getElementById("spinner3").style.display = "block";
    document.getElementById("pageButtons").style.display = "none";
    document.getElementById("bookContainer").style.display = "none";
    document.getElementById("pageNavigation").style.display = "none";
    fetch('/export')
    .then(response => {
        if (response.status === 200) {
        // File download successful
        return response.blob(); // Assuming the response contains a file
        } else if (response.status === 204) {
        // No content returned, do nothing
        console.log('No content returned from the server.');
        return Promise.resolve();
        } else {
        // Handle other status codes
        console.error('Error:', response.statusText);
        throw new Error('Error occurred while downloading file.');
        }
    })
    .then(blob => {
        // Assuming blob is the file data returned by the server
        if (blob) {
        // Handle file download
        // For example, create a link element and trigger a download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'video.mp4'; // Set the filename
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
    })
    .finally(() => {
        document.getElementById("spinner3").style.display = "none";
        document.getElementById("pageButtons").style.display = "block";
        document.getElementById("bookContainer").style.display = "block";
        document.getElementById("pageNavigation").style.display = "block";   
    });

}

// Initialize the first question
showQuestion(0);
