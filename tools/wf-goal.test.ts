// Regression harness for extensions/wf-goal.ts — drives the REAL module
// through a stubbed ExtensionAPI and asserts the input→rewrite contract.
// Run: bun tools/wf-goal.test.ts
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import wfGoalExtension from "../extensions/wf-goal.ts";

type Handler = (event: { text: string }) => Promise<{ text?: string } | undefined>;

if (import.meta.main) {
  const handlers: Handler[] = [];
  const stub = {
    setLabel: (_label: string) => {},
    on: (_event: string, handler: Handler) => { handlers.push(handler); },
  };
  const pi = stub as unknown as ExtensionAPI;

  wfGoalExtension(pi);
  if (handlers.length !== 1) throw new Error(`expected 1 input handler, got ${handlers.length}`);
  const handler = handlers[0];

const FLOW_HEAD = "Run this task using the dag-workflow skill.";
// omp fires a magic keyword only for the exact lowercase word standing alone in
// prose (same boundaries as omp's tui/src/prompt/magic-keywords.ts), never
// inside a code fence or tag. The keywords must open the objective, before the
// task text: an unclosed fence or tag in the task masks everything after it.
const KEYWORDS = ["ultrathink", "workflowz"];
const standalone = (word: string) =>
  new RegExp(
    "^[^`<>]*" + String.raw`(?<![\p{L}\p{N}_./\\-])(?<!::)` + word +
      String.raw`(?![\p{L}\p{N}_/\\-])(?!\.[\p{L}\p{N}_-])(?!\()` + "[^`<>]*$",
    "mu",
  );
const goalHead = (task: string) =>
  `/goal ${KEYWORDS.join(" ")}\n\ntask: ${task}\n\n${FLOW_HEAD}`;

const cases: Array<[string, string | null]> = [
  ["/wf 골 테스트!", goalHead("골 테스트!", )],
  ["/wf\ntask text", goalHead("task text")],
  ["/wf\n\n빈 줄 태스크", goalHead("빈 줄 태스크")],
  ["/wf\ttab 태스크", goalHead("tab 태스크")],
  ["/wf\r\nCRLF 태스크", goalHead("CRLF 태스크")],
  ["/wf 골 테스트!\n", goalHead("골 테스트!")],
  ["/wf 골 테스트!\n\n두 번째 줄", goalHead("골 테스트!\n\n두 번째 줄")],
  ["/wf     code", goalHead("code")],
  ["/wf test task\n~~~", goalHead("test task\n~~~")],   // unclosed fence in the task
  ["/wf fix <div> layout", goalHead("fix <div> layout")], // unclosed tag in the task
  // no-rewrite cases
  ["/wf", null],
  ["/wf\n", null],
  ["/wf ", null],
  ["/wf\t", null],
  ["/wf\n\n", null],
  ["/uwf task", null],          // /uwf no longer triggers (removed)
  ["/uwf\nultrathink task", null],
  ["/goal task: anything", null],
  ["일반 메시지 /wf 안녕", null],
  ["/wfx", null],
];

let failed = 0;
for (const [input, expected] of cases) {
  let out: { text?: string } | undefined;
  try {
    out = await handler({ text: input });
  } catch (e) {
    console.log(`ERROR ${JSON.stringify(input)}: ${String(e)}`);
    failed++;
    continue;
  }
  const actual = out?.text ?? null;
  if (expected === null) {
    if (actual !== null) {
      console.log(`FAIL ${JSON.stringify(input)} → expected no rewrite, got ${JSON.stringify(actual.slice(0, 80))}`);
      failed++;
    } else {
      console.log(`PASS ${JSON.stringify(input)} → no rewrite`);
    }
  } else {
    const tailOk = actual !== null && actual.includes("skills/dag-workflow/SKILL.md");
    const missing = actual === null ? KEYWORDS : KEYWORDS.filter((word) => !standalone(word).test(actual));
    if (missing.length > 0) {
      console.log(`FAIL ${JSON.stringify(input)} → keyword not standalone prose: ${missing.join(", ")}`);
      failed++;
    } else if (actual === null || !actual.startsWith(expected) || !tailOk) {
      console.log(`FAIL ${JSON.stringify(input)}\n  expected head: ${JSON.stringify(expected)}\n  actual head:   ${JSON.stringify(actual?.slice(0, expected.length + 4))}`);
      failed++;
    } else {
      console.log(`PASS ${JSON.stringify(input)} → head OK, skill read OK, keywords OK`);
    }
  }
}
if (failed > 0) {
  console.log(`\n${failed}/${cases.length} CASES FAILED`);
  process.exit(1);
}
console.log(`\nALL ${cases.length} CASES PASSED`);
}
