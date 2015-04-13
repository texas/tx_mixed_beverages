import L from 'leaflet';
import $ from 'jquery';
import _ from 'lodash';

import { N_RESULTS } from '../settings';
import { thousands, distance } from '../utils';
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
        <div>
          Markers: <span class="markers"></span>
          Value: <span class="value"></span>
        </div>
        <div>
          <input type="search" class="search" placeholder="Search...">
          <ol class="top-locations"></ol>
        </div>
      </div>`);
    this.ui = {
      container: $container,
      search: $container.find('input'),
      markers: $container.find('span.markers'),
      value: $container.find('span.value'),
      top: $container.find('ol.top-locations')
    };
    map.nav = this;


    // Event handlers
    var _keyup = (evt) => {
      var matches = [];
      if (evt.which === 27) {
        this.ui.search.val('');
        return;
      }
      var needle = this.ui.search.val().toUpperCase();
      if (needle.length > 2) {
        var searchIndex = this.nav.searchIndex;
        for (var i = 0; i < searchIndex.length; ++i) {
          if (searchIndex[i][0].indexOf(needle) !== -1) {
            matches.push(searchIndex[i][1]);
          }
          if (matches.length > N_RESULTS) {
            break;
          }
        }
      }
      this.nav.showMarkers(matches);
    };

    this.ui.search.on('keyup', _.debounce(_keyup, 200));
    // don't build the search index until someone starts typing
    this.ui.search.one('keyup', this.nav.buildSearchIndex.bind(this.nav));

    this.ui.top.on('click', 'li', function (evt) {
      var marker = $(this).data('marker');
      showLocationPopup(marker);
      evt.stopPropagation();  // keep click from closing the popup
    });

    return $container[0];
  }

  // Public methods

  showMarkers(markers) {
    this.control.ui.top.empty();
    var $li;
    var center = this.map.getCenter();
    for (var i = 0; i < Math.min(markers.length, N_RESULTS); ++i) {
      let markerData = markers[i].feature.properties.data;
      $li = $(
        `<li>
          <span class="name">${ markerData.name }</span>
          <span class="distance">(${ distance(center.distanceTo(markers[i].getLatLng()) / 1000) } km)</span>
          <span class="tax">${ thousands(markerData.avg_tax) }</span>
        </li>`);
      $li.data('marker', markers[i]);
      this.control.ui.top.append($li);
    }
  }

  showStatsFor(data) {
    var sorted = _.sortBy(data.markers, function (x) {
      return -parseFloat(x.feature.properties.data.avg_tax);
    });
    this.showMarkers(sorted);
    this.control.ui.markers.text(data.markers.length);
    this.control.ui.value.text(thousands(data.value));
  }

  _isLoaded() {
    var $container = this.control.ui.container;
    $container.removeClass('status-loading').addClass('status-loaded');
  }

  // prep search index
  saveMarkers(markers) {
    this.markers = markers;
    this.searchIndex = [];
    this._isLoaded();
  }

  buildSearchIndex() {
    if (this.searchIndex.length) {
      return;
    }
    this.markers.eachLayer((marker) => {
      var name = marker.feature.properties.data.name;
      if (name) {
        this.searchIndex.push([name, marker]);
      }
    });
  }

  render() {
    var NavControl = L.Control.extend({
      options: {
        position: 'topright'
      },
      onAdd: this.onAdd,
      // HACK
      nav: this
    });
    this.control = new NavControl();
    return this.control;
  }
}
