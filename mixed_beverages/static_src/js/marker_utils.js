/* global URLS: false */
var $ = require('jquery');

var locationCache = {};
var thousands = require('./utils').thousands;


// Render data
//
// @returns DOMNode
var contentize = function (data) {
  console.log(data);
  var $container = $('<div class="location"/>');
  $container.append('<span>' + data.latest.name + '</span> ');
  $container.append('<a target="admin" title="fix marker location" ' +
    'class="location--ind q-' +
    data.feature.properties.coordinate_quality + '" '+
    'href="/admin/receipts/location/' + data.feature.id + '/">' +
    '&nbsp</a>');
  var $list = $('<dl class="dl-horizontal"/>').appendTo($container);
  $.each(data.receipts, function (idx, x) {
    $list.append('<dt>' + x.date.replace(/\-\d+$/, '') + '</dt>');
    $list.append('<dd>' + thousands(x.tax) + '</dd>');
  });
  return $container[0];
};


module.exports.showLocationPopup = function (marker) {
  if (marker._popup) {
    marker.openPopup();
    return;
  }
  var id = marker.feature.id;
  var showPopup = function (data) {
    if (!marker._map) {
      console.warn('Marker has not been rendered yet', marker);
      return;
    }
    marker.bindPopup(contentize(data)).openPopup();
  };

  var data = locationCache[id];
  if (!data) {
    $.getJSON(URLS.location + id + '/', function (data) {
      data.feature = marker.feature;
      locationCache[id] = data;
      showPopup(data);
    });
  } else {
    showPopup(data);
  }
};
