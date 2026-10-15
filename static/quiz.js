
// The questions, choices, correct answers, and explanations.

const questions = [
  {question: "Which keyword declares a block-scoped variable that can later be reassigned?", choices: ["var", "let", "const", "static"], answer: 1, explanation: "let declares a block-scoped variable whose value may later be reassigned."},
  {question: "Which JavaScript operator tests strict equality?", choices: ["=", "==", "===", "!="], answer: 2, explanation: "The === operator compares both value and type."},
  {question: "Which property gives the number of elements in an array?", choices: ["size", "count", "length", "total"], answer: 2, explanation: "An array's length property gives its number of elements."},
  {question: "What is the index of the first element in an array?", choices: ["0", "1", "-1", "It depends on the array"], answer: 0, explanation: "JavaScript arrays use zero-based indexes, so the first element is at index 0."},
  {question: "What does a function's return statement do?", choices: ["Repeats the function", "Displays a message", "Declares a variable", "Ends the function and sends back a value"], answer: 3, explanation: "return ends the function call and optionally provides a value to its caller."},
  {question: "What is the result of 7 % 3?", choices: ["2", "1", "3", "0"], answer: 1, explanation: "The remainder operator % returns 1 because 7 divided by 3 leaves a remainder of 1."},
  {question: "Which loop is commonly used when the number of repetitions is known?", choices: ["if", "switch", "for", "return"], answer: 2, explanation: "A for loop combines initialization, a condition, and an update to control repetitions."},
  {question: "Given const student = {name: 'Maya'}, how do you read the name?", choices: ["student.name", "student( name )", "student->name", "name.student"], answer: 0, explanation: "Dot notation reads a named property of an object: student.name."},
  {question: "What does 'JavaScript'.toUpperCase() return?", choices: ["javascript", "JavaScript", "JAVASCRIPT", "Java Script"], answer: 2, explanation: "toUpperCase() returns a new string with its letters converted to uppercase."},
  {question: "What is the value of true && false?", choices: ["true", "false"], answer: 1, explanation: "Logical AND is true only when both Boolean operands are true."}
];

// Start at the first question.
let currentQuestion = 0;

// Store the user's answer for each question.
const userAnswers = new Array(questions.length);

// Save the selected choice's index.
function saveAnswer(choiceIndex) {
  userAnswers[currentQuestion] = choiceIndex;
}

// Next button.
function goNext() {
  // Stop at the last question.
  if (currentQuestion < questions.length - 1) {
    currentQuestion++;
    renderQuestion();
  }
}

// Previous button.
function goPrevious() {
  // Stop at the first question.
  if (currentQuestion > 0) {
    currentQuestion--;
    renderQuestion();
  }
}

// First button.
function goFirst() {
  currentQuestion = 0;
  renderQuestion();
}

// Last button.
function goLast() {
  currentQuestion = questions.length - 1;
  renderQuestion();
}

// Count the correct answers.
function calculateScore() {
  let score = 0;

  // Check every question.
  for (let i = 0; i < questions.length; i++) {
    // Add one point if the answer is correct.
    if (userAnswers[i] === questions[i].answer) {
      score++;
    }
  }

  return score;
}

// Convert the score to a rounded percentage.
function calculatePercentage(score) {
  return Math.round((score / questions.length) * 100);
}

// Choose a message based on the percentage.
function getPerformanceMessage(percentage) {
  if (percentage >= 80) return "Excellent";
  if (percentage >= 60) return "Good";
  if (percentage >= 50) return "Pass";
  return "Needs improvement";
}

// Prepare the correction text.
function buildCorrection() {
  let correction = "";

  for (let i = 0; i < questions.length; i++) {
    const q = questions[i];

    // undefined means unanswered; 0 means the first choice.
    const selected = userAnswers[i] === undefined
      ? "Not Answered"
      : q.choices[userAnswers[i]];

    // Check whether the answer is correct.
    const result = userAnswers[i] === q.answer ? "Correct" : "Incorrect";

    // Add feedback. \n starts a new line.
    correction += `Question ${i + 1}: ${q.question}\n`;
    correction += `Your answer: ${selected}\n`;
    correction += `Correct answer: ${q.choices[q.answer]}\n`;
    correction += `Result: ${result}\n`;
    correction += `Explanation: ${q.explanation}\n\n`;
  }

  return correction;
}

// PROVIDED INTERFACE CODE

// Submit button: calculate and display results.
function submitQuiz() {
  const score = calculateScore();
  const percentage = calculatePercentage(score);
  const message = getPerformanceMessage(percentage);
  const correction = buildCorrection();
  showResults(score, percentage, message, correction);
}

// Display the current question and choices.
function renderQuestion() {
  const q = questions[currentQuestion];

  // Display "Question 1 of 10", etc.
  document.getElementById("progress").textContent =
    `Question ${currentQuestion + 1} of ${questions.length}`;

  // Display the question text.
  document.getElementById("questionText").textContent = q.question;

  // Clear the old choices.
  const choicesContainer = document.getElementById("choices");
  choicesContainer.innerHTML = "";

  // Create each answer choice.
  for (let i = 0; i < q.choices.length; i++) {
    const label = document.createElement("label");
    label.className = "choice";

    const radio = document.createElement("input");
    radio.type = "radio";

    // Same name allows only one selected answer.
    radio.name = "answer";
    radio.value = i;

    // Restore the previously selected answer.
    if (userAnswers[currentQuestion] === i) {
      radio.checked = true;
    }

    // Save the answer when clicked.
    radio.onclick = function () {
      saveAnswer(i);
    };

    // Add the radio button and its text to the page.
    label.appendChild(radio);
    label.appendChild(document.createTextNode(" " + q.choices[i]));
    choicesContainer.appendChild(label);
  }

  // Disable First and Previous on the first question.
  document.getElementById("firstBtn").disabled = currentQuestion === 0;
  document.getElementById("previousBtn").disabled = currentQuestion === 0;

  // Disable Next and Last on the last question.
  document.getElementById("nextBtn").disabled =
    currentQuestion === questions.length - 1;
  document.getElementById("lastBtn").disabled =
    currentQuestion === questions.length - 1;
}

// Show the results on the page.
function showResults(score, percentage, message, correction) {
  // Hide the quiz and show the results.
  document.getElementById("quizPanel").style.display = "none";
  document.getElementById("resultsPanel").style.display = "block";

  // Fill the result elements with text.
  document.getElementById("scoreText").textContent =
    `Score: ${score} / ${questions.length}`;
  document.getElementById("percentageText").textContent =
    `Percentage: ${percentage}%`;
  document.getElementById("performanceText").textContent = message;
  document.getElementById("correction").textContent = correction;
}

// Show the first question when the page opens.
renderQuestion();