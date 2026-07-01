import { exportToPDF, exportToExcel } from './services/exportService.js';
import { getLocation } from './services/geolocationService.js';
import { populateCurrentDateTime, populateCurrentDate, autoGrow } from './utils/helpers.js';
import * as PhotoManager from './components/managers/photoManager.js';
import { initMapPanel } from './components/managers/mapManager.js';
import { initPhotoInventoryGrid } from './components/managers/inventoryPhotos.js';
import * as GlobChoices from './components/choices/globChoices.js';
import * as BridgeChoices from './components/choices/bridgeChoices.js';
import * as CulvertChoices from './components/choices/culvertChoices.js';

// Setup Initialization bindings
window.onload = populateCurrentDateTime;

document.addEventListener('DOMContentLoaded', () => {
    populateCurrentDate();
    initMapPanel();
    initPhotoInventoryGrid();
    populateDropdowns();

    // Table Cell Autofocus Engine Integration
    const interactiveContainers = document.querySelectorAll('.matrix-container, #remedial-table');
    
    interactiveContainers.forEach(container => {
        container.addEventListener('click', (event) => {
            const cell = event.target.closest('td');
            if (!cell) return;

            if (cell.classList.contains('photo-cell') || event.target.closest('.photo-cell')) return;

            const interactiveTags = ['INPUT', 'SELECT', 'TEXTAREA', 'BUTTON'];
            if (interactiveTags.includes(event.target.tagName)) return;

            const input = cell.querySelector('input, select, textarea');
            if (input) {
                input.focus();
                if (input.type === 'text' && input.value) {
                    const currentVal = input.value;
                    input.value = '';
                    input.value = currentVal;
                }
            }
        });
    });
});

// --- CRITICAL ES6 SCOPE EXPOSURE ---
window.exportToPDF = exportToPDF;
window.exportToExcel = exportToExcel;
window.getLocation = getLocation;
window.autoGrow = autoGrow;


// Expose PhotoManager methods for inline HTML triggers
window.openPhotoManager = PhotoManager.openPhotoManager;
window.closePhotoModal = PhotoManager.closePhotoModal;
window.triggerCameraInput = PhotoManager.triggerCameraInput;
window.triggerGalleryInput = PhotoManager.triggerGalleryInput;
window.handleRowPhotoUpload = PhotoManager.handleRowPhotoUpload;
window.closeImageViewer = PhotoManager.closeImageViewer;
window.deleteSingleAsset = PhotoManager.deleteSingleAsset;
window.deleteSelectedPhotos = PhotoManager.deleteSelectedPhotos;

function populateSelect(selectId, data) {
    const select = document.getElementById(selectId);
    if (!select) return;
    
    // Check if we need to clear existing options (keep placeholder if any)
    const hasPlaceholder = select.querySelector('option[disabled][hidden]') !== null;
    if (!hasPlaceholder) {
        select.innerHTML = '<option value="" disabled selected hidden></option>';
    } else {
        select.innerHTML = select.firstElementChild.outerHTML; // Keep placeholder
    }
    
    data.forEach(item => {
        const option = document.createElement('option');
        option.value = item.label;
        option.textContent = item.label;
        select.appendChild(option);
    });
}

function populateDatalist(datalistId, data) {
    const datalist = document.getElementById(datalistId);
    if (!datalist) return;
    datalist.innerHTML = '';
    data.forEach(item => {
        const option = document.createElement('option');
        option.value = item.label;
        datalist.appendChild(option);
    });
}

function populateDropdowns() {
    populateDatalist('inspector-names', GlobChoices.INSPECTORS);
    populateSelect('size-category', BridgeChoices.SIZE_CATEGORY);
    populateSelect('size-category-cul', CulvertChoices.SIZE_CATEGORY_CUL);
    populateSelect('bridge-type', BridgeChoices.BRIDGE_TYPE);
    populateSelect('culvert-type', CulvertChoices.CULVERT_TYPE);
    populateSelect('feature-crossed', GlobChoices.FEATURE_CROSSED);
    populateSelect('bridge-orientation', GlobChoices.STRUC_ORIENTATION);
    populateSelect('culvert-orientation', GlobChoices.STRUC_ORIENTATION);
    populateSelect('river-flow-direction', GlobChoices.RIVER_FLOW_DIRECTION);
    populateSelect('road-over-under', GlobChoices.ROAD_OVERUNDER);
    populateSelect('vertical-alignment', GlobChoices.VERTICAL_ALIGNMNT);
    populateSelect('horizontal-alignment', GlobChoices.HORIZONTAL_ALIGNMENT);
    populateSelect('camber-crossfall', GlobChoices.CAMBER_CROSSFALL);
}