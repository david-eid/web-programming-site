// ======================================================
// QUESTIONS
// ======================================================
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
// Each question object should have the following structure:
//   {
//     question:
//       "Which keyword declares a block-scoped variable that can later be reassigned?",
//     choices: ["var", "let", "const", "static"],
//     answer: 1,
//     explanation:
//       "let declares a block-scoped variable whose value may later be reassigned.",
//   },

// ======================================================
// APPLICATION STATE
// ======================================================
let currentQuestion = 0;
const userAnswers = new Array(questions.length);

// ======================================================
// SAVE AN ANSWER
// ======================================================
function saveAnswer(choiceIndex) {
  userAnswers[currentQuestion] = choiceIndex;
}

// ======================================================
// NAVIGATION
// ======================================================
function goNext() {
  if (currentQuestion < questions.length - 1) {
    currentQuestion++;
    renderQuestion();
  }
}

function goPrevious() {
  if (currentQuestion > 0) {
    currentQuestion--;
    renderQuestion();
  }
}

function goFirst() {
  currentQuestion = 0;
  renderQuestion();
}
function goLast() {
  currentQuestion = questions.length - 1;
  renderQuestion();
}

// ======================================================
// CALCULATE SCORE
// ======================================================
function calculateScore() {
  let score = 0;
  for (let i = 0; i < questions.length; i++) {
    if (userAnswers[i] === questions[i].answer) {
      score++;
    }
  }
  return score;
}

// ======================================================
// CALCULATE PERCENTAGE
// ======================================================
function calculatePercentage(score) {
  return Math.round((score / questions.length) * 100);
}

// ======================================================
// PERFORMANCE MESSAGE
// ======================================================
function getPerformanceMessage(percentage) {
  if (percentage >= 80) return "Excellent";
  if (percentage >= 60) return "Good";
  if (percentage >= 50) return "Pass";
  return "Needs improvement";
}

// ======================================================
// BUILD CORRECTION
// ======================================================
function buildCorrection() {
  let correction = "";

  for (let i = 0; i < questions.length; i++) {
    const q = questions[i];
    // Index 0 is a valid answer; only undefined means unanswered.
    const selected = userAnswers[i] === undefined
      ? "Not answered"
      : q.choices[userAnswers[i]];
    const result = userAnswers[i] === q.answer ? "Correct" : "Incorrect";
    correction += `Question ${i + 1}: ${q.question}\n`;
    correction += `Your answer: ${selected}\n`;
    correction += `Correct answer: ${q.choices[q.answer]}\n`;
    correction += `Result: ${result}\n`;
    correction += `Explanation: ${q.explanation}\n\n`;
  }

  return correction;
}

// ======================================================
// PROVIDED INTERFACE CODE
//
// DOM manipulation and events will be studied later.
// ======================================================

// ======================================================
// SUBMIT QUIZ
// ======================================================
function submitQuiz() {
  const score = calculateScore();
  const percentage = calculatePercentage(score);
  const message = getPerformanceMessage(percentage);
  const correction = buildCorrection();
  showResults(score, percentage, message, correction);
}

function renderQuestion() {
  const q = questions[currentQuestion];

  // --------------------------------------------------
  // QUESTION NUMBER
  // --------------------------------------------------
  document.getElementById("progress").textContent =
    `Question ${currentQuestion + 1} of ${questions.length}`;

  // --------------------------------------------------
  // QUESTION
  // --------------------------------------------------
  document.getElementById("questionText").textContent = q.question;

  // --------------------------------------------------
  // CHOICES
  // --------------------------------------------------
  const choicesContainer = document.getElementById("choices");
  choicesContainer.innerHTML = "";
  for (let i = 0; i < q.choices.length; i++) {
    const label = document.createElement("label");
    label.className = "choice";
    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = "answer";
    radio.value = i;
    // Restore an answer previously selected
    // by the user.
    if (userAnswers[currentQuestion] === i) {
      radio.checked = true;
    }
    // When the user selects this answer,
    // save its index.
    radio.onclick = function () {
      saveAnswer(i);
    };
    label.appendChild(radio);
    label.appendChild(document.createTextNode(" " + q.choices[i]));
    choicesContainer.appendChild(label);
  }

  // --------------------------------------------------
  // NAVIGATION BUTTONS
  // --------------------------------------------------
  document.getElementById("firstBtn").disabled = currentQuestion === 0;
  document.getElementById("previousBtn").disabled = currentQuestion === 0;
  document.getElementById("nextBtn").disabled =
    currentQuestion === questions.length - 1;
  document.getElementById("lastBtn").disabled =
    currentQuestion === questions.length - 1;
}

// ======================================================
// DISPLAY RESULTS
// ======================================================
function showResults(score, percentage, message, correction) {
  document.getElementById("quizPanel").style.display = "none";
  document.getElementById("resultsPanel").style.display = "block";
  document.getElementById("scoreText").textContent =
    `Score: ${score} / ${questions.length}`;
  document.getElementById("percentageText").textContent =
    `Percentage: ${percentage}%`;
  document.getElementById("performanceText").textContent = message;
  document.getElementById("correction").textContent = correction;
}

// ======================================================
// START APPLICATION
// ======================================================
renderQuestion();
