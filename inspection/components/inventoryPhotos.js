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
    { id: 1, label: "View 1: Structure inlet in evaluation", placeholder: "Show total number of cells" },
    { id: 2, label: "View 2: Structure from outlet in elevation", placeholder: "Show total number of cells and apron slabs" },
    { id: 3, label: "View 3: Structure from upper", placeholder: "In direction of increasing chainage" },
    { id: 4, label: "View 4: Structure from oppisite end of approach", placeholder: "In direction of decreasing chainage" },
    { id: 5, label: "View 5: View taken from the top of fill of feature crossed", placeholder: "Road or upstream river view" },
    { id: 6, label: "View 6: View taken from the top of fill of fature crossed", placeholder: "Road or downstream river view" },
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
                            <button type="button" class="photo-manage-btn" onclick="openBridgePhotoModal('bridge_photo_${viewA.id}')">
                                <i class="fa-regular fa-image"></i><span class="photo-counter" id="counter-bridge_photo_${viewA.id}">0</span>
                            </button>
                        </td>
                        ${viewB ? `
                        <td>${viewB.label}</td>
                        <td class="photo-cell">
                            <button type="button" class="photo-manage-btn" onclick="openBridgePhotoModal('bridge_photo_${viewB.id}')">
                                <i class="fa-regular fa-image"></i><span class="photo-counter" id="counter-bridge_photo_${viewB.id}">0</span>
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
 * Constructs a single-column detailed assessment table row structure
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
                <button type="button" class="photo-manage-btn" onclick="openPhotoModal('cul_photo_${view.id}')">
                    <i class="fa-regular fa-image"></i> Manage 
                    <span class="photo-counter" id="counter-cul_photo_${view.id}">0</span>
                </button>
            </td>
            <td width="40%">
                <input type="text" 
                       id="cul_photo_${view.id}_notes" 
                       name="cul_photo_${view.id}_notes" 
                       placeholder="${view.placeholder}">
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Binds live event listeners to Bridge file inputs to update counters dynamically
 */
function bindBridgeCounterListeners() {
    const inputs = document.querySelectorAll('.photo-file-input');
    
    inputs.forEach(input => {
        input.addEventListener('change', function() {
            const containerCell = this.closest('.photo-cell');
            const counterSpan = containerCell.querySelector('.photo-counter');
            const fileCount = this.files ? this.files.length : 0;
            
            if (counterSpan) {
                counterSpan.textContent = fileCount;
                
                const targetBtn = containerCell.querySelector('.photo-manage-btn');
                if (fileCount > 0) {
                    counterSpan.classList.add('has-photos');
                    if (targetBtn) targetBtn.style.borderColor = '#2563eb';
                } else {
                    counterSpan.classList.remove('has-photos');
                    if (targetBtn) targetBtn.style.borderColor = '';
                }
            }
        });
    });
}

/**
 * Global synchronization loop to read live memory state and update visual indicators
 */
export function updateAllPhotoCounters() {
    const culvertStorage = window.culvertImages || {}; 
    
    CULVERT_INVENTORY_VIEWS.forEach(view => {
        const counterId = `counter-cul_photo_${view.id}`;
        const counterEl = document.getElementById(counterId);
        if (counterEl) {
            const key = `cul_photo_${view.id}`;
            const count = (culvertStorage[key] && Array.isArray(culvertStorage[key])) ? culvertStorage[key].length : 0;
            counterEl.textContent = count;
            
            const parentBtn = counterEl.closest('.photo-manage-btn');
            if (count > 0) {
                counterEl.classList.add('has-photos');
                if (parentBtn) parentBtn.classList.add('has-photos');
            } else {
                counterEl.classList.remove('has-photos');
                if (parentBtn) parentBtn.classList.remove('has-photos');
            }
        }
    });
}

/**
 * Orchestrates Automatic UI Construction Sequence Based on DOM Detection
 */
function runPhotoInterfaceInitializers() {
    initPhotoInventoryGrid();
    renderCulvertPhotoInventoryTable();
    
    bindBridgeCounterListeners();

    if (typeof updateAllPhotoCounters === "function") {
        updateAllPhotoCounters();
    }
}

// Attach lifecycle loading orchestrator safely
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", runPhotoInterfaceInitializers);
} else {
    runPhotoInterfaceInitializers();
}