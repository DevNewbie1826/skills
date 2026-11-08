import type { PageRule } from "../rule"
import { bodyTextViewportEdge } from "./body-text-viewport-edge"
import { clippedOverflowContainer } from "./clipped-overflow-container"
import { contentHiddenAtRest } from "./content-hidden-at-rest"
import { crampedPadding } from "./cramped-padding"
import { firstViewportColumnOverflow } from "./first-viewport-column-overflow"
import { headingRhythm } from "./heading-rhythm"
import { nestedCards } from "./nested-cards"
import { textOcclusion } from "./text-occlusion"
import { textOverflow } from "./text-overflow"
import { unbalancedHeading } from "./unbalanced-heading"
import { viewportReflow } from "./viewport-reflow"

export const LAYOUT_RULES: readonly PageRule[] = [
	nestedCards,
	textOcclusion,
	firstViewportColumnOverflow,
	crampedPadding,
	bodyTextViewportEdge,
	textOverflow,
	clippedOverflowContainer,
	headingRhythm,
	unbalancedHeading,
	contentHiddenAtRest,
	viewportReflow,
]
