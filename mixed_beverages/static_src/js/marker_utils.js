/* global URLS: false */
var $ = require('jquery');
import { DECLUSTER_ZOOM } from './settings';

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
  var url = URLS.location_fix.replace('0', data.feature.id);
  $container.append(`<span>${ data.latest.name }</span> `);
  $container.append(`<a target="admin" title="${ quality }: ${ quality_descriptions[quality] }"
    class="location--ind q-${ quality }"
    href="${ url }">&nbsp</a>`);
  var $list = $('<dl class="dl-horizontal"/>').appendTo($container);
  $.each(data.receipts, function (idx, x) {
    $list.append(`<dt>${ x.date.replace(/\-\d+$/, '') }</dt>`);
    $list.append(`<dd>${ thousands(x.tax) }</dd>`);
  });
  return $container[0];
};


var locationCache = {};
export function showLocationPopup(marker) {
  var id = marker.feature.id;
  var map = marker._map || marker.__parent._group._map;  // HACK

  var showPopup = function () {
    if (!marker._map) {
      map.panTo(marker.getLatLng());
      if (map.getZoom() < DECLUSTER_ZOOM) {
        map.setZoom(DECLUSTER_ZOOM);
      }
      marker.once('add', function () {
        marker.openPopup();
      });
      return;
    }
    marker.openPopup();
  };

  var setupPopup = function (data) {
    if (!marker._popup) {
      marker.bindPopup(contentize(data));
    }
    showPopup();
  };

  if (marker._popup) {
    showPopup();
    return;
  }

  var data = locationCache[id];
  if (!data) {
    $.getJSON(URLS.location + id + '/', function (data) {
      data.feature = marker.feature;
      locationCache[id] = data;
      setupPopup(data);
    });
  } else {
    setupPopup(data);
  }
}
