/* global data */
import L from 'leaflet';
import $ from 'jquery';

var map;
var original;
var corrected;
var ui = {};


function _dragend(e) {
  var latlng = e.target.getLatLng();
  e.target.openPopup();
  document.getElementById('fixit-form-lat').value = latlng.lat;
  document.getElementById('fixit-form-lng').value = latlng.lng;
}


function addReferencePoint() {
  original = L.marker([data.lat, data.lng], {
    opacity: 0.5
  }).addTo(map);

  corrected = L.marker([data.lat, data.lng], {
    draggable: true,
    zIndexOffset: 1
  })
    .on('dragend', _dragend)
    .bindPopup(document.getElementById('fixit-form'))
    .addTo(map);
}


function _onAdd(map) {
  var $container = $(`<div class="nav leaflet-bar">
    <p class="help">Drag pin to set a new location for</p>
    <div>${ data.data.name }</div>
    <div class="address">${ data.address }</div>
    <input placeholder="Paste blob here."/>
    </div>`);
  ui.input = $container.find('input');
  return $container[0];
}


function addNav() {
  var NavControl = L.Control.extend({
    position: 'topright',
    onAdd: _onAdd
  });
  var nav = new NavControl();
  nav.addTo(map);
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
  addNav();
}
