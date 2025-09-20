module.exports = {
  root: true,
  env: { browser: true, es2021: true, node: true },
  extends: [
    "standard",
    "plugin:react/recommended"
  ],
  parserOptions: { ecmaVersion: "latest", sourceType: "module" },
  plugins: ["react"],
  rules: {
    "comma-dangle": ["error", "only-multiline"],
    "react/prop-types": "off" // if you’re not using PropTypes
  },
  ignorePatterns: [
    "node_modules/",
    "dist/",
    "build/",
    "frontend/src/styles/tokens-meta.js" // ignore if it’s generated/meta data
  ]
};
