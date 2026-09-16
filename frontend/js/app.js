"use strict";


/* =========================
   DOM Elements
   ========================= */

const uploadForm = document.getElementById("upload-form");
const reportFileInput = document.getElementById("report-file");
const fileNameElement = document.getElementById("file-name");
const uploadStatus = document.getElementById("upload-status");
const uploadButton = document.getElementById("upload-button");


/* =========================
   File Selection
   ========================= */

reportFileInput.addEventListener("change", () => {
    const file = reportFileInput.files[0];

    if (!file) {
        fileNameElement.textContent = "No file selected";
        return;
    }

    fileNameElement.textContent = file.name;
});


/* =========================
   Upload Form
   ========================= */

uploadForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const file = reportFileInput.files[0];

    if (!file) {
        showStatus(
            "Please select a PDF report first.",
            "error"
        );

        return;
    }

    showStatus(
        `Selected file: ${file.name}`,
        "success"
    );
});


/* =========================
   Status Helper
   ========================= */

function showStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = `upload-status ${type}`;
}