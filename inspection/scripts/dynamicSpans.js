function initDynamicSpans() {
    const classSpansInput = document.getElementById("classification-spans");
    const structSpansInput = document.getElementById("structure-spans");

    const pierItemsBody = document.getElementById("pier-items-body");
    const supportItemsBody = document.getElementById("support-items-body");
    const spanItemsBody = document.getElementById("span-items-body");

    function renderTables() {
        let spans = parseInt(classSpansInput.value, 10);
        if (isNaN(spans) || spans < 1) {
            spans = 1; // Minimum 1 span
        }
        
        // Update structure spans
        structSpansInput.value = spans;

        const piers = Math.max(0, spans - 1);

        renderPierItems(piers);
        renderSupportItems(spans);
        renderSpanItems(spans);
    }

    function createRatingBox(type = "text", itemKey = "", itemLabel = "", position = "") {
        return `<td><div class="rating-box" data-item-key="${itemKey}" data-item-label="${itemLabel}" data-position="${position}"><div><input type="${type}" placeholder="-"></div><div><input type="${type}" placeholder="-"></div><div><input type="${type}" placeholder="-"></div></div></td>`;
    }

    function renderPierItems(piers) {
        const items = [
            { id: 12, name: "Pier Protection Works", key: "PierProtectionWorks" },
            { id: 13, name: "Pier Foundations", key: "PierFoundations" },
            { id: 14, name: "Piers & Columns", key: "PiersColumns" }
        ];

        let html = "";
        
        if (piers === 0) {
            // Render 1 empty row with "-" for positions if 0 piers
            items.forEach(item => {
                html += `<tr>
                    <td>${item.id}. ${item.name}</td>
                    <td class="cell-center">-</td>${createRatingBox("text", item.key, `${item.id}. ${item.name}`, "-")}
                    <td class="cell-center"></td><td></td>
                </tr>`;
            });
        } else {
            const rows = Math.ceil(piers / 2);
            items.forEach(item => {
                for (let r = 0; r < rows; r++) {
                    html += `<tr>`;
                    if (r === 0) {
                        html += `<td rowspan="${rows}">${item.id}. ${item.name}</td>`;
                    }
                    
                    let p1Idx = r * 2 + 1;
                    let p2Idx = r * 2 + 2;
                    
                    if (p1Idx <= piers) {
                        html += `<td class="cell-center">P${p1Idx}</td>${createRatingBox("text", item.key, `${item.id}. ${item.name}`, `P${p1Idx}`)}`;
                    } else {
                        html += `<td class="cell-center"></td><td></td>`;
                    }
                    
                    if (p2Idx <= piers) {
                        html += `<td class="cell-center">P${p2Idx}</td>${createRatingBox("text", item.key, `${item.id}. ${item.name}`, `P${p2Idx}`)}`;
                    } else {
                        html += `<td class="cell-center"></td><td></td>`;
                    }
                    html += `</tr>`;
                }
            });
        }
        
        if (pierItemsBody) pierItemsBody.innerHTML = html;
    }

    function renderSupportItems(spans) {
        const items = [
            { id: 15, name: "Bearings", key: "Bearings" },
            { id: 16, name: "Support Drainage", key: "SupportedDrainage" },
            { id: 17, name: "Expansion Joints", key: "ExpansionJoints" }
        ];

        const piers = Math.max(0, spans - 1);
        let positions = ["A1", "A2"];
        for (let i = 1; i <= piers; i++) {
            positions.push(`P${i}`);
        }

        const rows = Math.ceil(positions.length / 2);
        let html = "";

        items.forEach(item => {
            for (let r = 0; r < rows; r++) {
                html += `<tr>`;
                if (r === 0) {
                    html += `<td rowspan="${rows}">${item.id}. ${item.name}</td>`;
                }
                
                let pos1 = positions[r * 2];
                let pos2 = positions[r * 2 + 1];
                
                if (pos1) {
                    html += `<td class="cell-center">${pos1}</td>${createRatingBox("text", item.key, `${item.id}. ${item.name}`, pos1)}`;
                } else {
                    html += `<td class="cell-center"></td><td></td>`;
                }
                
                if (pos2) {
                    html += `<td class="cell-center">${pos2}</td>${createRatingBox("text", item.key, `${item.id}. ${item.name}`, pos2)}`;
                } else {
                    html += `<td class="cell-center"></td><td></td>`;
                }
                html += `</tr>`;
            }
        });
        
        if (supportItemsBody) supportItemsBody.innerHTML = html;
    }

    function renderSpanItems(spans) {
        const items = [
            { id: 18, name: "Longitudinal Members", key: "LongitudinalMembers" },
            { id: 19, name: "Transverse Members", key: "TransverseMembers" },
            { id: 20, name: "Decks and Slabs", key: "DecksSlabs" }
        ];

        let positions = [];
        for (let i = 1; i <= spans; i++) {
            positions.push(`S${i}`);
        }

        const rows = Math.ceil(positions.length / 2);
        let html = "";

        items.forEach(item => {
            for (let r = 0; r < rows; r++) {
                html += `<tr>`;
                if (r === 0) {
                    html += `<td rowspan="${rows}">${item.id}. ${item.name}</td>`;
                }
                
                let pos1 = positions[r * 2];
                let pos2 = positions[r * 2 + 1];
                
                if (pos1) {
                    html += `<td class="cell-center">${pos1}</td>${createRatingBox("number", item.key, `${item.id}. ${item.name}`, pos1)}`;
                } else {
                    html += `<td class="cell-center"></td><td></td>`;
                }
                
                if (pos2) {
                    html += `<td class="cell-center">${pos2}</td>${createRatingBox("number", item.key, `${item.id}. ${item.name}`, pos2)}`;
                } else {
                    html += `<td class="cell-center"></td><td></td>`;
                }
                html += `</tr>`;
            }
        });
        
        if (spanItemsBody) spanItemsBody.innerHTML = html;
    }

    if (classSpansInput) {
        classSpansInput.addEventListener("input", renderTables);
    }
    
    // Initial render
    if (classSpansInput && structSpansInput && pierItemsBody && supportItemsBody && spanItemsBody) {
        renderTables();
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDynamicSpans);
} else {
    initDynamicSpans();
}
