var L = require('leaflet');


var map = L.map('map').setView([31.505, -98.09], 6);

L.tileLayer('http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.jpg', {
  maxZoom: 18,
  attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.'
}).addTo(map);
