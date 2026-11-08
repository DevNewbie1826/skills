/** The frontend detect SDK's public API: everything below is for callers outside this repository (a skill script, a project's own lint step). */
/** @public */
export { blend, colorsIn, contrastRatio, luminance, parseColor, type Rgba } from "./core"
/** @public */
export { parseConfig } from "./config"
/** @public */
export { DEFAULT_VIEWPORTS, detectFiles, detectPage, type DetectPageOptions, REFLOW_VIEWPORTS } from "./detect"
/** @public */
export { effectiveSeverity, hasFailures, type LintOptions, lintSnapshot, lintSources, sortFindings } from "./lint"
/** @public */
export { formatFindingsText, summarize } from "./report"
/** @public */
export { RenderError, type RenderRequest, type RenderTarget, type Renderer } from "./render"
/** @public */
export { createWebViewRenderer } from "./render"
export type { PageContext, PageHit, PageRule, Rule, SourceContext, SourceHit, SourceRule } from "./rule"
/** @public */
export { ALL_RULES } from "./rules"
/** @public */
export { type LoadedTokens, loadTokens, mergeTokenColors, TOKEN_RULES } from "./token-rules"
/** @public */
export { collectPageSnapshot } from "./snapshot"
/** @public */
export { STYLE_PROPS } from "./snapshot"
export type * from "./types"
