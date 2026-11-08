import type { SourceRule } from "../rule"
import { hardCodedColor } from "./hard-coded-color"

export { type LoadedTokens, loadTokens, mergeTokenColors } from "./tokens"

/** Source rules that read the project's design tokens; each stays silent when the config names none. */
export const TOKEN_RULES: readonly SourceRule[] = [hardCodedColor]
