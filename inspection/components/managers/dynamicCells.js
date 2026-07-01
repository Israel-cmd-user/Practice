function initDynamicCells() {
    const classCellsInput = document.getElementById("classification-cells");
    const structCellsInput = document.getElementById("structure-cells");
    const specificPositionsBody = document.getElementById("specific-positions-body");

    function renderCells() {
        let cells = parseInt(classCellsInput.value, 10);
        if (isNaN(cells) || cells < 1) {
            cells = 1; // Minimum 1 cell
        }

        // Update structure cells
        if (structCellsInput) {
            structCellsInput.value = cells;
        }

        let html = "";
        for (let i = 1; i <= cells; i++) {
            html += `<tr data-row-id="${i}">
                <td>${i}</td>
                <td colspan="3">
                    <div class="rating-box" data-item-key="Walls" data-item-label="10. Walls" data-position="C${i}">
                        <div><input type="text"></div><div><input type="text"></div><div><input type="text"></div>
                    </div>
                </td>
                <td colspan="3">
                    <div class="rating-box" data-item-key="TopSlab" data-item-label="11. Top Slab" data-position="C${i}">
                        <div><input type="text"></div><div><input type="text"></div><div><input type="text"></div>
                    </div>
                </td>
                <td colspan="3">
                    <div class="rating-box" data-item-key="InvertSlab" data-item-label="12. Invert Slab" data-position="C${i}">
                        <div><input type="text"></div><div><input type="text"></div><div><input type="text"></div>
                    </div>
                </td>
                <td colspan="3">
                    <div class="rating-box" data-item-key="CellDeformation" data-item-label="13. Cell Deformation" data-position="C${i}">
                        <div><input type="text"></div><div><input type="text"></div><div><input type="text"></div>
                    </div>
                </td>
            </tr>`;
        }

        if (specificPositionsBody) {
            specificPositionsBody.innerHTML = html;
        }
    }

    if (classCellsInput) {
        classCellsInput.addEventListener("input", renderCells);
    }
    
    // Initial render
    if (classCellsInput && specificPositionsBody) {
        renderCells();
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDynamicCells);
} else {
    initDynamicCells();
}
