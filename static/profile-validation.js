const form = document.getElementById("profile-form");
const review = document.getElementById("profile-review");
const reviewValues = document.getElementById("review-values");
const sectionLinks = document.querySelector(".profile-sections");
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

function editProfile() {
    review.classList.add("is-hidden");
    form.classList.remove("is-hidden");
    sectionLinks.classList.remove("is-hidden");
    document.getElementById("student_id").focus();
}

form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (!form.reportValidity()) {
        return;
    }
    const data = new FormData(form);
    reviewValues.textContent = "";
    fields.forEach(function (field) {
        const label = document.createElement("dt");
        const value = document.createElement("dd");
        label.textContent = field[1];
        const answers = data.getAll(field[0]);
        value.textContent = answers.join(", ") || "Not provided / none selected";
        reviewValues.appendChild(label);
        reviewValues.appendChild(value);
    });
    form.classList.add("is-hidden");
    sectionLinks.classList.add("is-hidden");
    review.classList.remove("is-hidden");
    document.getElementById("review-heading").focus();
});

document.getElementById("edit-profile").addEventListener("click", editProfile);

document.getElementById("confirm-profile").addEventListener("click", function () {
    if (!form.checkValidity()) {
        editProfile();
        form.reportValidity();
        return;
    }
    form.submit();
});
