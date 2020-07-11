import { format as d3Format } from "d3-format"
import * as d3 from "d3"
import colorbrewer from "colorbrewer"
import Bus from "@condenast/quick-bus"

export const thousands = d3Format("$,.0f")
export const distance = d3Format(",.1f")

export const taxColorScale = d3
  .scaleLinear()
  .clamp(true)
  .domain([100000, 25000, 10000, 5000, 1000, 0])
  .range(colorbrewer.Spectral[6])

export const channel = new Bus()
