/**
 * Unified Asset Photo Engine
 * Handles rendering for Inventory components and direct inline file counter tracking
 * for Bridge Inventory, Culvert Inventory, Bridge Inspection, and Culvert Inspection.
 */

const BRIDGE_INVENTORY_VIEWS = [
    { id: 1, label: "View 1: Bridge in Elevation" },
    { id: 2, label: "View 2: Elevation from Opposite Side" },
    { id: 3, label: "View 3: Bridge from Upper Approach" },
    { id: 4, label: "View 4: Upper Approach Opposite End" },
    { id: 5, label: "View 5: Top View of Feature Crossed" },
    { id: 6, label: "View 6: Top View Feature Crossed Opp. End" },
    { id: 7, label: "View 7: Deck Edge Cantilever Soffit Profile" },
    { id: 8, label: "View 8: Opposite Deck Edge Profile" },
    { id: 9, label: "View 9: Underside of Main Deck Structure" },
    { id: 10, label: "View 10: Typical Pier Structural Element" },
    { id: 11, label: "View 11: Typical Abutment Configuration" },
    { id: 12, label: "View 12: Structure Number on Endblock" },
    { id: 13, label: "View 13: Secondary ID Markings / Tags" },
    { id: 14, label: "View 14: Typical Parapet Safety Elevation" },
    { id: 15, label: "View 15: Typical Roadway Expansion Joint" },
    { id: 16, label: "View 16: Other Notable Salient Feature" }
];

const CULVERT_INVENTORY_VIEWS = [
    { id: 1, label: "View 1: Structure inlet in elevation", placeholder: "Show total number of cells" },
    { id: 2, label: "View 2: Structure from outlet in elevation", placeholder: "Show total number of cells and apron slabs" },
    { id: 3, label: "View 3: Structure from upper approach", placeholder: "In direction of increasing chainage" },
    { id: 4, label: "View 4: Structure from opposite end of approach", placeholder: "In direction of decreasing chainage" },
    { id: 5, label: "View 5: View taken from the top of fill of feature crossed", placeholder: "Road or upstream river view" },
    { id: 6, label: "View 6: View taken from the top of fill of feature crossed", placeholder: "Road or downstream river view" },
    { id: 7, label: "View 7: View of inside of bridge barrel showing roof walls & floor", placeholder: "" },
    { id: 8, label: "View 8: Structure number", placeholder: "" },
    { id: 9, label: "View 9: Any other salient feature", placeholder: "" }
];

/**
 * Renders the Bridge Photo Inventory Component
 * Constructs a 2-column paired layout table structure
 */
export function initPhotoInventoryGrid() {
    const container = document.getElementById('photo-inventory-grid');
    if (!container) return; 

    let htmlContent = '';
    for (let i = 0; i < BRIDGE_INVENTORY_VIEWS.length; i += 2) {
        const viewA = BRIDGE_INVENTORY_VIEWS[i];
        const viewB = BRIDGE_INVENTORY_VIEWS[i + 1];

        htmlContent += `
            <tr>
                <td>${viewA.label}</td>
                <td class="photo-cell">
                    <input type="file" id="p-img-${viewA.id}" class="photo-file-input" multiple style="display: none;">
                    <button type="button" class="photo-manage-btn" data-target="p-img-${viewA.id}">
                        <i class="fa-regular fa-image"></i> <span class="photo-counter" id="counter-p-img-${viewA.id}">0</span>
                    </button>
                </td>
                ${viewB ? `
                <td>${viewB.label}</td>
                <td class="photo-cell">
                    <input type="file" id="p-img-${viewB.id}" class="photo-file-input" multiple style="display: none;">
                    <button type="button" class="photo-manage-btn" data-target="p-img-${viewB.id}">
                        <i class="fa-regular fa-image"></i> <span class="photo-counter" id="counter-p-img-${viewB.id}">0</span>
                    </button>
                </td>
                ` : `<td></td><td></td>`}
            </tr>
        `;
    }
    container.innerHTML = htmlContent;
}

/**
 * Renders the Culvert Photo Inventory Component
 * Upgraded to use direct inline upload matching the Bridge layout pattern
 */
export function renderCulvertPhotoInventoryTable() {
    const tableBody = document.getElementById("photo-inventory-tbody");
    if (!tableBody) return; 

    tableBody.innerHTML = ""; 
    CULVERT_INVENTORY_VIEWS.forEach(view => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td width="40%" style="font-weight: 500; padding: 6px 10px;">${view.label}</td>
            <td class="photo-cell" width="20%">
                <input type="file" id="cul-p-img-${view.id}" class="photo-file-input" multiple style="display: none;">
                <button type="button" class="photo-manage-btn" data-target="cul-p-img-${view.id}">
                    <i class="fa-regular fa-image"></i> 
                    <span class="photo-counter" id="counter-cul-p-img-${view.id}">0</span>
                </button>
            </td>
            <td width="40%">
                <input type="text" id="cul_photo_${view.id}_notes" name="cul_photo_${view.id}_notes" placeholder="${view.placeholder || ''}" disabled>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

/**
 * Robust Centralized Event Handler for ALL upload components
 * Manages every photo-cell container across forms dynamically via event delegation
 */
function bindGlobalPhotoInterfaceEvents() {
    // Intercepts any click event on a manage photo button across any form view
    document.body.addEventListener('click', (e) => {
        const btn = e.target.closest('.photo-manage-btn');
        if (btn && btn.dataset.target) {
            const inputEl = document.getElementById(btn.dataset.target);
            if (inputEl) inputEl.click();
        }
    });

    // Automatically monitors file picking adjustments across any input asset row
    document.body.addEventListener('change', (e) => {
        if (e.target && e.target.classList.contains('photo-file-input')) {
            const inputEl = e.target;
            const containerCell = inputEl.closest('.photo-cell');
            
            if (containerCell) {
                const counterEl = containerCell.querySelector('.photo-counter');
                const count = inputEl.files ? inputEl.files.length : 0;
                
                if (counterEl) {
                    counterEl.textContent = count;
                    const parentBtn = containerCell.querySelector('.photo-manage-btn');
                    
                    if (count > 0) {
                        counterEl.classList.add('has-photos');
                        if (parentBtn) {
                            parentBtn.classList.add('has-photos');
                            parentBtn.style.borderColor = '#2563eb';
                        }
                    } else {
                        counterEl.classList.remove('has-photos');
                        if (parentBtn) {
                            parentBtn.classList.remove('has-photos');
                            parentBtn.style.borderColor = '';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Renders the Remedial Work Matrix Rows securely
 * Eliminates legacy document.write architecture patterns
 */
export function renderRemedialWorkTable() {
    const tableBody = document.getElementById("remedial-table-tbody");
    if (!tableBody) return; // Guard clause 

    let htmlContent = '';
    
    // Generates the identical 10 rows matching your layout
    for (let i = 1; i <= 10; i++) {
        htmlContent += `
            <tr data-row-id="${i}">
                <td>${i}</td>
                <td><input type="text"></td>
                <td><input type="text" class="cell-center"></td>
                <td><input type="text"></td>
                <td><input type="text" class="cell-center"></td>
                <td><input type="text" class="cell-center"></td>
                <td><input type="text" class="cell-center"></td>
                <td><input type="text" class="cell-center"></td>
                <td><input type="text"></td>
                <td class="photo-cell" style="text-align: center; vertical-align: middle; padding: 2px;">
                    <input type="file" id="br-rem-img-${i}" accept="image/*" multiple class="photo-file-input" style="display: none;">
                    <button type="button" class="photo-manage-btn" data-target="br-rem-img-${i}" style="padding: 4px 8px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: #fff;">
                        <i class="fa-regular fa-image"></i> <span class="photo-counter" id="counter-br-rem-img-${i}">0</span>
                    </button>
                </td>
            </tr>
        `;
    }
    
    // Inject all content safely at once
    tableBody.innerHTML = htmlContent;
}

/**
 * Renders the Culvert Remedial Work Matrix Rows securely
 * Standardizes layout engines across various asset forms
 */
export function renderCulvertRemedialTable() {
    const tableBody = document.getElementById("culvert-remedial-tbody");
    if (!tableBody) return; // Silent safety exit if rendering a different form type

    let htmlContent = '';
    
    for (let i = 1; i <= 10; i++) {
        htmlContent += `
            <tr data-row-id="${i}">
                <td>${i}</td>
                <td><input type="text"></td>
                <td><input type="text" class="cell-center"></td>
                <td><input type="text"></td>
                <td><input type="text" class="cell-center"></td>
                <td><input type="text" class="cell-center"></td>
                <td><input type="text" class="cell-center"></td>
                <td><input type="text" class="cell-center"></td>
                <td><input type="text"></td>
                <td class="photo-cell" style="text-align: center; vertical-align: middle; padding: 2px;">
                    <input type="file" id="cul-rem-img-${i}" accept="image/*" multiple class="photo-file-input" style="display: none;">
                    <button type="button" class="photo-manage-btn" data-target="cul-rem-img-${i}" style="padding: 4px 8px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: #fff;">
                        <i class="fa-regular fa-image"></i> <span class="photo-counter" id="counter-cul-rem-img-${i}">0</span>
                    </button>
                </td>
            </tr>
        `;
    }
    
    tableBody.innerHTML = htmlContent;
}

/**
 * Orchestrates Layout Sequence and initialization
 */
function runPhotoInterfaceInitializers() {
    initPhotoInventoryGrid();
    renderCulvertPhotoInventoryTable();
    renderRemedialWorkTable();
    renderCulvertRemedialTable();
    bindGlobalPhotoInterfaceEvents();
    
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", runPhotoInterfaceInitializers);
} else {
    runPhotoInterfaceInitializers();
}

