import L from "leaflet"

// Extend the Control.Zoom UI to add a "Geolocate" button
//
// References:
// https://github.com/Leaflet/Leaflet/blob/master/src/control/Control.Zoom.js
// https://github.com/alanshaw/leaflet-zoom-min/blob/master/L.Control.ZoomMin.js
L.Control.GeoZoom = L.Control.Zoom.extend({
  onAdd(map) {
    const zoomName = "leaflet-control-zoom"
    const container = L.DomUtil.create("div", `${zoomName} leaflet-bar`)

    this._map = map

    this._zoomInButton = this._createButton(
      this.options.zoomInText,
      this.options.zoomInTitle,
      `${zoomName}-in`,
      container,
      this._zoomIn,
      this
    )
    this._zoomOutButton = this._createButton(
      this.options.zoomOutText,
      this.options.zoomOutTitle,
      `${zoomName}-out`,
      container,
      this._zoomOut,
      this
    )
    if ("geolocation" in navigator) {
      this._locateButton = this._createButton(
        "&#x1F30E;",
        "Locate me",
        `${zoomName}-locate`,
        container,
        this._locate,
        this
      )
    }

    this._updateDisabled()
    map.on("zoomend zoomlevelschange", this._updateDisabled, this)

    return container
  },
  _locate() {
    navigator.geolocation.getCurrentPosition((position) => {
      this._map.panTo([position.coords.latitude, position.coords.longitude])
    })
  },
})
