"use strict";


/* =========================
   Configuration
   ========================= */

// const API_BASE_URL = "http://127.0.0.1:8000/api/v1";


/* =========================
   DOM Elements
   ========================= */

const uploadForm = document.getElementById("upload-form");
const reportFileInput = document.getElementById("report-file");
const fileNameElement = document.getElementById("file-name");
const uploadStatus = document.getElementById("upload-status");
const uploadButton = document.getElementById("upload-button");

const resultSection = document.getElementById("result-section");
const reportIdElement = document.getElementById("report-id");
const reportStatusElement = document.getElementById("report-status");


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

    clearStatus();
    hideResult();
});


/* =========================
   Upload Form
   ========================= */

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const file = reportFileInput.files[0];

    if (!file) {
        showStatus(
            "Please select a PDF report first.",
            "error"
        );

        return;
    }

    if (file.type !== "application/pdf") {
        showStatus(
            "Please select a PDF file.",
            "error"
        );

        return;
    }

    setLoadingState(true);
    clearStatus();
    hideResult();

    try {
        const response = await fetch(
            `${MEDEXPLAIN_CONFIG.API_BASE_URL}/reports`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    filename: file.name
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to create the report."
            );
        }

        showStatus(
            "Report created successfully.",
            "success"
        );

        showResult(data);

    } catch (error) {
        console.error("Upload error:", error);

        showStatus(
            "Unable to connect to the MedExplain API.",
            "error"
        );

    } finally {
        setLoadingState(false);
    }
});


/* =========================
   UI Helpers
   ========================= */

function showStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = `upload-status ${type}`;
}


function clearStatus() {
    uploadStatus.textContent = "";
    uploadStatus.className = "upload-status";
}


function showResult(data) {
    reportIdElement.textContent = data.report_id;
    reportStatusElement.textContent = data.status;

    resultSection.hidden = false;
}


function hideResult() {
    resultSection.hidden = true;
}


function setLoadingState(isLoading) {
    uploadButton.disabled = isLoading;

    if (isLoading) {
        uploadButton.textContent = "Creating Report...";
    } else {
        uploadButton.textContent = "Upload Report";
    }
}