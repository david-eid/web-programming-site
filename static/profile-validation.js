// Find the form and review elements in the HTML.
const form = document.getElementById("profile-form");
const review = document.getElementById("profile-review");
const reviewValues = document.getElementById("review-values");

// Find the form's section navigation.
const sectionLinks = document.querySelector(".profile-sections");

// Each pair contains: the field's name and its review label.
const fields = [
    ["student_id", "Student ID"],
    ["fullname", "Full name"],
    ["email", "USEK email"],
    ["phone", "Mobile number"],
    ["birthdate", "Date of birth"],
    ["portfolio", "Portfolio / GitHub URL"],
    ["gin446", "GIN446 website URL"],
    ["major", "Engineering major"],
    ["gpa", "Current GPA / 100"],
    ["credits", "Credits completed / 148"],
    ["graduation_month", "Expected graduation month and year"],
    ["graduation", "Expected graduation"],
    ["internship_completed", "Internship completed"],
    ["skills", "Technical skills"],
    ["language", "Primary programming language"],
    ["software", "Engineering software used"],
    ["project_title", "Proposed project title"],
    ["project_area", "Preferred project area"],
    ["description", "Brief project description"],
    ["team_size", "Preferred team size"],
    ["project_color", "Project dashboard color"],
    ["meeting_date", "Preferred meeting date"],
    ["meeting_time", "Preferred meeting time"],
    ["confirmation", "I confirm that the information provided is accurate"],
    ["form_version", "Form version"]
];

// Return from the review to the form.
function editProfile() {
    // Hide the review using the CSS class.
    review.classList.add("is-hidden");

    // Show the form and its section links.
    form.classList.remove("is-hidden");
    sectionLinks.classList.remove("is-hidden");

    // Move keyboard focus to Student ID.
    document.getElementById("student_id").focus();
}

// Run when the user submits the form.
form.addEventListener("submit", function (event) {
    // Stop the form from sending immediately.
    event.preventDefault();

    // Show validation errors and stop if the form is invalid.
    if (!form.reportValidity()) {
        return;
    }

    // Collect the form's current values.
    const data = new FormData(form);

    // Clear any previous review.
    reviewValues.textContent = "";

    // Add each field to the review.
    fields.forEach(function (field) {
        // dt holds the label; dd holds the answer.
        const label = document.createElement("dt");
        const value = document.createElement("dd");

        // Use the readable label from the pair.
        label.textContent = field[1];

        // Get all values for this field, including multiple selections.
        const answers = data.getAll(field[0]);

        // Separate answers with commas, or show a fallback message.
        value.textContent = answers.join(", ") || "Not provided / none selected";

        // Add the label and answer to the review.
        reviewValues.appendChild(label);
        reviewValues.appendChild(value);
    });

    // Hide the form and section links.
    form.classList.add("is-hidden");
    sectionLinks.classList.add("is-hidden");

    // Show the review.
    review.classList.remove("is-hidden");

    // Move focus to the review heading.
    document.getElementById("review-heading").focus();
});

// Edit button: return to the form with its values preserved.
document.getElementById("edit-profile").addEventListener("click", editProfile);

// Confirm button: check again, then send the form.
document.getElementById("confirm-profile").addEventListener("click", function () {
    // If invalid, return to the form and show errors.
    if (!form.checkValidity()) {
        editProfile();
        form.reportValidity();
        return;
    }

    // Send to the form's action URL using its method.
    // submit() skips the submit event, so the review does not repeat.
    form.submit();
});