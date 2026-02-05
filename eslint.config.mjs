import js from "@eslint/js"
import prettier from "eslint-config-prettier"

export default [
  js.configs.recommended,
  prettier,
  {
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        // Browser globals
        window: "readonly",
        document: "readonly",
        navigator: "readonly",
        console: "readonly",
        setTimeout: "readonly",
        clearTimeout: "readonly",
        setInterval: "readonly",
        clearInterval: "readonly",
        location: "readonly",
        history: "readonly",
        fetch: "readonly",
        URLSearchParams: "readonly",
        // Node globals
        process: "readonly",
        __dirname: "readonly",
        __filename: "readonly",
        module: "readonly",
        require: "readonly",
        // Project globals
        URLS: "writable",
        CONFIG: "readonly",
      },
    },
    rules: {},
  },
  {
    ignores: [
      "node_modules/",
      ".venv/",
      "_site/",
      "mixed_beverages/static/",
      "mixed_beverages/static_root/",
      "*.bundle.js",
    ],
  },
]
