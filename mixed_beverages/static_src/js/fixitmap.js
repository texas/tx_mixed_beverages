/* global data */
import L from 'leaflet';

var map;
var original;
var corrected;


function _dragend(e) {
  var latlng = e.target.getLatLng();
  e.target.openPopup();
  document.getElementById('fixit-form-lat').value = latlng.lat;
  document.getElementById('fixit-form-lng').value = latlng.lng;
}


function addReferencePoint() {
  original = L.marker([data.lat, data.lng], {
    opacity: 0.5
  }).addTo(map)
    .bindPopup(`<div><div>${ data.data.name }</div><div class="address">${ data.address }</div></div>`).openPopup();

  corrected = L.marker([data.lat, data.lng], {
    draggable: true,
    zIndexOffset: 1
  })
    .on('dragend', _dragend)
    .bindPopup(document.getElementById('fixit-form'))
    .addTo(map);
}


export function render() {
  map = L.map('map').setView([data.lat, data.lng], 16);

  L.tileLayer('http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.jpg', {
    maxZoom: 18,
    attribution: `Map tiles by <a href="http://stamen.com">Stamen Design</a>,
                  under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>.
                  Data by <a href="http://openstreetmap.org">OpenStreetMap</a>,
                  under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.
                  <a href="/about/">About</a> this site.`
  }).addTo(map);
  addReferencePoint();
}
