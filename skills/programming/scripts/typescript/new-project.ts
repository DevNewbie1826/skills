#!/usr/bin/env bun
/**
 * Scaffold a new TypeScript project with strict defaults.
 *
 * Usage:
 *   node scripts/typescript/new-project.ts my-api --runtime node
 *   bun scripts/typescript/new-project.ts my-api --runtime bun
 */

import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import process from "node:process";
import { parseArgs } from "node:util";

type Runtime = "bun" | "node";

const { values, positionals } = parseArgs({
  args: process.argv.slice(2),
  options: {
    path: { type: "string", default: "." },
    runtime: { type: "string", default: "bun" },
    help: { type: "boolean", short: "h", default: false },
  },
  allowPositionals: true,
  strict: true,
});

if (values.help || positionals.length === 0) {
  console.log(`Usage: node|bun|tsx new-project.ts <name> [--path <dir>] [--runtime bun|node]

Arguments:
  name                  Project directory name (kebab-case)

Options:
  --path <dir>          Parent directory (default: current dir)
  --runtime bun|node    Generated project runtime (default: bun)
  -h, --help            Show this help`);
  process.exit(values.help ? 0 : 2);
}

const requestedRuntime = values.runtime ?? "bun";
if (requestedRuntime !== "bun" && requestedRuntime !== "node") {
  console.error(`Error: unsupported runtime ${requestedRuntime}. Use bun or node.`);
  process.exit(2);
}
const runtime: Runtime = requestedRuntime;
const name = positionals[0]!;
const root = resolve(values.path!, name);

if (existsSync(root)) {
  console.error(`Error: ${root} already exists`);
  process.exit(1);
}

const packageScripts = runtime === "bun"
  ? {
      dev: "bun --hot src/index.ts",
      start: "bun src/index.ts",
      build: "bun build src/index.ts --target bun --outdir dist",
      check: "bunx biome check . && bunx tsc --noEmit && bun test",
      "check:fix": "bunx biome check --write .",
      test: "bun test",
    }
  : {
      dev: "tsx watch src/index.ts",
      start: "tsx src/index.ts",
      build: "tsc --noEmit",
      check: "biome check . && tsc --noEmit && node --test",
      "check:fix": "biome check --write .",
      test: "node --test",
    };

const pkg = runtime === "bun"
  ? {
      name,
      version: "0.0.1",
      private: true,
      type: "module",
      scripts: packageScripts,
      dependencies: { hono: "^4.12.5", zod: "^3.24.0" },
      devDependencies: {
        "@biomejs/biome": "^1.9.0",
        "@types/bun": "latest",
        typescript: "^5.8.0",
      },
    }
  : {
      name,
      version: "0.0.1",
      private: true,
      type: "module",
      scripts: packageScripts,
      dependencies: { hono: "^4.12.5", zod: "^3.24.0" },
      devDependencies: {
        "@biomejs/biome": "^1.9.0",
        "@hono/node-server": "^2.0.11",
        "@types/node": "^22.0.0",
        tsx: "^4.23.1",
        typescript: "^5.8.0",
      },
    };

const tsconfig = `{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true,
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "target": "ESNext",
    "lib": ["ESNext"],
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "dist",
    "rootDir": "src",
    "module": "${runtime === "node" ? "NodeNext" : "ESNext"}",
    "moduleResolution": "${runtime === "node" ? "NodeNext" : "bundler"}",
    "types": ["${runtime === "node" ? "node" : "bun-types"}"],
    "skipLibCheck": true,
    "noEmit": true
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
`;

const biome = {
  $schema: "https://biomejs.dev/schemas/1.9.0/schema.json",
  organizeImports: { enabled: true },
  formatter: {
    enabled: true,
    indentStyle: "space",
    indentWidth: 2,
    lineWidth: 100,
  },
  linter: {
    enabled: true,
    rules: {
      recommended: true,
      complexity: {
        noBannedTypes: "error",
        noExtraBooleanCast: "error",
        noUselessConstructor: "error",
        noUselessRename: "error",
        noVoid: "error",
      },
      correctness: {
        noUnusedVariables: "error",
        noUnusedImports: "error",
        useExhaustiveDependencies: "warn",
      },
      style: {
        noNonNullAssertion: "error",
        useConst: "error",
        noParameterAssign: "error",
      },
      suspicious: {
        noExplicitAny: "error",
      },
    },
  },
};

const appSource = `import { Hono } from "hono";

const app = new Hono();

app.get("/", (c) => c.json({ status: "ok" }));

export default app;
`;

const indexTs = runtime === "bun"
  ? `${appSource}
const port = Number(process.env.PORT ?? 3000);
const server = Bun.serve({ fetch: app.fetch, port });

console.log(\`Listening on http://127.0.0.1:\${server.port}\`);
`
  : `import { serve } from "@hono/node-server";
${appSource}
const port = Number(process.env.PORT ?? 3000);

serve({ fetch: app.fetch, port }, (info) => {
  console.log(\`Listening on http://127.0.0.1:\${info.port}\`);
});
`;

const readme = runtime === "bun"
  ? `# ${name}

## Development

\`\`\`bash
bun install
bun run dev
\`\`\`
`
  : `# ${name}

## Development

\`\`\`bash
npm install
npm run dev
\`\`\`
`;

const gitignore = `node_modules/
dist/
*.tsbuildinfo
.env
.env.*
`;

mkdirSync(join(root, "src"), { recursive: true });
writeFileSync(join(root, "package.json"), JSON.stringify(pkg, null, 2) + "\n");
writeFileSync(join(root, "tsconfig.json"), tsconfig);
writeFileSync(join(root, "biome.json"), JSON.stringify(biome, null, 2) + "\n");
writeFileSync(join(root, "src", "index.ts"), indexTs);
if (runtime === "bun") {
  mkdirSync(join(root, "tests"), { recursive: true });
  writeFileSync(
    join(root, "tests", "smoke.test.ts"),
    'const moduleName = "bun:test";\nconst { expect, test } = await import(moduleName);\n\ntest("smoke", () => {\n  expect(true).toBe(true);\n});\n',
  );
}
writeFileSync(join(root, "README.md"), readme);
writeFileSync(join(root, ".gitignore"), gitignore);

const installCommand = runtime === "bun" ? "bun install && bun run dev" : "npm install && npm run dev";
console.log(`✓ Created: ${root}`);
console.log(`  cd ${name} && ${installCommand}`);
