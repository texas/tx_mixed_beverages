import L from 'leaflet';
import $ from 'jquery';

import { thousands, taxColorScale } from '../utils';


export default class {
  render() {
    var Legend = L.Control.extend({
      options: {
        position: 'bottomleft'
      },
      onAdd: function () {
        var $container = $('<div class="legend leaflet-bar"/>');
        var $list = $('<dl>').appendTo($container);
        $.each(taxColorScale.domain(), function (idx, level) {
          $list.append('<dt><span style="background: ' + taxColorScale(level) + ';">&nbsp;</span></dt>');
          $list.append('<dd>' + thousands(level) + '</dd>');
        });
        return $container[0];
      }
    });
    return new Legend();
  }
}
