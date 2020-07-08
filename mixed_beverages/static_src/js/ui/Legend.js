import L from "leaflet"
import $ from "jquery"
import * as d3 from "d3"

import { thousands, taxColorScale } from "../utils"

export default class {
  render() {
    const Legend = L.Control.extend({
      options: {
        position: "bottomleft",
      },
      onAdd: function () {
        var $container = $('<div class="legend leaflet-bar"/>')
        var $list = $("<dl>").appendTo($container)
        $.each(taxColorScale.domain(), function (idx, level) {
          var fill = taxColorScale(level)
          var border = d3.rgb(fill).darker(1)
          $list.append(`<dt>
            <span style="background: ${fill}; border: 1px solid ${border};">&nbsp;</span>
            </dt>`)
          $list.append("<dd>" + thousands(level) + "</dd>")
        })
        return $container[0]
      },
    })
    return new Legend()
  }
}
