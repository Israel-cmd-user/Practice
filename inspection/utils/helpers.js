export function populateCurrentDateTime() {
    const dateTimeInput = document.getElementById('inspection-datetime') || document.getElementById('date-time');

    if (!dateTimeInput) return; 

    const now = new Date();
    
    if (dateTimeInput.type === 'datetime-local') {
        const tzoffset = now.getTimezoneOffset() * 60000; 
        const localISOTime = (new Date(now - tzoffset)).toISOString().slice(0, 16);
        dateTimeInput.value = localISOTime;
    } else {
        // Fallback for standard text fields
        dateTimeInput.value = now.toLocaleString();
    }
}

export function populateCurrentDate() {                           
    const dateInput = document.getElementById('inspection-date') || document.getElementById('date');
    
    // CRITICAL GUARD CLAUSE: If this element is missing on the current HTML page, exit
    if (!dateInput) return;

    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    
    // Formats safely to standard YYYY-MM-DD format
    dateInput.value = `${year}-${month}-${day}`;
}

/**
 * Auto-resizes textareas dynamically based on content volume to prevent layout clamping.
 * @param {HTMLElement} element - The context textarea element passed via 'this'
 */
export function autoGrow(element) {
    if (!element) return;
    
    // Reset height pass to allow accurate shrink calculations on backspaces
    element.style.height = "auto"; 
    
    // Recalculate containment bounds to match layout scrolling constraints
    element.style.height = (element.scrollHeight) + "px";
}