# Architecture

## Map point data

1. `/location/all.geojson` is served by `MarkerList` in
   `mixed_beverages/apps/lazy_geo/views.py`. `bigmap.js` fetches it once and
   adds all markers to the map.
2. `MarkerList` returns locations that have a coordinate and a nonzero
   `avg_total`.
3. Each feature is about 248 bytes. Current state: 14,070 features, 3.49 MB.
4. Geocoding the remaining locations with nonzero `avg_total` (7,467) adds
   about 1.85 MB. The file becomes about 5.3 MB for about 21,500 features.
5. The response has a one-week `Cache-Control` header. Gzip would reduce the
   transfer to about 1 MB. [INFERENCE] The ratio is an estimate, not measured.

### Decision: do not split the points

Splitting the file into tiles or chunks is not worth the work at this size.
Gzip and the one-week cache keep transfer cost low.

Open item: browser render time for about 21,500 markers is not measured.
Measure it before you reconsider splitting. If rendering is slow, see
`PLAN_map_tiles.local.md`.
