import L from 'leaflet';

import * as bigmap from './bigmap';


// need to manually specify this
L.Icon.Default.imagePath = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.3/images';


// BEGIN
if (document.body.className.indexOf('bigmap') !== -1) {
  bigmap.render();
}
