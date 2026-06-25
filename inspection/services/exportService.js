export function exportToPDF() {
    const element = document.getElementById('inspection-report');
    const opt = {
        margin:       [0.2, 0.2, 0.2, 0.2],
        filename:     'STRUMAN-Inspection-B0003-SinglePage.pdf',
        image:        { type: 'jpeg', quality: 1.0 },
        html2canvas:  { scale: 2, useCORS: true, logging: false },
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
    html2pdf().set(opt).from(element).save();
}

export function exportToExcel() {
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