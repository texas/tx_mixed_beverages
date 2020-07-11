import L from "leaflet"
import $ from "jquery"
import { rgb as d3Rgb } from "d3-color"

import { thousands, taxColorScale } from "../utils"

export default function legendFactory() {
  const Legend = L.Control.extend({
    options: {
      position: "bottomleft",
    },
    onAdd() {
      const $container = $('<div class="legend leaflet-bar"/>')
      const $list = $("<dl>").appendTo($container)
      Object.values(taxColorScale.domain()).forEach((level) => {
        const fill = taxColorScale(level)
        const border = d3Rgb(fill).darker(1)
        $list.append(`<dt>
          <span style="background: ${fill}; border: 1px solid ${border};">&nbsp;</span>
          </dt>`)
        $list.append(`<dd>${thousands(level)}</dd>`)
      })
      return $container[0]
    },
  })
  return new Legend()
}
