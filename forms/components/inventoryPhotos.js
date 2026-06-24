const photoViews = [
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

export function initPhotoInventoryGrid() {
    const container = document.getElementById('photo-inventory-grid');
    if (!container) return; // Guard clause in case a different HTML sheet is loaded

    let htmlContent = '';
    
    // Loop through array by steps of 2 to build paired layout table rows (<tr>)
    for (let i = 0; i < photoViews.length; i += 2) {
        const viewA = photoViews[i];
        const viewB = photoViews[i + 1];

        htmlContent += `
            <tr>
                <td>${viewA.label}</td>
                <td class="photo-cell">
                    <input type="file" id="p-img-${viewA.id}" class="photo-file-input" multiple>
                    <button type="button" class="photo-manage-btn" onclick="document.getElementById('p-img-${viewA.id}').click()">
                        <i class="fa-regular fa-image"></i><span class="photo-counter">0</span>
                    </button>
                </td>
                <td>${viewB.label}</td>
                <td class="photo-cell">
                    <input type="file" id="p-img-${viewB.id}" class="photo-file-input" multiple>
                    <button type="button" class="photo-manage-btn" onclick="document.getElementById('p-img-${viewB.id}').click()">
                        <i class="fa-regular fa-image"></i><span class="photo-counter">0</span>
                    </button>
                </td>
            </tr>
        `;
    }

    container.innerHTML = htmlContent;
}