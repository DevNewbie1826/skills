# Attribution / Notice

Read this when reviewing provenance and license notices for this skill.

This skill adapts third-party prose redistributed under its original license and reimplements checking behavior described by a third project. The material has been rewritten for a neutral, self-contained skill pack; it isn't a byte-for-byte copy of any upstream. The required license notices remain below.

---

## Korean writing and Naver guidance (prose adapted)

The Naver lane (Search Advisor setup, Yeti crawler access, sitemap, the AI 브리핑 citation hypotheses such as label-value grids, primary-source signals, freshness and mobile first screen), the answer-first and citable-paragraph writing guidance, and the article-page head and JSON-LD checklist are adapted from `github.com/leopard627/fire-your-seo-agency` (references/neo-naver.md, content.md, seo.md, aeo.md, geo.md).

```text
MIT License

Copyright (c) 2026 leopard627

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

- Changes: rewritten in neutral English with Korean examples; site-wide operations (content pipelines, blog two-track strategy, measurement cadence) left out because this skill covers one page; every Naver claim re-checked against searchadvisor.naver.com and labelled verified or unverified.

---

## Head tags and schema templates (prose adapted)

The head-tag inventory (charset in the first 1024 bytes, viewport, canonical, Open Graph and Twitter fields, icons, theme-color), the JSON-LD templates for Organization, WebSite, Article and BreadcrumbList, and the idea of a priority-ordered audit with a numeric score are adapted from `github.com/SurDijon/seo-unified-skill` (references/head-tags.md, schema-templates.md, audit-framework.md).

```text
MIT License

Copyright (c) 2026 Benjamin SurDijon

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

- Changes: reduced to static single-page HTML; the per-tag weights replaced by this skill's error/warn/info severities and score formula; length thresholds replaced by the owner values recorded in references/rules.md; GEO, local, and link-building material left out.

---

## Checker behavior reference (no code copied)

`github.com/AgriciDaniel/claude-seo` served as a behavior reference for what an on-page checker should look at (title and description presence, heading order, image alt, canonical, JSON-LD parse and deprecated types, placeholder detection). `scripts/check_page.py` reimplements those checks from scratch with the Python standard library. No code, identifiers, or prose from that project were copied, and its AI-phrase list (CC BY-SA 4.0 derived) is deliberately not used anywhere in this skill.

```text
MIT License

Copyright (c) 2026 agricidaniel

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

## Project-local material

The rule catalog IDs, severities, the verified/unverified labels and their official URLs, the 3-round fix loop, the report format, and the model checklist are project-local.
