# Strict tsconfig + Biome

> Read this when creating or reviewing strict TypeScript compiler and formatter configuration.

The canonical ultra-strict config, matching what `scripts/typescript/new-project.ts` generates. Copy-paste, then add your own paths.

## tsconfig.json

```jsonc
{
  "compilerOptions": {
    // ── Strict core ──────────────────────────────────────────
    "strict": true,                            // enables the strict-family flags listed in the comment below
    // strict includes: strictNullChecks, strictFunctionTypes,
    // strictBindCallApply, strictPropertyInitialization,
    // noImplicitAny, noImplicitThis, alwaysStrict, useUnknownInCatchVariables

    // ── Additional strict flags (NOT included in "strict") ──
    "noUncheckedIndexedAccess": true,           // obj[key] is T | undefined, not T
    "exactOptionalPropertyTypes": true,         // { x?: string } !== { x: string | undefined }
    "noFallthroughCasesInSwitch": true,         // switch fall-through is an error
    "forceConsistentCasingInFileNames": true,   // prevents case-sensitivity bugs on macOS/Win

    // ── Module system ────────────────────────────────────────
    "module": "ESNext",                         // "NodeNext" for the Node variant
    "moduleResolution": "bundler",              // "NodeNext" for the Node variant
    "verbatimModuleSyntax": true,               // forces `import type` for type-only imports
    "isolatedModules": true,                    // safe for esbuild / swc / Bun transpilation
    "esModuleInterop": true,
    "resolveJsonModule": true,

    // ── Target ───────────────────────────────────────────────
    "target": "ESNext",
    "lib": ["ESNext"],
    "types": ["bun"],                           // from @types/bun; ["node"] for the Node variant

    // ── Emit ─────────────────────────────────────────────────
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "dist",
    "rootDir": "src",
    "noEmit": true,                             // the runner and bundler compile; tsc only typechecks

    // ── Performance ──────────────────────────────────────────
    "skipLibCheck": true                        // skip checking .d.ts files for speed
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

## biome.json

```json
{
  "$schema": "https://biomejs.dev/schemas/1.9.0/schema.json",
  "organizeImports": {
    "enabled": true
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "suspicious": {
        "noExplicitAny": "error",
        "noConfusingVoidType": "error",
        "noFallthroughSwitchClause": "error"
      },
      "style": {
        "noDefaultExport": "error",
        "useImportType": "error",
        "noNonNullAssertion": "error",
        "noParameterAssign": "error"
      },
      "correctness": {
        "noUnusedVariables": "error",
        "noUnusedImports": "error"
      },
      "complexity": {
        "noBannedTypes": "error"
      }
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "double",
      "semicolons": "asNeeded"
    }
  },
  "files": {
    "ignore": ["node_modules", "dist", "build", ".next", ".nuxt", "coverage"]
  }
}
```

## Sources

- TypeScript: [tsconfig reference](https://www.typescriptlang.org/tsconfig)
- Biome: [configuration](https://biomejs.dev/reference/configuration/)
- Total TypeScript: [tsconfig cheat sheet](https://www.totaltypescript.com/tsconfig-cheat-sheet)
