import * as d3 from "d3"
import _ from "lodash"
import { channel, thousands, taxColorScale } from "../utils"

const MONTHS = "JFMAMJJASOND"

export default class {
  constructor(elem, data, options) {
    this.width = options.width
    this.height = options.height
    this.range = options.range
    this.elem = elem

    // Add space for the axes
    this.margin = {
      top: 5,
      right: 0,
      bottom: 15,
      left: 28,
    }
    this.fullData = this.transformData(data)
    this.data = [...this.fullData]
    this.plotHeight = this.height - this.margin.top - this.margin.bottom
    this.plotWidth = this.width - this.margin.left - this.margin.right
    this.findBounds()
    this.render()
  }

  transformData(data) {
    const parseTime = d3.timeParse("%Y-%m-%d")
    return data.map((x) => {
      const date = parseTime(x.date)
      const month = date.getFullYear() * 12 + date.getMonth()
      return { tax: parseFloat(x.total), month, date: x.date }
    })
  }

  findBounds() {
    const maxTax = d3.max(this.data, (d) => d.tax)
    this.yScale = d3.scaleLinear().domain([0, maxTax]).range([this.plotHeight, 0])

    const now = new Date()
    const nowMonth = now.getFullYear() * 12 + now.getMonth()
    const start = nowMonth - this.range[0]
    const end = nowMonth - this.range[1]
    this.xScale = d3.scaleLinear().domain([start, end]).range([0, this.plotWidth])
    this.data = this.fullData.filter((x) => x.month >= start && x.month <= end)
    channel.on("change.*", async (msg) => {
      await Promise.resolve() // Wait for `range` to get updated
      const start = nowMonth - this.range[0]
      const end = nowMonth - this.range[1]
      this.xScale.domain([start, end])
      this.data = this.fullData.filter((x) => x.month >= start && x.month <= end)
      this.refresh()
    })
  }

  xAxis() {
    const _xDomain = this.xScale.domain()
    return d3
      .axisBottom(this.xScale)
      .ticks(_xDomain[1] - _xDomain[0]) // only make ticks at months
      .tickSize(4, 0)
      .tickFormat((value) => MONTHS[value % 12])
  }

  render() {
    const svg = d3
      .select(this.elem)
      .append("svg")
      .attr("width", this.width)
      .attr("height", this.height)
      .attr("viewbox", `0 0 ${this.width} ${this.height}`)
      .attr("preserveAspectRatio", "xMinYMin meet")

    // Plot
    const plot = svg
      .append("g")
      .attr("transform", `translate(${this.margin.left}, ${this.margin.top})`)

    this.plot = plot
    this.refresh()
    // axes
    const barSpacing = this.xScale(this.xScale.domain()[0] + 1)
    const barWidth = Math.max(Math.floor(barSpacing) - 3, 1)
    svg
      .append("g")
      .attr("class", "x axis")
      .attr("title", "date")
      .attr(
        "transform",
        `translate(${(barWidth >> 1) + this.margin.left}, ${this.height - this.margin.bottom})`
      )
      .call(this.xAxis())

    const yAxis = d3.axisLeft(this.yScale).tickSize(4, 0).tickFormat(d3.format("~s"))
    svg
      .append("g")
      .attr("class", "y axis")
      .attr("title", "tax")
      .attr("transform", `translate(${this.margin.left}, ${this.margin.top})`)
      .call(yAxis)
  }

  refresh() {
    const barSpacing = this.xScale(this.xScale.domain()[0] + 1)
    const barWidth = Math.max(Math.floor(barSpacing) - 3, 1)

    const selection = this.plot.selectAll("rect").data(this.data)

    selection
      .enter()
      .append("rect")
      .style("stroke", (d) => d3.rgb(taxColorScale(d.tax)).darker(1))
      .style("fill", (d) => d3.rgb(taxColorScale(d.tax)).darker(1))
      .style("fill-opacity", "0.5")
      .attr("width", barWidth)
      .attr("height", (d) => this.plotHeight - this.yScale(d.tax))
      .attr("transform", (d) => `translate(${this.xScale(d.month)}, ${this.yScale(d.tax)})`)
      .append("title")
      .html((d) => `${d.date} - ${thousands(d.tax)}`)

    selection
      .attr("width", barWidth)
      .attr("height", (d) => this.plotHeight - this.yScale(d.tax))
      .attr("transform", (d) => `translate(${this.xScale(d.month)}, ${this.yScale(d.tax)})`)
      .append("title")
      .html((d) => `${d.date} - ${thousands(d.tax)}`)

    selection.exit().remove()
  }
}
