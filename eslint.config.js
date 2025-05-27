// eslint.config.js
// Minimal flat config for ESLint v9+
export default [
  {
    files: ["**/*.js"],
    ignores: ["**/node_modules/**", "dist/**", "partials/**"], // Ignore build artifacts and deps
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: {
        browser: true,
        node: true,
        fetch: true,
        document: true,
        window: true,
        console: true,
        process: true, // For Node.js scripts
        // Minimal necessary globals for specific files if needed by rules
        // Example: For main.js and components
        CustomEvent: "readonly",
        HTMLElement: "readonly",
        SVGElement: "readonly",
        Node: "readonly",
        Text: "readonly",
        localStorage: "readonly",
        navigator: "readonly",
        IntersectionObserver: "readonly",
      },
    },
    rules: {
      "no-unused-vars": "warn",
      "comma-dangle": ["error", "never"],
      semi: ["error", "always"],
      indent: ["warn", 2],
      "space-before-function-paren": [
        "error",
        {
          anonymous: "never",
          named: "never",
          asyncArrow: "always",
        },
      ],
      quotes: ["warn", "single"],
    },
  },
];
