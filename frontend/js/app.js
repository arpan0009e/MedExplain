// =========================================================
// MedExplain frontend
// =========================================================

const API_BASE_URL =
    window.APP_CONFIG?.API_BASE_URL || "http://localhost:8000";


// =========================================================
// DOM elements
// =========================================================

const uploadForm = document.getElementById("upload-form");
const reportFile = document.getElementById("report-file");
const fileName = document.getElementById("file-name");
const uploadButton = document.getElementById("upload-button");
const uploadStatus = document.getElementById("upload-status");

const resultSection = document.getElementById("result-section");
const reportFilename = document.getElementById("report-filename");
const reportPageCount = document.getElementById("report-page-count");
const reportText = document.getElementById("report-text");

const questionSection = document.getElementById("question-section");
const questionForm = document.getElementById("question-form");
const questionInput = document.getElementById("question-input");
const explainButton = document.getElementById("explain-button");
const explanationStatus = document.getElementById("explanation-status");

const explanationResult = document.getElementById("explanation-result");
const explanationAnswer = document.getElementById("explanation-answer");

const sourcesSection = document.getElementById("sources-section");
const sourceList = document.getElementById("source-list");

let currentSources = [];


// =========================================================
// File selection
// =========================================================

reportFile?.addEventListener("change", () => {
    const file = reportFile.files?.[0];

    if (!file) {
        fileName.textContent = "";
        return;
    }

    fileName.textContent = file.name;
});


// =========================================================
// Upload report
// =========================================================

uploadForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    const file = reportFile.files?.[0];

    if (!file) {
        setStatus(uploadStatus, "Please choose a PDF report.", true);
        return;
    }

    if (file.type !== "application/pdf") {
        setStatus(uploadStatus, "Only PDF files are supported.", true);
        return;
    }

    const maxSize = 10 * 1024 * 1024;

    if (file.size > maxSize) {
        setStatus(uploadStatus, "The PDF must be smaller than 10 MB.", true);
        return;
    }

    setButtonLoading(uploadButton, true, "Uploading...");
    setStatus(uploadStatus, "Uploading your report...");

    hideElement(resultSection);
    hideElement(questionSection);
    hideElement(explanationResult);
    hideElement(sourcesSection);

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/v1/reports/upload`,
            {
                method: "POST",
                body: formData,
            }
        );

        const data = await parseResponse(response);

        reportFilename.textContent = data.filename || file.name;

        const pageCount = Number(data.page_count || 0);

        reportPageCount.textContent =
            `${pageCount} ${pageCount === 1 ? "page" : "pages"}`;

        reportText.textContent = data.text || "No report text was returned.";

        showElement(resultSection);
        showElement(questionSection);

        setStatus(
            uploadStatus,
            "Report uploaded successfully."
        );

        questionInput?.focus();

        resultSection.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });

    } catch (error) {
        console.error("Upload error:", error);

        setStatus(
            uploadStatus,
            error.message || "Unable to upload the report.",
            true
        );
    } finally {
        setButtonLoading(uploadButton, false, "Upload report");
    }
});


// =========================================================
// Ask question
// =========================================================

questionForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    const question = questionInput.value.trim();

    if (!question) {
        setStatus(
            explanationStatus,
            "Please enter a question.",
            true
        );
        return;
    }

    const reportId = await getCurrentReportId();

    if (!reportId) {
        setStatus(
            explanationStatus,
            "Please upload a report first.",
            true
        );
        return;
    }

    setButtonLoading(explainButton, true, "Explaining...");
    setStatus(
        explanationStatus,
        "Reading the report and preparing an explanation..."
    );

    hideElement(explanationResult);
    hideElement(sourcesSection);

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/v1/reports/${encodeURIComponent(reportId)}/explain`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    question,
                }),
            }
        );

        const data = await parseResponse(response);

        currentSources = normalizeSources(data.sources);

        renderExplanation(data.answer || "");
        renderSources(currentSources);

        showElement(explanationResult);

        if (currentSources.length > 0) {
            showElement(sourcesSection);
        }

        setStatus(
            explanationStatus,
            "Explanation ready."
        );

        explanationResult.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });

    } catch (error) {
        console.error("Explanation error:", error);

        setStatus(
            explanationStatus,
            error.message || "Unable to generate the explanation.",
            true
        );
    } finally {
        setButtonLoading(explainButton, false, "Explain");
    }
});


// =========================================================
// Store report ID
// =========================================================
//
// The upload response already gives us the report ID.
// We keep it in memory for the current page session.
//

let currentReportId = null;


// Capture report ID after upload.
//
// This listener runs after the main upload listener above.
uploadForm?.addEventListener("submit", async () => {
    // The actual ID is captured by the custom upload flow below.
});


// =========================================================
// Upload helper override
// =========================================================
//
// The upload handler above needs the returned report ID.
// We capture it through a small fetch wrapper.
//

const originalFetch = window.fetch;

window.fetch = async (...args) => {
    const response = await originalFetch(...args);

    try {
        const url = String(args[0]);

        if (
            url.includes("/api/v1/reports/upload") &&
            response.ok
        ) {
            const clonedResponse = response.clone();
            const data = await clonedResponse.json();

            if (data.report_id) {
                currentReportId = data.report_id;
            }
        }
    } catch (error) {
        console.debug("Could not capture report ID.", error);
    }

    return response;
};


// =========================================================
// Report ID
// =========================================================

async function getCurrentReportId() {
    return currentReportId;
}


// =========================================================
// API response helper
// =========================================================

async function parseResponse(response) {
    let data = null;

    try {
        data = await response.json();
    } catch {
        throw new Error(
            `Server returned an invalid response (${response.status}).`
        );
    }

    if (!response.ok) {
        const message =
            data?.detail ||
            data?.message ||
            `Request failed with status ${response.status}.`;

        throw new Error(message);
    }

    return data;
}


// =========================================================
// Status UI
// =========================================================

function setStatus(element, message, isError = false) {
    if (!element) {
        return;
    }

    element.textContent = message;

    element.classList.toggle("error", isError);
}


// =========================================================
// Button loading state
// =========================================================

function setButtonLoading(button, loading, text) {
    if (!button) {
        return;
    }

    button.disabled = loading;

    if (loading) {
        button.dataset.originalText = button.textContent;
        button.textContent = text;
    } else {
        button.textContent =
            button.dataset.originalText || text;
    }
}


// =========================================================
// Visibility helpers
// =========================================================

function showElement(element) {
    if (!element) {
        return;
    }

    element.hidden = false;
}


function hideElement(element) {
    if (!element) {
        return;
    }

    element.hidden = true;
}


// =========================================================
// Sources
// =========================================================

function normalizeSources(sources) {
    if (!Array.isArray(sources)) {
        return [];
    }

    return sources
        .map((source) => ({
            title: String(source?.title || "Medical reference"),
            source: String(source?.source || ""),
            source_url: String(source?.source_url || ""),
        }))
        .filter((source) => source.title || source.source_url);
}


function renderSources(sources) {
    if (!sourceList) {
        return;
    }

    sourceList.replaceChildren();

    sources.forEach((source, index) => {
        const listItem = document.createElement("li");

        listItem.id = `source-${index + 1}`;
        listItem.tabIndex = -1;

        const title = document.createElement("span");
        title.className = "source-title";
        title.textContent = source.title;

        listItem.appendChild(title);

        if (source.source) {
            const provider = document.createElement("span");
            provider.className = "source-provider";
            provider.textContent = source.source;

            listItem.appendChild(provider);
        }

        if (source.source_url) {
            const link = document.createElement("a");

            link.className = "source-url";
            link.href = source.source_url;
            link.target = "_blank";
            link.rel = "noopener noreferrer";
            link.textContent = "Open source";

            listItem.appendChild(link);
        }

        sourceList.appendChild(listItem);
    });
}


// =========================================================
// Explanation rendering
// =========================================================

function renderExplanation(answer) {
    if (!explanationAnswer) {
        return;
    }

    explanationAnswer.replaceChildren();

    const fragment = renderSafeMarkdown(answer);

    explanationAnswer.appendChild(fragment);
}


// =========================================================
// Safe Markdown renderer
// =========================================================

function renderSafeMarkdown(markdown) {
    const fragment = document.createDocumentFragment();

    if (!markdown) {
        return fragment;
    }

    const lines = String(markdown).split(/\r?\n/);

    let currentList = null;
    let currentListType = null;

    for (const line of lines) {
        const trimmed = line.trim();

        if (!trimmed) {
            currentList = null;
            currentListType = null;
            continue;
        }


        // ---------------------------------------------
        // Headings
        // ---------------------------------------------

        const headingMatch = trimmed.match(
            /^(#{1,3})\s+(.+)$/
        );

        if (headingMatch) {
            currentList = null;
            currentListType = null;

            const level = headingMatch[1].length;

            const heading = document.createElement(
                `h${level}`
            );

            appendInlineContent(
                heading,
                headingMatch[2]
            );

            fragment.appendChild(heading);

            continue;
        }


        // ---------------------------------------------
        // Bullet list
        // ---------------------------------------------

        const bulletMatch = trimmed.match(
            /^[-*]\s+(.+)$/
        );

        if (bulletMatch) {
            if (
                !currentList ||
                currentListType !== "ul"
            ) {
                currentList =
                    document.createElement("ul");

                currentListType = "ul";

                fragment.appendChild(currentList);
            }

            const listItem =
                document.createElement("li");

            appendInlineContent(
                listItem,
                bulletMatch[1]
            );

            currentList.appendChild(listItem);

            continue;
        }


        // ---------------------------------------------
        // Numbered list
        // ---------------------------------------------

        const numberedMatch = trimmed.match(
            /^\d+\.\s+(.+)$/
        );

        if (numberedMatch) {
            if (
                !currentList ||
                currentListType !== "ol"
            ) {
                currentList =
                    document.createElement("ol");

                currentListType = "ol";

                fragment.appendChild(currentList);
            }

            const listItem =
                document.createElement("li");

            appendInlineContent(
                listItem,
                numberedMatch[1]
            );

            currentList.appendChild(listItem);

            continue;
        }


        // ---------------------------------------------
        // Normal paragraph
        // ---------------------------------------------

        currentList = null;
        currentListType = null;

        const paragraph =
            document.createElement("p");

        appendInlineContent(
            paragraph,
            trimmed
        );

        fragment.appendChild(paragraph);
    }

    return fragment;
}


// =========================================================
// Inline formatting
// =========================================================

function appendInlineContent(element, text) {
    const citationPattern = /\[(\d+)\]/g;

    let lastIndex = 0;
    let match;

    while ((match = citationPattern.exec(text)) !== null) {

        const beforeCitation =
            text.slice(lastIndex, match.index);

        if (beforeCitation) {
            appendFormattedText(
                element,
                beforeCitation
            );
        }

        const citationNumber =
            Number(match[1]);

        if (
            citationNumber >= 1 &&
            citationNumber <= currentSources.length
        ) {
            const citation =
                createCitationLink(citationNumber);

            element.appendChild(citation);
        } else {
            element.appendChild(
                document.createTextNode(match[0])
            );
        }

        lastIndex =
            citationPattern.lastIndex;
    }

    const remainingText =
        text.slice(lastIndex);

    if (remainingText) {
        appendFormattedText(
            element,
            remainingText
        );
    }
}


// =========================================================
// Bold formatting
// =========================================================

function appendFormattedText(element, text) {
    const boldPattern = /\*\*(.+?)\*\*/g;

    let lastIndex = 0;
    let match;

    while ((match = boldPattern.exec(text)) !== null) {

        const before =
            text.slice(lastIndex, match.index);

        if (before) {
            element.appendChild(
                document.createTextNode(before)
            );
        }

        const strong =
            document.createElement("strong");

        strong.textContent = match[1];

        element.appendChild(strong);

        lastIndex =
            boldPattern.lastIndex;
    }

    const remaining =
        text.slice(lastIndex);

    if (remaining) {
        element.appendChild(
            document.createTextNode(remaining)
        );
    }
}


// =========================================================
// Citation link
// =========================================================

function createCitationLink(number) {
    const source = currentSources[number - 1];

    const link = document.createElement("a");

    link.className = "source-reference";

    link.textContent = `[${number}]`;

    link.setAttribute(
        "aria-label",
        `Open source ${number}`
    );

    if (source?.source_url) {
        link.href = source.source_url;

        link.target = "_blank";
        link.rel = "noopener noreferrer";
    } else {
        link.href = `#source-${number}`;

        link.addEventListener("click", (event) => {
            event.preventDefault();

            scrollToSource(number);
        });
    }

    return link;
}


// =========================================================
// Scroll to source
// =========================================================

function scrollToSource(number) {
    const sourceElement =
        document.getElementById(
            `source-${number}`
        );

    if (!sourceElement) {
        return;
    }

    sourceElement.scrollIntoView({
        behavior: "smooth",
        block: "center",
    });

    sourceElement.focus({
        preventScroll: true,
    });
}