/* global URLS: false */
var L = require('leaflet');
require('leaflet.markercluster');
var $ = require('jquery');

// need to manually specify this
L.Icon.Default.imagePath = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.3/images';

var map = L.map('map').setView([31.505, -98.09], 6);

L.tileLayer('http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.jpg', {
  maxZoom: 18,
  attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.'
}).addTo(map);

$.getJSON(URLS.geojson, function (data) {
  var markers = new L.MarkerClusterGroup({
    disableClusteringAtZoom: 15,
    maxClusterRadius: 50,
    polygonOptions: {
    }
  });
  L.geoJson(data).addTo(markers);
  markers.addTo(map);
});
