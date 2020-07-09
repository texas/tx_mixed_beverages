import * as d3 from "d3"
import colorbrewer from "colorbrewer"

export const thousands = d3.format("$,.0f")
export const distance = d3.format(",.1f")

export const taxColorScale = d3
  .scaleLinear()
  .clamp(true)
  .domain([50000, 10000, 5000, 1000, 0])
  .range(colorbrewer.Spectral[5])

export function extractLatLng(s) {
  var bits = s.match(/([-\d.]+),([-\d.]+)(,(\d+)z)?/)
  if (!bits) {
    return
  }
  var data = {
    lat: bits[1],
    lng: bits[2],
  }
  if (bits.length === 5) {
    data.zoom = bits[4]
  }
  return data
}
