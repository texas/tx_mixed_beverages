import { max as d3Max } from "d3-array"
import { axisBottom as d3AxisBottom, axisLeft as d3AxisLeft } from "d3-axis"
import { rgb as d3Rgb } from "d3-color"
import { format as d3Format } from "d3-format"
import { scaleLinear as d3ScaleLinear } from "d3-scale"
import { select as d3Select } from "d3-selection"
import { timeParse as d3TimeParse } from "d3-time-format"
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
    const parseTime = d3TimeParse("%Y-%m-%d")
    return data.map((x) => {
      const date = parseTime(x.date)
      const month = date.getFullYear() * 12 + date.getMonth()
      return {
        month,
        date: x.date,
        liquor: parseFloat(x.liquor),
        wine: parseFloat(x.wine),
        beer: parseFloat(x.beer),
        cover: parseFloat(x.cover),
        total: parseFloat(x.total),
      }
    })
  }

  findBounds() {
    const maxTax = d3Max(this.data, (d) => d.total)
    this.yScale = d3ScaleLinear().domain([0, maxTax]).range([this.plotHeight, 0])

    const now = new Date()
    const nowMonth = now.getFullYear() * 12 + now.getMonth()
    const start = nowMonth - this.range[0]
    const end = nowMonth - this.range[1]
    this.xScale = d3ScaleLinear().domain([start, end]).range([0, this.plotWidth])
    this.data = this.fullData.filter((x) => x.month >= start && x.month <= end)
    channel.on("change.*", async (/* msg */) => {
      await Promise.resolve() // Wait for `range` to get updated
      const start = nowMonth - this.range[0]
      const end = nowMonth - this.range[1]
      this.xScale.domain([start, end])
      this.data = this.fullData.filter((x) => x.month >= start && x.month <= end)
      const maxTax = d3Max(this.data, (d) => d.total)
      if (maxTax) {
        this.yScale = d3ScaleLinear().domain([0, maxTax]).range([this.plotHeight, 0])
      }
      this.refresh()
    })
  }

  xAxis() {
    const _xDomain = this.xScale.domain()
    return d3AxisBottom(this.xScale)
      .ticks(_xDomain[1] - _xDomain[0]) // only make ticks at months
      .tickSize(4, 0)
      .tickFormat((value) => MONTHS[value % 12])
  }

  render() {
    const svg = d3Select(this.elem)
      .append("svg")
      .attr("width", this.width)
      .attr("height", this.height)
      .attr("viewbox", `0 0 ${this.width} ${this.height}`)
      .attr("preserveAspectRatio", "xMinYMin meet")

    const plot = svg
      .append("g")
      .attr("transform", `translate(${this.margin.left}, ${this.margin.top})`)
    this.plot = plot
    this.xAxisContainer = svg.append("g").attr("class", "x axis").attr("title", "date")
    this.yAxisContainer = svg
      .append("g")
      .attr("class", "y axis")
      .attr("title", "tax")
      .attr("transform", `translate(${this.margin.left}, ${this.margin.top})`)
    this.refresh()
  }

  refresh() {
    const barSpacing = this.xScale(this.xScale.domain()[0] + 1)
    const barWidth = Math.max(Math.floor(barSpacing) - 3, 1)

    const selection = this.plot
      .selectAll(".bar-group")
      .data(this.data)
      .enter()
      .append("g")
      .attr("class", "bar-group")
      .attr("transform", (d) => `translate(${this.xScale(d.month)} 0)`)
    selection
      .append("rect")
      .attr("class", "bar bar-total")
      .style("stroke", (d) => console.log("rect stroke") || d3Rgb(taxColorScale(d.total)).darker(1))
      .attr("width", barWidth)
      .attr("height", (d) => this.plotHeight - this.yScale(d.total))
      .attr("transform", (d) => `translate(0 ${this.yScale(d.total)})`)
      .append("title")
      .html((d) => `Total: ${d.date} - ${thousands(d.total)}`)
    selection
      .append("rect")
      .attr("class", "bar bar-liquor")
      .attr("width", barWidth)
      .attr("height", (d) => this.plotHeight - this.yScale(d.liquor))
      .attr("transform", (d) => `translate(0 ${this.yScale(d.liquor)})`)
      .append("title")
      .html((d) => `Liquor: ${d.date} - ${thousands(d.liquor)}`)
    selection
      .append("rect")
      .attr("class", "bar bar-wine")
      .attr("width", barWidth)
      .attr("height", (d) => this.plotHeight - this.yScale(d.wine))
      .attr("transform", (d) => `translate(0 ${this.yScale(d.liquor + d.wine)})`)
      .append("title")
      .html((d) => `Wine: ${d.date} - ${thousands(d.wine)}`)
    selection
      .append("rect")
      .attr("class", "bar bar-beer")
      .attr("width", barWidth)
      .attr("height", (d) => this.plotHeight - this.yScale(d.beer))
      .attr("transform", (d) => `translate(0 ${this.yScale(d.liquor + d.wine + d.beer)})`)
      .append("title")
      .html((d) => `Beer: ${d.date} - ${thousands(d.beer)}`)
    selection
      .append("rect")
      .attr("class", "bar bar-cover")
      .attr("width", barWidth)
      .attr("height", (d) => this.plotHeight - this.yScale(d.cover))
      .attr("transform", (d) => `translate(0 ${this.yScale(d.liquor + d.wine + d.beer + d.cover)})`)
      .append("title")
      .html((d) => `Cover: ${d.date} - ${thousands(d.cover)}`)

    // UPDATE
    // selection
    //   .selectAll(".bar-total")
    //   .style("stroke", (d) => d3Rgb(taxColorScale(d.total)).darker(1))
    //   .attr("width", barWidth)
    //   .attr("height", (d) => this.plotHeight - this.yScale(d.total))
    //   .attr("transform", (d) => `translate(${this.xScale(d.month)}, ${this.yScale(d.total)})`)
    //   .append("title")
    //   .html((d) => `Total: ${d.date} - ${thousands(d.total)}`)
    // selection
    //   .selectAll(".bar-liquor")
    //   .attr("width", barWidth)
    //   .attr("height", (d) => this.plotHeight - this.yScale(d.liquor))
    //   .attr("transform", (d) => `translate(${this.xScale(d.month)}, ${this.yScale(d.liquor)})`)
    //   .append("title")
    //   .html((d) => `Liquor: ${d.date} - ${thousands(d.liquor)}`)

    // EXIT
    selection.exit().remove()

    this.xAxisContainer
      .attr(
        // Shift to center w/ bar
        "transform",
        `translate(${(barWidth >> 1) + this.margin.left}, ${this.height - this.margin.bottom})`
      )
      .call(this.xAxis())
    const yAxis = d3AxisLeft(this.yScale).tickSize(4, 0).tickFormat(d3Format("~s"))
    this.yAxisContainer.call(yAxis)
  }
}
