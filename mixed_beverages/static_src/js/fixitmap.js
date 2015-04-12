/* global data */
import L from 'leaflet';

var map;
var original;
var corrected;


function _dragend(e) {
  window.zz = e;
  console.log(this, e)
  e.target.openPopup();
}

function addReferencePoint() {
  original = L.marker([data.lat, data.lng], {
  }).addTo(map)
    .bindPopup(data.data.name).openPopup();

  corrected = L.marker([data.lat, data.lng], {
    draggable: true
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
