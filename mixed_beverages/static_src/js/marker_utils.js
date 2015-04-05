/* global URLS: false */
var $ = require('jquery');

var locationCache = {};
module.exports.showLocationPopup = function (marker) {
  if (marker._popup) {
    marker.openPopup();
    return;
  }
  var id = marker.feature.id;
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
      locationCache[id] = data;
      showPopup(data);
    });
  } else {
    showPopup(data);
  }
};
