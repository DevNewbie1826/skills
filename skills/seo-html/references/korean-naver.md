# Korean pages and Naver

Read this when the page is in Korean or needs to perform on Naver search.

Each Naver item below says whether Naver's own Search Advisor guide backs it (verified, with the page) or not (unverified). Google rules still apply; Naver adds to them.

## Title

- Naver sets no title length limit ("별도의 글자 수 제한은 없지만", verified: https://searchadvisor.naver.com/guide/markup-content). It asks for a title that displays well, is unique per page, doesn't repeat a keyword two or more times, and carries no spam or promo words (NAV-01).
- The checker measures a weighted display width, the same for every language: after collapsing whitespace, each wide or fullwidth code point (East Asian Width W or F, so every Hangul syllable) counts 2.0 units and every other code point 1.0. It warns when the title is outside 50-60 units (HEAD-04) or the description is outside 150-160 units (HEAD-06). Both are owner values, unverified. The basis: Google and Naver set no length limit and cut text to the display width, and a wide CJK glyph takes about two Latin widths. Latin letters, digits, and spaces count 1.0 each, so mixed titles need no separate range.
- Put the key term in the first 20 or so syllables (KR-02, unverified).
- Width is counted per code point, never per byte: "여권 갱신 기간" is 6 syllables x 2.0 + 2 spaces x 1.0 = 14 units, not 22 bytes.

## Description

- 150-160 weighted width units (HEAD-06, see above), 1-2 sentences, unique per page, not a keyword list, not the body pasted in (NAV-02, verified: https://searchadvisor.naver.com/guide/markup-content).
- Never the same as the title. Naver penalizes it, and the checker flags it as HEAD-10 (verified, same page).

## Open Graph image

Naver uses og:image as the search thumbnail (verified: https://searchadvisor.naver.com/guide/markup-content):

- larger than 150x150 pixels,
- file size at least 5,000 bytes,
- aspect ratio no wider than 3:1,
- unique per page.

The checker reads declared `og:image:width` and `og:image:height` (OG-04). It can't see the file, so file size and uniqueness are model checks (NAV-03). Naver also recommends og:type, og:title, og:description, og:image, and og:url.

## Robots, canonical, mobile

- Robots meta values index, noindex, follow, nofollow apply to Naver's crawler Yeti too; `<meta name="yeti">` targets it alone (verified: https://searchadvisor.naver.com/guide/markup-structure).
- `nosourceinfo` in robots meta turns off Naver's AI-generated source descriptions for the page (verified, same page). Use it only on request; the checker reports it as info (HEAD-11).
- Canonical must be absolute (verified, same page).
- Responsive pages use `<meta name="viewport" content="width=device-width">` (verified: https://searchadvisor.naver.com/guide/markup-mobile).
- Naver reads schema.org as JSON-LD, Microdata, or RDFa and recommends JSON-LD or Microdata (verified: https://searchadvisor.naver.com/guide/structured-data-intro).

## Site-level (not checked by this skill)

These matter, but they're about the site, not one page. Mention them in the report as follow-up:

- Register the site in Search Advisor (searchadvisor.naver.com) and verify ownership.
- robots.txt allows `Yeti`, the sitemap is submitted, and duplicate URLs 301 to the canonical (verified: https://searchadvisor.naver.com/guide/seo-basic-robots).
- Request collection for important new pages after publishing.

## AI 브리핑 (unverified)

Naver's AI briefing at the top of results cites pages paragraph by paragraph. Naver doesn't document what gets cited. Practitioner observations, all unverified:

- Facts in label-value grids (계약금액, 기간, 상대방 ...) get quoted more than prose (KR-03).
- Pages that name and link the primary source (공시, 공식 발표) get chosen.
- Fresh pages win right after an event.
- The answer must be visible on the first mobile screen (NAV-04).

Verify by searching the target query in the Naver app and noting which pages the briefing cites.

## Korean writing

- Pick one register and keep it: 합니다체 for guides and reports, 해요체 for casual blogs (KR-01).
- Run spelling and spacing (맞춤법, 띄어쓰기) carefully; Korean readers notice spacing errors fast.
- Write numbers with units and dates in full: "2026년 10월 14일 기준 수수료는 5만 3천 원입니다" beats "현재 약 5만 원".
- Answer first, as in [writing.md](writing.md): "여권 갱신은 2026년 기준 보통 4~8일 걸립니다." then the details.
- Mixed scripts are fine for proper nouns; don't translate brand names into Hangul unless the brand does.
- Link text says where it goes: "외교부 여권 안내" rather than "여기" or "더보기" (LINK-03).
