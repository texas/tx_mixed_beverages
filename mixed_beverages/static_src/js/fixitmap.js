/* global data */
import L from 'leaflet';
import $ from 'jquery';
import {extractLatLng} from './utils';

var map;
var originalPoint;
var original;
var corrected;


function _dragend(e) {
  var latlng = e.target.getLatLng();
  e.target.openPopup();
  document.getElementById('fixit-form-lat').value = latlng.lat;
  document.getElementById('fixit-form-lng').value = latlng.lng;
}


function addReferencePoint() {
  original = L.marker(originalPoint, {
    opacity: 0.5
  }).addTo(map);

  var correctedPoint = data.id ? [data.lat, data.lng] : [data.to_lat, data.to_lng];
  corrected = L.marker(correctedPoint, {
    draggable: true,
    zIndexOffset: 1
  })
    .on('dragend', _dragend)
    .bindPopup(document.getElementById('fixit-form'))
    .addTo(map);
  if (!data.id) {
    corrected.openPopup();
  }
}


function _onKeyup(e) {
  if (e.which === 27) {
    this.value = '';
    return;
  }
  var data = extractLatLng(this.value);
  if (data && data.lat) {
    corrected.setLatLng([data.lat, data.lng]);
    _dragend({target: corrected});
  }
}


function _onAdd(map) {
  var lookup = data.data.name + ',' + data.address.replace('\n', ',');
  var $container = $(`<div class="nav leaflet-bar">
    <p class="help">Drag pin to set a new location for</p>
    <div>${ data.data.name }</div>
    <div class="address">
      <a href="https://www.google.com/maps/?q=${ lookup }" rel="noreferrer" target="_blank">${ data.address }</a>
    </div>
    <input placeholder="Paste blob here."/>
    </div>`);
  if (data.data.status) {
    $container.append(`<div class="status status-${ data.data.status }">${ data.data.status }</div>`);
  }
  $container.find('input').on('keyup', _onKeyup);
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
  originalPoint = data.id ? [data.lat, data.lng] : [data.fro_lat, data.fro_lng];
  map = L.map('map').setView(originalPoint, 16);

  L.tileLayer('http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.png', {
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
