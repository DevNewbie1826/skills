import type { PageRule } from "../rule"
import { repeatedContainerText } from "./repeated-container-text"
import { skippedHeading } from "./skipped-heading"
import { brokenImage } from "./broken-image"
import { scriptError } from "./script-error"

export const COPY_RULES: readonly PageRule[] = [repeatedContainerText, skippedHeading, brokenImage, scriptError]
