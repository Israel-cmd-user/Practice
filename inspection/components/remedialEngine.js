import { CONSTRUCTION_ELEMENTS } from './choices.js';

function getRatedItems() {
    const ratingBoxes = document.querySelectorAll('.rating-box');
    const ratedItemsMap = new Map(); // key: itemKey -> { label, positions: [] }

    ratingBoxes.forEach(box => {
        const inputs = box.querySelectorAll('input');
        if (inputs.length >= 3) {
            const rInput = inputs[2];
            if (rInput.value.trim() !== '') {
                const itemKey = box.dataset.itemKey;
                const itemLabel = box.dataset.itemLabel;
                const position = box.dataset.position;

                if (itemKey && itemLabel) {
                    if (!ratedItemsMap.has(itemKey)) {
                        ratedItemsMap.set(itemKey, { label: itemLabel, positions: [] });
                    }
                    if (position && position !== '-' && position !== '') {
                        ratedItemsMap.get(itemKey).positions.push(position);
                    }
                }
            }
        }
    });

    return Array.from(ratedItemsMap.entries()).map(([key, data]) => ({
        key,
        label: data.label,
        positions: data.positions
    }));
}

function updateRemedialTable() {
    const tbody = document.getElementById('remedial-table-tbody');
    if (!tbody) return;

    // Save current values before rebuilding
    const currentValues = new Map();
    const existingRows = tbody.querySelectorAll('tr');
    existingRows.forEach((row, index) => {
        const inputs = row.querySelectorAll('input, select');
        const rowData = {};
        inputs.forEach((input, i) => {
            rowData[i] = input.value;
        });
        currentValues.set(index, rowData);

        const fileInput = row.querySelector('.photo-file-input');
        if (fileInput && fileInput.files.length > 0) {
            currentValues.set(`files-${index}`, fileInput.files);
        }

        const counterSpan = row.querySelector('.photo-counter');
        if (counterSpan) {
            currentValues.set(`counter-${index}`, counterSpan.textContent);
        }
    });

    const ratedItems = getRatedItems();
    const rowCount = Math.max(10, ratedItems.length);
    let html = '';

    for (let i = 0; i < rowCount; i++) {
        const item = ratedItems[i];

        if (item) {
            // Build Inspection Item cell
            let inspectionItemHtml = '';
            if (item.positions.length <= 1) {
                const posSuffix = item.positions.length === 1 ? ` (${item.positions[0]})` : '';
                inspectionItemHtml = `${item.label}${posSuffix}`;
            } else {
                let options = item.positions.map(p => `<option value="${p}">${item.label} (${p})</option>`).join('');
                inspectionItemHtml = `<select style="width:100%; border:none; background:transparent;">${options}</select>`;
            }

            // Build Activity Description cell
            let activityOptionsHtml = '<option value=""></option>';
            const activities = CONSTRUCTION_ELEMENTS[item.key] || [];
            activities.forEach(act => {
                activityOptionsHtml += `<option value="${act.label}">${act.id} - ${act.label}</option>`;
            });
            let activityDescriptionHtml = `<select style="width:100%;">${activityOptionsHtml}</select>`;

            const photoCount = currentValues.get(`counter-${i}`) || '0';
            const photoClass = parseInt(photoCount) > 0 ? 'has-photos' : '';
            const btnStyle = parseInt(photoCount) > 0 ? 'border-color: #2563eb;' : '';

            html += `<tr data-row-id="${i + 1}">
                <td class="cell-center">${i + 1}</td>
                <td>${inspectionItemHtml}</td>
                <td><input type="text"></td>
                <td>${activityDescriptionHtml}</td>
                <td><input type="text"></td>
                <td><input type="text"></td>
                <td><input type="text"></td>
                <td><input type="text"></td>
                <td><input type="text"></td>
                <td class="photo-cell" style="text-align: center; vertical-align: middle; padding: 2px;">
                    <input type="file" id="br-rem-img-${i + 1}" accept="image/*" multiple class="photo-file-input" style="display: none;">
                    <button type="button" class="photo-manage-btn ${photoClass}" data-target="br-rem-img-${i + 1}" style="padding: 4px 8px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: #fff; ${btnStyle}">
                        <i class="fa-regular fa-image"></i> <span class="photo-counter ${photoClass}" id="counter-br-rem-img-${i + 1}">${photoCount}</span>
                    </button>
                </td>
            </tr>`;
        } else {
            // Empty row
            const photoCount = currentValues.get(`counter-${i}`) || '0';
            const photoClass = parseInt(photoCount) > 0 ? 'has-photos' : '';
            const btnStyle = parseInt(photoCount) > 0 ? 'border-color: #2563eb;' : '';

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
                    <button type="button" class="photo-manage-btn ${photoClass}" data-target="br-rem-img-${i + 1}" style="padding: 4px 8px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: #fff; ${btnStyle}">
                        <i class="fa-regular fa-image"></i> <span class="photo-counter ${photoClass}" id="counter-br-rem-img-${i + 1}">${photoCount}</span>
                    </button>
                </td>
            </tr>`;
        }
    }

    tbody.innerHTML = html;

    // Restore current values to prevent losing data while typing in R input
    const newRows = tbody.querySelectorAll('tr');
    newRows.forEach((row, index) => {
        const rowData = currentValues.get(index);
        if (rowData) {
            const inputs = row.querySelectorAll('input, select');
            inputs.forEach((input, i) => {
                // Do not override newly generated select fields if they correspond to dynamic dropdowns
                if (input.tagName === 'SELECT' && input.options.length > 0 && ratedItems[index]) {
                    if (input.querySelector(`option[value="${rowData[i]}"]`)) {
                        input.value = rowData[i];
                    }
                } else {
                    input.value = rowData[i];
                }
            });

            const fileInput = row.querySelector('.photo-file-input');
            const savedFiles = currentValues.get(`files-${index}`);
            if (fileInput && savedFiles) {
                fileInput.files = savedFiles;
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

    // Also listen for changes to spans (which generate new dynamic rows)
    const classSpansInput = document.getElementById("classification-spans");
    if (classSpansInput) {
        classSpansInput.addEventListener("input", () => {
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
