const sleep = ms => new Promise(res => setTimeout(res, ms));

async function extractAllAssetsComplete() {
    console.log(" Starting complete multi-page asset extraction...");
    console.log(" PDF Types included: IVS, IVPS, ISS, ISPS");
    
    let allImages = [];
    let allPDFs = [];
    let currentPage = 1;
    let keepLoading = true;
    const pageSize = 100; 
    
    // The list of all document type codes used by the server
    const pdfTypes = ["IVS", "IVPS", "ISS", "ISPS"];

    try {
        while (keepLoading) {
            console.log(` Fetching structure list page ${currentPage}...`);
            
            let structResponse = await fetch(`db/structlist?page=${currentPage}&size=${pageSize}`);
            if (!structResponse.ok) {
                throw new Error(`Failed to fetch page ${currentPage}. Session may have expired.`);
            }
            
            let structData = await structResponse.json();
            let records = structData.data || structData; 

            if (!records || records.length === 0) {
                console.log(" Reached the end of the database records.");
                keepLoading = false;
                break;
            }

            console.log(` Processing ${records.length} structures from page ${currentPage}...`);

            // Loop through the structures on the current page
            for (let i = 0; i < records.length; i++) {
                let id = records[i].structure_no;
                if (!id) continue;

                // Generate URLs for all 4 PDF document types for this structure
                pdfTypes.forEach(type => {
                    allPDFs.push(`https://strumanweb.co.za/nara/structurefile/${id}/${type}`);
                });

                // Safety pause to keep requests spaced out cleanly
                await sleep(400); 

                // Fetch the photo list payload for this structure
                try {
                    let photoResponse = await fetch(`db/photolist?id=${id}`);
                    if (photoResponse.ok) {
                        let photos = await photoResponse.json();
                        photos.forEach(photo => {
                            const filename = photo.name;
                            const folderId = filename.split('_')[0];
                            allImages.push(`https://strumanweb.co.za/nara/photo/${folderId}/${filename}`);
                        });
                    }
                } catch (photoErr) {
                    console.warn(` Skipped photos for structure ${id}`);
                }
            }

            currentPage++; 
            await sleep(500); // Pause briefly between database pages
        }

        console.log(" Complete Extraction Finished!");
        console.log(` Total Image URLs Generated: ${allImages.length}`);
        console.log(` Total PDF URLs Generated: ${allPDFs.length}`);
        
        displayResultsWindow(allImages, allPDFs);

    } catch (err) {
        console.error(" Critical Error running extraction:", err);
    }
}

// Generates the visual layout window overlay on your screen to copy links
function displayResultsWindow(images, pdfs) {
    let outputText = "=== ALL PDF LINKS ===\n" + pdfs.join("\n") + "\n\n=== ALL IMAGE LINKS ===\n" + images.join("\n");
    let el = document.createElement('textarea');
    el.value = outputText;
    el.style = "position:fixed;top:5%;left:10%;width:80%;height:85%;z-index:99999;padding:20px;background-color:#1e1e1e;color:#00ff00;font-family:monospace;font-size:14px;";
    let closeBtn = document.createElement('button');
    closeBtn.innerText = "Close Window";
    closeBtn.style = "position:fixed;top:1%;left:10%;z-index:100000;padding:8px 16px;cursor:pointer;font-weight:bold;";
    closeBtn.onclick = () => { el.remove(); closeBtn.remove(); };
    document.body.appendChild(el);
    document.body.appendChild(closeBtn);
}

// Run the script
extractAllAssetsComplete();