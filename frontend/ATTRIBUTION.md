# Attribution / Notice

Read this when reviewing provenance and license notices for the bundled frontend references.

This skill includes third-party material redistributed under its original licenses. The material has been adapted for a neutral, self-contained skill pack; references are no longer represented as byte-for-byte copies of an upstream layout. Required license notices remain below. A full Apache-2.0 text is provided in `LICENSE-Apache-2.0.txt`.

---

## Brand design-reference corpus

The Layer B brand design references under `references/design/` are derived from an Apache-2.0 design-reference corpus. They capture visual systems such as palettes, typography, component anatomy, layout principles, responsive behavior, and design prompts. They are used for identification and descriptive design analysis only; product names, trademarks, assets, and proprietary copy remain the property of their respective owners.

- Copyright 2026 design-reference contributors
- Licensed under the Apache License, Version 2.0
- Changes: paths and wording may be adapted for neutral portability; references must not be treated as instructions to copy protected brand assets or copy.

---

## Taste, image-concept, and design-spec references

The style, image-to-code, image-concept, output, and design-spec references under `references/design/` are derived from a third-party design-guidance collection. This includes `taste-skill.md`, `cinematic-taste-skill.md`, `minimalist-skill.md`, `brutalist-skill.md`, `soft-skill.md`, `redesign-skill.md`, `image-to-code-skill.md`, `output-skill.md`, `mockup-export-skill.md`, `image-gen-concepts-web.md`, `image-gen-concepts-mobile.md`, `image-gen-brandkit.md`, and `mockup-export-example.md`.

`taste-skill.md`, `image-to-code-skill.md`, `image-gen-concepts-web.md`, `image-gen-concepts-mobile.md`, and `image-gen-brandkit.md` are each split into a core file and section files under their corresponding references/design/<same-name>/ directory. Their content was moved verbatim, with added routing lines and a Contents table. The section directories are references/design/taste-skill/, references/design/image-to-code-skill/, references/design/image-gen-concepts-web/, references/design/image-gen-concepts-mobile/, and references/design/image-gen-brandkit/.

```text
MIT License

Copyright (c) 2026 Leonxlnx

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## UI/UX design intelligence

The search engine, dataset, and documentation under `references/ui-ux-db/` are derived from a third-party UI/UX design-intelligence collection and adapted for self-contained use. Its README guidance is split into `references/ui-ux-db/guide/`.

```text
MIT License

Copyright (c) 2024 Next Level Builder

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Design operating references

The role and skill-reference corpus under `references/designpowers/vendor/` is derived from third-party design operating guidance. It remains reference input only; it does not install a runtime, automation, or separate workflow.

```text
MIT License

Copyright (c) 2026 MC Dean

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Project-local adaptations

`SKILL.md`, routing references, the performance audit helper, and the neutralized cross-reference layer are maintained with this skill. `aside.md`, `lazyweb.md`, and `clone-from-url.md` are project-local synthesis guides based on live-site research and runtime extraction patterns. They do not grant permission to copy third-party trademarks, assets, or proprietary copy.

---

## StyleGallery layout, motion, design-engineering, game-UI, platform-guides, and design-terminology corpus

The layout patterns, recipes, and guides, motion references, design-engineering references, game-UI references, platform guides, and design terminology under references/stylegallery/ are derived from StyleGallery.

- Source: https://github.com/changeroa/StyleGallery at revision 2a9ae14e1ed1e6ebc9ec525a7c305a7cc9830b34 (2026-09-23)
- Copyright (c) 2026 IYEN
- Documentation license: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/. The license notice is vendored at references/stylegallery/LICENSE-DOCS and the upstream third-party notice at references/stylegallery/NOTICE.
- No upstream source code is redistributed in this pack, so the MIT code license from upstream is not reproduced here. Externally adapted leaves keep their original rights as recorded in each leaf's frontmatter per the upstream NOTICE.
- Changes: documentation Markdown subset only. Excluded upstream governance and tooling: `consumer-reference/`, `quality/`, `scripts/`, `tests/`, `examples/`, `design-engineering/reference-profiles/`, `game-ui/unity/data/`, `DOMAINS.md`, `GOVERNANCE.md`, `AGENTS.md`, `README.md`, and the log. Links to excluded files were rewritten to pinned upstream URLs at the revision above. Generated-file maintenance comments were removed, and one-line routing cues were inserted into index files that lacked them. Paths mirror upstream under references/stylegallery/. The corpus was regenerated by this repository's sync tool; the procedure is recorded in references/stylegallery/UPSTREAM.md.

---

## AI-slop taxonomy, detection patterns, and scanner

The `references/deslop/` ruleset (`taxonomy.md`, `detection.md`, `fixes.md`, and `scripts/`) is derived from github.com/yetone/kill-ai-slop by yetone and adapted for the frontend pack.

- Licensed under the Apache License, Version 2.0 (full text in `LICENSE-Apache-2.0.txt`).
- Changes: integrated as a ruleset of the frontend skill rather than a standalone skill; `README.md` rewritten as a pack ruleset guide; `detection.md` adapted for the pack link checker (`$SKILL_DIR`-prefixed inline paths in two prose mentions, and the tell-11 font-size regex rewritten to the equivalent `[4-9]\.?[0-9]*rem`); `scan.mjs` and `rules.ru.mjs` vendored verbatim from upstream; `taxonomy.md` and `fixes.md` are upstream text plus one added routing line and a modification notice (no longer byte-identical); `README.md` and `detection.md` likewise carry a routing line and a modification notice.
