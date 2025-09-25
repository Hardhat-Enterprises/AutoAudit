module.exports = {
  extends: ["stylelint-config-standard"],
  rules: {
    "at-rule-no-unknown": [true, {
      ignoreAtRules: ["tailwind", "apply", "layer", "variants", "responsive", "screen"]
    }],
    "block-no-empty": null,            // relax if tokens produce empty blocks
    "no-descending-specificity": null, // common with utility layers
  },
  ignoreFiles: [
    "node_modules/**",
    "dist/**",
    "build/**"
  ]
};
