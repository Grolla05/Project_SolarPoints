// Variáveis globais para o mapa e as camadas
let map;
let markerClusterLayer;
let heatmapLayer;

// Função principal que inicia o mapa e as visualizações
function loadMap(locations) {
    if (map) {
        updateMapLayers(locations);
        return;
    }
    if (locations.length === 0) {
        document.getElementById('map').innerHTML = '<div class="flex items-center justify-center h-full text-slate-400"><p>Nenhum dado de localização para exibir.</p></div>';
        return;
    }
    const initialLocation = [locations[0].latitude, locations[0].longitude];
    map = L.map('map').setView(initialLocation, 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    updateMapLayers(locations);
    setupViewSwitcher();
}

// Atualiza as camadas com novos dados (útil para filtros)
function updateMapLayers(locations) {
    if (markerClusterLayer && map.hasLayer(markerClusterLayer)) {
        map.removeLayer(markerClusterLayer);
    }
    if (heatmapLayer && map.hasLayer(heatmapLayer)) {
        map.removeLayer(heatmapLayer);
    }
    markerClusterLayer = createMarkerClusterLayer(locations);
    heatmapLayer = createHeatmapLayer(locations);
    if (document.getElementById('view-heatmap-btn').classList.contains('active-view-btn')) {
        map.addLayer(heatmapLayer);
    } else {
        map.addLayer(markerClusterLayer);
    }
}

// Função para criar a camada de MARCADORES DINÂMICOS E AGRUPADOS
function createMarkerClusterLayer(locations) {
    const markers = L.markerClusterGroup();

    const createIcon = (color) => new L.Icon({
        iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
    });

    const blueIcon = createIcon('blue'),
          yellowIcon = createIcon('yellow'),
          redIcon = createIcon('red');

    locations.forEach(item => {
        if (!item.latitude || !item.longitude) return;

        let chosenIcon = blueIcon;
        const contador = item.contador || 0;

        if (contador >= 251 && contador <= 1000) {
            chosenIcon = yellowIcon;
        } else if (contador >= 1001) {
            chosenIcon = redIcon;
        }

        const marker = L.marker([item.latitude, item.longitude], { icon: chosenIcon });
        marker.bindPopup(`
            <div style="color: #333; font-family: sans-serif; line-height: 1.5;">
                <h3 style="margin: 0 0 5px 0; color: #1e293b; font-size: 16px;">Dispositivo ID: ${item.id}</h3>
                <p style="margin: 0;"><strong>Fluxo:</strong> ${contador}/dia</p>
                <p style="margin: 0; font-size: 12px; color: #64748b;"><strong>Coords:</strong> ${item.latitude}, ${item.longitude}</p>
            </div>`);
        markers.addLayer(marker);
    });
    return markers;
}

// Função para criar a camada de MAPA DE CALOR (HEATMAP)
function createHeatmapLayer(locations) {
    // Se não houver locais, retorna uma camada vazia para evitar erros.
    if (locations.length === 0) {
        return L.featureGroup([]);
    }

    // Transforma os dados para o formato [lat, lng, intensidade]
    const heatPoints = locations.map(item => [item.latitude, item.longitude, item.contador || 0]);

    // --- LÓGICA DINÂMICA ADICIONADA AQUI ---
    // 1. Encontra o maior valor de 'contador' no array de localizações.
    // O '...locations.map(...)' cria uma lista apenas com os valores do contador.
    // O 'Math.max(...)' encontra o maior número dessa lista.
    const maxContador = Math.max(...locations.map(item => item.contador || 0));

    // 2. Define o valor máximo para o heatmap.
    // Usamos o maior valor encontrado, ou 1 como padrão para evitar divisão por zero se todos os contadores forem 0.
    const dynamicMax = maxContador > 0 ? maxContador : 1;

    // 3. Usa a variável 'dynamicMax' na opção 'max' do heatmap.
    return L.heatLayer(heatPoints, {
        radius: 25,
        blur: 15,
        maxZoom: 18,
        max: dynamicMax
    });
}

// Adiciona os eventos de clique aos botões de troca de view
function setupViewSwitcher() {
    // ... (esta função permanece exatamente a mesma)
    const markersBtn = document.getElementById('view-markers-btn');
    const heatmapBtn = document.getElementById('view-heatmap-btn');

    markersBtn.addEventListener('click', () => {
        if (map.hasLayer(heatmapLayer)) map.removeLayer(heatmapLayer);
        if (!map.hasLayer(markerClusterLayer)) map.addLayer(markerClusterLayer);
        markersBtn.classList.add('active-view-btn');
        heatmapBtn.classList.remove('active-view-btn');
    });

    heatmapBtn.addEventListener('click', () => {
        if (map.hasLayer(markerClusterLayer)) map.removeLayer(markerClusterLayer);
        if (!map.hasLayer(heatmapLayer)) map.addLayer(heatmapLayer);
        heatmapBtn.classList.add('active-view-btn');
        markersBtn.classList.remove('active-view-btn');
    });
}