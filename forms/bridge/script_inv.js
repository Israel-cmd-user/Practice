let structuralMapInstance = null; // Global instance tracker to avoid layout initialization clashes

document.getElementById('gps-capture-panel').addEventListener('click', function(event) {
    // Avoid interrupting direct keyboard coordinate overrides inside input blocks
    if (event.target.closest('.telemetry-fields')) return;

    const statusDisplay = document.getElementById('geo-status-indicator');
    const latitudeInput = document.getElementById('geo-lat');
    const longitudeInput = document.getElementById('geo-lon');
    const watermark = document.getElementById('map-watermark');

    if (!navigator.geolocation) {
        statusDisplay.textContent = "Status Error: Geolocation context missing.";
        statusDisplay.className = "telemetry-status error";
        return;
    }

    statusDisplay.textContent = "Status: Connecting to tracking hardware arrays...";
    statusDisplay.className = "telemetry-status";

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            // Formats coordinates safely to 6 decimal places for field engineering accuracy
            latitudeInput.value = lat.toFixed(6);
            longitudeInput.value = lon.toFixed(6);

            statusDisplay.textContent = `Status: Location synchronized successfully.`;
            statusDisplay.className = "telemetry-status success";
            
            // Hide watermark placeholder icon layer
            watermark.style.display = 'none';

            // Initialize map instance or fly seamlessly to updated coordinates if already open
            if (!structuralMapInstance) {
                structuralMapInstance = L.map('live-mini-map', {
                    zoomControl: false, // Turn off controls to preserve clean UI boundaries
                    attributionControl: false
                }).setView([lat, lon], 15);

                // Load high-density clean terrain tile layers
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(structuralMapInstance);

                // Apply a distinct structural pinpoint marker component
                L.marker([lat, lon]).addTo(structuralMapInstance);
            } else {
                structuralMapInstance.setView([lat, lon], 15);
                // Wipe existing layers and replace current marker context
                structuralMapInstance.eachLayer((layer) => {
                    if (layer instanceof L.Marker) structuralMapInstance.removeLayer(layer);
                });
                L.marker([lat, lon]).addTo(structuralMapInstance);
            }
            
            // Force rendering refresh pass to fix bounding box edge layout updates
            setTimeout(() => structuralMapInstance.invalidateSize(), 200);
        },
        (error) => {
            statusDisplay.className = "telemetry-status error";
            statusDisplay.textContent = `Status Error: Handshake failed (${error.message})`;
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
});