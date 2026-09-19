"use strict";

/* =========================
   DOM Elements
   ========================= */

const uploadForm = document.getElementById("upload-form");
const reportFileInput = document.getElementById("report-file");
const fileNameElement = document.getElementById("file-name");
const uploadStatus = document.getElementById("upload-status");
const uploadButton = document.getElementById("upload-button");

const resultSection = document.getElementById("result-section");
const reportFilenameElement =
    document.getElementById("report-filename");
const reportPageCountElement =
    document.getElementById("report-page-count");
const reportTextElement =
    document.getElementById("report-text");


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
        showStatus("Please select a PDF report first.", "error");
        return;
    }

    if (file.type !== "application/pdf") {
        showStatus("Please select a PDF file.", "error");
        return;
    }

    setLoadingState(true);
    clearStatus();
    hideResult();

    try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(
            `${MEDEXPLAIN_CONFIG.API_BASE_URL}/reports/upload`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to upload the report."
            );
        }

        showStatus("Report uploaded successfully.", "success");
        showResult(data);

    } catch (error) {
        console.error("Upload error:", error);

        showStatus(
            error.message || "Unable to connect to the MedExplain API.",
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
    reportFilenameElement.textContent = data.filename;
    reportPageCountElement.textContent = data.page_count;
    reportTextElement.textContent = data.text;

    resultSection.hidden = false;
}

function hideResult() {
    resultSection.hidden = true;
}

function setLoadingState(isLoading) {
    uploadButton.disabled = isLoading;

    if (isLoading) {
        uploadButton.textContent = "Uploading...";
    } else {
        uploadButton.textContent = "Upload Report";
    }
}
