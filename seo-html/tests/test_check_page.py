"""Golden-fixture and mutation tests for scripts/check_page.py.

Every script rule in the plan catalog gets one test asserting the rule id
appears with its catalog severity on a failing input. Threshold cases are
built in-test from the module constants so a constant change fails loudly.
No network, no clock: all runs are in-process or subprocess checks of the
local script.
"""
from __future__ import annotations

import io
import json
import os
import random
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from contextlib import redirect_stdout
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
TEMPLATE_PATH = SKILL_DIR / "templates" / "page.html"
CHECKER_PATH = SCRIPTS_DIR / "check_page.py"
sys.path.insert(0, str(SCRIPTS_DIR))

import check_page as cp  # noqa: E402

GOOD_EN_TITLE = "On-Page SEO Basics: Titles, Meta Tags, and Clean Structure"
GOOD_EN_DESCRIPTION = (
    "Search optimization starts on the page: a sharp title and description, a "
    "canonical URL, social preview cards, semantic HTML, and structured data "
    "step by step."
)
GOOD_KO_TITLE = "네이버와 구글 검색 상위 노출을 위한 SEO 기초 가이드"
GOOD_KO_DESCRIPTION = (
    "네이버와 구글 상위 노출에 필요한 검색 최적화 기초를 정리했습니다. "
    "제목과 설명 작성법, 시맨틱 구조, 대표 이미지와 구조화 데이터까지 실전 "
    "예시와 함께 설명합니다."
)

# Hard-coded copy of the plan's script-rule catalog (id -> severity).
CATALOG_RULES = {
    "HEAD-01": "error", "HEAD-02": "error", "HEAD-03": "error", "HEAD-04": "warn",
    "HEAD-05": "error", "HEAD-06": "warn", "HEAD-07": "error", "HEAD-08": "info",
    "HEAD-09": "error", "HEAD-10": "warn", "HEAD-11": "info",
    "OG-01": "error", "OG-02": "warn", "OG-03": "warn", "OG-04": "warn",
    "OG-05": "info", "OG-06": "warn", "OG-07": "info",
    "TW-01": "warn", "TW-02": "info",
    "SEM-01": "error", "SEM-02": "warn", "SEM-03": "info", "SEM-04": "warn",
    "SEM-05": "info", "SEM-06": "warn",
    "H-01": "error", "H-02": "warn", "H-03": "warn",
    "LD-01": "error", "LD-02": "error", "LD-03": "error", "LD-04": "error",
    "LD-05": "error", "LD-06": "error", "LD-07": "info", "LD-08": "warn",
    "LD-09": "error", "LD-10": "error", "LD-11": "warn", "LD-12": "warn",
    "LD-13": "warn", "LD-14": "warn",
    "IMG-01": "error", "IMG-02": "warn", "IMG-03": "warn", "IMG-04": "info",
    "LINK-01": "error", "LINK-02": "warn", "LINK-03": "warn", "LINK-04": "info",
    "A11Y-01": "warn", "PERF-01": "info",
    "CONT-01": "error", "CONT-02": "warn", "CONT-03": "info",
}

ASSERTED_IDS = set()

TEMPLATE_FILL = {
    "LANG": "ko",
    "TITLE": GOOD_KO_TITLE,
    "DESCRIPTION": GOOD_KO_DESCRIPTION,
    "CANONICAL_URL": "https://example.com/ko/guide/seo-basics",
    "SITE_NAME": "예제 노트",
    "SITE_URL": "https://example.com",
    "OG_LOCALE": "ko_KR",
    "OG_IMAGE_URL": "https://example.com/images/seo-basics-ko.png",
    "OG_IMAGE_ALT": "제목부터 구조화 데이터까지 검색 최적화 기초 항목을 정리한 체크리스트 카드",
    "H1": "네이버와 구글 검색 상위 노출 가이드",
    "PUBLISHED_ISO": "2026-09-01",
    "PUBLISHED_DISPLAY": "2026년 9월 1일",
    "MODIFIED_ISO": "2026-10-05",
    "AUTHOR_NAME": "김하늘",
    "LEAD_ANSWER": (
        "검색 최적화는 특별한 비법에서 시작하지 않습니다. 문서의 머리 정보, "
        "본문 구조, 구조화 데이터를 검색 엔진이 읽을 수 있는 형태로 정리하는 일이 "
        "곧 기본기입니다. 이 문서에서는 페이지 단위에서 반드시 점검해야 할 항목을 "
        "순서대로 설명합니다."
    ),
    "SECTION_1_TITLE": "메타 정보를 먼저 정리하세요",
    "SECTION_1_BODY": (
        "문자 인코딩 선언을 가장 앞에 두면 파서가 인코딩을 추측하지 않습니다. "
        "뷰포트 메타는 모바일 화면 사용성을 책임지고, 제목은 주제를, 설명은 문서의 "
        "약속을 한두 문장으로 요약합니다. 정규 URL은 이 문서의 원본 주소가 어디인지 "
        "크롤러에게 알려 줍니다."
    ),
    "STAT_SENTENCE": "2026년 독자 설문에서 응답자의 47%가 제목을 본문을 다 쓴 뒤에 수정한다고 답했습니다.",
    "STAT_SOURCE_URL": "https://example.com/survey/title-habits",
    "STAT_SOURCE_NAME": "독자 설문",
    "FIGURE_IMAGE_URL": "https://example.com/images/seo-basics-figure-ko.png",
    "FIGURE_IMAGE_ALT": "제목, 설명, 정규 URL, 소셜 미리보기 태그 순서를 표시한 머리 영역",
    "FIGURE_CAPTION": "잘 정리된 문서의 머리 영역 예시입니다.",
    "SECTION_2_TITLE": "시맨틱 구조로 본문을 만드세요",
    "SECTION_2_BODY": (
        "main 랜드마크 하나와 h1 하나, 단계를 건너뛰지 않는 제목 구조는 독자와 "
        "크롤러 모두에게 명확한 목차를 줍니다. 본문은 article로 감싸고, 그림에는 "
        "캡션을 붙이고, 날짜에는 기계가 읽을 수 있는 datetime 속성을 함께 씁니다."
    ),
    "SECTION_3_TITLE": "구조화 데이터를 신뢰받게 쓰세요",
    "SECTION_3_BODY": (
        "JSON-LD 블록 하나에 조직, 웹사이트, 문서, 글, 이동 경로를 그래프로 "
        "연결하세요. 모든 주소는 절대 주소로, 모든 날짜는 ISO 8601 형식으로 쓰고, "
        "글 제목은 화면에 보이는 h1과 같게 맞추면 마크업과 문서가 같은 이야기를 "
        "하게 됩니다."
    ),
    "BREADCRUMB_2": "가이드",
    "BREADCRUMB_2_SLUG": "guide",
}


def fixture_text(name):
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


# Delta re-review round 2: the surviving malformed authorities from the
# review table, and the positive controls that must stay clean.
DELTA2_BAD_AUTHORITIES = (
    "https://[2001:db8::1]junk/",
    "https://[2001:db8::1]junk:443/",
    "https://[127.0.0.1]/",
    "https://[example.com]/",
    "https://example.com:+443/",
    "https://example.com: 443/",
    "https://example.com:\uff14\uff14\uff14/",
)
DELTA2_GOOD_AUTHORITIES = (
    "https://[2001:db8::1]:443/path",
    "https://\uc608\uc2dc.\ud55c\uad6d/\uacbd\ub85c",
    "https://xn--9n2bp8qxa.example/",
    "https://example.com./path",
    "https://user:pass@example.com:65535/path",
    "https://192.0.2.1:8000/path",
)

# Delta re-review round 3, required change 1: scoped IPv6 literals.
# RFC 9844 (August 2025) obsoleted RFC 6874 and removed zone
# identifiers from URI syntax, and ipaddress.IPv6Address accepts any
# non-empty scope text, so every "%" (and any other character outside
# RFC 3986 IPv6address) must be rejected by the shared validator.
DELTA3_ZONE_AUTHORITIES = (
    "https://[::1%25bad scope]/",
    "https://[::1%25bad|scope]/",
    "https://[::1%25bad\\scope]/",
    "https://[fe80::1%25eth0]/",
)
# Delta re-review round 3, required change 2: RFC 3986 port is *DIGIT,
# so zero padding is spelling, not value; the value stays bounded.
DELTA3_PADDED_GOOD_AUTHORITIES = (
    "https://example.com:000443/",
    "https://[2001:db8::1]:000443/",
    "https://user:pass@example.com:065535/",
    "http://example.com:000080/",
    "https://example.com:" + "0" * 5000 + "443/",
)
DELTA3_PADDED_BAD_AUTHORITIES = (
    "https://example.com:0000/",
    "https://example.com:065536/",
    "https://example.com:" + "0" * 5000 + "65536/",
)


def run_checker_cli(args, env_extra=None):
    """Run the real CLI as a subprocess and capture raw bytes, so tests
    control the stdout/stderr decoding (UTF-8) exactly."""
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, str(CHECKER_PATH)] + [str(a) for a in args],
        capture_output=True, env=env)


def write_temp_page(text, prefix="page"):
    with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8",
            prefix=prefix) as handle:
        handle.write(text)
        return handle.name


class RuleCase(unittest.TestCase):
    maxDiff = None

    def result_for(self, text, **kwargs):
        return cp.run_check(text, kwargs.pop("file_label", "case.html"), **kwargs)

    def fixture_result(self, name, **kwargs):
        return self.result_for(fixture_text(name), file_label=name, **kwargs)

    def pairs_of(self, result):
        return {(finding["id"], finding["severity"])
                for finding in result["findings"]}

    def assert_rule(self, rule_id, result, severity=None):
        severity = severity or CATALOG_RULES[rule_id]
        pairs = self.pairs_of(result)
        self.assertIn(
            (rule_id, severity), pairs,
            "%s with severity %s expected; findings: %r"
            % (rule_id, severity, sorted(pairs)))
        if severity is None or severity == CATALOG_RULES[rule_id]:
            self.assertEqual(cp.RULES[rule_id], severity)
        ASSERTED_IDS.add(rule_id)

    def mutated(self, name, *replacements):
        text = fixture_text(name)
        for old, new in replacements:
            self.assertEqual(
                text.count(old), 1,
                "fixture drift: anchor occurs %d times: %r"
                % (text.count(old), old[:70]))
            text = text.replace(old, new)
        return text

    def with_main_body(self, name, inner_html):
        text = fixture_text(name)
        self.assertEqual(text.count("  <main>"), 1)
        self.assertEqual(text.count("  </main>"), 1)
        before, rest = text.split("  <main>", 1)
        _, after = rest.split("  </main>", 1)
        return "%s  <main>\n%s\n  </main>%s" % (before, inner_html, after)


class TestRegistry(RuleCase):

    def test_rules_registry_equals_catalog(self):
        self.assertEqual(cp.RULES, CATALOG_RULES)
        self.assertEqual(list(cp.RULES), list(CATALOG_RULES))
        self.assertEqual(len(cp.RULES), 56)
        for severity in cp.RULES.values():
            self.assertIn(severity, ("error", "warn", "info"))

    def test_plan_amendment_a2_constants(self):
        self.assertEqual(cp.WIDE_WEIGHT, 2.0)
        self.assertEqual(cp.TITLE_WIDTH, (50, 60))
        self.assertEqual(cp.DESCRIPTION_WIDTH, (150, 160))
        self.assertEqual(cp.THIN_MIN_CHARS, 300)
        self.assertEqual(cp.KEYWORD_DENSITY, (1.0, 3.0))
        self.assertEqual(cp.ALT_MAX, 125)
        self.assertEqual(cp.OG_IMAGE_MIN, (150, 150))
        self.assertEqual(cp.OG_IMAGE_MAX_RATIO, 3.0)
        self.assertEqual(cp.OG_IMAGE_RECOMMENDED, (1200, 630))

    def test_weighted_width_model(self):
        self.assertEqual(cp.width_units("가" * 28), 56)
        self.assertEqual(cp.width_units("a" * 55), 55)
        self.assertEqual(cp.width_units("가a"), 3)


class TestGoodFixtures(RuleCase):

    def test_good_en_has_no_errors_or_warns(self):
        result = self.fixture_result("good-en.html")
        bad = [f for f in result["findings"]
               if f["severity"] in ("error", "warn")]
        self.assertEqual(bad, [])
        self.assertEqual(result["lang"], "en")

    def test_good_ko_has_no_errors_or_warns(self):
        result = self.fixture_result("good-ko.html")
        bad = [f for f in result["findings"]
               if f["severity"] in ("error", "warn")]
        self.assertEqual(bad, [])
        self.assertEqual(result["lang"], "ko")

    def test_good_ko_lengths_inside_windows(self):
        self.assertTrue(cp.TITLE_WIDTH[0]
                        <= cp.width_units(GOOD_KO_TITLE) <= cp.TITLE_WIDTH[1])
        self.assertTrue(cp.DESCRIPTION_WIDTH[0]
                        <= cp.width_units(GOOD_KO_DESCRIPTION)
                        <= cp.DESCRIPTION_WIDTH[1])

    def test_good_ko_has_no_nosourceinfo(self):
        result = self.fixture_result("good-ko.html")
        self.assertNotIn(("HEAD-11", "info"), self.pairs_of(result))

    def test_good_en_lengths_inside_windows(self):
        self.assertTrue(cp.TITLE_WIDTH[0]
                        <= cp.width_units(GOOD_EN_TITLE) <= cp.TITLE_WIDTH[1])
        self.assertTrue(cp.DESCRIPTION_WIDTH[0]
                        <= cp.width_units(GOOD_EN_DESCRIPTION)
                        <= cp.DESCRIPTION_WIDTH[1])


class TestHeadRules(RuleCase):

    def test_head_01(self):
        self.assert_rule("HEAD-01", self.fixture_result("bad-head.html"))

    def test_head_01_charset_beyond_first_1024_bytes(self):
        padded = "<!-- %s -->\n%s" % ("x" * 1200, fixture_text("good-en.html"))
        self.assert_rule("HEAD-01", self.result_for(padded))

    def test_head_02(self):
        self.assert_rule("HEAD-02", self.fixture_result("bad-head.html"))

    def test_head_03(self):
        self.assert_rule("HEAD-03", self.fixture_result("bad-head.html"))

    def test_head_04(self):
        text = self.mutated(
            "good-en.html",
            ("<title>%s</title>" % GOOD_EN_TITLE, "<title>%s</title>" % ("A" * 61)))
        self.assert_rule("HEAD-04", self.result_for(text))

    def test_head_05(self):
        self.assert_rule("HEAD-05", self.fixture_result("bad-head.html"))

    def test_head_06(self):
        text = self.mutated(
            "good-en.html",
            ('<meta name="description" content="%s">' % GOOD_EN_DESCRIPTION,
             '<meta name="description" content="%s">' % ("B" * 161)))
        self.assert_rule("HEAD-06", self.result_for(text))

    def test_head_07(self):
        self.assert_rule("HEAD-07", self.fixture_result("bad-head.html"))

    def test_head_07_allow_noindex_downgrades_to_info(self):
        result = self.fixture_result("bad-head.html", allow_noindex=True)
        pairs = self.pairs_of(result)
        self.assertIn(("HEAD-07", "info"), pairs)
        self.assertNotIn(("HEAD-07", "error"), pairs)

    def test_head_08(self):
        self.assert_rule("HEAD-08", self.fixture_result("bad-head.html"))

    def test_head_09(self):
        self.assert_rule("HEAD-09", self.fixture_result("bad-head.html"))

    def test_head_10(self):
        text = self.mutated(
            "good-en.html",
            ('<meta name="description" content="%s">' % GOOD_EN_DESCRIPTION,
             '<meta name="description" content="%s">' % GOOD_EN_TITLE))
        self.assert_rule("HEAD-10", self.result_for(text))

    def test_head_11(self):
        self.assert_rule("HEAD-11", self.fixture_result("bad-head.html"))


class TestOgTwitterRules(RuleCase):

    def test_og_01(self):
        self.assert_rule("OG-01", self.fixture_result("bad-og-twitter.html"))

    def test_og_02(self):
        self.assert_rule("OG-02", self.fixture_result("bad-og-twitter.html"))

    def test_og_03(self):
        self.assert_rule("OG-03", self.fixture_result("bad-og-twitter.html"))

    def test_og_04(self):
        self.assert_rule("OG-04", self.fixture_result("bad-og-twitter.html"))

    def test_og_05(self):
        self.assert_rule("OG-05", self.fixture_result("bad-og-twitter.html"))

    def test_og_06(self):
        self.assert_rule("OG-06", self.fixture_result("bad-og-twitter.html"))

    def test_og_07(self):
        self.assert_rule("OG-07", self.fixture_result("bad-og-twitter.html"))

    def test_tw_01(self):
        self.assert_rule("TW-01", self.fixture_result("bad-og-twitter.html"))

    def test_tw_02(self):
        self.assert_rule("TW-02", self.fixture_result("bad-og-twitter.html"))


class TestSemanticHeadingRules(RuleCase):

    def test_sem_01(self):
        self.assert_rule("SEM-01", self.fixture_result("bad-semantic-headings.html"))

    def test_sem_02(self):
        self.assert_rule("SEM-02", self.fixture_result("bad-semantic-headings.html"))

    def test_sem_03(self):
        self.assert_rule("SEM-03", self.fixture_result("bad-semantic-headings.html"))

    def test_sem_04(self):
        self.assert_rule("SEM-04", self.fixture_result("bad-semantic-headings.html"))

    def test_sem_05(self):
        self.assert_rule("SEM-05", self.fixture_result("bad-semantic-headings.html"))

    def test_sem_06(self):
        self.assert_rule("SEM-06", self.fixture_result("bad-semantic-headings.html"))

    def test_h_01(self):
        self.assert_rule("H-01", self.fixture_result("bad-semantic-headings.html"))

    def test_h_02(self):
        self.assert_rule("H-02", self.fixture_result("bad-semantic-headings.html"))

    def test_h_03(self):
        self.assert_rule("H-03", self.fixture_result("bad-semantic-headings.html"))


class TestJsonLdRules(RuleCase):

    def test_ld_01_broken_json(self):
        self.assert_rule("LD-01", self.fixture_result("edge-broken-jsonld.html"))

    def test_ld_01_no_block(self):
        text = self.mutated(
            "good-en.html",
            ('<script type="application/ld+json">', '<script type="text/json">'))
        self.assert_rule("LD-01", self.result_for(text))

    def test_ld_02(self):
        self.assert_rule("LD-02", self.fixture_result("bad-jsonld.html"))

    def test_ld_02_http_context_is_warn(self):
        text = self.mutated(
            "good-en.html",
            ('"@context": "https://schema.org"', '"@context": "http://schema.org"'))
        self.assert_rule("LD-02", self.result_for(text), severity="warn")

    def test_ld_03(self):
        self.assert_rule("LD-03", self.fixture_result("bad-jsonld.html"))

    def test_ld_04(self):
        self.assert_rule("LD-04", self.fixture_result("bad-jsonld.html"))

    def test_ld_05(self):
        self.assert_rule("LD-05", self.fixture_result("bad-jsonld.html"))

    def test_ld_06(self):
        self.assert_rule("LD-06", self.fixture_result("bad-jsonld.html"))

    def test_ld_07(self):
        self.assert_rule("LD-07", self.fixture_result("bad-jsonld.html"))

    def test_ld_08(self):
        self.assert_rule("LD-08", self.fixture_result("bad-jsonld.html"))

    def test_ld_09(self):
        self.assert_rule("LD-09", self.fixture_result("bad-jsonld.html"))

    def test_ld_10(self):
        self.assert_rule("LD-10", self.fixture_result("bad-jsonld.html"))

    def test_ld_11(self):
        self.assert_rule("LD-11", self.fixture_result("bad-jsonld.html"))

    def test_ld_12(self):
        self.assert_rule("LD-12", self.fixture_result("bad-jsonld.html"))

    def test_ld_13(self):
        self.assert_rule("LD-13", self.fixture_result("bad-jsonld.html"))

    def test_ld_14(self):
        self.assert_rule("LD-14", self.fixture_result("bad-jsonld.html"))


class TestImageRules(RuleCase):

    def test_img_01(self):
        self.assert_rule("IMG-01", self.fixture_result("bad-images.html"))

    def test_img_02(self):
        self.assert_rule("IMG-02", self.fixture_result("bad-images.html"))

    def test_img_03(self):
        self.assert_rule("IMG-03", self.fixture_result("bad-images.html"))

    def test_img_04(self):
        self.assert_rule("IMG-04", self.fixture_result("bad-images.html"))

    def test_img_04_fires_when_first_main_image_is_lazy(self):
        text = self.mutated(
            "good-ko.html",
            ('width="1200" height="675">',
             'width="1200" height="675" loading="lazy">'))
        self.assert_rule("IMG-04", self.result_for(text))

    def test_img_04_silent_when_first_main_image_is_not_lazy(self):
        result = self.fixture_result("good-ko.html")
        self.assertNotIn(
            "IMG-04", {finding["id"] for finding in result["findings"]})

    def test_img_04_silent_when_lazy_image_is_not_first_in_main(self):
        text = self.mutated(
            "good-ko.html",
            ("같은 이야기를 하게 됩니다.</p>",
             "같은 이야기를 하게 됩니다.</p>\n"
             "        <img "
             'src="https://example.com/images/seo-basics-diagram-ko.png" '
             'alt="구조화 데이터 그래프 예시" width="800" height="450" '
             'loading="lazy">'))
        result = self.result_for(text)
        self.assertNotIn(
            "IMG-04", {finding["id"] for finding in result["findings"]})


class TestLinkA11yPerfRules(RuleCase):

    def test_link_01(self):
        self.assert_rule("LINK-01", self.fixture_result("bad-links-a11y-perf.html"))

    def test_link_02_warn(self):
        self.assert_rule("LINK-02",
                         self.fixture_result("bad-links-a11y-perf.html"),
                         severity="warn")

    def test_link_02_no_xdefault_is_info(self):
        self.assert_rule("LINK-02",
                         self.fixture_result("bad-links-a11y-perf.html"),
                         severity="info")

    def test_link_03(self):
        self.assert_rule("LINK-03", self.fixture_result("bad-links-a11y-perf.html"))

    def test_link_04(self):
        self.assert_rule("LINK-04", self.fixture_result("bad-links-a11y-perf.html"))

    def test_a11y_01(self):
        self.assert_rule("A11Y-01", self.fixture_result("bad-links-a11y-perf.html"))

    def test_perf_01(self):
        self.assert_rule("PERF-01", self.fixture_result("bad-links-a11y-perf.html"))


class TestContentRules(RuleCase):

    def test_cont_01(self):
        self.assert_rule("CONT-01", self.fixture_result("bad-content.html"))

    def test_cont_01_threshold_from_constant(self):
        chars = cp.THIN_MIN_CHARS - 1
        self.assertGreater(chars, 0)
        text = self.with_main_body(
            "good-en.html",
            "    <article>\n      <p>%s</p>\n    </article>" % ("가" * chars))
        result = self.result_for(text)
        self.assertEqual(
            len(cp.collapse_ws("가" * chars)), cp.THIN_MIN_CHARS - 1)
        self.assert_rule("CONT-01", result)

    def test_cont_02_keyword_absent(self):
        result = self.result_for(fixture_text("good-en.html"), keyword="zebra")
        self.assert_rule("CONT-02", result)

    def test_cont_02_keyword_density_inside_window(self):
        words = ["maple"] * 2 + ["birch"] * 98
        self.assertEqual(len(words), 100)
        density = 100.0 * 2 / 100
        self.assertTrue(cp.KEYWORD_DENSITY[0] <= density <= cp.KEYWORD_DENSITY[1])
        text = self.with_main_body(
            "good-en.html",
            "    <article>\n      <p>%s</p>\n    </article>" % " ".join(words))
        result = self.result_for(text, keyword="maple")
        self.assertNotIn(("CONT-02", "warn"), self.pairs_of(result))

    def test_cont_03(self):
        self.assert_rule("CONT-03", self.fixture_result("bad-content.html"))


class TestThresholds(RuleCase):

    def test_hangul_title_width_boundaries(self):
        in_range_syllables = cp.TITLE_WIDTH[0] // 2 + 3
        over_syllables = cp.TITLE_WIDTH[1] // 2 + 1
        self.assertGreaterEqual(2 * in_range_syllables, cp.TITLE_WIDTH[0])
        self.assertLessEqual(2 * in_range_syllables, cp.TITLE_WIDTH[1])
        self.assertGreater(2 * over_syllables, cp.TITLE_WIDTH[1])

        okay = self.mutated(
            "good-ko.html",
            ("<title>%s</title>" % GOOD_KO_TITLE,
             "<title>%s</title>" % ("가" * in_range_syllables)))
        result = self.result_for(okay)
        self.assertNotIn(("HEAD-04", "warn"), self.pairs_of(result))

        over = self.mutated(
            "good-ko.html",
            ("<title>%s</title>" % GOOD_KO_TITLE,
             "<title>%s</title>" % ("가" * over_syllables)))
        self.assert_rule("HEAD-04", self.result_for(over))

    def test_ascii_title_width_passes(self):
        letters = (cp.TITLE_WIDTH[0] + cp.TITLE_WIDTH[1]) // 2
        self.assertTrue(cp.TITLE_WIDTH[0] <= letters <= cp.TITLE_WIDTH[1])
        text = self.mutated(
            "good-en.html",
            ("<title>%s</title>" % GOOD_EN_TITLE,
             "<title>%s</title>" % ("a" * letters)))
        result = self.result_for(text)
        self.assertNotIn(("HEAD-04", "warn"), self.pairs_of(result))

    def test_description_width_boundary(self):
        chars = cp.DESCRIPTION_WIDTH[1] + 1
        self.assertGreater(chars, cp.DESCRIPTION_WIDTH[1])
        text = self.mutated(
            "good-en.html",
            ('<meta name="description" content="%s">' % GOOD_EN_DESCRIPTION,
             '<meta name="description" content="%s">' % ("b" * chars)))
        self.assert_rule("HEAD-06", self.result_for(text))


class TestLanguageDetection(RuleCase):

    def test_auto_lang_from_html_attribute(self):
        self.assertEqual(self.fixture_result("good-ko.html")["lang"], "ko")
        self.assertEqual(self.fixture_result("good-en.html")["lang"], "en")

    def test_auto_lang_hangul_ratio(self):
        text = self.mutated("good-ko.html", ('<html lang="ko">', '<html>'))
        result = self.result_for(text)
        self.assertEqual(result["lang"], "ko")
        self.assert_rule("HEAD-09", result)

    def test_auto_lang_english_fallback(self):
        text = self.mutated("good-en.html", ('<html lang="en">', '<html>'))
        result = self.result_for(text)
        self.assertEqual(result["lang"], "en")
        self.assert_rule("HEAD-09", result)

    def test_explicit_lang_mismatch_fires_head_09(self):
        result = self.result_for(fixture_text("good-ko.html"), lang="en")
        self.assert_rule("HEAD-09", result)


class TestEdgeCases(RuleCase):

    def test_empty_file_reports_errors_without_crashing(self):
        result = self.fixture_result("edge-empty.html")
        self.assertTrue(result["findings"])
        self.assertGreater(result["summary"]["error"], 0)

    def test_page_without_head_reports_charset_error(self):
        self.assert_rule("HEAD-01", self.fixture_result("edge-no-head.html"))

    def test_decorative_empty_alt_does_not_fire_img_01(self):
        result = self.fixture_result("edge-decorative-alt.html")
        self.assertNotIn(("IMG-01", "error"), self.pairs_of(result))
        bad = [f for f in result["findings"]
               if f["severity"] in ("error", "warn")]
        self.assertEqual(bad, [])


class TestExitCodes(unittest.TestCase):

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(CHECKER_PATH)] + [str(a) for a in args],
            capture_output=True, text=True)

    def test_exit_0_for_good_fixture(self):
        self.assertEqual(self.run_cli(FIXTURES_DIR / "good-en.html").returncode, 0)

    def test_exit_1_for_bad_head_fixture(self):
        self.assertEqual(self.run_cli(FIXTURES_DIR / "bad-head.html").returncode, 1)

    def test_exit_2_for_missing_file(self):
        process = self.run_cli(FIXTURES_DIR / "does-not-exist.html")
        self.assertEqual(process.returncode, 2)
        self.assertIn("cannot read", process.stderr)

    def test_exit_2_for_undecodable_file(self):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as handle:
            handle.write(b"\xff\xfe\x00\xd8 not utf 8")
            path = handle.name
        try:
            process = self.run_cli(path)
        finally:
            Path(path).unlink()
        self.assertEqual(process.returncode, 2)
        self.assertIn("cannot decode", process.stderr)

    def test_exit_2_for_usage_error(self):
        self.assertEqual(self.run_cli().returncode, 2)

    def test_warn_only_exits_0_without_strict_and_1_with_strict(self):
        text = fixture_text("good-en.html").replace(
            '  <meta property="og:description" content="%s">\n' % GOOD_EN_DESCRIPTION,
            "")
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False, encoding="utf-8") as handle:
            handle.write(text)
            path = handle.name
        try:
            self.assertEqual(self.run_cli(path).returncode, 0)
            self.assertEqual(self.run_cli(path, "--strict").returncode, 1)
        finally:
            Path(path).unlink()

    def test_json_output_shape(self):
        process = self.run_cli(FIXTURES_DIR / "good-ko.html", "--json")
        self.assertEqual(process.returncode, 0)
        report = json.loads(process.stdout)
        self.assertEqual(set(report),
                         {"file", "lang", "summary", "findings", "extracted"})
        self.assertEqual(set(report["summary"]),
                         {"error", "warn", "info", "score"})
        self.assertEqual(report["summary"]["error"], 0)
        self.assertEqual(set(report["extracted"]),
                         {"title", "title_len", "description_len", "h1", "og",
                          "twitter", "canonical", "jsonld_types", "images"})
        self.assertEqual(report["lang"], "ko")
        self.assertEqual(report["extracted"]["canonical"],
                         "https://example.com/ko/guide/seo-basics")
        self.assertEqual(report["extracted"]["jsonld_types"],
                         ["Organization", "WebSite", "WebPage", "Article",
                          "BreadcrumbList"])


class TestTemplate(RuleCase):

    def filled_template(self):
        text = TEMPLATE_PATH.read_text(encoding="utf-8")
        for token, value in TEMPLATE_FILL.items():
            text = text.replace("{{%s}}" % token, value)
        self.assertNotIn("{{", text)
        return text

    def test_filled_template_is_clean(self):
        low, high = cp.TITLE_WIDTH
        self.assertTrue(low <= cp.width_units(TEMPLATE_FILL["TITLE"]) <= high)
        low, high = cp.DESCRIPTION_WIDTH
        self.assertTrue(low <= cp.width_units(TEMPLATE_FILL["DESCRIPTION"]) <= high)
        result = self.result_for(self.filled_template(), lang="ko")
        bad = [f for f in result["findings"]
               if f["severity"] in ("error", "warn")]
        self.assertEqual(bad, [])

    def test_unfilled_template_fails_ld_05(self):
        result = self.result_for(
            TEMPLATE_PATH.read_text(encoding="utf-8"))
        self.assert_rule("LD-05", result)
        self.assertGreater(result["summary"]["error"], 0)


class TestHardenedParsing(RuleCase):
    """Regressions for the review-blocker classes (R1-R5) and their delta
    re-review survivors: unusable numeric magnitudes (bounded at
    MAX_DIMENSION, overflow-free ratio comparison), URL authority
    validation (valid host and port; IPv4/IPv6/IDNA hosts accepted), the
    complete charset byte extent, impossible calendar dates, and
    source-order text extraction."""

    def run_json_cli(self, text):
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False, encoding="utf-8") as handle:
            handle.write(text)
            path = handle.name
        try:
            return subprocess.run(
                [sys.executable, str(CHECKER_PATH), path, "--json"],
                capture_output=True, text=True)
        finally:
            Path(path).unlink()

    def test_r1_og_image_width_superscript_yields_parseable_json(self):
        text = self.mutated(
            "good-en.html",
            ('<meta property="og:image:width" content="1200">',
             '<meta property="og:image:width" content="\u00b2">'))
        process = self.run_json_cli(text)
        self.assertNotIn("Traceback", process.stderr)
        self.assertEqual(process.returncode, 0)
        report = json.loads(process.stdout)
        severities = {finding["id"]: finding["severity"]
                      for finding in report["findings"]}
        self.assertEqual(severities.get("OG-07"), "info")
        self.assertNotIn("OG-04", severities)
        self.assertEqual(report["summary"]["error"], 0)

    def test_r1_unusable_og_dimensions_count_as_missing(self):
        for junk in ("", " ", "12px", "-5", "1e3", "\u00b2", "\uff11\uff12"):
            with self.subTest(junk=junk):
                text = self.mutated(
                    "good-en.html",
                    ('<meta property="og:image:width" content="1200">',
                     '<meta property="og:image:width" content="%s">' % junk))
                result = self.result_for(text)
                self.assert_rule("OG-07", result)
                self.assertNotIn(
                    "OG-04", {finding["id"] for finding in result["findings"]})

    def test_r1_img_width_superscript_yields_parseable_json(self):
        text = self.mutated(
            "good-en.html",
            ('width="1200" height="675"', 'width="\u00b2" height="675"'))
        process = self.run_json_cli(text)
        self.assertNotIn("Traceback", process.stderr)
        self.assertEqual(process.returncode, 0)
        report = json.loads(process.stdout)
        severities = {finding["id"]: finding["severity"]
                      for finding in report["findings"]}
        self.assertEqual(severities.get("IMG-03"), "warn")
        self.assertEqual(report["summary"]["error"], 0)

    def test_r1_unusable_img_dimensions_fire_img_03(self):
        for junk in ("", "12px", "1e3", "-5"):
            with self.subTest(junk=junk):
                text = self.mutated(
                    "good-en.html",
                    ('width="1200" height="675"',
                     'width="%s" height="675"' % junk))
                self.assert_rule("IMG-03", self.result_for(text))

    def test_r1_huge_og_width_yields_parseable_json(self):
        text = self.mutated(
            "good-en.html",
            ('<meta property="og:image:width" content="1200">',
             '<meta property="og:image:width" content="%s">' % ("9" * 400)))
        process = self.run_json_cli(text)
        self.assertNotIn("Traceback", process.stderr)
        self.assertEqual(process.returncode, 0)
        report = json.loads(process.stdout)
        severities = {finding["id"]: finding["severity"]
                      for finding in report["findings"]}
        self.assertEqual(severities.get("OG-07"), "info")
        self.assertNotIn("OG-04", severities)
        self.assertEqual(report["summary"]["error"], 0)

    def test_r1_huge_og_dimensions_yield_parseable_json(self):
        text = self.mutated(
            "good-en.html",
            ('<meta property="og:image:width" content="1200">',
             '<meta property="og:image:width" content="%s">' % ("9" * 400)),
            ('<meta property="og:image:height" content="630">',
             '<meta property="og:image:height" content="%s">' % ("9" * 400)))
        process = self.run_json_cli(text)
        self.assertNotIn("Traceback", process.stderr)
        self.assertEqual(process.returncode, 0)
        report = json.loads(process.stdout)
        severities = {finding["id"]: finding["severity"]
                      for finding in report["findings"]}
        self.assertEqual(severities.get("OG-07"), "info")
        self.assertNotIn("OG-04", severities)
        self.assertEqual(report["summary"]["error"], 0)

    def test_r1_huge_img_width_yields_parseable_json(self):
        text = self.mutated(
            "good-en.html",
            ('width="1200" height="675"',
             'width="%s" height="675"' % ("9" * 400)))
        process = self.run_json_cli(text)
        self.assertNotIn("Traceback", process.stderr)
        self.assertEqual(process.returncode, 0)
        report = json.loads(process.stdout)
        severities = {finding["id"]: finding["severity"]
                      for finding in report["findings"]}
        self.assertEqual(severities.get("IMG-03"), "warn")
        self.assertEqual(report["summary"]["error"], 0)

    def test_r1_dimension_magnitude_bound_from_constant(self):
        self.assertEqual(cp.MAX_DIMENSION, 100000)
        self.assertEqual(cp.parse_dimension(str(cp.MAX_DIMENSION)),
                         cp.MAX_DIMENSION)
        self.assertIsNone(cp.parse_dimension(str(cp.MAX_DIMENSION + 1)))
        self.assertIsNone(cp.parse_dimension("9" * 400))
        self.assertEqual(cp.parse_dimension("0" * 402 + "1"), 1)
        self.assertEqual(cp.parse_dimension("001200"), 1200)
        self.assertEqual(cp.parse_dimension("0"), 0)

    def test_r1_extreme_usable_dimensions_fire_og_04(self):
        text = self.mutated(
            "good-en.html",
            ('<meta property="og:image:width" content="1200">',
             '<meta property="og:image:width" content="%d">' % cp.MAX_DIMENSION),
            ('<meta property="og:image:height" content="630">',
             '<meta property="og:image:height" content="1000">'))
        self.assert_rule("OG-04", self.result_for(text))

    def test_r2_hostless_canonical_fires_link_01(self):
        text = self.mutated(
            "good-en.html",
            ('<link rel="canonical" href="https://example.com/guide/seo-basics">',
             '<link rel="canonical" href="https://">'),
            ('<meta property="og:url" content="https://example.com/guide/seo-basics">',
             '<meta property="og:url" content="https://">'))
        result = self.result_for(text)
        self.assert_rule("LINK-01", result)
        self.assert_rule("OG-06", result)

    def test_r2_hostless_ld_image_fires_ld_13(self):
        text = self.mutated(
            "good-en.html",
            ('"image": "https://example.com/images/seo-basics.png",',
             '"image": "https://",'))
        self.assert_rule("LD-13", self.result_for(text))

    def test_r2_hreflang_href_must_be_absolute(self):
        canonical_line = ('  <link rel="canonical" '
                          'href="https://example.com/guide/seo-basics">\n')
        hreflang_lines = (
            '  <link rel="alternate" hreflang="en" '
            'href="https://example.com/guide/seo-basics">\n'
            '  <link rel="alternate" hreflang="ko-KR" '
            'href="https://example.com/ko/guide/seo-basics">\n'
            '  <link rel="alternate" hreflang="x-default" '
            'href="https://example.com/guide/seo-basics">\n')
        text = self.mutated(
            "good-en.html", (canonical_line, canonical_line + hreflang_lines))
        self.assertEqual(self.result_for(text)["summary"]["warn"], 0)
        for broken_href in ("/ko/guide/seo-basics", "https://"):
            with self.subTest(href=broken_href):
                broken = text.replace(
                    'hreflang="ko-KR" href="https://example.com/ko/guide/seo-basics"',
                    'hreflang="ko-KR" href="%s"' % broken_href)
                self.assert_rule("LINK-02", self.result_for(broken))

    def test_r2_invalid_host_characters_fire_link_01_and_og_06(self):
        text = self.mutated(
            "good-en.html",
            ('<link rel="canonical" href="https://example.com/guide/seo-basics">',
             '<link rel="canonical" href="https://exa mple.com/">'),
            ('<meta property="og:url" content="https://example.com/guide/seo-basics">',
             '<meta property="og:url" content="https://exa mple.com/">'))
        result = self.result_for(text)
        self.assert_rule("LINK-01", result)
        self.assert_rule("OG-06", result)

    def test_r2_invalid_host_ld_image_fires_ld_13(self):
        text = self.mutated(
            "good-en.html",
            ('"image": "https://example.com/images/seo-basics.png",',
             '"image": "https://exa mple.com/images/seo-basics.png",'))
        self.assert_rule("LD-13", self.result_for(text))

    def test_r2_out_of_range_port_fires_link_01(self):
        text = self.mutated(
            "good-en.html",
            ('<link rel="canonical" href="https://example.com/guide/seo-basics">',
             '<link rel="canonical" href="https://example.com:99999/">'),
            ('<meta property="og:url" content="https://example.com/guide/seo-basics">',
             '<meta property="og:url" content="https://example.com:99999/">'))
        result = self.result_for(text)
        self.assert_rule("LINK-01", result)
        self.assert_rule("OG-06", result)

    def test_r2_valid_ipv6_and_internationalized_hosts_stay_clean(self):
        for url in ("https://[2001:db8::1]:443/path", "https://예시.한국/경로"):
            with self.subTest(url=url):
                text = self.mutated(
                    "good-en.html",
                    ('<link rel="canonical" href="https://example.com/guide/seo-basics">',
                     '<link rel="canonical" href="%s">' % url),
                    ('<meta property="og:url" content="https://example.com/guide/seo-basics">',
                     '<meta property="og:url" content="%s">' % url))
                result = self.result_for(text)
                self.assertNotIn(
                    "LINK-01",
                    {finding["id"] for finding in result["findings"]})
                self.assertNotIn(
                    "OG-06",
                    {finding["id"] for finding in result["findings"]})
                bad = [finding for finding in result["findings"]
                       if finding["severity"] in ("error", "warn")]
                self.assertEqual(bad, [])

    def test_r2_url_authority_validator_matrix(self):
        good = ("https://example.com/", "http://example.com:8080/path",
                "https://[2001:db8::1]:443/path", "http://127.0.0.1:8000/x",
                "https://예시.한국/경로", "https://example.com./x")
        bad = ("https://exa mple.com/", "https://example.com:99999/",
               "https://example.com:0/", "https://example..com/",
               "https://exa_mple.com/", "https://",
               "https://user:pass@/path", "/relative/path",
               "ftp://example.com/", "not a url")
        for url in good:
            with self.subTest(url=url):
                self.assertTrue(cp.is_absolute_http_url(url), url)
        for url in bad:
            with self.subTest(url=url):
                self.assertFalse(cp.is_absolute_http_url(url), url)

    def shifted_charset_page(self, tag_start_byte):
        """good-en.html with an ASCII comment prepended so the charset
        start tag's "<" lands on the given UTF-8 byte offset."""
        text = fixture_text("good-en.html")
        start = text.index("<meta charset")
        prefix_bytes = len(text[:start].encode("utf-8"))
        pad = tag_start_byte - prefix_bytes
        self.assertGreaterEqual(pad, 7, "padding comment must fit")
        comment = "<!--" + "x" * (pad - 7) + "-->"
        self.assertEqual(len(comment.encode("utf-8")), pad)
        return comment + text

    def test_r3_charset_ending_exactly_at_limit_passes(self):
        text = fixture_text("good-en.html")
        start = text.index("<meta charset")
        end = text.index(">", start) + 1
        tag_bytes = len(text[start:end].encode("utf-8"))
        page = self.shifted_charset_page(cp.CHARSET_MAX_BYTES - tag_bytes)
        result = self.result_for(page)
        self.assertNotIn(
            "HEAD-01", {finding["id"] for finding in result["findings"]})
        bad = [finding for finding in result["findings"]
               if finding["severity"] in ("error", "warn")]
        self.assertEqual(bad, [])

    def test_r3_charset_starting_before_limit_ending_after_fires(self):
        page = self.shifted_charset_page(cp.CHARSET_MAX_BYTES - 1)
        self.assert_rule("HEAD-01", self.result_for(page))

    def test_r3_unicode_line_separator_before_charset_fires(self):
        # html.parser does not treat U+2028 as a line break, so a
        # splitlines()-based line map measures the wrong tag's extent and
        # this page wrongly passed. The charset tag spans UTF-8 bytes
        # 1020 up to 1042 (exclusive) here, beyond the limit.
        text = "<!--\u2028" + "x" * 967 + "-->\n" + fixture_text("good-en.html")
        result = self.result_for(text)
        self.assert_rule("HEAD-01", result)
        evidence = [finding["evidence"] for finding in result["findings"]
                    if finding["id"] == "HEAD-01"]
        self.assertTrue(any("1042" in item for item in evidence),
                        "expected the full declaration extent, got %r" % evidence)

    def test_r3_crlf_line_endings_keep_page_clean(self):
        text = fixture_text("good-en.html").replace("\n", "\r\n")
        result = self.result_for(text)
        bad = [finding for finding in result["findings"]
               if finding["severity"] in ("error", "warn")]
        self.assertEqual(bad, [])

    def test_r3_lone_cr_before_charset_fires(self):
        # The parser breaks lines at "\n" only, never at a lone "\r";
        # the charset declaration ends at byte 1040, beyond the limit.
        text = "<!--\r" + "x" * 967 + "-->\n" + fixture_text("good-en.html")
        result = self.result_for(text)
        self.assert_rule("HEAD-01", result)
        evidence = [finding["evidence"] for finding in result["findings"]
                    if finding["id"] == "HEAD-01"]
        self.assertTrue(any("1040" in item for item in evidence),
                        "expected the full declaration extent, got %r" % evidence)

    def test_r4_sem_06_impossible_calendar_date_fires(self):
        text = self.mutated(
            "good-en.html",
            ('<time datetime="2026-09-01">', '<time datetime="2026-02-30">'))
        self.assert_rule("SEM-06", self.result_for(text))

    def test_r4_sem_06_impossible_date_time_and_offset_fire(self):
        for value in ("2026-13-01", "2026-01-01T25:00",
                      "2026-01-01T09:30+99:99", "2026", "2026-02"):
            with self.subTest(value=value):
                text = self.mutated(
                    "good-en.html",
                    ('<time datetime="2026-09-01">',
                     '<time datetime="%s">' % value))
                self.assert_rule("SEM-06", self.result_for(text))

    def test_r4_sem_06_valid_forms_still_pass(self):
        for value in ("2026-02-28", "2026-02-28T09:30", "2026-02-28T09:30:45",
                      "2026-02-28T09:30:45.25Z", "2026-02-28 09:30+09:00",
                      "2026-12-31T23:59:59-05:30"):
            with self.subTest(value=value):
                text = self.mutated(
                    "good-en.html",
                    ('<time datetime="2026-09-01">',
                     '<time datetime="%s">' % value))
                result = self.result_for(text)
                self.assertNotIn(
                    "SEM-06",
                    {finding["id"] for finding in result["findings"]})

    def test_r4_ld_12_impossible_calendar_date_fires(self):
        text = self.mutated(
            "good-en.html",
            ('"datePublished": "2026-09-01",',
             '"datePublished": "2026-02-30",'))
        self.assert_rule("LD-12", self.result_for(text))

    def test_r4_ld_12_impossible_time_and_month_fire(self):
        for value in ("2026-13-01T10:00", "2026-01-01T25:00+09:00",
                      "2026-02-30T00:00:00Z"):
            with self.subTest(value=value):
                text = self.mutated(
                    "good-en.html",
                    ('"datePublished": "2026-09-01",',
                     '"datePublished": "%s",' % value))
                self.assert_rule("LD-12", self.result_for(text))

    def test_r5_text_content_interleaves_children_in_source_order(self):
        root = cp.build_tree("<p>On-Page <span>SEO Basics</span>: Titles</p>")
        self.assertEqual(root.find("p").text_content(),
                         "On-Page SEO Basics: Titles")

    def test_r5_h1_with_inline_span_extracts_in_source_order(self):
        text = self.mutated(
            "good-en.html",
            ("<h1>On-Page SEO Basics: Titles, Meta Tags, and Clean Structure</h1>",
             "<h1>On-Page <span>SEO Basics</span>: Titles, Meta Tags, "
             "and Clean Structure</h1>"))
        result = self.result_for(text)
        self.assertEqual(
            result["extracted"]["h1"],
            "On-Page SEO Basics: Titles, Meta Tags, and Clean Structure")
        self.assertNotIn(
            "LD-14", {finding["id"] for finding in result["findings"]})
        bad = [finding for finding in result["findings"]
               if finding["severity"] in ("error", "warn")]
        self.assertEqual(bad, [])


class TestDeepNesting(RuleCase):
    """FU-4: markup and JSON-LD nested far past the interpreter recursion
    limit are walked with explicit stacks, so the CLI keeps its exit
    contract, the JSON report stays parseable, and extracted text keeps
    its source order."""

    DEPTH = 5000

    def run_deep_cli(self, text):
        path = write_temp_page(text, prefix="deep-")
        try:
            return run_checker_cli([path, "--json"])
        finally:
            Path(path).unlink()

    def test_main_with_5000_nested_divs_reports_clean(self):
        text = self.mutated(
            "good-en.html",
            ("  </main>",
             "  %s%s\n  </main>"
             % ("<div>" * self.DEPTH, "</div>" * self.DEPTH)))
        process = self.run_deep_cli(text)
        self.assertNotIn(b"Traceback", process.stderr)
        self.assertEqual(process.returncode, 0)
        report = json.loads(process.stdout.decode("utf-8"))
        self.assertEqual(report["summary"],
                         {"error": 0, "warn": 0, "info": 0, "score": 100})

    def test_h1_in_5000_nested_spans_extracts_in_source_order(self):
        text = self.mutated(
            "good-en.html",
            ("<h1>%s</h1>" % GOOD_EN_TITLE,
             "<h1>%s%s%s</h1>"
             % ("<span>" * self.DEPTH, GOOD_EN_TITLE,
                "</span>" * self.DEPTH)))
        process = self.run_deep_cli(text)
        self.assertNotIn(b"Traceback", process.stderr)
        self.assertEqual(process.returncode, 0)
        report = json.loads(process.stdout.decode("utf-8"))
        self.assertEqual(report["extracted"]["h1"], GOOD_EN_TITLE)
        bad = [finding for finding in report["findings"]
               if finding["severity"] in ("error", "warn")]
        self.assertEqual(bad, [])

    def test_jsonld_nested_5000_levels_fires_ld_01_error(self):
        deep_block = ('<script type="application/ld+json">'
                      + '{"n":' * self.DEPTH + "1" + "}" * self.DEPTH
                      + "</script>")
        text = self.mutated(
            "good-en.html",
            ('<script type="application/ld+json">',
             deep_block + '<script type="application/ld+json">'))
        process = self.run_deep_cli(text)
        self.assertNotIn(b"Traceback", process.stderr)
        self.assertEqual(process.returncode, 1)
        report = json.loads(process.stdout.decode("utf-8"))
        severities = {finding["id"]: finding["severity"]
                      for finding in report["findings"]}
        self.assertEqual(severities.get("LD-01"), "error")
        self.assertEqual(report["summary"]["error"], 1)


class TestAuthorityValidation(RuleCase):
    """Delta re-review round 2, required change 2: the shared URL
    validator checks the complete raw authority - brackets, userinfo,
    and the original port text - instead of the flattened hostname and
    coerced integer port that urlsplit's accessors return."""

    canonical_anchor = ('<link rel="canonical" '
                        'href="https://example.com/guide/seo-basics">')
    og_url_anchor = ('<meta property="og:url" '
                     'content="https://example.com/guide/seo-basics">')

    def page_with_urls(self, url):
        return self.mutated(
            "good-en.html",
            (self.canonical_anchor,
             '<link rel="canonical" href="%s">' % url),
            (self.og_url_anchor,
             '<meta property="og:url" content="%s">' % url))

    def test_shared_validator_rejects_malformed_authorities(self):
        for url in DELTA2_BAD_AUTHORITIES:
            with self.subTest(url=url):
                self.assertFalse(cp.is_absolute_http_url(url), url)

    def test_shared_validator_accepts_valid_authorities(self):
        for url in DELTA2_GOOD_AUTHORITIES:
            with self.subTest(url=url):
                self.assertTrue(cp.is_absolute_http_url(url), url)

    def test_shared_validator_still_rejects_previous_classes(self):
        self.assertFalse(cp.is_absolute_http_url("http://2001:db8::1:443/"))
        self.assertFalse(cp.is_absolute_http_url("https://example.com:0/"))
        self.assertFalse(cp.is_absolute_http_url("https://\ud800.example/"))

    def test_canonical_and_og_url_reject_malformed_authorities(self):
        for url in DELTA2_BAD_AUTHORITIES:
            with self.subTest(url=url):
                result = self.result_for(self.page_with_urls(url))
                self.assert_rule("LINK-01", result)
                self.assert_rule("OG-06", result)

    def test_canonical_and_og_url_cli_exits_1(self):
        path = write_temp_page(
            self.page_with_urls(DELTA2_BAD_AUTHORITIES[0]))
        try:
            process = run_checker_cli([path, "--json"])
        finally:
            Path(path).unlink()
        self.assertEqual(process.returncode, 1)
        self.assertNotIn(b"Traceback", process.stderr)
        report = json.loads(process.stdout.decode("utf-8"))
        severities = {finding["id"]: finding["severity"]
                      for finding in report["findings"]}
        self.assertEqual(severities.get("LINK-01"), "error")
        self.assertEqual(severities.get("OG-06"), "warn")

    def hreflang_page_with_ko_href(self, url):
        canonical_line = ('  <link rel="canonical" '
                          'href="https://example.com/guide/seo-basics">\n')
        hreflang_lines = (
            '  <link rel="alternate" hreflang="en" '
            'href="https://example.com/guide/seo-basics">\n'
            '  <link rel="alternate" hreflang="ko-KR" '
            'href="https://example.com/ko/guide/seo-basics">\n'
            '  <link rel="alternate" hreflang="x-default" '
            'href="https://example.com/guide/seo-basics">\n')
        complete = self.mutated(
            "good-en.html", (canonical_line, canonical_line + hreflang_lines))
        self.assertEqual(self.result_for(complete)["summary"]["warn"], 0)
        broken = complete.replace(
            'hreflang="ko-KR" href="https://example.com/ko/guide/seo-basics"',
            'hreflang="ko-KR" href="%s"' % url)
        self.assertNotEqual(broken, complete)
        return broken

    def test_hreflang_href_rejects_malformed_authorities(self):
        for url in DELTA2_BAD_AUTHORITIES:
            with self.subTest(url=url):
                self.assert_rule(
                    "LINK-02", self.result_for(self.hreflang_page_with_ko_href(url)))

    def test_ld13_article_image_shapes_reject_malformed_authority(self):
        image_anchor = '"image": "https://example.com/images/seo-basics.png",'
        shapes = ('"https://[2001:db8::1]junk/"',
                  '["https://[2001:db8::1]junk/"]',
                  '{"@id": "https://[2001:db8::1]junk/"}',
                  '[{"url": "https://[2001:db8::1]junk/"}]')
        for shape in shapes:
            with self.subTest(shape=shape):
                text = self.mutated(
                    "good-en.html",
                    (image_anchor, '"image": %s,' % shape))
                self.assert_rule("LD-13", self.result_for(text))

    def test_ld13_article_image_rejects_every_malformed_authority(self):
        image_anchor = '"image": "https://example.com/images/seo-basics.png",'
        for url in DELTA2_BAD_AUTHORITIES:
            with self.subTest(url=url):
                text = self.mutated(
                    "good-en.html",
                    (image_anchor, '"image": "%s",' % url))
                self.assert_rule("LD-13", self.result_for(text))

    def test_authority_positive_controls_stay_clean(self):
        for url in DELTA2_GOOD_AUTHORITIES:
            with self.subTest(url=url):
                result = self.result_for(self.page_with_urls(url))
                bad = [finding for finding in result["findings"]
                       if finding["severity"] in ("error", "warn")]
                self.assertEqual(bad, [])

    def test_shared_validator_rejects_zone_identifier_literals(self):
        for url in DELTA3_ZONE_AUTHORITIES:
            with self.subTest(url=url):
                self.assertFalse(cp.is_absolute_http_url(url), url)

    def test_shared_validator_keeps_pure_ipv6_literals_valid(self):
        self.assertTrue(cp.is_absolute_http_url("https://[2001:db8::1]:443/path"))
        self.assertTrue(cp.is_absolute_http_url("https://[::1]/"))
        self.assertTrue(cp.is_absolute_http_url("https://[::ffff:192.0.2.1]:80/"))

    def test_canonical_and_og_url_reject_zone_identifiers(self):
        for url in DELTA3_ZONE_AUTHORITIES:
            with self.subTest(url=url):
                result = self.result_for(self.page_with_urls(url))
                self.assert_rule("LINK-01", result)
                self.assert_rule("OG-06", result)

    def test_canonical_and_og_url_cli_rejects_zone_identifier(self):
        path = write_temp_page(self.page_with_urls(DELTA3_ZONE_AUTHORITIES[0]))
        try:
            process = run_checker_cli([path, "--json"])
        finally:
            Path(path).unlink()
        self.assertEqual(process.returncode, 1)
        self.assertNotIn(b"Traceback", process.stderr)
        report = json.loads(process.stdout.decode("utf-8"))
        severities = {finding["id"]: finding["severity"]
                      for finding in report["findings"]}
        self.assertEqual(severities.get("LINK-01"), "error")
        self.assertEqual(severities.get("OG-06"), "warn")

    def test_hreflang_href_rejects_zone_identifiers(self):
        for url in DELTA3_ZONE_AUTHORITIES:
            with self.subTest(url=url):
                self.assert_rule(
                    "LINK-02", self.result_for(self.hreflang_page_with_ko_href(url)))

    def test_ld13_article_image_shapes_reject_zone_identifier(self):
        image_anchor = '"image": "https://example.com/images/seo-basics.png",'
        zone = DELTA3_ZONE_AUTHORITIES[0]
        shapes = ('"%s"' % zone,
                  '["%s"]' % zone,
                  '{"@id": "%s"}' % zone,
                  '[{"@id": "%s"}]' % zone,
                  '{"url": "%s"}' % zone,
                  '[{"url": "%s"}]' % zone)
        for shape in shapes:
            with self.subTest(shape=shape):
                text = self.mutated(
                    "good-en.html",
                    (image_anchor, '"image": %s,' % shape))
                self.assert_rule("LD-13", self.result_for(text))

    def test_shared_validator_accepts_zero_padded_ports(self):
        for url in DELTA3_PADDED_GOOD_AUTHORITIES:
            with self.subTest(url=url):
                self.assertTrue(cp.is_absolute_http_url(url), url)

    def test_shared_validator_rejects_zero_value_and_oversized_padded_ports(self):
        for url in DELTA3_PADDED_BAD_AUTHORITIES:
            with self.subTest(url=url):
                self.assertFalse(cp.is_absolute_http_url(url), url)

    def test_canonical_and_og_url_stay_clean_for_padded_ports(self):
        for url in DELTA3_PADDED_GOOD_AUTHORITIES:
            with self.subTest(url=url):
                result = self.result_for(self.page_with_urls(url))
                bad = [finding for finding in result["findings"]
                       if finding["severity"] in ("error", "warn")]
                self.assertEqual(bad, [])

    def test_canonical_and_og_url_cli_accepts_5000_zero_padded_port(self):
        url = "https://example.com:" + "0" * 5000 + "443/"
        path = write_temp_page(self.page_with_urls(url))
        try:
            process = run_checker_cli([path, "--json"])
        finally:
            Path(path).unlink()
        self.assertEqual(process.returncode, 0)
        self.assertNotIn(b"Traceback", process.stderr)
        report = json.loads(process.stdout.decode("utf-8"))
        pairs = {(finding["id"], finding["severity"])
                 for finding in report["findings"]}
        self.assertNotIn(("LINK-01", "error"), pairs)
        self.assertNotIn(("OG-06", "warn"), pairs)


class TestSafeReportOutput(RuleCase):
    """Delta re-review round 2, required change 1: printing the report
    (JSON and text mode, and the stderr file-echo messages) never raises
    on content the stream encoding cannot represent - a lone surrogate
    inside a finding, Korean text under an ASCII stdout encoding - and
    the JSON stays parseable UTF-8 with severities unchanged."""

    surrogate_image = ('"image": "https://example.com/images/seo-basics.png",',
                       '"image": "https://\\ud800.example/",')

    def surrogate_page(self):
        # The ld+json block carries the literal escape \ud800; json.loads
        # turns it into a lone surrogate inside the emitted LD-13 finding.
        return self.mutated("good-en.html", self.surrogate_image)

    def run_surrogate_cli(self, *args):
        path = write_temp_page(self.surrogate_page())
        try:
            # A strict UTF-8 stdout reproduces the crash surface: the raw
            # surrogate must never reach the stream encoder.
            return run_checker_cli([path] + list(args),
                                   {"PYTHONIOENCODING": "utf-8"})
        finally:
            Path(path).unlink()

    def test_surrogate_finding_json_mode_exits_0_with_ld13_warn(self):
        process = self.run_surrogate_cli("--json")
        self.assertEqual(process.returncode, 0)
        self.assertNotIn(b"Traceback", process.stderr)
        report = json.loads(process.stdout.decode("utf-8"))
        severities = {finding["id"]: finding["severity"]
                      for finding in report["findings"]}
        self.assertEqual(severities.get("LD-13"), "warn")
        self.assertEqual(report["summary"],
                         {"error": 0, "warn": 1, "info": 0, "score": 97})

    def test_surrogate_finding_json_mode_strict_exits_1(self):
        process = self.run_surrogate_cli("--json", "--strict")
        self.assertEqual(process.returncode, 1)
        self.assertNotIn(b"Traceback", process.stderr)
        report = json.loads(process.stdout.decode("utf-8"))
        severities = {finding["id"]: finding["severity"]
                      for finding in report["findings"]}
        self.assertEqual(severities.get("LD-13"), "warn")

    def test_surrogate_finding_text_mode_exits_0(self):
        process = self.run_surrogate_cli()
        self.assertEqual(process.returncode, 0)
        self.assertNotIn(b"Traceback", process.stderr)
        text = process.stdout.decode("utf-8")
        self.assertIn("WARN LD-13 line", text)
        self.assertIn("summary: file=", text)

    def test_surrogate_finding_text_mode_strict_exits_1(self):
        process = self.run_surrogate_cli("--strict")
        self.assertEqual(process.returncode, 1)
        self.assertNotIn(b"Traceback", process.stderr)
        self.assertIn("WARN LD-13 line", process.stdout.decode("utf-8"))

    def test_ascii_stdout_keeps_json_utf8_and_korean_intact(self):
        process = run_checker_cli(
            [FIXTURES_DIR / "good-ko.html", "--json"],
            {"PYTHONIOENCODING": "ascii"})
        self.assertEqual(process.returncode, 0)
        self.assertNotIn(b"Traceback", process.stderr)
        report = json.loads(process.stdout.decode("utf-8"))
        self.assertEqual(report["extracted"]["title"], GOOD_KO_TITLE)
        self.assertEqual(report["summary"]["error"], 0)
        self.assertEqual(report["summary"]["warn"], 0)

    def test_ascii_stdout_text_mode_prints_korean_finding_text(self):
        # Text mode prints each finding's message; H-03 echoes the heading
        # text itself, so an ASCII stdout must still receive the Hangul.
        text = self.mutated(
            "good-ko.html",
            ("<h2>\uba54\ud0c0 \uc815\ubcf4\ub97c \uba3c\uc800 \uc815\ub9ac\ud558\uc138\uc694</h2>",
             "<h2>\uac00\ub098</h2>"))
        path = write_temp_page(text)
        try:
            process = run_checker_cli([path], {"PYTHONIOENCODING": "ascii"})
        finally:
            Path(path).unlink()
        self.assertEqual(process.returncode, 0)
        self.assertNotIn(b"Traceback", process.stderr)
        out = process.stdout.decode("utf-8")
        self.assertIn("WARN H-03 line", out)
        self.assertIn("\uac00\ub098", out)
        self.assertIn("summary: file=", out)

    def test_cannot_read_echoes_utf8_name_on_ascii_stderr(self):
        process = run_checker_cli(
            [FIXTURES_DIR / "\ud398\uc774\uc9c0-\uc5c6\uc74c.html"],
            {"PYTHONIOENCODING": "ascii:strict"})
        self.assertEqual(process.returncode, 2)
        self.assertNotIn(b"Traceback", process.stderr)
        err = process.stderr.decode("utf-8")
        self.assertIn("cannot read", err)
        self.assertIn("\ud398\uc774\uc9c0-\uc5c6\uc74c", err)


class TestRobustnessBoundary(RuleCase):
    """Owner scope addition A and C: one check failing unexpectedly
    degrades to an internal-error info finding instead of a traceback,
    and seeded page mutations never break the JSON report or its exit
    contract."""

    def run_main(self, text, *args):
        """Run the CLI main() entry in-process on a temp file; return
        (exit code, parsed JSON report) with stdout captured."""
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False, encoding="utf-8") as handle:
            handle.write(text)
            path = handle.name
        try:
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = cp.main([path, "--json"] + list(args))
            return code, json.loads(buffer.getvalue())
        finally:
            Path(path).unlink()

    def test_a_forced_check_exception_yields_internal_error_finding(self):
        text = fixture_text("good-en.html")
        with unittest.mock.patch.object(
                cp.PageChecker, "check_twitter",
                side_effect=RuntimeError("boom")):
            result = self.result_for(text)
        self.assertEqual(len(result["findings"]), 1)
        finding = result["findings"][0]
        self.assertEqual(finding["id"], "TW-01")
        self.assertEqual(finding["severity"], "info")
        self.assertTrue(finding["message"].startswith(
            "internal error: RuntimeError"))
        self.assertEqual(result["summary"]["error"], 0)
        self.assertEqual(result["summary"]["info"], 1)

    def test_a_forced_check_exception_main_prints_parseable_json(self):
        text = fixture_text("good-en.html")
        with unittest.mock.patch.object(
                cp.PageChecker, "check_semantic",
                side_effect=KeyError("burst")):
            code, report = self.run_main(text)
        self.assertIn(code, (0, 1))
        self.assertEqual(code, 0)
        internal = [finding for finding in report["findings"]
                    if finding["message"].startswith("internal error:")]
        self.assertEqual(len(internal), 1)
        self.assertEqual(internal[0]["id"], "SEM-01")
        self.assertEqual(internal[0]["severity"], "info")
        self.assertIn("KeyError", internal[0]["message"])
        self.assertEqual(report["summary"]["error"], 0)

    def test_a_json_report_parses_for_extreme_dimension_inputs(self):
        cases = [
            self.mutated(
                "good-en.html",
                ('<meta property="og:image:width" content="1200">',
                 '<meta property="og:image:width" content="%s">' % ("9" * 400)),
                ('<meta property="og:image:height" content="630">',
                 '<meta property="og:image:height" content="%s">' % ("9" * 400))),
            self.mutated(
                "good-en.html",
                ('width="1200" height="675"',
                 'width="%s" height="675"' % ("9" * 400))),
        ]
        for text in cases:
            with self.subTest():
                code, report = self.run_main(text)
                self.assertIn(code, (0, 1))
                self.assertEqual(code, 0)
                self.assertEqual(report["summary"]["error"], 0)

    def test_c_seeded_fuzz_mutations_always_yield_parseable_json(self):
        rng = random.Random(20261014)
        sources = (fixture_text("good-en.html"), fixture_text("good-ko.html"))
        specials = ("\u2028", "\u2029", "\u0085", "\r", "\r\n", "\x00",
                    "9" * 400, "0" * 400 + "7", "<!--", "<meta charset=",
                    'content="', "utf-8", "\uac00", "\u00e9", "&amp;", "&#0;")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fuzz.html"
            for index in range(200):
                text = rng.choice(sources)
                for _ in range(rng.randint(1, 6)):
                    if not text:
                        break
                    start = rng.randrange(len(text))
                    operation = rng.randint(0, 2)
                    if operation == 0:      # insert
                        text = text[:start] + rng.choice(specials) + text[start:]
                    else:
                        stop = min(len(text), start + rng.randint(1, 40))
                        if operation == 1:  # delete
                            text = text[:start] + text[stop:]
                        else:               # replace
                            text = text[:start] + rng.choice(specials) + text[stop:]
                path.write_text(text, encoding="utf-8")
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    code = cp.main([str(path), "--json"])
                with self.subTest(index=index):
                    self.assertIn(code, (0, 1))
                    report = json.loads(buffer.getvalue())
                    self.assertEqual(
                        set(report),
                        {"file", "lang", "summary", "findings", "extracted"})


class TestUnionCoverage(RuleCase):

    def test_every_rule_has_a_failing_case(self):
        missing = set(cp.RULES) - ASSERTED_IDS
        self.assertEqual(
            missing, set(),
            "rules never asserted on a failing input: %r" % sorted(missing))


if __name__ == "__main__":
    unittest.main()
