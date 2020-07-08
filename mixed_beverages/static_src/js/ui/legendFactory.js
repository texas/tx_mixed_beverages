import L from "leaflet"
import $ from "jquery"
import * as d3 from "d3"

import { thousands, taxColorScale } from "../utils"

export default function legendFactory() {
  const Legend = L.Control.extend({
    options: {
      position: "bottomleft",
    },
    onAdd: function () {
      const $container = $('<div class="legend leaflet-bar"/>')
      const $list = $("<dl>").appendTo($container)
      $.each(taxColorScale.domain(), function (idx, level) {
        const fill = taxColorScale(level)
        const border = d3.rgb(fill).darker(1)
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
