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

const questionForm = document.getElementById("question-form");
const questionInput = document.getElementById("question-input");
const explainButton = document.getElementById("explain-button");
const explanationStatus =
    document.getElementById("explanation-status");

const explanationResult =
    document.getElementById("explanation-result");
const explanationAnswer =
    document.getElementById("explanation-answer");
const sourceList =
    document.getElementById("source-list");


/* =========================
   Application State
   ========================= */

let currentReportId = null;


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

    clearUploadStatus();
    clearExplanation();
    hideResult();

    currentReportId = null;
});


/* =========================
   Upload Form
   ========================= */

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const file = reportFileInput.files[0];

    if (!file) {
        showUploadStatus(
            "Please select a PDF report first.",
            "error"
        );
        return;
    }

    if (file.type !== "application/pdf") {
        showUploadStatus(
            "Please select a PDF file.",
            "error"
        );
        return;
    }

    setUploadLoadingState(true);
    clearUploadStatus();
    clearExplanation();
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

        const data = await parseResponse(response);

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to upload the report."
            );
        }

        currentReportId = data.report_id;

        showUploadStatus(
            "Report uploaded successfully.",
            "success"
        );

        showResult(data);

    } catch (error) {
        console.error("Upload error:", error);

        currentReportId = null;

        showUploadStatus(
            error.message ||
                "Unable to connect to the MedExplain API.",
            "error"
        );

    } finally {
        setUploadLoadingState(false);
    }
});


/* =========================
   Question Form
   ========================= */

questionForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const question = questionInput.value.trim();

    if (!currentReportId) {
        showExplanationStatus(
            "Please upload a report before asking a question.",
            "error"
        );
        return;
    }

    if (!question) {
        showExplanationStatus(
            "Please enter a question.",
            "error"
        );
        return;
    }

    setExplanationLoadingState(true);
    clearExplanationStatus();
    hideExplanation();

    try {
        const response = await fetch(
            `${MEDEXPLAIN_CONFIG.API_BASE_URL}/reports/${encodeURIComponent(currentReportId)}/explain`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    question: question
                })
            }
        );

        const data = await parseResponse(response);

        if (!response.ok) {
            throw new Error(
                data.detail ||
                    "Unable to generate the explanation."
            );
        }

        showExplanation(data);

        showExplanationStatus(
            "Explanation generated successfully.",
            "success"
        );

    } catch (error) {
        console.error("Explanation error:", error);

        showExplanationStatus(
            error.message ||
                "Unable to generate the explanation.",
            "error"
        );

    } finally {
        setExplanationLoadingState(false);
    }
});


/* =========================
   API Response Helper
   ========================= */

async function parseResponse(response) {
    const contentType =
        response.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
        return await response.json();
    }

    const text = await response.text();

    return {
        detail: text || "Unexpected API response."
    };
}


/* =========================
   Upload UI Helpers
   ========================= */

function showUploadStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className =
        `upload-status ${type}`;
}

function clearUploadStatus() {
    uploadStatus.textContent = "";
    uploadStatus.className = "upload-status";
}

function showResult(data) {
    reportFilenameElement.textContent =
        data.filename;

    reportPageCountElement.textContent =
        data.page_count;

    reportTextElement.textContent =
        data.text;

    resultSection.hidden = false;
}

function hideResult() {
    resultSection.hidden = true;
}

function setUploadLoadingState(isLoading) {
    uploadButton.disabled = isLoading;

    if (isLoading) {
        uploadButton.textContent = "Uploading...";
    } else {
        uploadButton.textContent = "Upload Report";
    }
}


/* =========================
   Explanation UI Helpers
   ========================= */

function showExplanationStatus(message, type) {
    explanationStatus.textContent = message;
    explanationStatus.className =
        `explanation-status ${type}`;
}

function clearExplanationStatus() {
    explanationStatus.textContent = "";
    explanationStatus.className =
        "explanation-status";
}

function showExplanation(data) {
    explanationAnswer.replaceChildren();

    renderSafeMarkdown(
        data.answer || "",
        explanationAnswer
    );

    sourceList.replaceChildren();

    if (Array.isArray(data.sources)) {
        data.sources.forEach((source) => {
            const listItem =
                document.createElement("li");

            const title =
                document.createElement("strong");

            title.textContent =
                source.title || "Medical source";

            listItem.appendChild(title);

            if (source.source) {
                const sourceName =
                    document.createElement("span");

                sourceName.textContent =
                    ` — ${source.source}`;

                listItem.appendChild(sourceName);
            }

            if (source.source_url) {
                const link =
                    document.createElement("a");

                link.href = source.source_url;
                link.target = "_blank";
                link.rel =
                    "noopener noreferrer";

                link.textContent =
                    " View source";

                listItem.appendChild(link);
            }

            sourceList.appendChild(listItem);
        });
    }

    explanationResult.hidden = false;
}

function hideExplanation() {
    explanationResult.hidden = true;
}

function clearExplanation() {
    clearExplanationStatus();

    explanationAnswer.replaceChildren();
    sourceList.replaceChildren();

    hideExplanation();
}

function setExplanationLoadingState(isLoading) {
    explainButton.disabled = isLoading;

    if (isLoading) {
        explainButton.textContent =
            "Generating explanation...";
    } else {
        explainButton.textContent =
            "Explain";
    }
}


/* =========================
   Safe Markdown Rendering
   ========================= */

/*
 * The LLM returns simple Markdown such as:
 *
 * **Reported Value:** 13.5 g/dL
 *
 * - Hemoglobin carries oxygen.
 * - Reference ranges can vary.
 *
 * We intentionally support only a small subset of Markdown.
 *
 * We create DOM nodes with textContent instead of
 * inserting the model response as raw HTML.
 */

function renderSafeMarkdown(markdown, container) {
    const lines = markdown.replace(/\r\n/g, "\n").split("\n");

    let currentList = null;

    for (const line of lines) {
        const trimmedLine = line.trim();

        if (!trimmedLine) {
            currentList = null;
            continue;
        }

        /* =========================
           Bullet List
           ========================= */

        if (
            trimmedLine.startsWith("- ") ||
            trimmedLine.startsWith("* ")
        ) {
            if (!currentList) {
                currentList =
                    document.createElement("ul");

                currentList.className =
                    "explanation-list";

                container.appendChild(currentList);
            }

            const listItem =
                document.createElement("li");

            appendSafeInlineMarkdown(
                trimmedLine.slice(2),
                listItem
            );

            currentList.appendChild(listItem);

            continue;
        }

        currentList = null;

        /* =========================
           Headings
           ========================= */

        if (trimmedLine.startsWith("### ")) {
            const heading =
                document.createElement("h4");

            appendSafeInlineMarkdown(
                trimmedLine.slice(4),
                heading
            );

            container.appendChild(heading);

            continue;
        }

        if (trimmedLine.startsWith("## ")) {
            const heading =
                document.createElement("h3");

            appendSafeInlineMarkdown(
                trimmedLine.slice(3),
                heading
            );

            container.appendChild(heading);

            continue;
        }

        if (trimmedLine.startsWith("# ")) {
            const heading =
                document.createElement("h3");

            appendSafeInlineMarkdown(
                trimmedLine.slice(2),
                heading
            );

            container.appendChild(heading);

            continue;
        }

        /* =========================
           Normal Paragraph
           ========================= */

        const paragraph =
            document.createElement("p");

        appendSafeInlineMarkdown(
            trimmedLine,
            paragraph
        );

        container.appendChild(paragraph);
    }
}


/*
 * Supports only:
 *
 * **bold text**
 *
 * Everything else is treated as plain text.
 */

function appendSafeInlineMarkdown(text, container) {
    const boldPattern = /\*\*(.*?)\*\*/g;

    let lastIndex = 0;
    let match;

    while ((match = boldPattern.exec(text)) !== null) {
        const normalText =
            text.slice(lastIndex, match.index);

        if (normalText) {
            container.appendChild(
                document.createTextNode(normalText)
            );
        }

        const bold =
            document.createElement("strong");

        bold.textContent = match[1];

        container.appendChild(bold);

        lastIndex =
            match.index + match[0].length;
    }

    const remainingText =
        text.slice(lastIndex);

    if (remainingText) {
        container.appendChild(
            document.createTextNode(remainingText)
        );
    }
}