#!/usr/bin/env python3
"""
Generate 3 LinkedIn screenshot images for MedExplain AI blog post.
"""
from PIL import Image, ImageDraw, ImageFont
import textwrap, os

# ── colours (VS Code Dark+ palette) ──────────────────────────────────────────
BG          = (30,  30,  30)
BG_PANEL    = (37,  37,  38)
BG_LINE_HL  = (45,  50,  60)     # highlighted line tint
GUTTER      = (62,  62,  62)
FG          = (212, 212, 212)    # normal text
KW          = (86,  156, 214)    # blue  – keywords / def
STR         = (206, 145, 120)    # orange – strings
COMMENT     = (106, 153, 85)     # green  – comments
PUNCT       = (180, 180, 180)
NAME_FN     = (220, 220, 170)    # yellow – function names
NAME_CLS    = (78,  201, 176)    # teal   – class / type
PARAM       = (156, 220, 254)    # light-blue – params
NUMBER      = (181, 206, 168)
RED_ANNOT   = (255, 80,  80)
RED_BG      = (255, 80,  80, 60) # semi-transparent for highlight overlay

FONT_PATH  = "/System/Library/Fonts/SFNSMono.ttf"
FONT_UI    = "/System/Library/Fonts/SFNS.ttf"

def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

def load_ui_font(size):
    try:
        return ImageFont.truetype(FONT_UI, size)
    except:
        return load_font(size)

# ── helpers ───────────────────────────────────────────────────────────────────
def char_size(font):
    """Return (w, h) for a single character."""
    bbox = font.getbbox("M")
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def draw_title_bar(draw, x, y, w, title, font):
    draw.rectangle([x, y, x+w, y+28], fill=(50, 50, 50))
    # three dots
    for i, col in enumerate([(255,95,86),(255,189,46),(39,201,63)]):
        draw.ellipse([x+12+i*20, y+8, x+22+i*20, y+18], fill=col)
    draw.text((x + w//2 - 60, y+6), title, fill=(200,200,200), font=font)

def token_spans(line: str):
    """
    Very light hand-rolled tokenizer for Python lines used in this script.
    Returns list of (text, colour).
    """
    import re

    KEYWORDS = {"def","return","if","for","in","not","and","or","import","from",
                "class","try","except","raise","with","as","None","True","False",
                "global","else","elif","pass"}

    result = []
    # full-line comment
    stripped = line.lstrip()
    if stripped.startswith("#"):
        result.append((line, COMMENT))
        return result

    # tokenize roughly
    pattern = re.compile(
        r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"\n]*"|\'[^\'\\n]*\')'   # strings
        r'|(\b(?:def|return|if|for|in|not|and|or|import|from|class|try|except|raise|with|as|None|True|False|global|else|elif|pass)\b)'  # keywords
        r'|(\b[A-Z][A-Z0-9_]{2,}\b)'     # CONSTANTS
        r'|(\bdef\s+(\w+))'              # function def name (caught by keyword above too)
        r'|(#.*$)'                       # inline comment
        r'|(\w+)'                        # identifiers
        r'|([^\w\s])'                    # punctuation
    )

    pos = 0
    for m in pattern.finditer(line):
        start, end = m.span()
        if start > pos:
            result.append((line[pos:start], FG))
        tok = m.group()
        if m.group(1):                   # string
            result.append((tok, STR))
        elif m.group(2):                 # keyword
            result.append((tok, KW))
        elif m.group(3):                 # CONSTANT
            result.append((tok, NAME_CLS))
        elif m.group(6):                 # comment
            result.append((tok, COMMENT))
        elif m.group(7):                 # identifier – colour by context
            # function call heuristic: followed by '('
            rest = line[end:]
            if rest.lstrip().startswith("("):
                result.append((tok, NAME_FN))
            else:
                result.append((tok, FG))
        else:
            result.append((tok, PUNCT))
        pos = end
    if pos < len(line):
        result.append((line[pos:], FG))
    return result

def draw_code_block(draw, lines, x, y, font, cw, ch,
                    highlight_text=None, highlight_color=RED_ANNOT,
                    line_numbers=True, gutter_w=40):
    """Draw syntax-highlighted code lines. Returns final y."""
    lnum_font = load_font(max(10, font.size - 2))
    for i, line in enumerate(lines):
        ly = y + i * (ch + 4)
        # gutter
        if line_numbers:
            lnum = str(i + 1)
            draw.text((x + gutter_w - len(lnum)*7 - 4, ly), lnum,
                      fill=GUTTER, font=lnum_font)
        cx = x + (gutter_w if line_numbers else 0)

        # highlight whole line if it contains the target text
        if highlight_text and highlight_text in line:
            draw.rectangle([cx - 2, ly - 2,
                            cx + len(line)*cw + 4, ly + ch + 2],
                           fill=(60, 30, 30))

        spans = token_spans(line)
        for tok, col in spans:
            draw.text((cx, ly), tok, fill=col, font=font)
            bbox = font.getbbox(tok)
            cx += bbox[2] - bbox[0]

    return y + len(lines) * (ch + 4)

# ══════════════════════════════════════════════════════════════════════════════
# IMAGE 1 – Two functions side by side with red annotation on "Summary:"
# ══════════════════════════════════════════════════════════════════════════════
def make_image1():
    FONT_SIZE = 14
    font  = load_font(FONT_SIZE)
    font_sm = load_ui_font(12)
    font_title = load_ui_font(13)
    cw, ch = char_size(font)

    build_prompt_lines = [
        'def build_prompt(report_text: str,',
        '                 report_type: str) -> str:',
        '    return (',
        '        "System: You are MedExplain, a medical report"',
        '        " explanation assistant.\\n"',
        '        "You must be clear, concise, and avoid"',
        '        " giving medical advice.\\n"',
        '        f"User report type: {report_type}\\n"',
        '        f"User report text: {report_text}\\n"',
        '        "Task: Provide a structured explanation"',
        '        " for a non-medical reader.\\n"',
        '        "Required format:\\n"',
        '        "- Summary: <plain-language summary>\\n"',  # ← "Summary:"
        '        "- Key findings: <comma-separated list>\\n"',
        '        "- Recommendations: <safe next steps>\\n"',
        '        "- Disclaimer: <safety notice>\\n"',
        '    )',
    ]

    parse_lines = [
        'def parse_structured_response(',
        '        text: str, source: str) -> AnalyzeResponse:',
        '    summary = ""',
        '    findings: List[str] = []',
        '    recommendations: List[str] = []',
        '    disclaimer = DISCLAIMER',
        '    for line in text.splitlines():',
        '        cleaned = line.strip().lstrip("-•* ").strip()',
        '        lowered = cleaned.lower()',
        '        if lowered.startswith("summary:")  # ← matches here',
        '           or lowered.startswith("summary -"):',
        '            summary = cleaned.split(":", 1)[1].strip()',
        '        elif lowered.startswith("key findings:"):',
        '            ...',
        '    if not summary:',
        '        summary = "Summary unavailable from model response."',
        '    ...',
        '    return AnalyzeResponse(...)',
    ]

    pad = 20
    gutter_w = 36
    col_w = max(len(l) for l in build_prompt_lines + parse_lines) * cw + gutter_w + pad
    col_w = max(col_w, 420)
    n_rows = max(len(build_prompt_lines), len(parse_lines))
    code_h = n_rows * (ch + 4) + 10
    W = col_w * 2 + pad * 3
    H = code_h + 120
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img, "RGBA")

    # header bar
    draw.rectangle([0, 0, W, 40], fill=(37, 37, 38))
    draw.text((pad, 12), "main.py — MedExplain AI", fill=(200, 200, 200), font=font_title)

    # panel backgrounds
    left_x, right_x = pad, pad * 2 + col_w
    top_y = 50

    for px in [left_x, right_x]:
        draw.rectangle([px, top_y, px + col_w, top_y + code_h + 30], fill=BG_PANEL)
        draw_title_bar(draw, px, top_y, col_w,
                       "build_prompt()" if px == left_x else "parse_structured_response()",
                       font_sm)

    # draw code
    draw_code_block(draw, build_prompt_lines,
                    left_x, top_y + 36, font, cw, ch,
                    highlight_text="Summary:",
                    gutter_w=gutter_w)
    draw_code_block(draw, parse_lines,
                    right_x, top_y + 36, font, cw, ch,
                    highlight_text='"summary:"',
                    gutter_w=gutter_w)

    # ── red annotation: find pixel positions of "Summary:" in each panel ──
    # Left panel: line index 12 (0-based) → "- Summary: <plain-language summary>\n"
    left_hl_line  = 12
    right_hl_line = 9   # if lowered.startswith("summary:")

    def line_y(panel_top, line_idx):
        return panel_top + 36 + line_idx * (ch + 4)

    ly_left  = line_y(top_y, left_hl_line)
    ly_right = line_y(top_y, right_hl_line)

    # approximate x position of "Summary:" token in left panel
    prefix_left = '        "- Summary: '
    tx_left = left_x + gutter_w + int(len(prefix_left) * cw * 0.6)
    tx_right = right_x + gutter_w + int(len('        if lowered.startswith("') * cw * 0.6)

    # draw red rounded rectangles around the token
    for tx, ty in [(tx_left, ly_left), (tx_right, ly_right)]:
        box_w = int(len("Summary:") * cw * 0.65) + 6
        draw.rectangle([tx - 3, ty - 2, tx + box_w, ty + ch + 2],
                       outline=RED_ANNOT, width=2)

    # connecting arrow between the two boxes
    ax1 = tx_left + int(len("Summary:") * cw * 0.65) / 2
    ax2 = tx_right + int(len("Summary:") * cw * 0.65) / 2
    ay1 = ly_left + ch // 2
    ay2 = ly_right + ch // 2

    # draw a curved arrow via a mid-point
    mid_x = (left_x + col_w + right_x) // 2
    mid_y = (ay1 + ay2) // 2 - 20
    # polyline as approximation
    pts = [(ax1, ay1), (mid_x, mid_y), (ax2, ay2)]
    draw.line(pts, fill=RED_ANNOT, width=2)
    # arrowhead
    draw.polygon([(ax2-5, ay2-8), (ax2+5, ay2-8), (ax2, ay2+2)], fill=RED_ANNOT)

    # caption
    caption = (
        '⚠  "Summary:" is hardcoded in build_prompt() (left) and again in parse_structured_response() (right).\n'
        '   One typo in the model output → silent failure.'
    )
    draw.text((pad, top_y + code_h + 38), caption, fill=(200, 180, 100), font=font_sm)

    out = "/Users/apple/Documents/GitHub/MedExplain_AI/screenshot_1_side_by_side.png"
    img.save(out)
    print(f"Saved: {out}")


# ══════════════════════════════════════════════════════════════════════════════
# IMAGE 2 – Silent failure JSON response
# ══════════════════════════════════════════════════════════════════════════════
def make_image2():
    import json

    # Simulate the exact JSON the endpoint returns when the model
    # returns a slightly off-format (no "Summary:" prefix)
    payload = {
        "summary": "Summary unavailable from model response.",
        "key_findings": ["not provided"],
        "recommendations": ["Review this report with a licensed clinician."],
        "disclaimer": "This information is for education only and is not medical advice. Consult a licensed clinician for diagnosis or treatment.",
        "source": "hf_inference"
    }
    pretty = json.dumps(payload, indent=2)

    FONT_SIZE = 15
    font       = load_font(FONT_SIZE)
    font_sm    = load_ui_font(12)
    font_label = load_ui_font(13)
    cw, ch     = char_size(font)

    lines = pretty.splitlines()
    pad   = 24
    W     = max(len(l) for l in lines) * cw + pad * 2 + 20
    W     = max(W, 560)
    H     = len(lines) * (ch + 5) + 130
    img   = Image.new("RGB", (W, H), (18, 18, 18))
    draw  = ImageDraw.Draw(img, "RGBA")

    # top bar – simulate browser / API client
    draw.rectangle([0, 0, W, 36], fill=(40, 40, 40))
    draw.text((14, 10), "POST /api/analyze   →   200 OK", fill=(100, 220, 100), font=font_label)
    # status dot (green)
    draw.ellipse([W-24, 12, W-12, 24], fill=(60, 200, 60))

    # JSON body
    KEY   = (156, 220, 254)
    VAL_S = (206, 145, 120)
    VAL_N = (181, 206, 168)
    BRACE = (220, 220, 150)

    import re
    def json_spans(line):
        spans = []
        # key
        m = re.match(r'^(\s*)("[\w_]+")\s*(:)(.*)', line)
        if m:
            spans.append((m.group(1), FG))
            spans.append((m.group(2), KEY))
            spans.append((": ", PUNCT))
            rest = m.group(4).strip().rstrip(",")
            trail = "," if m.group(4).strip().endswith(",") else ""
            if rest.startswith('"'):
                spans.append((rest, VAL_S))
            elif rest in ("true","false","null"):
                spans.append((rest, KW))
            elif re.match(r'^[\d.\-]+$', rest):
                spans.append((rest, VAL_N))
            else:
                spans.append((rest, FG))
            if trail:
                spans.append((trail, PUNCT))
            return spans
        # brace / bracket lines
        stripped = line.strip()
        if stripped in ('{', '}', '[', ']', '{,', '},', '],', '[,'):
            spans.append((line.rstrip(), BRACE))
            return spans
        spans.append((line, FG))
        return spans

    y = 44
    for i, line in enumerate(lines):
        ly = y + i * (ch + 5)
        # highlight the "Summary unavailable" line
        if "Summary unavailable" in line:
            draw.rectangle([pad - 4, ly - 2, W - pad + 4, ly + ch + 2],
                           fill=(70, 30, 30))
        cx = pad
        for tok, col in json_spans(line):
            draw.text((cx, ly), tok, fill=col, font=font)
            bbox = font.getbbox(tok)
            cx += bbox[2] - bbox[0]

    # red callout box
    hl_line_idx = next(i for i, l in enumerate(lines) if "Summary unavailable" in l)
    hl_y = y + hl_line_idx * (ch + 5)
    arrow_x = W - 20
    arrow_y = hl_y + ch // 2
    callout_x = W - 260
    callout_y = hl_y - 36

    # callout bubble
    draw.rectangle([callout_x, callout_y, callout_x+240, callout_y+28],
                   fill=(180, 30, 30), outline=RED_ANNOT, width=1)
    draw.text((callout_x + 8, callout_y + 6),
              "Silent failure — no 4xx, no error key!",
              fill=(255, 220, 220), font=font_sm)
    draw.line([(callout_x+120, callout_y+28), (arrow_x - 40, arrow_y)],
              fill=RED_ANNOT, width=2)

    # footer note
    note = "HTTP 200 · no \"error\" field · status: \"hf_inference\" — nothing alerts on this."
    draw.text((pad, H - 26), note, fill=(160, 160, 100), font=font_sm)

    out = "/Users/apple/Documents/GitHub/MedExplain_AI/screenshot_2_silent_failure.png"
    img.save(out)
    print(f"Saved: {out}")


# ══════════════════════════════════════════════════════════════════════════════
# IMAGE 3 – fallback_parse function with KNOWN_FINDINGS highlighted
# ══════════════════════════════════════════════════════════════════════════════
def make_image3():
    FONT_SIZE = 15
    font      = load_font(FONT_SIZE)
    font_sm   = load_ui_font(12)
    cw, ch    = char_size(font)

    lines = [
        'KNOWN_FINDINGS = [',
        '    "cardiomegaly",',
        '    "pneumonia",',
        '    "anemia",',
        '    "elevated glucose",',
        '    "cholesterol",',
        '    "renal",',
        '    "dehydration",',
        '    "no acute disease",',
        ']',
        '',
        'def fallback_parse(report_text: str,',
        '                   report_type: str) -> AnalyzeResponse:',
        '    lowered = report_text.lower()',
        '    findings = [term for term in KNOWN_FINDINGS',
        '                if term in lowered]',
        '    if not findings:',
        '        findings = ["no specific findings detected"]',
        '',
        '    summary = f"This {report_type} report mentions"',
        '              f" {\', \'.join(findings)}."',
        '    recommendations = [',
        '        "Review this report with a licensed clinician.",',
        '        "Seek urgent care if symptoms worsen.",',
        '    ]',
        '    return AnalyzeResponse(',
        '        summary=summary,',
        '        key_findings=findings,',
        '        recommendations=recommendations,',
        '        disclaimer=DISCLAIMER,',
        '        source="fallback",',
        '    )',
    ]

    pad      = 24
    gutter_w = 40
    W = max(len(l) for l in lines) * cw + pad * 2 + gutter_w + 20
    W = max(W, 560)
    H = len(lines) * (ch + 5) + 110
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img, "RGBA")

    # title bar
    draw.rectangle([0, 0, W, 32], fill=(37, 37, 38))
    draw.text((14, 8), "main.py · fallback_parse()", fill=(190, 190, 190), font=font_sm)
    for i, col in enumerate([(255,95,86),(255,189,46),(39,201,63)]):
        draw.ellipse([W-62+i*20, 8, W-52+i*20, 18], fill=col)

    # highlight KNOWN_FINDINGS block (lines 0-9)
    for li in range(10):
        ly = 40 + li * (ch + 5)
        draw.rectangle([pad - 4, ly - 1, W - pad + 4, ly + ch + 1],
                       fill=(40, 60, 40))

    # draw code
    draw_code_block(draw, lines, pad, 40, font, cw, ch,
                    gutter_w=gutter_w, line_numbers=True)

    # bracket annotation on KNOWN_FINDINGS
    bracket_x = W - pad - 20
    top_y_b   = 40 + 0 * (ch + 5)
    bot_y_b   = 40 + 9 * (ch + 5) + ch
    draw.line([(bracket_x, top_y_b), (bracket_x + 8, top_y_b)], fill=RED_ANNOT, width=2)
    draw.line([(bracket_x, top_y_b), (bracket_x, bot_y_b)],     fill=RED_ANNOT, width=2)
    draw.line([(bracket_x, bot_y_b), (bracket_x + 8, bot_y_b)], fill=RED_ANNOT, width=2)
    mid_b = (top_y_b + bot_y_b) // 2
    label = "8 hardcoded\nkeywords"
    draw.text((bracket_x + 12, mid_b - ch), label, fill=RED_ANNOT, font=font_sm)

    # caption
    caption = (
        '⚠  Your "AI fallback" is a list of 8 words.\n'
        '   Miss one term → silent empty findings, no warning to the user.'
    )
    draw.text((pad, H - 44), caption, fill=(200, 180, 100), font=font_sm)

    out = "/Users/apple/Documents/GitHub/MedExplain_AI/screenshot_3_known_findings.png"
    img.save(out)
    print(f"Saved: {out}")


if __name__ == "__main__":
    make_image1()
    make_image2()
    make_image3()
    print("\nAll 3 screenshots generated ✓")
