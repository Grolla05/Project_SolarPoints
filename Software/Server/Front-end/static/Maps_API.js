function loadMap(locations) {

    // Verifica se há localizações para exibir
    if (locations.length === 0) {
        document.getElementById('map').innerText = 'Nenhum dado de localização disponível.';
        return;
    }

    // Define a localização do primeiro item como o centro do mapa
    const initialLocation = [locations[0].latitude, locations[0].longitude];

    // Cria o mapa e define a vista inicial
    const map = L.map('map').setView(initialLocation, 12);

    // Adiciona a camada de mapa do OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Loop através das localizações e adiciona um marcador para cada uma
    locations.forEach(item => {
        const marker = L.marker([item.latitude, item.longitude]).addTo(map);

        // Adiciona um popup (modal) com o conteúdo personalizado
        marker.bindPopup(`
            <div style="padding: 8px">
                <h3 style="margin-top: 0">Dispositivo ID: ${item.id}</h3>
                <p><strong>Fluxo de Pessoas:</strong> ${item.contador}/dia</p>
                <p><strong>Latitude:</strong> ${item.latitude}</p>
                <p><strong>Longitude:</strong> ${item.longitude}</p>
            </div>
        `);
    });
}