# Attribution / Notice

Read this when reviewing provenance and license notices for this skill.

This skill adapts third-party material redistributed under its original license. The material has been rewritten for a neutral, self-contained skill pack; it is not represented as a byte-for-byte copy of the upstream. The required license notice remains below.

---

## Test-driven-development methodology

The red/green/refactor cycle, the two-principle test-quality framework ("name the break"; "exercise the real thing"), the mirror-assertion and change-detector patterns, and the mutation check are derived from `github.com/obra/superpowers` (skills/test-driven-development).

```text
MIT License

Copyright (c) 2025 Jesse Vincent

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

- Changes: rewritten in the pack's terse, evidence-first voice; superpowers' dogmatic enforcement ("Iron Law", "delete and restart", anti-rationalization tables, "not negotiable") intentionally omitted; the methodology merged with the pack's pre-existing fakes-before-mocks hierarchy and determinism rules; characterization-test and post-implementation-test exceptions made explicit.

---

## Project-local adaptations

`SKILL.md` is maintained locally but includes the upstream-derived methodology identified above; its pack-specific routing, the fakes-before-mocks hierarchy, and the determinism rules are project-local adaptations.
