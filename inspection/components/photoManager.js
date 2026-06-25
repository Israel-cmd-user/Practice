let rowPhotosState = {};
let activeRowId = null;

export function openPhotoManager(rowId) {
    activeRowId = rowId;
    document.getElementById('modal-item-id').textContent = rowId;
    
    if (!rowPhotosState[activeRowId]) {
        rowPhotosState[activeRowId] = [];
    }
    
    renderModalGallery();
    document.getElementById('photo-modal').style.display = 'flex';
}

export function closePhotoModal() {
    document.getElementById('photo-modal').style.display = 'none';
    activeRowId = null;
}

export function triggerCameraInput() {
    if (!activeRowId) return;
    const activeTargetInput = document.querySelector(`tr[data-row-id="${activeRowId}"] .photo-camera-input`);
    if (activeTargetInput) activeTargetInput.click();
}

export function triggerGalleryInput() {
    if (!activeRowId) return;
    const activeTargetInput = document.querySelector(`tr[data-row-id="${activeRowId}"] .photo-gallery-input`);
    if (activeTargetInput) activeTargetInput.click();
}

export function handleRowPhotoUpload(event, rowId) {
    const uploadedFiles = event.target.files;
    if (!uploadedFiles.length) return;

    if (!rowPhotosState[rowId]) rowPhotosState[rowId] = [];

    for (let i = 0; i < uploadedFiles.length; i++) {
        const file = uploadedFiles[i];
        const generatedUrl = URL.createObjectURL(file);
        
        rowPhotosState[rowId].push({
            id: 'img_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4),
            url: generatedUrl,
            file: file
        });
    }
    
    event.target.value = '';
    updateRowBadgeCounter(rowId);
    
    if (activeRowId === rowId) renderModalGallery();
}

function updateRowBadgeCounter(rowId) {
    const totalCount = rowPhotosState[rowId] ? rowPhotosState[rowId].length : 0;
    const targetBadge = document.querySelector(`tr[data-row-id="${rowId}"] .photo-counter`);
    
    if (targetBadge) {
        targetBadge.textContent = totalCount;
        if (totalCount > 0) {
            targetBadge.classList.add('has-photos');
        } else {
            targetBadge.classList.remove('has-photos');
        }
    }
}

function renderModalGallery() {
    const galleryContainer = document.getElementById('modal-gallery');
    galleryContainer.innerHTML = '';
    
    const currentAssets = rowPhotosState[activeRowId] || [];
    
    if (currentAssets.length === 0) {
        galleryContainer.innerHTML = `<div style="grid-column: 1/-1; text-align:center; color:#94a3b8; font-size:12px; padding:25px 10px;">
                                        No images attached. Tap "Upload / Capture" to interact.
                                      </div>`;
        return;
    }

    currentAssets.forEach(asset => {
        const wrapNode = document.createElement('div');
        wrapNode.className = 'thumb-wrapper';
        
        wrapNode.onclick = (e) => {
            if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'BUTTON') {
                viewSingleImageFullscreen(asset.url);
            }
        };

        wrapNode.innerHTML = `
            <input type="checkbox" class="thumb-checkbox" data-asset-id="${asset.id}" onclick="event.stopPropagation()">
            <img src="${asset.url}" alt="Attachment">
            <button type="button" class="thumb-delete-btn" onclick="event.stopPropagation(); window.deleteSingleAsset('${asset.id}')">&times;</button>
        `;
        galleryContainer.appendChild(wrapNode);
    });
}

export function viewSingleImageFullscreen(sourceUrl) {
    const viewerModal = document.getElementById('image-viewer-modal');
    const previewImageNode = document.getElementById('full-screen-image');
    previewImageNode.src = sourceUrl;
    viewerModal.style.display = 'flex';
}

export function closeImageViewer() {
    document.getElementById('image-viewer-modal').style.display = 'none';
}

export function deleteSingleAsset(assetId) {
    if (!rowPhotosState[activeRowId]) return;
    rowPhotosState[activeRowId] = rowPhotosState[activeRowId].filter(item => item.id !== assetId);
    updateRowBadgeCounter(activeRowId);
    renderModalGallery();
}

export function deleteSelectedPhotos() {
    if (!rowPhotosState[activeRowId] || rowPhotosState[activeRowId].length === 0) return;
    
    const activeCheckedBoxes = document.querySelectorAll('.thumb-checkbox:checked');
    const checkedIds = Array.from(activeCheckedBoxes).map(box => box.getAttribute('data-asset-id'));
    
    if (checkedIds.length === 0) {
        alert('Please check at least one checkbox on the thumbnails to perform bulk deletion.');
        return;
    }

    rowPhotosState[activeRowId] = rowPhotosState[activeRowId].filter(item => !checkedIds.includes(item.id));
    updateRowBadgeCounter(activeRowId);
    renderModalGallery();
}