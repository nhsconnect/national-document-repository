import { defineConfig, globalIgnores } from "eslint/config";
import { fixupPluginRules } from "@eslint/compat";
import unusedImports from "eslint-plugin-unused-imports";
import pluginCypress from "eslint-plugin-cypress";
import _import from "eslint-plugin-import";
import globals from "globals";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all
});

export default defineConfig([globalIgnores(["**/*.MD", "**/react-build-env-checker.js"]), {
    
    ...compat.extends("react-app", "plugin:prettier/recommended"),
    extends: [pluginCypress.configs.recommended],

    plugins: {
        "unused-imports": unusedImports,
        cypress: pluginCypress,
        import: fixupPluginRules(_import),
    },

    languageOptions: {
        globals: {
            ...globals.commonjs,
            ...globals.node,
        },

        ecmaVersion: 2020,
        sourceType: "commonjs",
    },

    rules: {
        "cypress/no-unnecessary-waiting": "warn",
        "object-curly-spacing": ["warn", "always"],
        "@typescript-eslint/semi": ["off"],

        "@typescript-eslint/no-unused-vars": ["warn", {
            vars: "all",
            args: "none",
        }],

        "@typescript-eslint/no-explicit-any": ["off", {
            ignoreRestArgs: true,
        }],

        "max-len": ["warn", {
            code: 100,
            tabWidth: 4,
            ignoreStrings: true,
            ignoreTemplateLiterals: true,
            ignoreComments: true,
        }],

        "testing-library/no-unnecessary-act": "off",

        "no-plusplus": ["error", {
            allowForLoopAfterthoughts: true,
        }],

        "react/jsx-key": "error",

        "import/no-extraneous-dependencies": ["error", {
            devDependencies: [
                "**/*.test.js",
                "**/*.test.jsx",
                "**/*.test.ts",
                "**/*.test.tsx",
                "src/tests/**/*",
                "**/cypress/**",
                "**/cypress.config.ts",
            ],
        }],

        "react/jsx-props-no-spreading": "off",
        "import/prefer-default-export": "off",
        "react/jsx-boolean-value": "off",
        "react/prop-types": "off",
        "react/no-unescaped-entities": "off",
        "react/jsx-one-expression-per-line": "off",
        "react/jsx-wrap-multilines": "off",
        "react/destructuring-assignment": "off",
        "no-console": "warn",
        extensions: "off",
        "prettier/prettier": "warn",
        "unused-imports/no-unused-imports": "warn",
    },
}, {
    files: ["**/*.test.tsx", "**/*.test.ts"],

    rules: {
        "jsx-a11y/anchor-has-content": ["off"],
        "jsx-a11y/no-redundant-roles": ["off"],
        "no-throw-literal": ["off"],
        "max-len": ["off"],
    },
}]);