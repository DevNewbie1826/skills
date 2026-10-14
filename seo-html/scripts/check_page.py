#!/usr/bin/env python3
"""Static SEO checker for one complete HTML page.

Checks a single static page against the rule catalog of the seo-html skill:
head metadata, Open Graph and Twitter cards, semantic structure, headings,
JSON-LD structured data, images, links, accessibility and performance hints,
and a few content-shape signals. Standard library only; runs on Python 3.9
and later.

Length windows use a weighted display width: characters that render East
Asian Wide or Fullwidth count 2.0 units, everything else 1.0, measured after
whitespace collapse, with one window for every language.

Usage:
    python3 check_page.py PAGE.html [--json] [--strict]
        [--lang ko|en|auto] [--keyword K] [--allow-noindex]

Exit codes:
    0  no error (and no warning with --strict)
    1  error present (or warning present with --strict)
    2  unreadable or undecodable file, or a usage error
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import re
import sys
import unicodedata
from datetime import date, time
from html.parser import HTMLParser
from urllib.parse import urlsplit

# Thresholds (module constants; tests import them).

WIDE_WEIGHT = 2.0
TITLE_WIDTH = (50, 60)
DESCRIPTION_WIDTH = (150, 160)
THIN_MIN_CHARS = 300
KEYWORD_DENSITY = (1.0, 3.0)
ALT_MAX = 125
OG_IMAGE_MIN = (150, 150)
OG_IMAGE_MAX_RATIO = 3.0
OG_IMAGE_RECOMMENDED = (1200, 630)
MAX_DIMENSION = 100000
CHARSET_MAX_BYTES = 1024
HANGUL_RATIO = 0.3

# Rule registry: rule id -> severity ("error" / "warn" / "info"). Each
# comment is the rule statement from the binding catalog.
RULES = {
    # head metadata
    "HEAD-01": "error",   # <meta charset> utf-8 within first 1024 bytes
    "HEAD-02": "error",   # viewport contains width=device-width
    "HEAD-03": "error",   # exactly one non-empty <title>
    "HEAD-04": "warn",    # title width inside TITLE_WIDTH units
    "HEAD-05": "error",   # exactly one non-empty meta description
    "HEAD-06": "warn",    # description width inside DESCRIPTION_WIDTH units
    "HEAD-07": "error",   # robots meta contains noindex/none (info with --allow-noindex)
    "HEAD-08": "info",    # icon link and theme-color present
    "HEAD-09": "error",   # <html lang> present; matches --lang when explicit
    "HEAD-10": "warn",    # description equals the title (Naver)
    "HEAD-11": "info",    # robots meta contains nosourceinfo (Naver)
    # Open Graph
    "OG-01": "error",     # og:title, og:type, og:image, og:url present
    "OG-02": "warn",      # og:description present
    "OG-03": "warn",      # og:image present without og:image:alt
    "OG-04": "warn",      # og:image dimensions under 150x150 or ratio over 3:1
    "OG-05": "info",      # og:site_name/og:locale present, locale matches lang
    "OG-06": "warn",      # og:url equals the canonical URL
    "OG-07": "info",      # og:image dimensions at least 1200x630 (recommended)
    # Twitter card
    "TW-01": "warn",      # twitter:card present and a known card type
    "TW-02": "info",      # twitter:title/description/image present (OG fallback)
    # semantic structure
    "SEM-01": "error",    # exactly one <main>
    "SEM-02": "warn",     # <header>, <footer>, <article> each present
    "SEM-03": "info",     # <nav> present
    "SEM-04": "warn",     # no div/span with onclick
    "SEM-05": "info",     # <figure> has a <figcaption>
    "SEM-06": "warn",     # <time> has a valid ISO 8601 datetime
    # headings
    "H-01": "error",      # exactly one <h1>
    "H-02": "warn",       # no heading level skip
    "H-03": "warn",       # headings not empty, digits-only, or <= 2 code points
    # JSON-LD
    "LD-01": "error",     # every ld+json block parses; at least one block exists
    "LD-02": "error",     # @context on top-level nodes (http:// form -> warn)
    "LD-03": "error",     # every node has @type (except @graph containers)
    "LD-04": "error",     # @graph is a list
    "LD-05": "error",     # no placeholder text in any JSON-LD string
    "LD-06": "error",     # no phased-out rich-result types
    "LD-07": "info",      # FAQPage present (no rich result since 2026-05-07)
    "LD-08": "warn",      # Article family carries headline/author/dates/image
    "LD-09": "error",     # BreadcrumbList ListItems have position + name (+ item)
    "LD-10": "error",     # Product has name and one of offers/review/aggregateRating
    "LD-11": "warn",      # Organization/WebSite have name and url
    "LD-12": "warn",      # date fields are ISO 8601
    "LD-13": "warn",      # url/@id/item/image/logo values are absolute http(s)
    "LD-14": "warn",      # Article headline / WebPage name visible in title or h1
    # images
    "IMG-01": "error",    # every <img> has an alt attribute
    "IMG-02": "warn",     # alt text length and shape
    "IMG-03": "warn",     # <img> declares width and height
    "IMG-04": "info",     # first <img> in <main> has loading="lazy"
    # links
    "LINK-01": "error",   # exactly one canonical, absolute http(s)
    "LINK-02": "warn",    # hreflang set complete and valid (no x-default -> info)
    "LINK-03": "warn",    # anchor text is descriptive
    "LINK-04": "info",    # no <a> with empty or "#" href
    # accessibility and performance
    "A11Y-01": "warn",    # form controls have an accessible name
    "PERF-01": "info",    # head scripts with src load async/defer/module
    # content shape
    "CONT-01": "error",   # visible text inside <main> is not thin
    "CONT-02": "warn",    # keyword density inside the window with --keyword
    "CONT-03": "info",    # statistics in a paragraph carry a source link
}

# Types phased out of rich results; Book with ReadAction/BorrowAction is
# folded into the same finding in the checker below.
PHASED_OUT_TYPES = ("HowTo", "ClaimReview", "CourseInfo", "EstimatedSalary", "LearningVideo", "SpecialAnnouncement", "VehicleListing")
ARTICLE_TYPES = ("Article", "BlogPosting", "NewsArticle")
ARTICLE_REQUIRED = ("headline", "author", "datePublished", "dateModified", "image")
DATE_KEYS = ("datePublished", "dateModified", "startDate", "uploadDate")
URL_KEYS = ("url", "@id", "item", "image", "logo")
ROBOTS_META_NAMES = ("robots", "googlebot", "yeti")
TWITTER_CARD_TYPES = ("summary", "summary_large_image", "app", "player")
BAD_ANCHOR_TEXTS = ("click here", "here", "read more", "more", "여기", "클릭", "여기를 클릭", "더보기", "자세히")

WS_RE = re.compile(r"\s+")
VIEWPORT_RE = re.compile(r"width\s*=\s*device-width", re.IGNORECASE)
ASCII_INT_RE = re.compile(r"^[0-9]+$")
HOST_LABEL_RE = re.compile(r"[A-Za-z0-9-]+")
HREFLANG_RE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z][A-Za-z0-9]{1,7})*$")
ISO_8601_RE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})"
    r"(?:[T ](\d{2}):(\d{2})(?::(\d{2})(\.\d+)?)?"
    r"(Z|[+-]\d{2}:?\d{2})?)?$"
)
FILENAME_LIKE_RE = re.compile(r"\.(?:jpe?g|png|gif|webp|avif|svg|bmp|ico)\b", re.IGNORECASE)
# Number followed by a percent sign or a magnitude unit, in either language.
STAT_RE = re.compile(
    r"\d+(?:\.\d+)?\s*(?:%|million|billion|trillion|thousand|명|개|건|만|억|천|원|달러|배)",
    re.IGNORECASE,
)
# Placeholder shapes inside JSON-LD strings: "[Business Name]"-style bracket
# tokens, REPLACE_* / TODO markers, lorem ipsum, and unfilled {{TOKEN}} slots.
PLACEHOLDER_RES = (
    re.compile(r"\[[A-Za-z][^\[\]\n]{0,80}\]"),
    re.compile(r"\bREPLACE(?:_[A-Z0-9]+)*\b"),
    re.compile(r"\bTODO\b"),
    re.compile(r"lorem ipsum", re.IGNORECASE),
    re.compile(r"\{\{[A-Z_][A-Z0-9_]*\}\}"),
)

VOID_ELEMENTS = frozenset(
    ("area", "base", "br", "col", "embed", "hr", "img", "input", "link",
     "meta", "param", "source", "track", "wbr")
)
SKIP_TEXT_TAGS = frozenset(("script", "style", "noscript", "template"))


def collapse_ws(value):
    return WS_RE.sub(" ", value).strip()


def normalize_text(value):
    return collapse_ws(value).casefold()


def display_width(value):
    """Weighted display width: East Asian Wide/Fullwidth count WIDE_WEIGHT
    units, every other character 1.0."""
    return sum(WIDE_WEIGHT if unicodedata.east_asian_width(ch) in ("W", "F")
               else 1.0 for ch in value)


def width_units(value):
    return int(round(display_width(collapse_ws(value))))


def is_hangul_letter(ch):
    return ("\uac00" <= ch <= "\ud7a3" or "\u1100" <= ch <= "\u11ff"
            or "\u3130" <= ch <= "\u318f")


def parse_dimension(value):
    """Parse a declared pixel dimension (og:image:width/height, img
    width/height). Only plain ASCII digit strings up to MAX_DIMENSION
    pixels are usable; anything else ("", "12px", "-5", "1e3", digit
    lookalikes such as the superscript two, or a magnitude above
    MAX_DIMENSION) is unusable and counts as not declared. Digit strings
    are compared by length after stripping leading zeros, so arbitrarily
    long values never reach a numeric conversion."""
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not ASCII_INT_RE.match(text):
        return None
    digits = text.lstrip("0") or "0"
    if len(digits) > len(str(MAX_DIMENSION)):
        return None
    number = int(digits)
    return number if number <= MAX_DIMENSION else None


def is_valid_host(host):
    """True when host is a usable unbracketed http(s) destination host: a
    dotted IPv4 literal accepted by ipaddress, or a dotted host whose
    labels are 1-63 characters of letters, digits, and hyphens with no
    empty labels (no whitespace or other out-of-label characters).
    Internationalized hosts are validated on their IDNA-encoded ASCII
    form; one optional trailing root dot is allowed. IPv6 literals are
    authority hosts only inside brackets, where is_valid_authority
    checks them with ipaddress.IPv6Address, so a colon-bearing host
    text never passes the label checks here."""
    if not host:
        return False
    try:
        ipaddress.IPv4Address(host)
        return True
    except ValueError:
        pass
    if not host.isascii():
        try:
            host = host.encode("idna").decode("ascii")
        except (UnicodeError, ValueError):
            return False
    if host.endswith("."):
        host = host[:-1]
    if not host:
        return False
    for label in host.split("."):
        if not 1 <= len(label) <= 63 or not HOST_LABEL_RE.fullmatch(label):
            return False
    return True


def _is_valid_port_text(port_text):
    """True when the text after ":" is an absent or usable port: empty
    text counts as no port (RFC 3986 allows one), otherwise 1-5 ASCII
    digits only - no sign, no whitespace, no digit lookalikes such as
    full-width digits, which int() would accept - with a value in
    1-65535."""
    if not port_text:
        return True
    if len(port_text) > 5 or not ASCII_INT_RE.fullmatch(port_text):
        return False
    return 1 <= int(port_text) <= 65535


def is_valid_authority(netloc):
    """True when the complete raw authority is usable. urlsplit's
    .hostname and .port accessors discard the bracket, userinfo, and
    original port text, so the netloc is validated as-is here: optional
    userinfo up to the last "@"; then either a bracketed IP literal,
    which must be exactly "[" + a valid IPv6 address (ipaddress.IPv6Address
    rejects bracketed IPv4 and DNS names) + nothing or ":" + port, or an
    unbracketed host (see is_valid_host) + nothing or ":" + port."""
    if not netloc:
        return False
    _, _, hostinfo = netloc.rpartition("@")
    if not hostinfo:
        return False
    if hostinfo.startswith("["):
        literal, bracket, tail = hostinfo.partition("]")
        if not bracket:
            return False            # unterminated IP literal
        try:
            ipaddress.IPv6Address(literal[1:])
        except ValueError:
            return False            # bracketed IPv4/DNS name or bad IPv6
        if not tail:
            return True
        if not tail.startswith(":"):
            return False            # junk after the closing bracket
        return _is_valid_port_text(tail[1:])
    if ":" in hostinfo:
        host, _, port_text = hostinfo.rpartition(":")
    else:
        host, port_text = hostinfo, ""
    if not _is_valid_port_text(port_text):
        return False
    return is_valid_host(host)


def is_absolute_http_url(value):
    """True when value is an absolute http(s) URL with a usable authority:
    an http/https scheme plus a complete, syntactically valid authority
    in the raw netloc (see is_valid_authority; brackets, userinfo, and
    port text are checked intact). A bare scheme such as "https://" is
    not a URL."""
    if not isinstance(value, str):
        return False
    try:
        parts = urlsplit(value.strip())
    except ValueError:
        return False
    if parts.scheme not in ("http", "https"):
        return False
    return is_valid_authority(parts.netloc)


def is_valid_iso8601(value):
    """True when value is an ISO 8601 date or date-time with real calendar
    values. The regex fixes the shape; this rejects impossible dates
    (2026-02-30, 2026-13-01), impossible times (25:00), and out-of-range
    offsets (+99:99)."""
    if not isinstance(value, str):
        return False
    match = ISO_8601_RE.match(value.strip())
    if match is None:
        return False
    try:
        date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return False
    if match.group(4) is None:
        return True
    zone = match.group(8)
    if zone not in (None, "Z"):
        offset_hours = int(zone[1:3])
        offset_minutes = int(zone[-2:])
        if offset_hours > 23 or offset_minutes > 59:
            return False
    try:
        time(int(match.group(4)), int(match.group(5)),
             int(match.group(6) or 0))
    except ValueError:
        return False
    return True


class Node:
    """One element: position, attributes, children, and direct text chunks."""

    __slots__ = ("tag", "attrs", "line", "col", "children", "parent", "parts")

    def __init__(self, tag, attrs, line, col):
        self.tag = tag
        self.attrs = {}
        for name, value in attrs or ():
            name = name.lower()
            if name not in self.attrs:
                self.attrs[name] = value if value is not None else ""
        self.line = line
        self.col = col
        self.children = []
        self.parent = None
        self.parts = []

    def iter_tree(self):
        yield self
        for child in self.children:
            yield from child.iter_tree()

    def find_all(self, tag):
        for node in self.iter_tree():
            if node.tag == tag:
                yield node

    def find(self, tag):
        for node in self.find_all(tag):
            return node
        return None

    def text_content(self, skip=SKIP_TEXT_TAGS):
        """Visible text of this element in source order: direct text
        chunks interleaved with child elements as the markup orders them."""
        if self.tag in skip:
            return ""
        parts = []
        for part in self.parts:
            if isinstance(part, str):
                parts.append(part)
            else:
                parts.append(part.text_content(skip))
        return "".join(parts)

    def has_ancestor(self, tags):
        node = self.parent
        while node is not None:
            if node.tag in tags:
                return True
            node = node.parent
        return False

    def has_descendant(self, tags):
        for node in self.iter_tree():
            if node is not self and node.tag in tags:
                return True
        return False


class TreeBuilder(HTMLParser):
    """Lenient tree builder: unmatched end tags are ignored, stray end tags
    never crash the parse, and void elements never enter the stack."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", (), 1, 0)
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        line, col = self.getpos()
        node = Node(tag, attrs, line, col)
        node.parent = self.stack[-1]
        self.stack[-1].children.append(node)
        self.stack[-1].parts.append(node)
        if tag not in VOID_ELEMENTS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        line, col = self.getpos()
        node = Node(tag, attrs, line, col)
        node.parent = self.stack[-1]
        self.stack[-1].children.append(node)
        self.stack[-1].parts.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data):
        self.stack[-1].parts.append(data)


def build_tree(text):
    builder = TreeBuilder()
    try:
        builder.feed(text)
        builder.close()
    except Exception:
        # Malformed markup must degrade to a partial tree, never crash.
        pass
    return builder.root


def ld_scripts(root):
    """Every ld+json script node, in document order. The type attribute is
    compared case-insensitively; other attributes are ignored."""
    return [script for script in root.find_all("script")
            if script.attrs.get("type", "").strip().lower() == "application/ld+json"]


def node_types(node):
    value = node.get("@type")
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def iter_ld_nodes(obj, top_level=True):
    """Yield (value, is_top_level) for root objects and @graph members;
    non-object values are yielded as-is so the caller can report them."""
    if isinstance(obj, dict):
        yield obj, top_level
        graph = obj.get("@graph")
        if isinstance(graph, list):
            for member in graph:
                yield from iter_ld_nodes(member, top_level=False)
    elif isinstance(obj, list):
        for member in obj:
            yield from iter_ld_nodes(member, top_level=top_level)
    else:
        yield obj, top_level


def iter_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_strings(item)


def placeholder_in_node(node):
    """First placeholder match among the node's strings; @graph is skipped
    because its members are scanned as nodes of their own."""
    for key, value in node.items():
        if key == "@graph":
            continue
        for text in iter_strings(value):
            for pattern in PLACEHOLDER_RES:
                match = pattern.search(text)
                if match:
                    return match.group(0)
    return None


def absolute_url_violations(node):
    """Yield (key, value) where a url-shaped property holds a string that is
    not an absolute http(s) URL (scheme http/https plus a non-empty host);
    dicts are followed into their url/@id."""
    for key in URL_KEYS:
        if key not in node:
            continue
        value = node[key]
        if isinstance(value, str):
            if not is_absolute_http_url(value):
                yield key, value
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    if not is_absolute_http_url(item):
                        yield key, item
                elif isinstance(item, dict):
                    inner = item.get("url") if isinstance(item.get("url"), str) \
                        else item.get("@id")
                    if isinstance(inner, str) and not is_absolute_http_url(inner):
                        yield key, inner
        elif isinstance(value, dict):
            inner = value.get("url") if isinstance(value.get("url"), str) \
                else value.get("@id")
            if isinstance(inner, str) and not is_absolute_http_url(inner):
                yield key, inner


class PageChecker:
    """Runs every rule in RULES over one parsed page."""

    # Checks in run order, each paired with the catalog ID that owns its
    # finding group; the owner ID attributes an internal error when a
    # check itself fails on unexpected input.
    CHECK_STEPS = (
        ("check_head", "HEAD-01"),
        ("check_open_graph", "OG-01"),
        ("check_twitter", "TW-01"),
        ("check_semantic", "SEM-01"),
        ("check_headings", "H-01"),
        ("check_jsonld", "LD-01"),
        ("check_images", "IMG-01"),
        ("check_links", "LINK-01"),
        ("check_a11y", "A11Y-01"),
        ("check_perf", "PERF-01"),
        ("check_content", "CONT-01"),
    )

    def __init__(self, text, file_label, lang_arg="auto", keyword=None,
                 allow_noindex=False):
        self.text = text
        self.file_label = file_label
        self.lang_arg = lang_arg
        self.keyword = keyword
        self.allow_noindex = allow_noindex
        self.root = build_tree(text)
        self.findings = []
        self.lang = "en"
        self.og = {}
        self.twitter = {}
        self.canonical_href = None
        self.extracted_title = ""
        self.extracted_h1 = ""
        self._jsonld_types = []
        # html.parser counts only "\n" as a line separator (updatepos),
        # so line starts are computed the same way here; str.splitlines()
        # would also break at \r, \u2028 and friends and desynchronize
        # char_offset() from the parser's reported positions.
        starts = [0]
        for match in re.finditer(r"\n", text):
            starts.append(match.end())
        self.line_starts = starts

    def emit(self, rule_id, line, message, evidence, fix, severity=None):
        self.findings.append({
            "id": rule_id,
            "severity": severity if severity is not None else RULES[rule_id],
            "line": max(1, int(line or 1)),
            "message": message,
            "evidence": collapse_ws(str(evidence))[:160] or "-",
            "fix": fix,
        })

    def char_offset(self, node):
        """Zero-based character offset of the node's "<" in the source."""
        if node.line - 1 < len(self.line_starts):
            return self.line_starts[node.line - 1] + node.col
        return 0

    def byte_offset(self, node):
        return len(self.text[:self.char_offset(node)].encode("utf-8"))

    def tag_end_byte(self, node):
        """UTF-8 byte offset one past the ">" that closes the node's start
        tag, honoring quoted attribute values; the document length when no
        closing ">" exists."""
        index = self.char_offset(node)
        quote = None
        while index < len(self.text):
            char = self.text[index]
            if quote is not None:
                if char == quote:
                    quote = None
            elif char in ('"', "'"):
                quote = char
            elif char == ">":
                return len(self.text[:index + 1].encode("utf-8"))
            index += 1
        return len(self.text.encode("utf-8"))

    def resolve_lang(self):
        if self.lang_arg in ("ko", "en"):
            return self.lang_arg
        html_tag = self.root.find("html")
        declared = html_tag.attrs.get("lang", "").strip() if html_tag is not None else ""
        if declared:
            primary = declared.lower().split("-")[0]
            if primary in ("ko", "en"):
                return primary
        body = self.root.find("body")
        source = body if body is not None else self.root
        letters = [ch for ch in source.text_content()
                   if unicodedata.category(ch).startswith("L")]
        if not letters:
            return "en"
        hangul = sum(1 for ch in letters if is_hangul_letter(ch))
        return "ko" if hangul / len(letters) > HANGUL_RATIO else "en"

    def check_head(self):
        metas = list(self.root.find_all("meta"))

        charset_node = None
        charset_value = ""
        for meta in metas:
            if "charset" in meta.attrs:
                charset_node, charset_value = meta, meta.attrs["charset"]
                break
            if meta.attrs.get("http-equiv", "").strip().lower() == "content-type":
                match = re.search(r"charset\s*=\s*([\w.+-]+)",
                                  meta.attrs.get("content", ""), re.IGNORECASE)
                if match:
                    charset_node, charset_value = meta, match.group(1)
                    break
        if charset_node is None:
            self.emit("HEAD-01", 1, "no utf-8 charset declaration found",
                      "no <meta charset> or Content-Type charset",
                      'add <meta charset="utf-8"> as the first element of <head>')
        elif charset_value.strip().lower() not in ("utf-8", "utf8"):
            self.emit("HEAD-01", charset_node.line, "charset is not utf-8",
                      'charset="%s"' % charset_value,
                      'declare utf-8: <meta charset="utf-8">')
        elif self.tag_end_byte(charset_node) > CHARSET_MAX_BYTES:
            self.emit("HEAD-01", charset_node.line,
                      "charset declaration ends beyond the first %d bytes"
                      % CHARSET_MAX_BYTES,
                      "declaration ends at byte %d"
                      % self.tag_end_byte(charset_node),
                      'move <meta charset="utf-8"> to the top of <head>, '
                      "before any long comment")

        if not any(meta.attrs.get("name", "").strip().lower() == "viewport"
                   and VIEWPORT_RE.search(meta.attrs.get("content", ""))
                   for meta in metas):
            self.emit("HEAD-02", 1, "viewport meta missing width=device-width",
                      "no usable <meta name=viewport>",
                      'add <meta name="viewport" '
                      'content="width=device-width, initial-scale=1">')

        titles = list(self.root.find_all("title"))
        if len(titles) != 1:
            self.emit("HEAD-03", titles[0].line if titles else 1,
                      "expected exactly one <title>, found %d" % len(titles),
                      "title elements: %d" % len(titles),
                      "keep exactly one <title> inside <head>")
        elif not collapse_ws(titles[0].text_content()):
            self.emit("HEAD-03", titles[0].line, "<title> is empty",
                      "empty title text",
                      "write a descriptive title inside the length window")

        descriptions = [meta for meta in metas
                        if meta.attrs.get("name", "").strip().lower() == "description"]
        nonempty = [meta for meta in descriptions
                    if collapse_ws(meta.attrs.get("content", ""))]
        if len(descriptions) != 1 or not nonempty:
            self.emit("HEAD-05", descriptions[0].line if descriptions else 1,
                      "expected exactly one non-empty meta description, "
                      "found %d" % len(nonempty),
                      "description metas: %d" % len(descriptions),
                      'add one <meta name="description" content="..."> '
                      "with a summary sentence")

        title_text = collapse_ws(titles[0].text_content()) if titles else ""
        title_node = titles[0] if titles else None
        if title_text:
            width = width_units(title_text)
            low, high = TITLE_WIDTH
            if not low <= width <= high:
                self.emit("HEAD-04", title_node.line,
                          "title width %d units, expected %d-%d"
                          % (width, low, high),
                          title_text[:80],
                          "rewrite the title to %d-%d width units" % (low, high))
        if nonempty:
            content = collapse_ws(nonempty[0].attrs.get("content", ""))
            width = width_units(content)
            low, high = DESCRIPTION_WIDTH
            if not low <= width <= high:
                self.emit("HEAD-06", nonempty[0].line,
                          "description width %d units, expected %d-%d"
                          % (width, low, high),
                          content[:80],
                          "rewrite the description to %d-%d width units"
                          % (low, high))

        robots_metas = [meta for meta in metas
                        if meta.attrs.get("name", "").strip().lower() in ROBOTS_META_NAMES]
        tokens = set()
        for meta in robots_metas:
            tokens.update(tok for tok in re.split(
                r"[,\s]+", meta.attrs.get("content", "").lower()) if tok)
        if "noindex" in tokens or "none" in tokens:
            self.emit("HEAD-07", robots_metas[0].line,
                      "robots meta blocks indexing",
                      " ".join(sorted(tokens)),
                      "use index,follow, or pass --allow-noindex when the "
                      "page is intentionally unindexed",
                      severity="info" if self.allow_noindex else None)
        if "nosourceinfo" in tokens:
            self.emit("HEAD-11", robots_metas[0].line,
                      "robots meta contains nosourceinfo "
                      "(AI source description off)",
                      "nosourceinfo",
                      "remove nosourceinfo when the page should show an "
                      "AI source description")

        has_icon = any("icon" in re.split(r"\s+", link.attrs.get("rel", "").lower())
                       for link in self.root.find_all("link"))
        has_theme = any(meta.attrs.get("name", "").strip().lower() == "theme-color"
                        for meta in metas)
        missing = [name for name, present in
                   (("icon link", has_icon), ("theme-color meta", has_theme))
                   if not present]
        if missing:
            self.emit("HEAD-08", 1,
                      "browser chrome hints incomplete: " + ", ".join(missing),
                      "missing: " + ", ".join(missing),
                      'add <link rel="icon" href="/favicon.ico"> and '
                      '<meta name="theme-color" content="#ffffff">')

        html_tag = self.root.find("html")
        declared = html_tag.attrs.get("lang", "").strip() if html_tag is not None else ""
        if not declared:
            self.emit("HEAD-09", html_tag.line if html_tag is not None else 1,
                      "<html> has no lang attribute",
                      "lang attribute missing",
                      'set the page language, e.g. <html lang="ko"> or '
                      '<html lang="en">')
        elif self.lang_arg in ("ko", "en") and not declared.lower().startswith(self.lang_arg):
            self.emit("HEAD-09", html_tag.line,
                      '<html lang="%s"> does not match --lang %s'
                      % (declared, self.lang_arg),
                      'lang="%s"' % declared,
                      'set lang to start with "%s", or drop --lang to use '
                      "auto detection" % self.lang_arg)

        if title_text and nonempty:
            description_text = collapse_ws(nonempty[0].attrs.get("content", ""))
            if description_text and normalize_text(description_text) == normalize_text(title_text):
                self.emit("HEAD-10", nonempty[0].line,
                          "meta description equals the title "
                          "(Naver penalizes this)",
                          "description == title: " + title_text[:60],
                          "write a different summary sentence for the description")

    def meta_by_property(self, prefix):
        found = {}
        for meta in self.root.find_all("meta"):
            prop = meta.attrs.get("property", "").strip().lower()
            if prop.startswith(prefix):
                found.setdefault(prop, meta.attrs.get("content", ""))
        return found

    def meta_by_name(self, prefix):
        found = {}
        for meta in self.root.find_all("meta"):
            name = meta.attrs.get("name", "").strip().lower()
            if name.startswith(prefix):
                found.setdefault(name, meta.attrs.get("content", ""))
        return found

    def check_open_graph(self):
        og = self.og
        canonical = self.canonical_href

        for prop in ("og:title", "og:type", "og:image", "og:url"):
            if not collapse_ws(og.get(prop, "")):
                self.emit("OG-01", 1, "%s is missing or empty" % prop,
                          "%s: %s" % (prop, og.get(prop, "") or "absent"),
                          'add <meta property="%s" content="..."> with a '
                          "non-empty value" % prop)

        if not collapse_ws(og.get("og:description", "")):
            self.emit("OG-02", 1, "og:description is missing or empty",
                      "og:description absent",
                      'add <meta property="og:description" content="...">')

        if collapse_ws(og.get("og:image", "")) and not collapse_ws(og.get("og:image:alt", "")):
            self.emit("OG-03", 1, "og:image present without og:image:alt",
                      "og:image:alt absent",
                      'add <meta property="og:image:alt" content="..."> '
                      "describing the image")

        width_text = og.get("og:image:width", "").strip()
        height_text = og.get("og:image:height", "").strip()
        width = parse_dimension(width_text)
        height = parse_dimension(height_text)
        if collapse_ws(og.get("og:image", "")):
            if width is not None and height is not None:
                if width < OG_IMAGE_MIN[0] or height < OG_IMAGE_MIN[1]:
                    self.emit("OG-04", 1,
                              "og:image %dx%d is under %dx%d"
                              % (width, height, OG_IMAGE_MIN[0], OG_IMAGE_MIN[1]),
                              "og:image:width=%d og:image:height=%d" % (width, height),
                              "provide a larger result thumbnail image")
                # Multiplication instead of float division keeps the
                # ratio comparison overflow-free for any usable values.
                elif max(width, height) > max(1, min(width, height)) * OG_IMAGE_MAX_RATIO:
                    self.emit("OG-04", 1,
                              "og:image aspect ratio %d:%d exceeds %s:1"
                              % (width, height, OG_IMAGE_MAX_RATIO),
                              "og:image:width=%d og:image:height=%d" % (width, height),
                              "crop the image to an aspect ratio of 3:1 or less")
            if width is None or height is None or width < OG_IMAGE_RECOMMENDED[0] \
                    or height < OG_IMAGE_RECOMMENDED[1]:
                shown_w = width if width is not None else (width_text or "?")
                shown_h = height if height is not None else (height_text or "?")
                self.emit("OG-07", 1,
                          "og:image %sx%s is below the recommended %dx%d"
                          % (shown_w, shown_h,
                             OG_IMAGE_RECOMMENDED[0], OG_IMAGE_RECOMMENDED[1]),
                          "og:image:width=%s og:image:height=%s" % (shown_w, shown_h),
                          "ship a %dx%d share image and declare both dimensions"
                          % OG_IMAGE_RECOMMENDED)

        if not collapse_ws(og.get("og:site_name", "")):
            self.emit("OG-05", 1, "og:site_name is missing or empty",
                      "og:site_name absent",
                      'add <meta property="og:site_name" content="...">')
        locale = collapse_ws(og.get("og:locale", ""))
        if not locale:
            self.emit("OG-05", 1, "og:locale is missing or empty",
                      "og:locale absent",
                      'add <meta property="og:locale" content="ko_KR"> or '
                      '"en_US" as fits')
        elif locale.split("_")[0].split("-")[0].lower() != self.lang:
            self.emit("OG-05", 1,
                      'og:locale "%s" does not match page language "%s"'
                      % (locale, self.lang),
                      "og:locale=%s lang=%s" % (locale, self.lang),
                      'use a locale matching the page language, e.g. "%s"'
                      % ("ko_KR" if self.lang == "ko" else "en_US"))

        og_url = collapse_ws(og.get("og:url", ""))
        if og_url and canonical and not is_absolute_http_url(og_url):
            self.emit("OG-06", 1, "og:url is not an absolute http(s) URL",
                      "og:url=%s" % og_url,
                      "set og:url to the same absolute URL as the canonical link")
        elif og_url and canonical and og_url != canonical:
            self.emit("OG-06", 1, "og:url differs from the canonical URL",
                      "og:url=%s canonical=%s" % (og_url, canonical),
                      "set og:url to the same absolute URL as the canonical link")

    def check_twitter(self):
        twitter = self.twitter
        card = collapse_ws(twitter.get("twitter:card", ""))
        if card not in TWITTER_CARD_TYPES:
            self.emit("TW-01", 1,
                      "twitter:card is missing or not a known card type",
                      "twitter:card=%s" % (card or "absent"),
                      'add <meta name="twitter:card" '
                      'content="summary_large_image"> (or summary, app, player)')
        missing = [name for name in ("twitter:title", "twitter:description",
                                     "twitter:image")
                   if not collapse_ws(twitter.get(name, ""))]
        if missing:
            self.emit("TW-02", 1,
                      "twitter card fields missing: " + ", ".join(missing),
                      "missing: " + ", ".join(missing),
                      "add the missing twitter:* metas, or rely on the "
                      "matching og:* fallback and document that choice")

    def check_semantic(self):
        mains = list(self.root.find_all("main"))
        if len(mains) != 1:
            self.emit("SEM-01", mains[0].line if mains else 1,
                      "expected exactly one <main>, found %d" % len(mains),
                      "main elements: %d" % len(mains),
                      "wrap the primary content of the page in exactly one <main>")

        for tag in ("header", "footer", "article"):
            if self.root.find(tag) is None:
                self.emit("SEM-02", 1, "<%s> is missing" % tag,
                          "no <%s> element" % tag,
                          "add a <%s> element for the page %s content"
                          % (tag, tag))

        if self.root.find("nav") is None:
            self.emit("SEM-03", 1, "<nav> is missing", "no <nav> element",
                      "add a <nav> with the main site links")

        for node in self.root.iter_tree():
            if node.tag in ("div", "span") and "onclick" in node.attrs:
                self.emit("SEM-04", node.line,
                          "<%s> carries an onclick handler" % node.tag,
                          "<%s onclick=...>" % node.tag,
                          "use a <button> for actions or an <a> for navigation")

        for figure in self.root.find_all("figure"):
            if not figure.has_descendant(("figcaption",)):
                self.emit("SEM-05", figure.line,
                          "<figure> has no <figcaption>",
                          "<figure> without caption",
                          "add a <figcaption> describing the figure")

        for time_tag in self.root.find_all("time"):
            value = time_tag.attrs.get("datetime", "").strip()
            if not value or not is_valid_iso8601(value):
                message = ('<time datetime="%s"> is not ISO 8601' % value
                           if value else "<time> has no datetime attribute")
                self.emit("SEM-06", time_tag.line, message,
                          "datetime=%s" % (value or "absent"),
                          'write a full ISO 8601 value, e.g. '
                          'datetime="2026-10-14" or '
                          'datetime="2026-10-14T09:30+09:00"')

    def check_headings(self):
        h1s = list(self.root.find_all("h1"))
        if len(h1s) != 1:
            self.emit("H-01", h1s[0].line if h1s else 1,
                      "expected exactly one <h1>, found %d" % len(h1s),
                      "h1 elements: %d" % len(h1s),
                      "keep exactly one <h1> that states the page topic")

        headings = []
        for level in range(1, 7):
            headings.extend((node, level) for node in self.root.find_all("h%d" % level))
        headings.sort(key=lambda pair: (pair[0].line, pair[0].col))
        for (_, previous), (node, level) in zip(headings, headings[1:]):
            if level > previous + 1:
                self.emit("H-02", node.line,
                          "heading level skip: h%d followed by h%d"
                          % (previous, level),
                          "h%d -> h%d" % (previous, level),
                          "use h%d or restructure the outline" % (previous + 1))
        for node, _level in headings:
            text = collapse_ws(node.text_content())
            digits_only = re.sub(r"[\s,.\-+%]", "", text)
            if len(text) <= 2 or (digits_only and digits_only.isdigit()):
                self.emit("H-03", node.line,
                          'heading text is empty, digits-only, or <= 2 code '
                          'points: "%s"' % text,
                          "heading text: %s" % (text or "(empty)"),
                          "write a descriptive heading of at least 3 code points")

    def check_jsonld(self):
        scripts = ld_scripts(self.root)
        if not scripts:
            self.emit("LD-01", 1, "no application/ld+json block found",
                      "0 ld+json scripts",
                      'add a <script type="application/ld+json"> with a '
                      "schema.org @graph")
        for index, script in enumerate(scripts, start=1):
            body = "".join(part for part in script.parts
                           if isinstance(part, str)).strip()
            try:
                data = json.loads(body)
            except json.JSONDecodeError as error:
                self.emit("LD-01", script.line,
                          "ld+json block %d does not parse: %s (line %d)"
                          % (index, error.msg, error.lineno),
                          body[:80],
                          "fix the JSON syntax so the block parses")
                continue
            if not isinstance(data, (dict, list)):
                self.emit("LD-03", script.line,
                          "ld+json block %d root is not an object or list" % index,
                          "root type: %s" % type(data).__name__,
                          "make the block root a JSON object (or a list of objects)")
                continue
            self._check_ld_nodes(data, script, index)

    def _check_ld_nodes(self, data, script, index):
        block = "block %d" % index
        for node, is_top in iter_ld_nodes(data, top_level=True):
            if not isinstance(node, dict):
                self.emit("LD-03", script.line,
                          "%s: a node is not a JSON object" % block,
                          "non-object node",
                          "make every root and @graph member an object")
                continue
            types = node_types(node)
            for value in types:
                if value not in self._jsonld_types:
                    self._jsonld_types.append(value)

            if is_top and "@context" not in node:
                self.emit("LD-02", script.line,
                          "%s: top-level node has no @context" % block,
                          "@type=%s" % (types[0] if types else "(none)"),
                          'add "@context": "https://schema.org" to the '
                          "top-level object")
            elif is_top:
                context = node.get("@context")
                contexts = context if isinstance(context, list) else [context]
                if any(isinstance(item, str) and item.strip().lower()
                       == "http://schema.org" for item in contexts):
                    self.emit("LD-02", script.line,
                              "%s: @context uses http://schema.org" % block,
                              "@context=http://schema.org",
                              'prefer "@context": "https://schema.org"',
                              severity="warn")

            if "@type" not in node and "@graph" not in node:
                self.emit("LD-03", script.line,
                          "%s: node has no @type" % block, "missing @type",
                          'give the node a "@type", e.g. "WebPage"')

            graph = node.get("@graph")
            if "@graph" in node and not isinstance(graph, list):
                self.emit("LD-04", script.line,
                          "%s: @graph is not a list" % block,
                          "@graph type: %s" % type(graph).__name__,
                          'make "@graph" a JSON array of node objects')

            placeholder = placeholder_in_node(node)
            if placeholder is not None:
                self.emit("LD-05", script.line,
                          "%s: placeholder text in JSON-LD: %s"
                          % (block, placeholder),
                          placeholder,
                          "replace %s with the real value before shipping"
                          % placeholder)

            phased = [value for value in types if value in PHASED_OUT_TYPES]
            actions = node.get("potentialAction")
            action_values = actions if isinstance(actions, list) else [actions]
            action_items = []
            for action in action_values:
                if isinstance(action, str):
                    action_items.append(action)
                elif isinstance(action, dict):
                    action_items.extend(node_types(action))
            if "Book" in types and any(
                    action in ("ReadAction", "BorrowAction") for action in action_items):
                phased.append("Book read/borrow action")
            if phased:
                self.emit("LD-06", script.line,
                          "%s: phased-out rich-result type(s): %s"
                          % (block, ", ".join(phased)),
                          "@type=%s" % ",".join(types),
                          "remove the phased-out type; use a type that still "
                          "earns rich results")

            if "FAQPage" in types:
                self.emit("LD-07", script.line,
                          "%s: FAQPage present (valid schema; no rich result "
                          "since 2026-05-07)" % block,
                          "@type=FAQPage",
                          "keep only if the markup still serves a purpose")

            if any(value in ARTICLE_TYPES for value in types):
                missing = [prop for prop in ARTICLE_REQUIRED
                           if prop not in node or node[prop] in ("", None, [], {})]
                if missing:
                    self.emit("LD-08", script.line,
                              "%s: %s missing %s"
                              % (block, types[0], ", ".join(missing)),
                              "missing: " + ", ".join(missing),
                              "add the recommended Article properties: "
                              "headline, author, datePublished, dateModified, image")

            if "BreadcrumbList" in types:
                self._check_breadcrumb(node, script, block)

            if "Product" in types:
                problems = []
                if not node.get("name"):
                    problems.append("name is missing")
                if not any(key in node for key in ("offers", "review", "aggregateRating")):
                    problems.append("none of offers/review/aggregateRating present")
                if problems:
                    self.emit("LD-10", script.line,
                              "%s: Product incomplete: %s"
                              % (block, "; ".join(problems)),
                              "; ".join(problems),
                              "give Product a name plus offers, review, or "
                              "aggregateRating")

            if any(value in ("Organization", "WebSite") for value in types):
                missing = [key for key in ("name", "url") if not node.get(key)]
                if missing:
                    self.emit("LD-11", script.line,
                              "%s: %s missing %s"
                              % (block, types[0], ", ".join(missing)),
                              "missing: " + ", ".join(missing),
                              "add the %s property with an absolute https URL "
                              "where applicable" % ", ".join(missing))

            for key in DATE_KEYS:
                if key in node:
                    value = node.get(key)
                    if not is_valid_iso8601(value):
                        self.emit("LD-12", script.line,
                                  "%s: %s is not ISO 8601: %r" % (block, key, value),
                                  "%s=%r" % (key, value),
                                  'write %s as "2026-10-14" or '
                                  '"2026-10-14T09:30+09:00"' % key)

            for key, value in absolute_url_violations(node):
                self.emit("LD-13", script.line,
                          "%s: %s is not an absolute http(s) URL: %s"
                          % (block, key, value),
                          "%s=%s" % (key, value),
                          "use an absolute URL for %s, e.g. "
                          "https://example.com/page" % key)

            if any(value in ARTICLE_TYPES for value in types):
                headline = node.get("headline")
                if isinstance(headline, str) and headline:
                    self._check_visible_name(headline, script, block,
                                             types[0], "headline")
            if "WebPage" in types:
                name = node.get("name")
                if isinstance(name, str) and name:
                    self._check_visible_name(name, script, block,
                                             "WebPage", "name")

    def _check_breadcrumb(self, node, script, block):
        items = node.get("itemListElement")
        if not isinstance(items, list):
            self.emit("LD-09", script.line,
                      "%s: BreadcrumbList itemListElement is not a list" % block,
                      "itemListElement type: %s" % type(items).__name__,
                      "make itemListElement an array of ListItem objects")
            return
        for position, item in enumerate(items):
            if not isinstance(item, dict):
                self.emit("LD-09", script.line,
                          "%s: breadcrumb item %d is not an object"
                          % (block, position + 1),
                          "non-object ListItem",
                          "use a ListItem object with position and name")
                continue
            problems = []
            raw_position = item.get("position")
            if not (isinstance(raw_position, int) and not isinstance(raw_position, bool)) \
                    and not (isinstance(raw_position, str) and raw_position.strip().isdigit()):
                problems.append("position missing or not a number")
            if not (isinstance(item.get("name"), str) and item.get("name", "").strip()):
                problems.append("name missing or empty")
            if position < len(items) - 1 and "item" not in item:
                problems.append("item required on all but the last ListItem")
            if problems:
                self.emit("LD-09", script.line,
                          "%s: breadcrumb item %d: %s"
                          % (block, position + 1, "; ".join(problems)),
                          "; ".join(problems),
                          "give every ListItem position and name, and item "
                          "on all but the last entry")

    def _check_visible_name(self, value, script, block, type_name, field):
        title = self.extracted_title or ""
        h1 = self.extracted_h1 or ""
        needle = normalize_text(value)
        if needle and (needle in normalize_text(title) or needle in normalize_text(h1)):
            return
        self.emit("LD-14", script.line,
                  "%s: %s %s not found in the visible title or h1"
                  % (block, type_name, field),
                  '%s="%s"' % (field, value),
                  "align the structured-data name with the visible title or h1")

    def check_images(self):
        for img in self.root.find_all("img"):
            src = img.attrs.get("src", "")
            if "alt" not in img.attrs:
                self.emit("IMG-01", img.line,
                          '<img src="%s"> has no alt attribute' % src,
                          "src=%s" % (src or "(none)"),
                          'add alt="..." for every image; use alt="" only '
                          "for decorative images")
            else:
                alt = img.attrs["alt"]
                if alt:
                    length = len(collapse_ws(alt))
                    if length > ALT_MAX:
                        self.emit("IMG-02", img.line,
                                  "alt text is %d code points (max %d)"
                                  % (length, ALT_MAX),
                                  "alt=%s" % alt[:80],
                                  "shorten the alt text to the essential description")
                    elif FILENAME_LIKE_RE.search(alt) or "/" in alt or "\\" in alt:
                        self.emit("IMG-02", img.line,
                                  "alt text looks like a filename or path",
                                  "alt=%s" % alt[:80],
                                  "describe the image content instead of the "
                                  "file name")
            if parse_dimension(img.attrs.get("width", "")) is None \
                    or parse_dimension(img.attrs.get("height", "")) is None:
                self.emit("IMG-03", img.line,
                          '<img src="%s"> does not declare width and height' % src,
                          "width=%s height=%s"
                          % (img.attrs.get("width", "absent"),
                             img.attrs.get("height", "absent")),
                          "add width and height attributes to reserve layout space")

        for img in self.root.find_all("img"):
            if img.has_ancestor(("main",)):
                if img.attrs.get("loading", "").strip().lower() == "lazy":
                    self.emit("IMG-04", img.line,
                              'the first <img> inside <main> has '
                              'loading="lazy"',
                              "loading=%s" % img.attrs.get("loading", "absent"),
                              'remove loading="lazy" from the first '
                              '(above-the-fold) image; keep it on later '
                              "images")
                break

    def check_links(self):
        canonicals = [link for link in self.root.find_all("link")
                      if "canonical" in re.split(r"\s+", link.attrs.get("rel", "").lower())]
        if len(canonicals) != 1:
            self.emit("LINK-01", canonicals[0].line if canonicals else 1,
                      "expected exactly one canonical link, found %d"
                      % len(canonicals),
                      "canonical links: %d" % len(canonicals),
                      'add one <link rel="canonical" '
                      'href="https://example.com/page">')
        else:
            href = canonicals[0].attrs.get("href", "").strip()
            if not is_absolute_http_url(href):
                self.emit("LINK-01", canonicals[0].line,
                          'canonical href="%s" is not an absolute http(s) URL'
                          % href,
                          "canonical=%s" % href,
                          "use the absolute self-referencing URL, e.g. "
                          "https://example.com/page")

        alternates = [link for link in self.root.find_all("link")
                      if "alternate" in re.split(r"\s+", link.attrs.get("rel", "").lower())
                      and collapse_ws(link.attrs.get("hreflang", ""))]
        if alternates:
            for link in alternates:
                code = link.attrs["hreflang"].strip()
                if code.lower() != "x-default" and not HREFLANG_RE.match(code):
                    self.emit("LINK-02", link.line,
                              'hreflang code "%s" is invalid' % code,
                              "hreflang=%s" % code,
                              "use a language-region code like ko-KR, en, "
                              "or x-default")
                href = link.attrs.get("href", "").strip()
                if not is_absolute_http_url(href):
                    self.emit("LINK-02", link.line,
                              'hreflang href="%s" is not an absolute http(s) URL'
                              % (href or "(empty)"),
                              "hreflang=%s href=%s" % (code, href or "(empty)"),
                              "point every hreflang entry at the absolute https "
                              "URL of that language version")
            if len(canonicals) == 1:
                canonical = canonicals[0].attrs.get("href", "").strip()
                hrefs = {link.attrs.get("href", "").strip() for link in alternates}
                if canonical not in hrefs:
                    self.emit("LINK-02", alternates[0].line,
                              "hreflang set does not include the canonical "
                              "URL as its self-reference",
                              "canonical=%s" % canonical,
                              "add a hreflang entry whose href equals the "
                              "canonical URL")
            if not any(link.attrs.get("hreflang", "").strip().lower() == "x-default"
                       for link in alternates):
                self.emit("LINK-02", alternates[0].line,
                          "hreflang set has no x-default entry",
                          "x-default absent",
                          'add <link rel="alternate" hreflang="x-default" '
                          'href="https://example.com/page"> for unmatched '
                          "locales",
                          severity="info")

        for anchor in self.root.find_all("a"):
            text = normalize_text(anchor.text_content())
            if text in BAD_ANCHOR_TEXTS:
                self.emit("LINK-03", anchor.line,
                          'non-descriptive anchor text: "%s"' % text,
                          "anchor=%s" % anchor.text_content().strip()[:60],
                          "write anchor text that names the destination")
            if "href" in anchor.attrs and anchor.attrs.get("href", "").strip() in ("", "#"):
                self.emit("LINK-04", anchor.line,
                          '<a> has an empty or "#" href',
                          "href=%r" % anchor.attrs.get("href", ""),
                          "point the link at a real destination or remove "
                          "the anchor")

    def check_a11y(self):
        labels_by_for = {}
        for label in self.root.find_all("label"):
            for_value = collapse_ws(label.attrs.get("for", ""))
            if for_value:
                labels_by_for.setdefault(for_value, label)
        for node in self.root.iter_tree():
            if node.tag not in ("input", "select", "textarea"):
                continue
            if node.tag == "input" and node.attrs.get("type", "").strip().lower() \
                    in ("hidden", "submit", "button"):
                continue
            if collapse_ws(node.attrs.get("aria-label", "")) or \
                    collapse_ws(node.attrs.get("aria-labelledby", "")):
                continue
            control_id = collapse_ws(node.attrs.get("id", ""))
            if control_id and control_id in labels_by_for:
                continue
            if node.has_ancestor(("label",)):
                continue
            self.emit("A11Y-01", node.line,
                      "<%s> has no label, aria-label, or aria-labelledby"
                      % node.tag,
                      "<%s id=%s>" % (node.tag, control_id or "(none)"),
                      "add a <label for=...>, wrap the control in a <label>, "
                      "or set aria-label")

    def check_perf(self):
        for script in self.root.find_all("script"):
            if not collapse_ws(script.attrs.get("src", "")):
                continue
            if not script.has_ancestor(("head",)):
                continue
            if "async" in script.attrs or "defer" in script.attrs:
                continue
            if script.attrs.get("type", "").strip().lower() == "module":
                continue
            self.emit("PERF-01", script.line,
                      'head script "%s" blocks parsing' % script.attrs["src"],
                      "src=%s" % script.attrs["src"],
                      'add async or defer (or type="module") to head scripts')

    def main_text(self):
        main = self.root.find("main")
        return collapse_ws(main.text_content()) if main is not None else ""

    def check_content(self):
        text = self.main_text()
        main_node = self.root.find("main")
        if len(text) < THIN_MIN_CHARS:
            self.emit("CONT-01", main_node.line if main_node is not None else 1,
                      "visible text in <main> is %d code points (min %d)"
                      % (len(text), THIN_MIN_CHARS),
                      "main text length: %d" % len(text),
                      "expand the main content to at least %d code points of "
                      "useful text" % THIN_MIN_CHARS)

        if self.keyword:
            low, high = KEYWORD_DENSITY
            keyword = collapse_ws(self.keyword).casefold()
            if self.lang == "ko":
                occurrences = text.casefold().count(keyword)
                density = (100.0 * occurrences * len(keyword) / len(text)) \
                    if text else 0.0
            else:
                tokens = re.findall(r"\w+", text.casefold())
                keyword_tokens = keyword.split()
                occurrences = 0
                if len(keyword_tokens) == 1:
                    occurrences = tokens.count(keyword)
                elif keyword_tokens and tokens:
                    for start in range(len(tokens) - len(keyword_tokens) + 1):
                        if tokens[start:start + len(keyword_tokens)] == keyword_tokens:
                            occurrences += 1
                density = (100.0 * occurrences * len(keyword_tokens)
                           / len(tokens)) if tokens else 0.0
            if density < low or density > high:
                self.emit("CONT-02", 1,
                          'keyword "%s" density is %.1f%% (expected %s-%s%%)'
                          % (self.keyword, density, low, high),
                          "density=%.1f%%" % density,
                          'adjust usage of "%s" so the density lands between '
                          "%s%% and %s%%" % (self.keyword, low, high))

        for paragraph in self.root.find_all("p"):
            if STAT_RE.search(paragraph.text_content()):
                if not paragraph.has_descendant(("a", "cite", "sup")):
                    self.emit("CONT-03", paragraph.line,
                              "paragraph states a statistic without a source link",
                              paragraph.text_content().strip()[:80],
                              "link the statistic to its primary source with "
                              "<a>, <cite>, or <sup>")

    def _internal_error_finding(self, owner_id, method_name, error):
        """Degrade one unexpectedly failing check to an info finding so
        the report still prints and the remaining checks still run; the
        severity is info rather than the rule's own, so an internal error
        never changes the exit contract by itself."""
        message = "internal error: %s in %s" % (type(error).__name__,
                                                method_name)
        try:
            detail = "%s: %s" % (type(error).__name__, error)
            evidence = collapse_ws(detail)[:160] or "-"
        except Exception:
            evidence = "-"
        self.findings.append({
            "id": owner_id,
            "severity": "info",
            "line": 1,
            "message": message,
            "evidence": evidence,
            "fix": "this check failed unexpectedly and was skipped; the "
                   "remaining checks still ran - please report the page",
        })

    def run(self):
        self.lang = self.resolve_lang()
        self.og = self.meta_by_property("og:")
        self.twitter = self.meta_by_name("twitter:")
        canonical_links = [link for link in self.root.find_all("link")
                           if "canonical" in re.split(r"\s+", link.attrs.get("rel", "").lower())]
        self.canonical_href = (canonical_links[0].attrs.get("href", "").strip()
                               if len(canonical_links) == 1 else None)
        titles = list(self.root.find_all("title"))
        self.extracted_title = collapse_ws(titles[0].text_content()) if titles else ""
        h1s = list(self.root.find_all("h1"))
        self.extracted_h1 = collapse_ws(h1s[0].text_content()) if h1s else ""
        descriptions = [meta for meta in self.root.find_all("meta")
                        if meta.attrs.get("name", "").strip().lower() == "description"
                        and collapse_ws(meta.attrs.get("content", ""))]
        description_text = collapse_ws(descriptions[0].attrs.get("content", "")) \
            if descriptions else ""

        for method_name, owner_id in self.CHECK_STEPS:
            try:
                getattr(self, method_name)()
            except Exception as error:
                self._internal_error_finding(owner_id, method_name, error)

        errors = sum(1 for item in self.findings if item["severity"] == "error")
        warns = sum(1 for item in self.findings if item["severity"] == "warn")
        infos = sum(1 for item in self.findings if item["severity"] == "info")
        return {
            "file": self.file_label,
            "lang": self.lang,
            "summary": {
                "error": errors,
                "warn": warns,
                "info": infos,
                "score": max(0, 100 - 10 * errors - 3 * warns),
            },
            "findings": self.findings,
            "extracted": {
                "title": self.extracted_title or None,
                "title_len": width_units(self.extracted_title)
                if self.extracted_title else None,
                "description_len": width_units(description_text)
                if description_text else None,
                "h1": self.extracted_h1 or None,
                "og": dict(self.og),
                "twitter": dict(self.twitter),
                "canonical": self.canonical_href,
                "jsonld_types": list(self._jsonld_types),
                "images": [
                    {
                        "src": img.attrs.get("src", ""),
                        "alt": img.attrs.get("alt") if "alt" in img.attrs else None,
                        "width": img.attrs.get("width", ""),
                        "height": img.attrs.get("height", ""),
                        "loading": img.attrs.get("loading", ""),
                    }
                    for img in self.root.find_all("img")
                ],
            },
        }


def run_check(text, file_label="<page>", lang="auto", keyword=None,
              allow_noindex=False):
    """Check one page and return the result dict (the CLI's JSON shape)."""
    return PageChecker(text, file_label, lang_arg=lang, keyword=keyword,
                       allow_noindex=allow_noindex).run()


def _write_line(stream, text):
    """Append one line to a real output stream without ever raising on
    string content the stream encoding cannot represent (lone
    surrogates, non-ASCII text, a non-UTF-8 PYTHONIOENCODING): UTF-8
    bytes go to the stream's binary buffer, with unencodable code points
    backslash-escaped so the bytes stay valid UTF-8 and a JSON report
    stays parseable. Streams without a buffer (StringIO in tests) get
    the text itself."""
    out = getattr(stream, "buffer", None)
    if out is not None:
        out.write((text + "\n").encode("utf-8", "backslashreplace"))
        out.flush()
    else:
        stream.write(text + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_page.py",
        description="Check one static HTML page against the seo-html rule catalog.")
    parser.add_argument("file", help="HTML file to check")
    parser.add_argument("--json", action="store_true",
                        help="emit a JSON report instead of text lines")
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 when warnings are present")
    parser.add_argument("--lang", choices=("ko", "en", "auto"), default="auto",
                        help="page language for locale checks (auto: html "
                             "lang, then Hangul ratio)")
    parser.add_argument("--keyword",
                        help="check the density of keyword K in the main content")
    parser.add_argument("--allow-noindex", action="store_true",
                        help="downgrade the noindex finding to info")
    args = parser.parse_args(argv)

    try:
        with open(args.file, "rb") as handle:
            raw = handle.read()
    except OSError as error:
        _write_line(sys.stderr, "cannot read %s: %s" % (args.file, error))
        return 2
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        _write_line(sys.stderr,
                    "cannot decode %s as utf-8: %s" % (args.file, error))
        return 2

    result = run_check(text, args.file, lang=args.lang, keyword=args.keyword,
                       allow_noindex=args.allow_noindex)

    if args.json:
        _write_line(sys.stdout, json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for finding in result["findings"]:
            _write_line(sys.stdout,
                        "%s %s line %d: %s -> %s"
                        % (finding["severity"].upper(), finding["id"],
                           finding["line"], finding["message"], finding["fix"]))
        summary = result["summary"]
        _write_line(sys.stdout,
                    "summary: file=%s lang=%s error=%d warn=%d info=%d score=%d"
                    % (result["file"], result["lang"], summary["error"],
                       summary["warn"], summary["info"], summary["score"]))

    if result["summary"]["error"]:
        return 1
    if args.strict and result["summary"]["warn"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
