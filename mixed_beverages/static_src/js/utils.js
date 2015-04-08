import d3 from 'd3';
import colorbrewer from 'colorbrewer';


export const thousands = d3.format('$,.0f');
export const distance = d3.format(',.1f');

export const taxColorScale = d3.scale.linear()
  .clamp(true)
  .domain([10000, 5000, 1000, 0])
  .range(colorbrewer.Spectral[4]);
