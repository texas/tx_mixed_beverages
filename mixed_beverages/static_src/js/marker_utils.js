/* global URLS: false */
const $ = require("jquery")
import { DECLUSTER_ZOOM } from "./settings"

import BarChart from "./d3/Chart"
import { channel } from "./utils"

const range = [12, 0]

channel.on("change.rangeBegin", (msg) => {
  range[0] = parseInt(msg, 10)j
})
channel.on("change.rangeEnd", (msg) => {
  range[1] = parseInt(msg, 10)
})

/**
 * Render data
 * @param {*} data
 * @returns DOMNode
 */
function contentize(data) {
  var quality = data.feature.properties.coordinate_quality
  var $container = $('<div class="location"/>')
  $container.append(`<span>${data.name}</span> `)
  new BarChart($container[0], data.receipts, {
    width: 300,
    height: 180,
  })
  return $container[0]
}

const locationCache = new Map()
export async function showLocationPopup(marker) {
  const map = marker._map || marker.__parent._group._map // HACK

  function showPopup() {
    if (!marker._map) {
      map.panTo(marker.getLatLng())
      if (map.getZoom() < DECLUSTER_ZOOM) {
        map.setZoom(DECLUSTER_ZOOM)
      }
      marker.once("add", function () {
        marker.openPopup()
      })
      return
    }
    marker.openPopup()
  }

  function setupPopup(data) {
    if (!marker._popup) {
      marker.bindPopup(contentize(data))
    }
    showPopup()
  }

  if (marker._popup) {
    showPopup()
    return
  }

  const { id } = marker.feature
  if (!locationCache.has(id)) {
    const resp = await fetch(`/location/${id}.json`)
    const jsonData = await resp.json()
    jsonData.feature = marker.feature
    locationCache.set(id, jsonData)
  }

  setupPopup(locationCache.get(id))
}
