/* global URLS: false */
const $ = require("jquery")
import { DECLUSTER_ZOOM } from "./settings"

import BarChart from "./d3/Chart"

/**
 * Render data
 * @param {*} data
 * @returns DOMNode
 */
function contentize(data) {
  var quality = data.feature.properties.coordinate_quality
  var $container = $('<div class="location"/>')
  $container.append(`<span>${data.data.name}</span> `)
  new BarChart($container[0], data.receipts, {
    width: 300,
    height: 180,
  })
  return $container[0]
}

var locationCache = {}
export function showLocationPopup(marker) {
  var id = marker.feature.id
  var map = marker._map || marker.__parent._group._map // HACK

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

  var data = locationCache[id]
  if (!data) {
    $.getJSON(URLS.location + id + "/", function (data) {
      data.feature = marker.feature
      locationCache[id] = data
      setupPopup(data)
    })
  } else {
    setupPopup(data)
  }
}
