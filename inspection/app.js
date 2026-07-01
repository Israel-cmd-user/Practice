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

const ChoicesMap = {
    'GlobChoices.INSPECTORS': GlobChoices.INSPECTORS,
    'BridgeChoices.SIZE_CATEGORY': BridgeChoices.SIZE_CATEGORY,
    'CulvertChoices.SIZE_CATEGORY_CUL': CulvertChoices.SIZE_CATEGORY_CUL,
    'BridgeChoices.BRIDGE_TYPE': BridgeChoices.BRIDGE_TYPE,
    'CulvertChoices.CULVERT_TYPE': CulvertChoices.CULVERT_TYPE,
    'GlobChoices.FEATURE_CROSSED': GlobChoices.FEATURE_CROSSED,
    'GlobChoices.STRUC_ORIENTATION': GlobChoices.STRUC_ORIENTATION,
    'GlobChoices.RIVER_FLOW_DIRECTION': GlobChoices.RIVER_FLOW_DIRECTION,
    'GlobChoices.ROAD_OVERUNDER': GlobChoices.ROAD_OVERUNDER,
    'GlobChoices.VERTICAL_ALIGNMNT': GlobChoices.VERTICAL_ALIGNMNT,
    'GlobChoices.HORIZONTAL_ALIGNMENT': GlobChoices.HORIZONTAL_ALIGNMENT,
    'GlobChoices.CAMBER_CROSSFALL': GlobChoices.CAMBER_CROSSFALL
};

function populateSelect(select, data) {
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

function populateDatalist(datalist, data) {
    if (!datalist) return;
    datalist.innerHTML = '';
    data.forEach(item => {
        const option = document.createElement('option');
        option.value = item.label;
        datalist.appendChild(option);
    });
}

function populateDropdowns() {
    document.querySelectorAll('[data-choices]').forEach(element => {
        const choiceKey = element.getAttribute('data-choices');
        const data = ChoicesMap[choiceKey];
        if (data) {
            if (element.tagName === 'SELECT') {
                populateSelect(element, data);
            } else if (element.tagName === 'DATALIST') {
                populateDatalist(element, data);
            }
        }
    });
}