/* global URLS: false */
var L = require('leaflet');
require('leaflet.markercluster');
var $ = require('jquery');
var _ = require('lodash');
var d3 = require('d3');
var colorbrewer = require('colorbrewer');
window.d3 = d3;  // DEBUG
// window.colorbrewer = colorbrewer;

// need to manually specify this
L.Icon.Default.imagePath = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.3/images';
var DECLUSTER_ZOOM = 15;

var marker_utils = require('./marker_utils');
var showLocationPopup = marker_utils.showLocationPopup;  // TODO splat
var utils = require('./utils');
var thousands = utils.thousands;  // TODO splat

var zoomToMarker = function (marker) {
  map.panTo(marker.getLatLng()).setZoom(DECLUSTER_ZOOM);
};

var taxColorScale = d3.scale.linear()
  .clamp(true)
  .domain([10000, 5000, 1000, 0])
  .range(colorbrewer.Spectral[4]);

var Legend = L.Control.extend({
  options: {
    position: 'bottomleft'
  },
  onAdd: function (map) {
    var $container = $('<div class="legend leaflet-bar"/>');
    var $list = $('<dl>').appendTo($container);
    $.each(taxColorScale.domain(), function (idx, level) {
      $list.append('<dt><span style="background: ' + taxColorScale(level) + ';">&nbsp;</span></dt>');
      $list.append('<dd>' + thousands(level) + '</dd>');
    });
    return $container[0];
  }
});


var Nav = L.Control.extend({
  options: {
    position: 'topright'
  },
  onAdd: function (map) {
    var $container = $('<div class="nav leaflet-bar status-loading"/>');
    $container.append('<div class="loading">Loading...</div>');
    $container.append('<div class="info">' +
      'Markers: <span class="markers"></span> ' +
      'Value: <span class="value"></span> ' +
      'Top: <ul class="top"></ul> ' +
      '</div>');
    this.ui = {
      markers: $container.find('span.markers'),
      value: $container.find('span.value'),
      top: $container.find('ul.top')
    };
    this.ui.top.on('click', 'li', function (evt) {
      var marker = $(this).data('marker');
      if (map.getZoom() < DECLUSTER_ZOOM) {
        zoomToMarker(marker);
        // FIXME user then has to click again because the marker does not exist yet
      }
      showLocationPopup(marker);
      evt.stopPropagation();  // keep click from closing the popup
    });
    map.nav = this;
    return $container[0];
  },
  // CUSTOM METHODS
  _loaded: function () {
    var $container = $(this.getContainer());
    $container.removeClass('status-loading').addClass('status-loaded');
  },
  showStatsFor: function (data) {
    var sorted = _.sortBy(data.markers, function (x) {
      return -parseFloat(x.feature.properties.data.avg_tax);
    });
    this.ui.top.empty();
    var $li;
    for (var i = 0; i < Math.min(sorted.length, 5); ++i) {
      $li = $('<li>' + thousands(sorted[i].feature.properties.data.avg_tax) + '</li>');
      $li.data('marker', sorted[i]);
      this.ui.top.append($li);
    }
    this.ui.markers.text(data.markers.length);
    this.ui.value.text(thousands(data.value));
  }
});

var markerStyle = function (feature) {
  var style = {
    fillOpacity: 0.8,
    opacity: 1,
    radius: 7,
    weight: 1
  };
  var tax = parseInt(feature.properties.data.avg_tax, 10);  // actually a float, but we don't care about cents
  if (isNaN(tax)) {
    style.color = "#000";
    style.dashArray = "5,5";  // TODO get this working
    style.radius = 5;
  } else if (tax === 0) {
    style.color = taxColorScale(tax);
    style.radius = 5;
  } else {
    style.color = taxColorScale(tax);
  }
  return style;
};
var pointToLayer = function (feature, latlng) {
  return L.circleMarker(latlng, markerStyle(feature));
};

var _getJSON = function (data) {
  map.nav._loaded();
  var markers = new L.MarkerClusterGroup({
    disableClusteringAtZoom: DECLUSTER_ZOOM,
    maxClusterRadius: 50
  });
  L.geoJson(data, {
    pointToLayer: pointToLayer
    // style: markerStyle
  }).addTo(markers);
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
    map.nav.showStatsFor(data);
  };
  updateNav();  // initial hit
  map.on('move', _.debounce(updateNav, 500));
};

// BEGIN

// var map = L.map('map').setView([31.505, -98.09], 8);
var map = L.map('map').setView([30.27045435, -97.7414384914151], DECLUSTER_ZOOM);  // DEBUG
map.addControl(new Legend());
map.addControl(new Nav());
window.map = map;  // DEBUG

L.tileLayer('http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.jpg', {
  maxZoom: 18,
  attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.'
}).addTo(map);


$.getJSON(URLS.geojson, _getJSON);
