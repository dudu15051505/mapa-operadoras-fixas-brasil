class mensagemErro extends Error {
	constructor(message) {
		super(message);
		this.name = "Erro";
	}
}

document.addEventListener('DOMContentLoaded', function() {
	const telaErroConteudoElement = document.getElementById('telaerro-conteudo');
	const telaErroElement = document.getElementById('telaerro');
   const map = L.map('map').setView([-14.235004, -51.925280], 5);
   
   const getJsonPath = (verOperadora, filename) => verOperadora ? `./js/locations/${verOperadora}/${filename}` : `./js/locations/tim/${filename}`;

	const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/" target="_blank">OpenStreetMap</a> contributors',
		maxZoom: 18,
	});

	const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
		attribution: 'Imagery &copy; <a href="https://www.arcgis.com/" target="_blank">ArcGIS</a>',
		maxZoom: 18,
	});

	const stamenTerrainLayer = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}{r}.png', {
		attribution: 'Map tiles by <a href="http://stamen.com" target="_blank">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0" target="_blank">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org" target="_blank">OpenStreetMap</a>, under <a href="http://creativecommons.org/licenses/by-sa/3.0" target="_blank">CC BY SA</a>',
		maxZoom: 18,
	});

	const esriWorldImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
		attribution: 'Tiles &copy; Esri &mdash; Source: Esri',
		maxZoom: 18
	});

	const cartoDBPositron = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
		attribution: '&copy; <a href="https://www.carto.com/" target="_blank">CartoDB</a> contributors'
	});

	const cartoDBVoyager = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png', {
		attribution: '&copy; <a href="https://www.carto.com/" target="_blank">CartoDB</a> contributors'
	});

	const cartoDBPositronNoLabels = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png', {
		attribution: '&copy; <a href="https://www.carto.com/" target="_blank">CartoDB</a> contributors'
	});

	const cartoDBVoyagerNoLabels = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}.png', {
		attribution: '&copy; <a href="https://www.carto.com/">CartoDB</a> contributors'
	});

	const cartoDBDarkMatterNoLabels = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}.png', {
		attribution: '&copy; <a href="https://www.carto.com/" target="_blank">CartoDB</a> contributors'
	});

	const esriWorldStreetMap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
		attribution: 'Tiles &copy; Esri &mdash; Source: Esri',
		maxZoom: 18
	});

	const esriWorldTopoMap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
		attribution: 'Tiles &copy; Esri &mdash; Source: Esri',
		maxZoom: 18
	});

	const baseLayers = {
		'OpenStreetMap': osmLayer,
		'Satélite': satelliteLayer,
		'Stamen Terrain': stamenTerrainLayer,
		"Esri World Imagery": esriWorldImagery,
		"CartoDB Positron": cartoDBPositron,
		"CartoDB Voyager": cartoDBVoyager,
		"CartoDB Positron (Sem rótulos)": cartoDBPositronNoLabels,
		"CartoDB Voyager (Sem rótulos)": cartoDBVoyagerNoLabels,
		"CartoDB Dark Matter (Sem rótulos)": cartoDBDarkMatterNoLabels,
		"Esri World Street Map": esriWorldStreetMap,
		"Esri World Topo Map": esriWorldTopoMap
	};

	const urls = [
		`./img/loading0.gif`,
		`./img/loading1.gif`,
		`./img/loading2.gif`
	];

	const locations = {};
	const overlayMaps = {};
	const locationLayers = {};

   for (const sigla of siglasUF) {
		locations[`locations-${sigla}pf`] = L.layerGroup();
		locations[`locations-${sigla}pj`] = L.layerGroup();
	 
		overlayMaps[`${sigla} - Pessoa Física <img height="20" width="15" src="./img/marker-icon-green.png"/>`] = locations[`locations-${sigla}pf`];
		overlayMaps[`${sigla} - Pessoa Jurídica <img height="20" width="15" src="./img/marker-icon-black.png"/>`] = locations[`locations-${sigla}pj`];
	 
		locationLayers[`${sigla}-PF`] = locations[`locations-${sigla}pf`];
		locationLayers[`${sigla}-PJ`] = locations[`locations-${sigla}pj`];
	}

	const primeiraLinha = verOperadora === "oi" || verOperadora === "pequenas" ? false : true;
	const carregarMarcacoesMapa = siglasUF.flatMap(sigla => [
		[primeiraLinha, `${sigla}-PF`, () => addMarkersAndLayers(getJsonPath(verOperadora, `locations-${sigla}-PF.json`), `${sigla}-PF`, 'green')],
  		[false, `${sigla}-PJ`, () => addMarkersAndLayers(getJsonPath(verOperadora, `locations-${sigla}-PJ.json`), `${sigla}-PJ`, 'black')]
	]);


	function deslocarMarcador(coordenada, maxOffset) {
		return parseFloat(coordenada) + (Math.random() * maxOffset - maxOffset / 2);
	}
	
	function ocultarTelaErro(status = 'none') {
		telaErroElement.style.display = status;
		ocultarTelaLoad();
	}
	
	function exibirErro(menssagem) {
		telaErroConteudoElement.innerHTML = menssagem;
		ocultarTelaErro('block');
	}

   function validarCampos() {
		const cep = document.getElementById('cep').value;
		const numero = document.getElementById('numero').value;

		ocultarTelaLoad();

		if (cep.length !== 8) {
			exibirErro('O campo CEP deve conter 8 números.');
			return false;
		}
		if (numero.length < 1 || numero.length > 9) {
			exibirErro('O campo Número deve conter de 1 a 9 números.');
			return false;
		}
		return true;
	}

	function Busca() {
		const buscaValor = document.getElementById('busca-valor').value;
		const url = 'https://nominatim.openstreetmap.org/search?format=json&q=' + buscaValor;

		fetch(url)
			.then(response => response.json())
			.then(data => {
				if (data.length > 0) {

					ocultarTelaErro();

					map.setView([parseFloat(data[0].lat), parseFloat(data[0].lon)], 10);
					L.marker([parseFloat(data[0].lat), parseFloat(data[0].lon)]).addTo(map);
				} else {
					console.error('Local não encontrado.');
					const urlPesquisaOpenStreetMap = `https://www.openstreetmap.org/search?query=${encodeURIComponent(buscaValor)}`;

					throw new mensagemErro(`Local não encontrado na base de geolocalização <a href="${urlPesquisaOpenStreetMap}#map=5/-13.240/-50.383" target="_blank">OpenStreetMap <img src="./img/osm_icon.svg" style="height: 20px;width: 20px;" /></a></b> <br><br>`);
				}
			})
			.catch(error => {
				exibirErro(error);
			});
	}

	async function loadDataList() {
		fetch('./js/locations/locations-data-lista.json')
			.then(response => {
				if (!response.ok) {
					throw new Error('Erro ao carregar lista de dados passados.');
				}
				return response.json();
				
			})
			.then(data => {
				const listaDataDadosElement = document.getElementById('lista-data-dados');
	
				data.forEach((value, index) => {
					const option = new Option(
						value.informacaoExtra ? `${value.operadora} - ${value.informacaoExtra}` : `${value.operadora}`,
						value.valorCampo);
					document.getElementById('lista-data-dados').appendChild(option);
	
				});
	
				if (verOperadora) {
					listaDataDadosElement.value = verOperadora;
				} else {
					const lastOption = listaDataDadosElement.options[0];
					lastOption.selected = true;
				}
	
				if (document.getElementById(`dados-info-${listaDataDadosElement.selectedIndex}`)) {
					const dadosInfoElement = document.getElementById(`dados-info-${listaDataDadosElement.selectedIndex}`);
					dadosInfoElement.style.display = 'block';
				}
	
			})
			.catch(error => {
				exibirErro(error);
			});
	}

	async function fetchJSON(url) {
		let resposta = [];

		try {
			const response = await fetch(url);
			if (!response.ok) {
				if (response.status === 404) {
					throw new Error('A URL não foi encontrada.');
			  } else {
					throw new Error('Erro ao carregar dados.');
			  }
		 }
		
			resposta.push(true, response.json());

			return resposta;
		} catch (error) {
			resposta.push(false, error);

			return resposta;
		}
	}

	async function addMarkersAndLayers(url, type, cor = 'blue') {
		try {
			const layerGroup = L.layerGroup();
         const response = await fetchJSON(url);

         if (response[0]) {
            const layerGroup = L.layerGroup();
				const response = await fetchJSON(url);

				if (response[0]) {
					const conteudo = await response[1];

					conteudo.forEach(function(dadosJson) {
						if(!(dadosJson.latitude == null) || !(dadosJson.longitude == null)) {
							const customIcon = L.icon({
								iconUrl: `./img/marker-icon-${cor}.png`,
								iconSize: [25, 41],
								iconAnchor: [12, 41],
								popupAnchor: [0, -41]
							});

							const marker = L.marker([
								verOperadora === 'pequenas' ? deslocarMarcador(dadosJson.latitude, 0.05) : deslocarMarcador(dadosJson.latitude, 0.005),
								verOperadora === 'pequenas' ? deslocarMarcador(dadosJson.longitude, 0.05) : deslocarMarcador(dadosJson.longitude, 0.005)
							], {
								icon: customIcon
							});

							markerTexto = `
							${dadosJson.cidade}, ${dadosJson.uf} <br> <br>
							${dadosJson.empresa} <br>
							Tipo de cliente: ${dadosJson["pf-ou-pj"]} <br>
							Tipo de produto: ${dadosJson["tipo-de-Produto"]} <br>
							Meio de acesso: ${dadosJson["meio-de-acesso"]} <br>
							Tecnologia: ${dadosJson.tecnologia} <br>
							`;

							marker.bindPopup(markerTexto);	
							marker.addTo(layerGroup);
						}
					});

					if (conteudo.length > 0) {
						if (type in locationLayers) {
							  locationLayers[type].addLayer(layerGroup);
						} else {
							throw new mensagemErro(`Tipo de localização desconhecido: ${type}`);
						}
					}
				}
			}
		} catch (error) {
			exibirErro(error);
		}
	}

	async function addLayerToMap(layerName) {
		const layer = locationLayers[layerName];
		if (layer) {
			layer.addTo(map);
		} else {
			exibirErro(`Camada não encontrada: ${layerName}`);
		}
	}

	L.control.layers(baseLayers, overlayMaps).addTo(map);

	loadDataList();

	carregarMarcacoesMapa.forEach(async (valor, index) => {
		try {
			const layers = await Promise.race([valor[2]()]);
			if (valor[0]) {
				addLayerToMap(valor[1]);
		  }
		} catch (error) {
			exibirErro(`Erro ao carregar dados: ${error}`);
		}
	});

   osmLayer.addTo(map);
   
	document.getElementById('busca').addEventListener('submit', function(event) {
		event.preventDefault();
		Busca();
	});
});