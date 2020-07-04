import * as d3 from "d3";
import _ from "lodash";
import { thousands, taxColorScale } from "../utils";

export default class {
  constructor(elem, data, options) {
    this.width = options.width;
    this.height = options.height;
    this.elem = elem;

    // space for the axes
    this.margin = {
      top: 5,
      right: 0,
      bottom: 15,
      left: 28,
    };
    this.data = this.transformData(data);
    this.plotHeight = this.height - this.margin.top - this.margin.bottom;
    this.plotWidth = this.width - this.margin.left - this.margin.right;
    this.findBounds();
    this.render();
  }

  transformData(data) {
    var formatter = d3.time.format("%Y-%m-%d");
    // use lodash because it's faster than native Array.map
    return _.map(data, (x) => {
      var date = formatter.parse(x.date);
      var month = date.getFullYear() * 12 + date.getMonth();
      return { tax: parseFloat(x.tax), month, date: x.date };
    });
  }

  findBounds() {
    var maxTax = d3.max(this.data, (d) => d.tax);
    this.yScale = d3.scale.linear().domain([0, maxTax]).range([this.plotHeight, 0]);

    var dates = d3.extent(this.data, (d) => d.month);
    this.xScale = d3.scale
      .linear()
      .domain([dates[0], dates[1] + 1])
      .range([0, this.plotWidth]);
  }

  xAxis() {
    var months = "JFMAMJJASOND";
    var xAxisFormat = (value) => months[value % 12];
    var _xDomain = this.xScale.domain();
    return d3.svg
      .axis()
      .orient("bottom")
      .scale(this.xScale)
      .ticks(_xDomain[1] - _xDomain[0]) // only make ticks at months
      .tickSize(4, 0)
      .tickFormat(xAxisFormat);
  }

  yAxis() {
    return d3.svg
      .axis()
      .orient("left")
      .scale(this.yScale)
      .tickSize(4, 0)
      .tickFormat(d3.format("sr"));
  }

  render() {
    var barSpacing = this.xScale(this.xScale.domain()[0] + 1);
    var barWidth = Math.floor(barSpacing) - 3;
    var svg = d3
      .select(this.elem)
      .append("svg")
      .attr("width", this.width)
      .attr("height", this.height)
      .attr("viewbox", `0 0 ${this.width} ${this.height}`)
      .attr("preserveAspectRatio", "xMinYMin meet");

    // plot
    var plot = svg
      .append("g")
      .attr("transform", `translate(${this.margin.left}, ${this.margin.top})`);
    plot
      .selectAll("rect")
      .data(this.data)
      .enter()
      .append("rect")
      .style({
        stroke: (d) => d3.rgb(taxColorScale(d.tax)).darker(1),
        fill: (d) => taxColorScale(d.tax),
        "fill-opacity": "0.5",
      })
      .attr("width", barWidth)
      .attr("height", (d) => this.plotHeight - this.yScale(d.tax))
      .attr("transform", (d) => `translate(${this.xScale(d.month)}, ${this.yScale(d.tax)})`)
      .append("title")
      .html((d) => `${d.date} - ${thousands(d.tax)}`);

    // axes
    svg
      .append("g")
      .attr("class", "x axis")
      .attr("title", "date")
      .attr(
        "transform",
        `translate(${(barWidth >> 1) + this.margin.left}, ${this.height - this.margin.bottom})`
      )
      .call(this.xAxis());
    svg
      .append("g")
      .attr("class", "y axis")
      .attr("title", "tax")
      .attr("transform", `translate(${this.margin.left}, ${this.margin.top})`)
      .call(this.yAxis());
  }
}
