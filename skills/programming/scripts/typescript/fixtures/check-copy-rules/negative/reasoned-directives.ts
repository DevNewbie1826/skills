// @ts-expect-error: the upstream overload misdeclares this parameter
const legacy = computeLegacy()

// linttool-disable-next-line rule-x -- legacy schema cannot change
const b = 2

// linttool-ignore(rule-a): generated file, spacing is fixed upstream
const c = 3

// @suppress unused-var: kept for the public API surface
export const d = 4
