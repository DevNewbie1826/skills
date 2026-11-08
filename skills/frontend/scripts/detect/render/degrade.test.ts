import { expect, test } from "bun:test"
import { detectPage } from "../detect"
import { RenderError, type Renderer } from "./renderer"

const unavailable = (): Renderer => ({
	render: async () => {
		throw new Error("no browser runtime available")
	},
	close: async () => {},
})

test("#given a renderer with no browser runtime #then detectPage surfaces a RenderError naming the render failure", async () => {
	const failure = await detectPage({ kind: "url", url: "https://example.test/" }, { renderer: unavailable() }).then(
		() => null,
		(error: unknown) => error,
	)
	expect(failure).toBeInstanceOf(RenderError)
	expect(failure instanceof RenderError ? failure.message : String(failure)).toMatch(/render failed for/)
	expect(failure instanceof RenderError ? failure.target : null).toBe("https://example.test/")
})

test("#given a render cause #then the RenderError constructor carries the target label", () => {
	const error = new RenderError("https://example.test/", new Error("no browser runtime available"))
	expect(error.target).toBe("https://example.test/")
	expect(error.message).toBe("render failed for https://example.test/: no browser runtime available")
})
