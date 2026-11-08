import type { PageRule } from "../rule"
import { grayOnColor } from "./gray-on-color"
import { lowContrast } from "./low-contrast"

export const COLOR_RULES: readonly PageRule[] = [lowContrast, grayOnColor]
