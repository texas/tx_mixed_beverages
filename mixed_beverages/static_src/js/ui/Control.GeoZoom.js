// references:
// https://github.com/Leaflet/Leaflet/blob/master/src/control/Control.Zoom.js
// https://github.com/alanshaw/leaflet-zoom-min/blob/master/L.Control.ZoomMin.js

import L from 'leaflet';


L.Control.GeoZoom = L.Control.Zoom.extend({
  onAdd: function (map) {
    var zoomName = 'leaflet-control-zoom',
        container = L.DomUtil.create('div', zoomName + ' leaflet-bar'),
        options = this.options;

    this._map = map;

    this._zoomInButton  = this._createButton(options.zoomInText, options.zoomInTitle,
            zoomName + '-in',  container, this._zoomIn, this);
    this._zoomOutButton = this._createButton(options.zoomOutText, options.zoomOutTitle,
            zoomName + '-out', container, this._zoomOut, this);
    if ('geolocation' in navigator) {
      this._locateButton = this._createButton('&#x2693;', 'locate me',
              zoomName + '-locate', container, this._locate, this);
    }

    this._updateDisabled();
    map.on('zoomend zoomlevelschange', this._updateDisabled, this);

    return container;
  },
  _locate: function () {
    var self = this;
    navigator.geolocation.getCurrentPosition(function (position) {
      self._map.panTo([position.coords.latitude, position.coords.longitude]);
    });
  }
});