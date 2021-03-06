/* global URLS: false */
import L from "leaflet"
import "leaflet.markercluster"
import "leaflet-hash"
import "./ui/Control.GeoZoom"
import debounce from "lodash/debounce"
import { rgb as d3Rgb } from "d3-color"
import Cookies from "cookies-js"

import { DECLUSTER_ZOOM } from "./settings"
import { showLocationPopup } from "./markerUtils"
import { taxColorScale } from "./utils"
import Nav from "./ui/Nav"
import legendFactory from "./ui/legendFactory"

let idToLayerMap = new Map()

function markerStyle(feature) {
  const style = {
    fillOpacity: 0.8,
    opacity: 0.9,
    radius: 7,
    weight: 1,
  }
  const tax = parseInt(feature.properties.data.avg_total, 10) // actually a float, but we don't care about cents
  if (tax === 0) {
    style.color = taxColorScale(tax)
    style.radius = 4
  } else {
    style.fillColor = taxColorScale(tax)
    style.color = d3Rgb(style.fillColor).darker(1)
  }
  return style
}

function addMarkersToMap(map, nav, data) {
  const markers = new L.MarkerClusterGroup({
    disableClusteringAtZoom: DECLUSTER_ZOOM,
    maxClusterRadius: 50,
  })
  window.markers = markers // DEBUG
  L.geoJson(data, {
    pointToLayer: (feature, latlng) => L.circleMarker(latlng, markerStyle(feature)),
  }).addTo(markers)
  nav.saveMarkers(markers)
  idToLayerMap = new Map(markers.getLayers().map((x) => [x.feature.id, x]))
  markers.addTo(map)
  markers.on("click", function (evt) {
    // console.log("marker", evt.layer, this); // DEBUG
    showLocationPopup(evt.layer)
  })
  window.onpopstate = (evt) => {
    if (!evt.state || !evt.state.id) {
      return
    }

    const layer = idToLayerMap.get(evt.state.id)
    layer && showLocationPopup(layer)
  }
  const locationId = parseInt(new URLSearchParams(location.search).get("id"), 10)
  if (locationId && idToLayerMap.has(locationId)) {
    history.replaceState({ id: locationId }, "") // Enable back button back to initial state
    const layer = idToLayerMap.get(locationId)
    layer && showLocationPopup(layer)
  }
  function updateNav() {
    const navData = {
      value: 0,
      markers: [],
    }
    const bounds = map.getBounds()
    markers.eachLayer(function (marker) {
      if (bounds.contains(marker.getLatLng())) {
        navData.markers.push(marker)
        navData.value += parseFloat(marker.feature.properties.data.avg_total || 0)
      }
    })
    nav.showStatsFor(navData)
  }
  updateNav() // initial hit
  map.on("move", debounce(updateNav, 500))
}

function firstVisit(map) {
  L.popup()
    .setLatLng(map.getCenter())
    .setContent(
      `<div>
    <h2>Welcome</h2>
    <p>
      This map helps explore the mixed beverage gross receipts taxes collected by
      the <a href="https://comptroller.texas.gov/taxes/mixed-beverage/sales.php"
      target="_blank">Texas
      Comptroller</a>.

      The amounts you see are the gross receipts for each location reported to
      the State.
    </p>
    <p>
      For more information, see <a href="/about/">about this site</a>.
    </p>
    </div>`
    )
    .openOn(map)
}

export async function render() {
  // map = L.map('map').setView([31.505, -98.09], 8)
  const map = L.map("map", {
    center: [30.2655, -97.7426],
    zoom: DECLUSTER_ZOOM,
    zoomControl: false,
  })
  if (Cookies.enabled && !Cookies.get("returning")) {
    Cookies.set("returning", "1", { expires: 86400 * 30 * 3 })
    firstVisit(map)
  }
  const nav = new Nav(map, showLocationPopup)
  map.addControl(new L.Control.GeoZoom())
  map.addControl(legendFactory())
  map.addControl(nav.render())
  window.map = map // DEBUG
  new L.hash(map)

  L.tileLayer("https://stamen-tiles.a.ssl.fastly.net/toner/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: `Map tiles by <a href="https://stamen.com">Stamen Design</a>,
                  under <a href="https://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>.
                  Data by <a href="https://openstreetmap.org">OpenStreetMap</a>,
                  under <a href="https://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.
                  <a href="/about/">About this site</a>.`,
  }).addTo(map)

  const res = await fetch(URLS.geojson)
  const data = await res.json()
  addMarkersToMap(map, nav, data)
}
