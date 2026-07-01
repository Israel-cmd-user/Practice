import { CONSTRUCTION_ELEMENTS } from '../choices/bridgeChoices.js';
import { MAINTENANCE_TASKS } from '../choices/culvertChoices.js';

// Module-scoped state to track the number of activities per (itemKey, position)
// Key: "itemKey_position", Value: integer count (default 1)
const activityCounts = new Map();

// Map to store current values by unique row key to prevent data loss
// Key: "itemKey_position_activityIndex", Value: object of row data
const rowDataStore = new Map();

function getRatedItems() {
    const ratingBoxes = document.querySelectorAll('.rating-box');
    const ratedItems = [];

    ratingBoxes.forEach(box => {
        const inputs = box.querySelectorAll('input');
        if (inputs.length >= 3) {
            const rInput = inputs[2];
            const rValue = rInput.value.trim();
            if (rValue !== '') {
                const itemKey = box.dataset.itemKey;
                const itemLabel = box.dataset.itemLabel;
                const position = box.dataset.position;

                if (itemKey && itemLabel && position && position !== '-' && position !== '') {
                    ratedItems.push({
                        key: itemKey,
                        label: itemLabel,
                        position: position,
                        relevancy: rValue
                    });
                }
            }
        }
    });

    return ratedItems;
}

function updateRemedialTable() {
    const tbody = document.getElementById('remedial-table-tbody');
    // For culverts the table is culvert-remedial-tbody, so check both
    const activeTbody = tbody || document.getElementById('culvert-remedial-tbody');
    if (!activeTbody) return;

    // Save current values before rebuilding
    const existingRows = activeTbody.querySelectorAll('tr[data-unique-key]');
    existingRows.forEach(row => {
        const uniqueKey = row.getAttribute('data-unique-key');
        if (!uniqueKey) return;

        const inputs = row.querySelectorAll('input, select');
        const rowData = {};
        inputs.forEach((input, i) => {
            rowData[i] = input.value;
        });

        const fileInput = row.querySelector('.photo-file-input');
        if (fileInput && fileInput.files.length > 0) {
            rowData.files = fileInput.files;
        }

        const counterSpan = row.querySelector('.photo-counter');
        if (counterSpan) {
            rowData.photoCount = counterSpan.textContent;
        }

        rowDataStore.set(uniqueKey, rowData);
    });

    const ratedItems = getRatedItems();
    
    // Flatten rated items based on activity counts
    const tableRowsData = [];
    ratedItems.forEach(item => {
        const countKey = `${item.key}_${item.position}`;
        const count = activityCounts.get(countKey) || 1;
        
        for (let aIndex = 0; aIndex < count; aIndex++) {
            tableRowsData.push({
                ...item,
                activityIndex: aIndex,
                uniqueKey: `${item.key}_${item.position}_${aIndex}`,
                isFirstActivity: (aIndex === 0),
                totalActivities: count
            });
        }
    });

    const rowCount = Math.max(10, tableRowsData.length);
    let html = '';

    for (let i = 0; i < rowCount; i++) {
        const item = tableRowsData[i];

        if (item) {
            // Remove Relevancy score display from label
            const inspectionItemHtml = `${item.label}`;

            // Build Activity Description cell
            let activityOptionsHtml = '<option value=""></option>';
            const activities = CONSTRUCTION_ELEMENTS[item.key] || MAINTENANCE_TASKS[item.key] || [];
            activities.forEach(act => {
                activityOptionsHtml += `<option value="${act.label}">${act.id} - ${act.label}</option>`;
            });
            let activityDescriptionHtml = `<select style="width:100%; border: none; background: transparent; white-space: normal; word-wrap: break-word; font-size: 11px;">${activityOptionsHtml}</select>`;

            // Add (+) button only on the first activity row for an item
            let actionHtml = '';
            if (item.isFirstActivity) {
                actionHtml = `<button type="button" class="add-activity-btn" data-count-key="${item.key}_${item.position}" style="margin-left: 5px; cursor: pointer; background: #e0e7ff; border: 1px solid #c7d2fe; border-radius: 4px; color: #4338ca; font-weight: bold; width: 20px; height: 20px; padding: 0; display: inline-flex; align-items: center; justify-content: center;" title="Add another activity"><i class="fa-solid fa-plus" style="font-size: 10px;"></i></button>`;
            }

            const savedData = rowDataStore.get(item.uniqueKey) || {};
            const photoCount = savedData.photoCount || '0';
            const photoClass = parseInt(photoCount) > 0 ? 'has-photos' : '';
            const btnStyle = parseInt(photoCount) > 0 ? 'color: #2563eb;' : 'color: inherit;';

            html += `<tr data-row-id="${i + 1}" data-unique-key="${item.uniqueKey}">
                <td class="cell-center">${i + 1}</td>
                <td>${inspectionItemHtml}${actionHtml}</td>
                <td><input type="text" style="text-align: center;"></td>
                <td>${activityDescriptionHtml}</td>
                <td><input type="text"></td>
                <td><input type="text"></td>
                <td><input type="text"></td>
                <td><input type="text"></td>
                <td><input type="text"></td>
                <td class="photo-cell" style="text-align: center; vertical-align: middle; padding: 2px;">
                    <input type="file" id="br-rem-img-${i + 1}" accept="image/*" multiple class="photo-file-input" style="display: none;">
                    <button type="button" class="photo-manage-btn ${photoClass}" data-target="br-rem-img-${i + 1}" style="padding: 4px 8px; cursor: pointer; border: none; background: transparent; ${btnStyle}">
                        <i class="fa-regular fa-image"></i> <span class="photo-counter ${photoClass}" id="counter-br-rem-img-${i + 1}">${photoCount}</span>
                    </button>
                </td>
            </tr>`;
        } else {
            // Empty row for padding
            html += `<tr data-row-id="${i + 1}">
                <td class="cell-center">${i + 1}</td>
                <td></td>
                <td><input type="text"></td>
                <td><input type="text"></td>
                <td><input type="text"></td>
                <td><input type="text"></td>
                <td><input type="text"></td>
                <td><input type="text"></td>
                <td><input type="text"></td>
                <td class="photo-cell" style="text-align: center; vertical-align: middle; padding: 2px;">
                    <input type="file" id="br-rem-img-${i + 1}" accept="image/*" multiple class="photo-file-input" style="display: none;">
                    <button type="button" class="photo-manage-btn" data-target="br-rem-img-${i + 1}" style="padding: 4px 8px; cursor: pointer; border: none; background: transparent; color: inherit;">
                        <i class="fa-regular fa-image"></i> <span class="photo-counter" id="counter-br-rem-img-${i + 1}">0</span>
                    </button>
                </td>
            </tr>`;
        }
    }

    activeTbody.innerHTML = html;

    // Restore current values
    const newRows = activeTbody.querySelectorAll('tr[data-unique-key]');
    newRows.forEach(row => {
        const uniqueKey = row.getAttribute('data-unique-key');
        const savedData = rowDataStore.get(uniqueKey);
        
        if (savedData) {
            const inputs = row.querySelectorAll('input, select');
            inputs.forEach((input, i) => {
                // Restore value, position handles itself
                if (input.tagName === 'SELECT' && input.options.length > 0) {
                    if (input.querySelector(`option[value="${savedData[i]}"]`)) {
                        input.value = savedData[i];
                    }
                } else {
                    input.value = savedData[i] !== undefined ? savedData[i] : input.value;
                }
            });

            const fileInput = row.querySelector('.photo-file-input');
            if (fileInput && savedData.files) {
                fileInput.files = savedData.files;
            }
        }
    });
}

export function initRemedialEngine() {
    document.addEventListener('input', (e) => {
        // If the target is an input inside a rating-box, update the table
        if (e.target.closest('.rating-box')) {
            updateRemedialTable();
        }
    });

    document.addEventListener('click', (e) => {
        const addBtn = e.target.closest('.add-activity-btn');
        if (addBtn) {
            const countKey = addBtn.getAttribute('data-count-key');
            if (countKey) {
                const currentCount = activityCounts.get(countKey) || 1;
                activityCounts.set(countKey, currentCount + 1);
                updateRemedialTable();
            }
        }
    });

    // Listen for changes to spans
    const classSpansInput = document.getElementById("classification-spans");
    if (classSpansInput) {
        classSpansInput.addEventListener("input", () => {
            setTimeout(updateRemedialTable, 50);
        });
    }
    
    // Listen for changes to cells
    const classCellsInput = document.getElementById("classification-cells");
    if (classCellsInput) {
        classCellsInput.addEventListener("input", () => {
            setTimeout(updateRemedialTable, 50);
        });
    }

    // Initial render
    setTimeout(updateRemedialTable, 100);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRemedialEngine);
} else {
    initRemedialEngine();
}
