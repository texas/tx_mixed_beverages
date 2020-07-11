import L from "leaflet"
import { rgb as d3Rgb } from "d3-color"

import { thousands, taxColorScale } from "../utils"

export default function legendFactory() {
  const Legend = L.Control.extend({
    options: {
      position: "bottomleft",
    },
    onAdd() {
      const $container = document.createElement("div")
      $container.className = "legend leaflet-bar"
      const $dl = document.createElement("dl")
      Object.values(taxColorScale.domain()).forEach((level) => {
        const fill = taxColorScale(level)
        const border = d3Rgb(fill).darker(1)
        const $dt = document.createElement("dt")
        const $dtSpan = document.createElement("span")
        $dtSpan.appendChild(document.createTextNode(" "))
        $dtSpan.style.backgroundColor = fill
        $dtSpan.style.border = `1px solid ${border}`
        $dt.appendChild($dtSpan)
        $dl.appendChild($dt)
        const $dd = document.createElement("dd")
        $dd.appendChild(document.createTextNode(thousands(level)))
        $dl.appendChild($dd)
      })
      $container.appendChild($dl)
      return $container
    },
  })
  return new Legend()
}
