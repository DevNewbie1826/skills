import type { Rule } from "./rule"
import { COLOR_RULES } from "./color-rules"
import { TYPOGRAPHY_RULES } from "./typography-rules"
import { LAYOUT_RULES } from "./layout-rules"
import { COPY_RULES } from "./copy-rules"

export const ALL_RULES: readonly Rule[] = [
	...COLOR_RULES,
	...TYPOGRAPHY_RULES,
	...LAYOUT_RULES,
	...COPY_RULES,
]
