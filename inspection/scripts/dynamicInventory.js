document.addEventListener('DOMContentLoaded', () => {
    const spanInput = document.getElementById('inventory-spans');
    const cellInput = document.getElementById('inventory-cells');

    // Identify which input is present on this page
    const activeInput = spanInput || cellInput;
    if (!activeInput) return;

    // Attach listener
    activeInput.addEventListener('input', generateCheckboxes);

    // Initial generation
    generateCheckboxes();
});

function generateCheckboxes() {
    const spanInput = document.getElementById('inventory-spans');
    const cellInput = document.getElementById('inventory-cells');
    
    // Determine the count based on whichever input is available
    const activeInput = spanInput || cellInput;
    if (!activeInput) return;

    let count = parseInt(activeInput.value, 10);
    if (isNaN(count) || count < 0) count = 0;

    // We generate labels for "AS", "S1", "S2" ... up to count
    const labels = ["AS"];
    for (let i = 1; i <= count; i++) {
        labels.push(`S${i}`);
    }

    // Function to populate a container
    const populateContainer = (containerId, inputName) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Preserve currently checked items to not lose data while typing
        const checkedValues = new Set();
        container.querySelectorAll('input[type="checkbox"]:checked').forEach(cb => {
            checkedValues.add(cb.value);
        });

        // Build new HTML
        container.innerHTML = '';
        labels.forEach(val => {
            const div = document.createElement('div');
            
            const label = document.createElement('label');
            label.style.padding = '0 4px';
            label.style.fontSize = '10px';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.name = inputName;
            checkbox.value = val;
            checkbox.style.width = '13px';
            checkbox.style.height = '13px';
            
            // Restore checked state if it previously existed
            if (checkedValues.has(val)) {
                checkbox.checked = true;
            }

            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(` ${val}`));
            
            div.appendChild(label);
            container.appendChild(div);
        });
    };

    // Populate the corresponding containers if they exist
    populateContainer('min-clearance-checkboxes', 'pos_min_clearance');
    populateContainer('expansion-joint-checkboxes', 'expansion_joint_loc');
}
