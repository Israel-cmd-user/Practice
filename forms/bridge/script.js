        // Export DOM directly to Vector A4 Single Page Layout via explicit scaling constraint
        function exportToPDF() {
            const element = document.getElementById('inspection-report');
            const opt = {
                margin:       [0.2, 0.2, 0.2, 0.2], // Micro bounds padding
                filename:     'STRUMAN-Inspection-B0003-SinglePage.pdf',
                image:        { type: 'jpeg', quality: 1.0 },
                html2canvas:  { scale: 2, useCORS: true, logging: false },
                jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
            };
            html2pdf().set(opt).from(element).save();
        }

        // Parse runtime elements array dataset structure into workbook files
        function exportToExcel() {
            let dataRows = [
                ["STRUMAN Single Page Data Extract - Structure B0003"],
                ["Structure Number", "B0003", "Structure Name", "Omatako River", "Date", "02/02/2008"],
                [],
                ["Item", "Inspection Element Item", "Position", "Activity Recommendation", "Qty", "Unit", "Urgency", "MS", "Remarks", "Photo Ref"]
            ];
            
            document.querySelectorAll("#remedial-table tbody tr").forEach(row => {
                let columns = [row.cells[0].innerText];
                row.querySelectorAll("input").forEach(inp => columns.push(inp.value));
                dataRows.push(columns);
            });

            const worksheet = XLSX.utils.aoa_to_sheet(dataRows);
            const workbook = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(workbook, worksheet, "Inspection Summary");
            XLSX.writeFile(workbook, "STRUMAN-B0003-Report.xlsx");
        }

  
        function populateCurrentDateTime() {
            const now = new Date();

            // Zero-pad single digits (e.g., 5 becomes 05)
            const day = String(now.getDate()).padStart(2, '0');
            const month = String(now.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
            const year = now.getFullYear();

            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');

            // Assemble into DD/MM/YYYY HH:MM:SS format
            const formattedDateTime = `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;

            // Inject into the text input
            document.getElementById('printDate').value = formattedDateTime;
        }

        // Run the function immediately when the page loads
        window.onload = populateCurrentDateTime;

        function populateCurrentDate() {
        const now = new Date();

        // Extract components
        const year = now.getFullYear();
        // Months are 0-indexed, so add 1. Pad with a leading zero if needed.
        const month = String(now.getMonth() + 1).padStart(2, '0'); 
        const day = String(now.getDate()).padStart(2, '0');

        // Assemble into the mandatory HTML5 YYYY-MM-DD format
        const formattedDate = `${year}-${month}-${day}`;

        // Inject into the date input field
        document.getElementById('currentDateInput').value = formattedDate;
        }

        // Example usage: Run it when the page loads
        window.addEventListener('DOMContentLoaded', populateCurrentDate);

        function autoGrow(element) {
            element.style.height = "auto";
            element.style.height = element.scrollHeight + "px";
            
            // Show scrollbar only if text exceeds max height
            if (element.scrollHeight > element.clientHeight) {
                element.style.overflowY = "auto";
            } else {
                element.style.overflowY = "hidden";
            }
        }

        
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(showPosition, showError);
            } else {
                alert("Geolocation is not supported by this browser.");
        }
        }

        function showPosition(position) {
            document.getElementById("lat").value = position.coords.latitude;
            document.getElementById("lon").value = position.coords.longitude;
        }

        function showError(error) {
            switch(error.code) {
                case error.PERMISSION_DENIED:
                alert("User denied the request for Geolocation.");
                break;
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
        // Select both the matrix container and the remedial table dynamically
        const interactiveContainers = document.querySelectorAll('.matrix-container, #remedial-table');
        
        interactiveContainers.forEach(container => {
            container.addEventListener('click', (event) => {
                // Find the closest table cell that was clicked
                const cell = event.target.closest('td');
                if (!cell) return;

                // If the user already clicked a native interactive element, do nothing
                const interactiveTags = ['INPUT', 'SELECT', 'TEXTAREA'];
                if (interactiveTags.includes(event.target.tagName)) return;

                // Locate the first input, select, or textarea within the clicked cell
                const input = cell.querySelector('input, select, textarea');
                if (input) {
                    input.focus();
                    
                    // If the input already contains text, move the cursor safely to the end
                    if (input.type === 'text' && input.value) {
                        const currentVal = input.value;
                        input.value = '';
                        input.value = currentVal;
                    }
                }
            });
        });
    });

    // Storage dictionary mapping row index positions to their captured assets
let rowPhotosState = {};
let activeRowId = null;

document.addEventListener('DOMContentLoaded', () => {
    // 1. Existing Cell Autofocus Engine Integration
    const interactiveContainers = document.querySelectorAll('.matrix-container, #remedial-table');
    
    interactiveContainers.forEach(container => {
        container.addEventListener('click', (event) => {
            const cell = event.target.closest('td');
            if (!cell) return;

            // CRITICAL SAFETIES: Bypass focus interceptor if interacting inside photo cell elements
            if (cell.classList.contains('photo-cell') || event.target.closest('.photo-cell')) {
                return;
            }

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

/* Photo Management Systems Core Functions */
function openPhotoManager(rowId) {
    activeRowId = rowId;
    document.getElementById('modal-item-id').textContent = rowId;
    
    if (!rowPhotosState[activeRowId]) {
        rowPhotosState[activeRowId] = [];
    }
    
    renderModalGallery();
    document.getElementById('photo-modal').style.display = 'flex';
}

function closePhotoModal() {
    document.getElementById('photo-modal').style.display = 'none';
    activeRowId = null;
}

function triggerFileInput() {
    if (!activeRowId) return;
    const activeTargetInput = document.querySelector(`tr[data-row-id="${activeRowId}"] .photo-file-input`);
    if (activeTargetInput) activeTargetInput.click();
}

function handleRowPhotoUpload(event, rowId) {
    const uploadedFiles = event.target.files;
    if (!uploadedFiles.length) return;

    if (!rowPhotosState[rowId]) rowPhotosState[rowId] = [];

    // Loop through uploaded/captured items and map them to runtime local system pointers
    for (let i = 0; i < uploadedFiles.length; i++) {
        const file = uploadedFiles[i];
        const generatedUrl = URL.createObjectURL(file);
        
        rowPhotosState[rowId].push({
            id: 'img_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4),
            url: generatedUrl,
            file: file
        });
    }
    
    // Clear the field state so engineers can re-upload identical files if needed
    event.target.value = '';

    updateRowBadgeCounter(rowId);
    
    if (activeRowId === rowId) {
        renderModalGallery();
    }
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
        
        // Single view triggers on structural image clicks
        wrapNode.onclick = (e) => {
            if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'BUTTON') {
                viewSingleImageFullscreen(asset.url);
            }
        };

        wrapNode.innerHTML = `
            <input type="checkbox" class="thumb-checkbox" data-asset-id="${asset.id}" onclick="event.stopPropagation()">
            <img src="${asset.url}" alt="Attachment">
            <button type="button" class="thumb-delete-btn" onclick="event.stopPropagation(); deleteSingleAsset('${asset.id}')">&times;</button>
        `;
        galleryContainer.appendChild(wrapNode);
    });
}

    // Option A: View Single Image (Maximize mode)
    function viewSingleImageFullscreen(sourceUrl) {
        const viewerModal = document.getElementById('image-viewer-modal');
        const previewImageNode = document.getElementById('full-screen-image');
        previewImageNode.src = sourceUrl;
        viewerModal.style.display = 'flex';
    }

    function closeImageViewer() {
        document.getElementById('image-viewer-modal').style.display = 'none';
    }

    // Option B: Delete One Image
    function deleteSingleAsset(assetId) {
        if (!rowPhotosState[activeRowId]) return;
        rowPhotosState[activeRowId] = rowPhotosState[activeRowId].filter(item => item.id !== assetId);
        updateRowBadgeCounter(activeRowId);
        renderModalGallery();
    }

    // Option C: Delete Multiple Selected Images
    function deleteSelectedPhotos() {
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