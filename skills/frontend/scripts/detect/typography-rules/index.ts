import type { PageRule } from "../rule"
import { flatTypeHierarchy } from "./flat-type-hierarchy"
import { lineLength } from "./line-length"
import { oversizedH1 } from "./oversized-h1"
import { tightLeading } from "./tight-leading"
import { tinyText } from "./tiny-text"
import { undersizedUiText } from "./undersized-ui-text"

export const TYPOGRAPHY_RULES: readonly PageRule[] = [
	flatTypeHierarchy, oversizedH1, tinyText, undersizedUiText, tightLeading, lineLength,
]
