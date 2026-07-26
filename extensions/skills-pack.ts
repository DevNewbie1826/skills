import { readFileSync, existsSync } from "node:fs";
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
  const skillsValue = getObjectProperty(getObjectProperty(manifestValue, "pi"), "skills");
  if (!Array.isArray(skillsValue)) {
    throw new Error("package.json must contain a pi.skills array");
  }

  const skills: string[] = [];
  for (const skill of skillsValue) {
    if (typeof skill === "string" && skill.length > 0) {
      skills.push(skill);
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
    `This session has a skill pack installed. When the task matches a skill below, load that skill's SKILL.md with the read tool BEFORE starting the work, follow it, and say in one sentence which skill you loaded. Load only the matching skill; if nothing matches, load none — do not read skills just in case. The absolute path pattern is ${root}/<name>/SKILL.md.`,
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

  pi.on("before_agent_start", async (event) => {
    cachedBootstrap ??= buildBootstrap(packRoot);
    if (!cachedBootstrap) return;
    return { systemPrompt: `${event.systemPrompt}\n\n${cachedBootstrap}` };
  });
}
