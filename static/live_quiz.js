// Week 7: data comes from the API; answers and cached questions last until reload.
let total = 0;
const cache = {};
const pending = {};
let busy = false;
let retryAction = null;

async function getQuestion(index) {
  if (!Number.isInteger(index) || index < 0 || index >= total) throw new Error("Invalid index");
  if (cache[index]) return cache[index];
  // Share an in-flight request too, rather than sending duplicate requests.
  if (pending[index]) return pending[index];
  pending[index] = (async () => {
    const response = await fetch(`/api/question/${index}`);
    if (!response.ok) throw new Error("HTTP " + response.status);
    const q = await response.json();
    if (!q || q.index !== index || typeof q.question !== "string" ||
        !Array.isArray(q.choices) || q.choices.length < 2 ||
        !q.choices.every(choice => typeof choice === "string") ||
        !Number.isInteger(q.answer) || q.answer < 0 || q.answer >= q.choices.length ||
        typeof q.explanation !== "string") throw new Error("Invalid question data");
    cache[index] = q;
    return q;
  })();
  try {
    return await pending[index];
  } catch (error) {
    // Let rendering/submission show the appropriate user-facing error.
    throw error;
  } finally {
    delete pending[index];
  }
}

function setBusy(value, message = "Loading...") {
  busy = value;
  document.getElementById("loading").textContent = message;
  document.getElementById("loading").hidden = !value;
  document.getElementById("quizPanel").setAttribute("aria-busy", String(value));
  document.getElementById("firstBtn").disabled = value || !total || currentQuestion === 0;
  document.getElementById("previousBtn").disabled = value || !total || currentQuestion === 0;
  document.getElementById("nextBtn").disabled = value || !total || currentQuestion === total - 1;
  document.getElementById("lastBtn").disabled = value || !total || currentQuestion === total - 1;
  document.getElementById("submitBtn").disabled = value || !cache[currentQuestion];
  document.getElementById("retryBtn").disabled = value;
  document.querySelectorAll('#choices input').forEach(input => { input.disabled = value; });
}

function clearError() {
  document.getElementById("error").hidden = true;
  document.getElementById("retryBtn").hidden = true;
}

function showError(message) {
  document.getElementById("error").textContent = message;
  document.getElementById("error").hidden = false;
  document.getElementById("retryBtn").hidden = false;
}

function retryQuiz() {
  if (!busy && retryAction) return retryAction();
}

// Start at the first question.
let currentQuestion = 0;

// Store the user's answer for each question.
const userAnswers = [];

// Save the selected choice's index.
function saveAnswer(choiceIndex) {
  if (!busy) userAnswers[currentQuestion] = choiceIndex;
}

// Navigation is locked during requests; only a successful render changes the index.
function goNext() { return renderQuestion(currentQuestion + 1); }
function goPrevious() { return renderQuestion(currentQuestion - 1); }
function goFirst() { return renderQuestion(0); }
function goLast() { return renderQuestion(total - 1); }

// Count the correct answers.
async function calculateScore() {
  let score = 0;

  // Check every question.
  for (let i = 0; i < total; i++) {
    // Add one point if the answer is correct.
    if (userAnswers[i] === (await getQuestion(i)).answer) {
      score++;
    }
  }

  return score;
}

// Convert the score to a rounded percentage.
function calculatePercentage(score) {
  return Math.round((score / total) * 100);
}

// Choose a message based on the percentage.
function getPerformanceMessage(percentage) {
  if (percentage >= 80) return "Excellent";
  if (percentage >= 60) return "Good";
  if (percentage >= 50) return "Pass";
  return "Needs improvement";
}

// Prepare the correction text.
async function buildCorrection() {
  let correction = "";

  for (let i = 0; i < total; i++) {
    const q = (await getQuestion(i));

    // undefined means unanswered; 0 means the first choice.
    const selected = userAnswers[i] === undefined
      ? "Not answered"
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
async function submitQuiz() {
  if (busy || !total || !cache[currentQuestion]) return;
  retryAction = submitQuiz;
  setBusy(true, "Calculating your results...");
  clearError();
  try {
    const score = await calculateScore();
    const percentage = calculatePercentage(score);
    const correction = await buildCorrection();
    showResults(score, percentage, getPerformanceMessage(percentage), correction);
  } catch (error) {
    showError("We couldn't complete your results. Your answers are saved. Try again.");
  } finally {
    setBusy(false);
  }
}

// Display the current question and choices.
async function renderQuestion(index = currentQuestion) {
  if (busy || !Number.isInteger(index) || index < 0 || index >= total) return;
  retryAction = () => renderQuestion(index);
  setBusy(true);
  clearError();
  try {
    const q = await getQuestion(index);
    currentQuestion = index;

    // Display "Question 1 of 10", etc.
    document.getElementById("progress").textContent =
      `Question ${currentQuestion + 1} of ${total}`;

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

    document.getElementById("questionText").focus({preventScroll: true});
  } catch (error) {
    showError("We couldn't load that question. Your answers are saved. Try again.");
  } finally {
    setBusy(false);
  }
}

// Show the results on the page.
function showResults(score, percentage, message, correction) {
  // Hide the quiz and show the results.
  document.getElementById("quizPanel").style.display = "none";
  document.getElementById("resultsPanel").style.display = "block";

  // Fill the result elements with text.
  document.getElementById("scoreText").textContent =
    `Score: ${score} / ${total}`;
  document.getElementById("percentageText").textContent =
    `Percentage: ${percentage}%`;
  document.getElementById("performanceText").textContent = message;
  document.getElementById("correction").textContent = correction;
}

// Fetch the count before rendering any question.
async function init() {
  if (busy) return;
  retryAction = init;
  setBusy(true);
  clearError();
  try {
    const response = await fetch("/api/questions/count");
    if (!response.ok) throw new Error("HTTP " + response.status);
    const data = await response.json();
    if (!Number.isInteger(data.count) || data.count < 0) throw new Error("Invalid count");
    total = data.count;
    if (total === 0) {
      showError("No questions are available yet. Please try again later.");
    }
  } catch (error) {
    showError("We couldn't start the quiz. Please check your connection and try again.");
  } finally {
    setBusy(false);
  }
  if (total > 0) await renderQuestion();
}

init();