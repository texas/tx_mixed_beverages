import sortBy from "lodash/sortBy"

import { DECLUSTER_ZOOM } from "./settings"
import Chart from "./d3/Chart"
import { channel } from "./utils"

const range = [12, 0]

channel.on("change.rangeBegin", (msg) => {
  range[0] = parseInt(msg, 10)
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
  // Get name history
  const nameHistory = []
  let lastName
  for (let receipt of sortBy(data.receipts, (x) => x.date)) {
    if (receipt.name !== lastName) {
      nameHistory.push([receipt.date, receipt.name])
      lastName = receipt.name
    }
  }
  const nameHistoryStr = nameHistory
    .map(([date, name]) => `${name} (${date.substr(0, 7)})`)
    .join(", ")

  const $container = document.createElement("div")
  $container.className = "location"
  const $name = document.createElement("span")
  $name.className = "name"
  $name.appendChild(document.createTextNode(nameHistoryStr))
  $container.appendChild($name)
  new Chart($container, data.receipts, {
    width: 300,
    height: 180,
    range,
  })
  return $container
}

const locationCache = new Map()
export async function showLocationPopup(marker) {
  const map = marker._map || marker.__parent._group._map // HACK

  function showPopup() {
    // TODO set document.location
    // TODO set ga pageview
    if (marker._map) {
      marker.openPopup()
      return
    }

    map.panTo(marker.getLatLng())
    if (map.getZoom() < DECLUSTER_ZOOM) {
      map.setZoom(DECLUSTER_ZOOM)
    }
    marker.once("add", function () {
      marker.openPopup()
    })
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
