/* global URLS: false */
import L from 'leaflet';
import 'leaflet.markercluster';
import 'leaflet-hash';
import './ui/Control.GeoZoom';
import $ from 'jquery';
import _ from 'lodash';
import d3 from 'd3';
import Cookies from 'cookies-js';
window.d3 = d3;  // DEBUG

import { DECLUSTER_ZOOM } from './settings';
import { showLocationPopup } from './marker_utils';
import { taxColorScale } from './utils';
import Nav from './ui/Nav';
import Legend from './ui/Legend';


var map, nav;


var markerStyle = function (feature) {
  var style = {
    fillOpacity: 0.8,
    opacity: 0.9,
    radius: 7,
    weight: 1
  };
  var tax = parseInt(feature.properties.data.avg_tax, 10);  // actually a float, but we don't care about cents
  if (tax === 0) {
    style.color = taxColorScale(tax);
    style.radius = 4;
  } else {
    style.fillColor = taxColorScale(tax);
    style.color = d3.rgb(style.fillColor).darker(1);
  }
  return style;
};


var _getJSON = function (data) {
  var markers = new L.MarkerClusterGroup({
    disableClusteringAtZoom: DECLUSTER_ZOOM,
    maxClusterRadius: 50
  });
  L.geoJson(data, {
    pointToLayer: (feature, latlng) => L.circleMarker(latlng, markerStyle(feature))
  }).addTo(markers);
  nav.saveMarkers(markers);
  markers.addTo(map);
  markers.on('click', function (evt) {
    // console.log('marker', evt.layer, this);  // DEBUG
    showLocationPopup(evt.layer);
  });
  var updateNav = function () {
    var data = {
      value: 0,
      markers: []
    };
    var bounds = map.getBounds();
    markers.eachLayer(function (marker) {
      if (bounds.contains(marker.getLatLng())) {
        data.markers.push(marker);
        data.value += parseFloat(marker.feature.properties.data.avg_tax || 0);
      }
    });
    nav.showStatsFor(data);
  };
  updateNav();  // initial hit
  map.on('move', _.debounce(updateNav, 500));
};


function firstVisit () {
  L.popup().setLatLng(map.getCenter()).setContent(`<div>
    <h2>Welcome</h2>
    <p>

      This map helps explore mixed beverage gross receipts taxes collected by
      the <a href="http://www.window.state.tx.us/taxinfo/mixbev/"
      target="_blank">Texas
      Comptroller</a>. This is <em>separate</em> from the
      regular sales tax collected and does not apply to beer/wine/liquor sales
      (since they are not mixed drinks).

    </p>
    <p>
      For more information, see <a href="/about/">about this site</a>.
    </p>
    </div>`).openOn(map);
}


export function render() {
  // map = L.map('map').setView([31.505, -98.09], 8);
  map = L.map('map', {
    center: [30.2655, -97.7426],
    zoom: DECLUSTER_ZOOM,
    zoomControl: false
  });
  if (Cookies.enabled && !Cookies.get('returning')) {
    Cookies.set('returning', '1', {expires: 86400 * 30 * 3});
    firstVisit();
  }
  var legend = new Legend();
  nav = new Nav(map, showLocationPopup);
  map.addControl(new L.Control.GeoZoom());
  map.addControl(legend.render());
  map.addControl(nav.render());
  window.map = map;  // DEBUG
  new L.hash(map);

  L.tileLayer('http://tile.stamen.com/toner/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: `Map tiles by <a href="http://stamen.com">Stamen Design</a>,
                  under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>.
                  Data by <a href="http://openstreetmap.org">OpenStreetMap</a>,
                  under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.
                  <a href="/about/">About</a> this site.`
  }).addTo(map);

  $.getJSON(URLS.geojson, _getJSON);
}
