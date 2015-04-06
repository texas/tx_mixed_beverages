/* global URLS: false */
var $ = require('jquery');

var locationCache = {};
var thousands = require('./utils').thousands;


var quality_descriptions = {
  'me': 'User Inputted',
  '00': 'AddressPoint',
  '01': 'GPS',
  '02': 'Parcel',
  '03': 'StreetSegmentInterpolation',
  '09': 'AddressZipCentroid',
  '10': 'POBoxZIPCentroid',
  '11': 'CityCentroid',
  '98': 'Unknown',
  '99': 'Unmatchable'
};

// Render data
//
// @returns DOMNode
var contentize = function (data) {
  var quality = data.feature.properties.coordinate_quality;
  var $container = $('<div class="location"/>');
  $container.append(`<span>${ data.latest.name }</span> `);
  $container.append(`<a target="admin" title="${ quality }: ${ quality_descriptions[quality] }"
    class="location--ind q-${ quality  }"
    href="${ URLS.location_admin }${ data.feature.id }/">&nbsp</a>`);
  var $list = $('<dl class="dl-horizontal"/>').appendTo($container);
  $.each(data.receipts, function (idx, x) {
    $list.append(`<dt>${ x.date.replace(/\-\d+$/, '') }</dt>`);
    $list.append(`<dd>${ thousands(x.tax) }</dd>`);
  });
  return $container[0];
};


export function showLocationPopup(marker) {
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
}
