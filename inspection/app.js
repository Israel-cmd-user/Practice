import { exportToPDF, exportToExcel } from './services/exportService.js';
import { getLocation } from './services/geolocationService.js';
import { populateCurrentDateTime, populateCurrentDate, autoGrow } from './utils/helpers.js';
import * as PhotoManager from './components/photoManager.js';
import { initMapPanel } from './components/mapManager.js';
import { initPhotoInventoryGrid } from './components/inventoryPhotos.js';

// Setup Initialization bindings
window.onload = populateCurrentDateTime;

document.addEventListener('DOMContentLoaded', () => {
    populateCurrentDate();
    initMapPanel();
    initPhotoInventoryGrid();

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