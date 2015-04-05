import L from 'leaflet';
import $ from 'jquery';
import _ from 'lodash';

import { DECLUSTER_ZOOM, N_RESULTS } from '../settings';
import { thousands } from '../utils';
import { showLocationPopup } from '../marker_utils';


export default class {
  constructor(map) {
    this.map = map;
  }

  // Leaflet Control methods

  onAdd(map) {
    var $container = $('<div class="nav leaflet-bar status-loading"/>');
    $container.append('<div class="loading">Loading...</div>');
    $container.append(`<div class="info">
      Markers: <span class="markers"></span>
      Value: <span class="value"></span>
      Top: <ol class="top-locations"></ol>
      </div>`);
    this.ui = {
      container: $container,
      markers: $container.find('span.markers'),
      value: $container.find('span.value'),
      top: $container.find('ol.top-locations')
    };
    map.nav = this;

    this.ui.top.on('click', 'li', function (evt) {
      var marker = $(this).data('marker');
      if (map.getZoom() < DECLUSTER_ZOOM) {
        map.panTo(marker.getLatLng()).setZoom(DECLUSTER_ZOOM);
        // FIXME user then has to click again because the marker does not exist yet
      }
      showLocationPopup(marker);
      evt.stopPropagation();  // keep click from closing the popup
    });

    return $container[0];
  }

  // Public methods

  showStatsFor(data) {
    var sorted = _.sortBy(data.markers, function (x) {
      return -parseFloat(x.feature.properties.data.avg_tax);
    });
    this.control.ui.top.empty();
    var $li;
    for (var i = 0; i < Math.min(sorted.length, N_RESULTS); ++i) {
      let markerData = sorted[i].feature.properties.data;
      $li = $(
        `<li>
          <span class="name">${ markerData.name }</span>
          <span class="tax">${ thousands(markerData.avg_tax) }</span>
        </li>`);
      $li.data('marker', sorted[i]);
      this.control.ui.top.append($li);
    }
    this.control.ui.markers.text(data.markers.length);
    this.control.ui.value.text(thousands(data.value));
  }

  isLoaded() {
    var $container = this.control.ui.container;
    $container.removeClass('status-loading').addClass('status-loaded');
  }

  render() {
    var NavControl = L.Control.extend({
      options: {
        position: 'topright'
      },
      onAdd: this.onAdd
    });
    this.control = new NavControl();
    return this.control;
  }
}
