/* global $: false */
import L from "leaflet"
import debounce from "lodash/debounce"
import sortBy from "lodash/sortBy"
import { N_RESULTS } from "../settings"
import { channel, thousands, distance } from "../utils"
import { DEFAULT_RANGE, showLocationPopup } from "../markerUtils"

export default class {
  constructor(map) {
    this.map = map
  }

  // Leaflet Control methods

  onAdd(map) {
    const $container = $('<div class="Nav leaflet-bar status-loading"/>')
    $container.append('<div class="loading">Loading...</div>')
    $container.append(`<div class="info">
        <div>
          Markers: <span class="markers"></span>
          Value: <span class="value"></span>
        </div>
        <div>
          <input type="search" class="search" placeholder="Search...">
          <ol class="top-locations"></ol>
        </div>
      </div>`)
    $container.append(`<div class="Nav--range-picker">
      <div class="grid">
      <label for="id_range_begin">From</label>
      <input type="range" id="id_range_begin" name="rangeBegin" min="0" max="60" value="${DEFAULT_RANGE[0]}"/>
      <span class="date-feedback" id="id_range_begin_txt"></span>
      </div>
      <div class="grid">
      <label for="id_range_end">To</label>
      <input type="range" id="id_range_end" name="rangeEnd" min="0" max=60" value="${DEFAULT_RANGE[1]}"/>
      <span class="date-feedback" id="id_range_end_txt"></span>
      </div>

    </div>`)
    this.ui = {
      container: $container,
      search: $container.find("input.search"),
      markers: $container.find("span.markers"),
      value: $container.find("span.value"),
      top: $container.find("ol.top-locations"),
    }
    $container
      .find("input[type=range]")
      .on("change", (evt) => {
        channel.emit(`change.${evt.target.name}`, evt.target.value)
        const now = new Date()
        const targetMonth = now.getFullYear() * 12 + now.getMonth() - parseInt(evt.target.value, 10)
        $(evt.target)
          .next()
          .text(
            `${Math.floor(targetMonth / 12)}-${((targetMonth % 12) + 1)
              .toString()
              .padStart(2, "0")}`
          )
      })
      .change()
    map.nav = this

    // Event handlers
    const _keyup = (evt) => {
      const matches = []
      if (evt.which === 27) {
        this.ui.search.val("")
        // FIXME, reset markers
        return
      }
      const needle = this.ui.search.val().toUpperCase()
      if (needle.length > 2) {
        const { searchIndex } = this.nav
        for (let i = 0; i < searchIndex.length; ++i) {
          if (searchIndex[i][0].indexOf(needle) !== -1) {
            matches.push(searchIndex[i][1])
          }
          if (matches.length > N_RESULTS) {
            break
          }
        }
      }
      this.nav.showMarkers(matches)
    }

    this.ui.search.on("keyup", debounce(_keyup, 200))
    // don't build the search index until someone starts typing
    this.ui.search.one("keyup", this.nav.buildSearchIndex.bind(this.nav))

    this.ui.top.on("click", "li", function (evt) {
      const marker = $(this).data("marker")
      showLocationPopup(marker)
      evt.stopPropagation() // keep click from closing the popup
    })

    return $container[0]
  }

  // Public methods

  showMarkers(markers) {
    this.control.ui.top.empty()
    const center = this.map.getCenter()
    for (let i = 0; i < Math.min(markers.length, N_RESULTS); ++i) {
      const markerData = markers[i].feature.properties
      const $li = $(
        `<li>
          <span class="name">${markerData.name}</span>
          <span class="distance">(${distance(
            center.distanceTo(markers[i].getLatLng()) / 1000
          )} km)</span>
          <span class="tax">${thousands(markerData.data.avg_total)}</span>
        </li>`
      )
      $li.data("marker", markers[i])
      this.control.ui.top.append($li)
    }
  }

  showStatsFor(data) {
    const sorted = sortBy(data.markers, (x) => -parseFloat(x.feature.properties.data.avg_total))
    this.showMarkers(sorted)
    this.control.ui.markers.text(data.markers.length)
    this.control.ui.value.text(thousands(data.value))
  }

  // prep search index
  saveMarkers(markers) {
    this.markers = markers
    this.searchIndex = []
    const $container = this.control.ui.container
    $container.removeClass("status-loading").addClass("status-loaded")
  }

  buildSearchIndex() {
    if (this.searchIndex.length) {
      return
    }
    this.markers.eachLayer((marker) => {
      const { name } = marker.feature.properties
      if (name) {
        this.searchIndex.push([name, marker])
      }
    })
  }

  render() {
    const NavControl = L.Control.extend({
      options: {
        position: "topright",
      },
      onAdd: this.onAdd,
      // HACK
      nav: this,
    })
    this.control = new NavControl()
    return this.control
  }
}
