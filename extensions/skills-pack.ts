import { readFileSync, readdirSync, existsSync, mkdirSync, symlinkSync, unlinkSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

type SkillMetadata = {
  readonly name: string;
  readonly description: string;
};

const packRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
let cachedBootstrap: string | undefined;

function getObjectProperty(value: unknown, key: string): unknown {
  return typeof value === "object" && value !== null
    ? (value as Record<string, unknown>)[key]
    : undefined;
}

function unquoteYamlScalar(value: string): string {
  const trimmed = value.trim();
  if (trimmed.length >= 2) {
    const first = trimmed[0];
    const last = trimmed[trimmed.length - 1];
    if ((first === '"' && last === '"') || (first === "'" && last === "'")) {
      return trimmed.slice(1, -1).replace(/\\"/g, '"');
    }
  }
  return trimmed.replace(/\\"/g, '"');
}

function parseFrontmatterField(
  frontmatter: string,
  fieldName: "name" | "description",
): string | undefined {
  for (const rawLine of frontmatter.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (line.length === 0) {
      continue;
    }

    const separatorIndex = line.indexOf(":");
    if (separatorIndex === -1) {
      continue;
    }

    if (line.slice(0, separatorIndex).trim() !== fieldName) {
      continue;
    }

    const value = unquoteYamlScalar(line.slice(separatorIndex + 1));
    return value.length > 0 ? value : undefined;
  }

  return undefined;
}

function extractFrontmatter(source: string): string | undefined {
  const match = /^---\r?\n([\s\S]*?)\r?\n---/.exec(source);
  return match?.[1];
}

function readSkillMetadata(skillMdPath: string): SkillMetadata | undefined {
  const source = readFileSync(skillMdPath, "utf8");
  const frontmatter = extractFrontmatter(source);
  if (frontmatter === undefined) {
    return undefined;
  }

  const name = parseFrontmatterField(frontmatter, "name");
  const description = parseFrontmatterField(frontmatter, "description");
  if (name === undefined || description === undefined) {
    return undefined;
  }

  return {
    name,
    description,
  };
}

function readPackSkills(root: string): readonly string[] {
  const manifestText = readFileSync(join(root, "package.json"), "utf8");
  const manifestValue: unknown = JSON.parse(manifestText);
  const containers = getObjectProperty(getObjectProperty(manifestValue, "pi"), "skills");
  if (!Array.isArray(containers)) {
    throw new Error("package.json must contain a pi.skills array");
  }

  // pi.skills lists CONTAINER directories (e.g. ["."] or ["./skills"]); each is
  // scanned one level deep for <container>/<name>/SKILL.md. This matches omp's
  // native plugin-skill discovery, which treats entries as containers, not names.
  const skills: string[] = [];
  for (const container of containers) {
    if (typeof container !== "string" || container.length === 0) continue;
    const containerDir = resolve(root, container);
    let entries: string[];
    try {
      entries = readdirSync(containerDir);
    } catch {
      continue;
    }
    for (const entry of entries) {
      if (existsSync(join(containerDir, entry, "SKILL.md"))) {
        skills.push(join(container, entry));
      }
    }
  }

  return skills;
}

export function buildBootstrap(root: string): string {
  let skills: readonly string[];
  try {
    skills = readPackSkills(root);
  } catch {
    return ""; // no readable manifest (e.g. loose-file install) — inject nothing
  }
  const bulletLines: string[] = [];

  for (const skillDir of skills) {
    const skillMdPath = join(root, skillDir, "SKILL.md");
    if (!existsSync(skillMdPath)) {
      continue;
    }

    const metadata = readSkillMetadata(skillMdPath);
    if (metadata === undefined) {
      continue;
    }

    bulletLines.push(`- **${metadata.name}** — ${metadata.description}`);
  }

  const sections: string[] = [
    `This session has a skill pack installed. When a skill below is plausibly relevant to the task, load its SKILL.md with the read tool BEFORE starting the work, follow it, and say in one sentence which skill you loaded. Err toward loading: a needless read costs one tool call, but skipping a relevant skill means doing the task without its methodology. Load none only when no skill plausibly applies. The absolute path pattern is ${root}/<name>/SKILL.md.`,
  ];

  if (bulletLines.length > 0) {
    sections.push("", ...bulletLines);
  }

  sections.push(
    "",
    "Delegation — when your runtime has a subagent/task tool, delegating is the DEFAULT for parallelizable exploration or research, long-running builds/tests/QA, and batch mechanical edits; name the skill each child must follow in its prompt. Do trivial single-file edits inline. With no such tool, do the work inline yourself and never invent delegation calls.",
  );

  return sections.join("\n");
}

export default function createSkillsPackExtension(pi: ExtensionAPI) {
  pi.on("resources_discover", async () => ({ skillPaths: [packRoot] }));

  // Register pack-internal agents (dag-workflow/agents/) via symlinks to ~/.omp/agent/agents/
  pi.on("session_start", async () => {
    const agentsDir = join(packRoot, "dag-workflow", "agents");
    if (!existsSync(agentsDir)) return;
    const targetDir = join(homedir(), ".omp", "agent", "agents");
    mkdirSync(targetDir, { recursive: true });
    for (const f of readdirSync(agentsDir).filter((f) => f.endsWith(".md"))) {
      const dst = join(targetDir, f);
      try { unlinkSync(dst); } catch { /* not present */ }
      try { symlinkSync(resolve(agentsDir, f), dst, "file"); } catch { /* permission or race */ }
    }
  });

  pi.on("before_agent_start", async (event) => {
    cachedBootstrap ??= buildBootstrap(packRoot);
    if (!cachedBootstrap) return;
    return { systemPrompt: `${event.systemPrompt}\n\n${cachedBootstrap}` };
  });
}
