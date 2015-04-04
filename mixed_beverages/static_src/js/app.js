/* global URLS: false */
var L = require('leaflet');
require('leaflet.markercluster');
var $ = require('jquery');

// need to manually specify this
L.Icon.Default.imagePath = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.3/images';

var map = L.map('map').setView([31.505, -98.09], 8);

L.tileLayer('http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.jpg', {
  maxZoom: 18,
  attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.'
}).addTo(map);


var locationCache = {};
var showLocation = function (id, stuff) {
  var contentize = function (data) {
    var $container = $('<div/>');
    $container.append('<span>' + data.latest.name + '</span>');
    var $list = $('<dl class="dl-horizontal"/>').appendTo($container);
    $.each(data.receipts, function (idx, x) {
      $list.append('<dt>' + x.date.replace(/\-\d+$/, '') + '</dt>');
      $list.append('<dd>$' + x.tax + '</dd>');
    });
    return $container[0];
  };
  // var self = this;
  var showInfo = function (data) {
    // self.bindPopup('test ' + data.latest.name).openPopup();
    var popup = L.popup({offset: [0, -15]})
      .setLatLng(stuff.latlng)
      .setContent(contentize(data))
      .openOn(map);
  };

  var data = locationCache[id];
  if (!data) {
    $.getJSON(URLS.location + id + '/', function (data) {
      locationCache[id] = data;
      showInfo(data);
    });
  } else {
    showInfo(data);
  }
};


$.getJSON(URLS.geojson, function (data) {
  var markers = new L.MarkerClusterGroup({
    disableClusteringAtZoom: 15,
    maxClusterRadius: 50
  });
  L.geoJson(data).addTo(markers);
  markers.addTo(map);
  markers.on('click', function (a) {
    // a.layer.feature.properties
    // console.log('marker', a, this);
    showLocation.call(this, a.layer.feature.id, a);
  });
});
