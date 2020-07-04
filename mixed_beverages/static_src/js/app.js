import L from "leaflet";

import * as bigmap from "./bigmap";
// import * as fixit from "./fixitmap";

// need to manually specify this
L.Icon.Default.imagePath = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.3/images";

// BEGIN
// var bodyClass = document.body.className;
// if (bodyClass.indexOf("bigmap") !== -1) {
bigmap.render();
// } else if (bodyClass.indexOf("fixit") !== -1) {
//   fixit.render();
// }
