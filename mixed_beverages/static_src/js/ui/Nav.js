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

  zoomToMarker(marker) {
    this.map.panTo(marker.getLatLng()).setZoom(DECLUSTER_ZOOM);
  }

  render() {
    var NavControl = L.Control.extend({
      options: {
        position: 'topright'
      },

      onAdd: function (map) {
        var $container = $('<div class="nav leaflet-bar status-loading"/>');
        $container.append('<div class="loading">Loading...</div>');
        $container.append(`<div class="info">
          Markers: <span class="markers"></span>
          Value: <span class="value"></span>
          Top: <ol class="top-locations"></ol>
          </div>`);
        this.ui = {
          markers: $container.find('span.markers'),
          value: $container.find('span.value'),
          top: $container.find('ol.top-locations')
        };
        this.ui.top.on('click', 'li', function (evt) {
          var marker = $(this).data('marker');
          if (map.getZoom() < DECLUSTER_ZOOM) {
            this.zoomToMarker(marker);
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
        for (var i = 0; i < Math.min(sorted.length, N_RESULTS); ++i) {
          let markerData = sorted[i].feature.properties.data;
          $li = $(
            `<li>
              <span class="name">${ markerData.name }</span>
              <span class="tax">${ thousands(markerData.avg_tax) }</span>
            </li>`);
          $li.data('marker', sorted[i]);
          this.ui.top.append($li);
        }
        this.ui.markers.text(data.markers.length);
        this.ui.value.text(thousands(data.value));
      }
    });
    return new NavControl();
  }
}
