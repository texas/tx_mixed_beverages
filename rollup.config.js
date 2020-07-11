import { nodeResolve } from "@rollup/plugin-node-resolve"

export default {
  input: "mixed_beverages/static_src/js/app.js",
  output: {
    directory: "mixed_beverages/static",
    format: "es",
  },
  plugins: [nodeResolve()],
}
