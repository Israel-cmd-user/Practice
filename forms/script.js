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
