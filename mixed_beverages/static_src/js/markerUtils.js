import sortBy from "lodash/sortBy"

import { DECLUSTER_ZOOM } from "./settings"
import Chart from "./d3/Chart"
import { channel } from "./utils"

// Display data from x months ago to y months ago
export const DEFAULT_RANGE = [24, 0]
const range = [...DEFAULT_RANGE]

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
  const nameHistory = []
  const namesListed = new Set()
  for (let receipt of sortBy(data.receipts, ["date"])) {
    if (namesListed.has(receipt.name)) {
      continue
    }
    nameHistory.push([receipt.date, receipt.name])
    namesListed.add(receipt.name)
  }
  const nameHistoryStr = nameHistory
    .map(([date, name]) => `${name} (${date.substr(0, 7)})`)
    .join(", ")

  const $container = document.createElement("div")
  $container.className = "location"
  const $name = document.createElement("span")
  $name.className = "name"
  // WISHLIST better markup for this list of names
  $name.appendChild(document.createTextNode(nameHistoryStr))
  $container.appendChild($name)
  new Chart($container, data.receipts, {
    width: 300,
    height: 180,
    range,
  })
  return $container
}

export async function showLocationPopup(marker) {
  const map = marker._map || marker.__parent._group._map // HACK

  function showPopup() {
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

  document.title = marker.feature.properties.name
  // Twitter requires og:title even though we already have <title>
  document.querySelector('meta[property="og:title"]').content = document.title

  history.pushState(
    { id: marker.feature.id },
    "",
    `?id=${marker.feature.id}&name=${encodeURI(marker.feature.properties.name)}${location.hash}`
  )
  if (window.gtag) {
    window.gtag("config", "UA-6535799-12", {
      page_path: `${window.location.pathname}${window.location.search}`,
    })
  }
  if (marker._popup) {
    showPopup()
    return
  }

  const { id } = marker.feature
  const resp = await fetch(`/location/${id}.json`)
  const jsonData = await resp.json()
  marker.bindPopup(contentize(jsonData))
  showPopup()
}
