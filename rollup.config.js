import resolve from "@rollup/plugin-node-resolve"
import commonjs from "@rollup/plugin-commonjs"

export default {
  input: "mixed_beverages/static_src/js/app.js",
  output: {
    // directory: "mixed_beverages/static",
    file: "mixed_beverages/static/app.bundle.js",
    format: "iife",
  },
  plugins: [resolve(), commonjs()],
}
