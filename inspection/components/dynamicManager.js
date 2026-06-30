// Global state engine to preserve data across re-renders
const inspectionState = {
    piers: {},    // e.g., { "12-P1": { d: "", e: "", r: "" }, "13-P1": { ... } }
    supports: {}, // e.g., { "15-A1": { d: "", e: "", r: "" }, "16-A1": { ... } }
    spans: {}     // e.g., { "18-S1": { d: "", e: "", r: "" }, "19-S1": { ... } }
};

/**
 * Initializes listeners for dynamic bridge structural tables
 */
export function initDynamicStructureManager() {
    // Find the 'No of spans' input inside the Structure Information table
    const spanInput = document.querySelector('input[type="number"]');
    
    if (spanInput) {
        spanInput.addEventListener('input', (e) => {
            const numSpans = parseInt(e.target.value, 10) || 0;
            renderDynamicTables(numSpans);
        });

        // Trigger initial rendering pass if a value already exists on load
        if (spanInput.value) {
            renderDynamicTables(parseInt(spanInput.value, 10) || 0);
        }
    }
}

/**
 * Core table state rendering coordinator
 */
function renderDynamicTables(numSpans) {
    const numPiers = Math.max(0, numSpans - 1);
    const numSupports = numSpans > 0 ? numSpans + 1 : 0; // Abutments/Supports line total

    renderPiers(numPiers);
    renderSupports(numSupports);
    renderSpans(numSpans);
}

/**
 * Generates rating input templates pulling directly from local state memory
 */
function createRatingBoxHtml(category, storageKey) {
    const current = inspectionState[category][storageKey] || { d: "", e: "", r: "" };
    return `
        <div class="rating-box" data-category="${category}" data-key="${storageKey}">
            <div><input type="text" placeholder="- " class="rating-input" data-field="d" value="${current.d}" oninput="saveRating(this)"></div>
            <div><input type="text" placeholder="- " class="rating-input" data-field="e" value="${current.e}" oninput="saveRating(this)"></div>
            <div><input type="text" placeholder="- " class="rating-input" data-field="r" value="${current.r}" oninput="saveRating(this)"></div>
        </div>
    `;
}

// Render Piers (Items 12, 13, 14 separated)
function renderPiers(count) {
    const tbody = document.getElementById("piers-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (count === 0) {
        tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; color:gray; padding: 10px;">No piers (0 or 1 span structure)</td></tr>`;
        return;
    }

    const items = [
        "12. Pier Protection Works",
        "13. Pier Foundations",
        "14. Piers & Columns"
    ];

    let html = "";
    items.forEach(itemLabel => {
        for (let i = 1; i <= count; i++) {
            const pierId = `P${i}`;
            const storageKey = `${itemLabel.substring(0, 2)}-${pierId}`; // e.g., "12-P1"
            html += `
                <tr>
                    <td style="font-weight: bold; padding-left: 6px;">${itemLabel}</td>
                    <td class="cell-center" style="font-weight:bold;">${pierId}</td>
                    <td>${createRatingBoxHtml("piers", storageKey)}</td>
                </tr>
            `;
        }
    });
    tbody.innerHTML = html;
}

// Render Other Support Items (Items 15, 16, 17 separated)
function renderSupports(count) {
    const tbody = document.getElementById("support-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (count === 0) return;

    const items = [
        "15. Bearings",
        "16. Support Drainage",
        "17. Expansion Joints"
    ];

    let html = "";
    items.forEach(itemLabel => {
        for (let i = 1; i <= count; i++) {
            const supportId = `A${i}`;
            const storageKey = `${itemLabel.substring(0, 2)}-${supportId}`; // e.g., "15-A1"
            html += `
                <tr>
                    <td style="font-weight: bold; padding-left: 6px;">${itemLabel}</td>
                    <td class="cell-center" style="font-weight:bold;">${supportId}</td>
                    <td>${createRatingBoxHtml("supports", storageKey)}</td>
                </tr>
            `;
        }
    });
    tbody.innerHTML = html;
}

// Render Span Items (Items 18, 19, 20 separated)
function renderSpans(count) {
    const tbody = document.getElementById("spans-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (count === 0) return;

    const items = [
        "18. Longitudinal Members",
        "19. Transverse Members",
        "20. Decks and Slabs"
    ];

    let html = "";
    items.forEach(itemLabel => {
        for (let i = 1; i <= count; i++) {
            const spanId = `S${i}`;
            const storageKey = `${itemLabel.substring(0, 2)}-${spanId}`; // e.g., "18-S1"
            html += `
                <tr>
                    <td style="font-weight: bold; padding-left: 6px;">${itemLabel}</td>
                    <td class="cell-center" style="font-weight:bold;">${spanId}</td>
                    <td>${createRatingBoxHtml("spans", storageKey)}</td>
                </tr>
            `;
        }
    });
    tbody.innerHTML = html;
}

/**
 * Persists value updates live into execution context memory
 */
export function saveRating(inputElement) {
    const box = inputElement.closest(".rating-box");
    const category = box.dataset.category;
    const key = box.dataset.key;
    const field = inputElement.dataset.field;

    if (!inspectionState[category][key]) {
        inspectionState[category][key] = { d: "", e: "", r: "" };
    }

    inspectionState[category][key][field] = inputElement.value;
}