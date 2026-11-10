#!/usr/bin/env python3
"""把閱讀策略學習單 HTML 轉成 PDF 與 Word（.docx）。

用法：
    python export.py 學習單.html            # 同時輸出 PDF 與 DOCX
    python export.py 學習單.html --pdf      # 只輸出 PDF
    python export.py 學習單.html --docx     # 只輸出 DOCX
    python export.py 學習單.html --iansui   # Word 改用芫荽字型（老師電腦需已安裝芫荽）

需求：
    PDF ：playwright（pip install playwright && playwright install chromium）
          沒有 playwright 時，請用瀏覽器開啟 HTML →「列印」→「另存為 PDF」。
    DOCX：python-docx、beautifulsoup4（pip install python-docx beautifulsoup4）

HTML 必須使用 references/template.html 的元件 class，Word 版才會正確對應。
"""
import sys
from pathlib import Path


# ---------------------------------------------------------------- PDF
def to_pdf(html: Path, out: Path) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return pdf_by_browser(html, out)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(html.resolve().as_uri())
        pg.wait_for_timeout(300)
        pg.pdf(path=str(out), format="A4", print_background=True,
               margin={"top": "12mm", "bottom": "12mm", "left": "12mm", "right": "12mm"})
        b.close()
    print(f"PDF：{out}")
    return True


def pdf_by_browser(html: Path, out: Path) -> bool:
    """沒有 playwright 時，改用電腦上的 Chrome／Edge／Chromium 無頭列印。"""
    import shutil
    import subprocess
    cands = [shutil.which(n) for n in ("chromium", "chromium-browser", "google-chrome", "chrome", "msedge")]
    cands += [
        "/opt/pw-browsers/chromium",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    import glob
    cands += glob.glob("/opt/pw-browsers/chromium*/chrome-linux*/chrome")
    exe = next((c for c in cands if c and Path(c).is_file()), None)
    if not exe:
        print("找不到 playwright 或 Chrome／Edge，略過 PDF。請用瀏覽器開啟 HTML →列印→另存為 PDF。")
        return False
    subprocess.run([exe, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out.resolve()}", html.resolve().as_uri()],
                   check=False, capture_output=True, timeout=120)
    if out.exists():
        print(f"PDF：{out}")
        return True
    print("PDF 產生失敗，請用瀏覽器列印另存 PDF。")
    return False


# ---------------------------------------------------------------- DOCX
def to_docx(html: Path, out: Path) -> bool:
    try:
        from bs4 import BeautifulSoup, NavigableString, Tag
        from docx import Document
        from docx.enum.table import WD_TABLE_ALIGNMENT
        from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Mm, Pt, RGBColor
    except ImportError:
        print("需要 python-docx 與 beautifulsoup4，略過 DOCX。")
        return False

    FONT = DOCX_FONT
    COLORS = {"s1": "E8F0FE", "s2": "E6F6EF", "s3": "FDF3E2", "s4": "F4EBFD"}
    NUM = {"1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤", "6": "⑥", "7": "⑦"}

    soup = BeautifulSoup(html.read_text(encoding="utf-8"), "html.parser")
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, side, Mm(12))
    st = doc.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    st.paragraph_format.space_after = Pt(1)
    st.paragraph_format.space_before = Pt(0)
    st.paragraph_format.line_spacing = 1.1

    def shade(cell, hexcolor):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), hexcolor)
        tcPr.append(shd)

    def has(el, c):
        return isinstance(el, Tag) and c in (el.get("class") or [])

    import base64
    import io

    def img_stream(img):
        """把 <img src> 轉成可放進 Word 的資料流（支援 data URI 與本機檔案）。"""
        src = (img.get("src") or "").strip()
        try:
            if src.startswith("data:"):
                return io.BytesIO(base64.b64decode(src.split(",", 1)[1]))
            f = (html.parent / src)
            if f.is_file():
                return io.BytesIO(f.read_bytes())
        except Exception:
            pass
        return None

    def add_img(target, img, width_mm):
        st_ = img_stream(img)
        if not st_:
            return False
        p = target.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        try:
            p.add_run().add_picture(st_, width=Mm(width_mm))
            return True
        except Exception:
            return False

    def ways_table(target, el):
        """通用版三種作答路徑：一列三格。"""
        ws_ = el.find_all(class_="way", recursive=False)
        names = {"✏️": "✏️ 寫一寫", "🧩": "🧩 選詞填空", "☑️": "☑️ 勾一勾"}
        t = table(target, 1, len(ws_), [44, 66, 60][:len(ws_)] if len(ws_) == 3 else None)
        for i, w in enumerate(ws_):
            c = t.cell(0, i)
            clear_first(c)
            lab = w.find("b")
            ltxt = lab.get_text(strip=True) if lab else ""
            if lab:
                lab.extract()
            para(c, names.get(ltxt, ltxt), size=9, color="6B7280")
            body = []

            def flush():
                if "".join(body).strip():
                    para(c, "".join(body).strip(), size=10.5)
                body.clear()
            for k in w.children:
                if has(k, "line"):
                    flush()
                    para(c, "＿" * 9, size=10)
                elif has(k, "opts"):
                    flush()
                    for o in k.find_all("span", recursive=False):
                        para(c, "☐ " + o.get_text(" ", strip=True), size=10)
                elif has(k, "chips"):
                    flush()
                    para(c, inline(k), size=9.5)
                else:
                    body.append(inline(k))
            flush()

    def pic_cards(target, el):
        """含圖片的圖卡：做成一列表格，每格＝圖片＋☐ 文字。"""
        cards = el.find_all("span", recursive=False)
        t = table(target, 1, len(cards), [24] * len(cards))
        for i, sp in enumerate(cards):
            c = t.cell(0, i)
            clear_first(c)
            im = sp.find("img")
            if im:
                add_img(c, im, 20)
            else:
                ic = sp.find("i")
                if ic:
                    para(c, ic.get_text(strip=True), size=18, align=WD_ALIGN_PARAGRAPH.CENTER)
            label = "".join(str(x) for x in sp.strings if not (x.parent.name == "i")).strip()
            para(c, "☐ " + label, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)

    def inline(el) -> str:
        """把元素轉成一行文字，套用勾選、填空、層次符號等。"""
        if isinstance(el, NavigableString):
            return str(el).replace("\n", " ")
        if not isinstance(el, Tag):
            return ""
        if el.name == "br":
            return "\n"
        if has(el, "blank"):
            return "＿＿＿＿＿＿"
        if has(el, "n"):
            t = el.get_text(strip=True)
            return NUM.get(t, t) + " "
        if has(el, "p"):
            return f"（{el.get_text(strip=True)}）"
        if has(el, "chips"):
            return "（詞語：" + "／".join(c.get_text(strip=True) for c in el.find_all("span")) + "）"
        if has(el, "opts"):
            return "　".join("☐ " + s.get_text(strip=True) for s in el.find_all("span", recursive=False))
        if has(el, "pics"):
            return "　".join("☐ " + s.get_text(" ", strip=True) for s in el.find_all("span", recursive=False))
        if el.name == "small":
            return "　" + el.get_text(strip=True)
        return "".join(inline(c) for c in el.children)

    def para(target, text, size=None, bold=False, align=None, color=None):
        p = target.add_paragraph()
        for i, part in enumerate(text.split("\n")):
            if i:
                p.add_run().add_break()
            r = p.add_run(part.strip() if i else part.rstrip())
            r.bold = bold
            if size:
                r.font.size = Pt(size)
            if color:
                r.font.color.rgb = RGBColor.from_string(color)
        if align:
            p.alignment = align
        return p

    def table(target, rows, cols, widths=None):
        t = target.add_table(rows=rows, cols=cols)
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        total = 186 if target is doc else 170
        ws = widths or [total / cols] * cols
        for i, col in enumerate(t.columns):
            col.width = Mm(ws[i])
        for row in t.rows:
            for i, c in enumerate(row.cells):
                c.width = Mm(ws[i])
        return t

    def clear_first(cell):
        # 新儲存格預設有一個空段落，拿掉避免多一行
        if cell.paragraphs and not cell.paragraphs[0].text:
            cell.paragraphs[0]._element.getparent().remove(cell.paragraphs[0]._element)

    def block(target, el):
        """把區塊元素寫入 target（Document 或 cell）。"""
        if isinstance(el, NavigableString):
            if str(el).strip():
                para(target, str(el).strip())
            return
        if not isinstance(el, Tag) or el.name in ("script", "style"):
            return
        if has(el, "row"):
            kids = [c for c in el.children if isinstance(c, Tag)]
            t = table(target, 1, len(kids))
            for i, k in enumerate(kids):
                c = t.cell(0, i)
                clear_first(c)
                block(c, k)
            return
        if has(el, "flow"):
            boxes = [c for c in el.children if has(c, "box")]
            t = table(target, 1, len(boxes))
            for i, k in enumerate(boxes):
                c = t.cell(0, i)
                clear_first(c)
                b = k.find("b")
                if b:
                    para(c, b.get_text(strip=True), bold=True, color="D97706")
                    b.extract()
                para(c, inline(k).strip() + ("　→" if i < len(boxes) - 1 else ""))
            return
        if has(el, "layers"):
            # 六何法八層：左欄層名、右欄任務
            rows_ = [k for k in el.children if has(k, "layer")]
            t = table(target, len(rows_), 2, [38, 148])
            for i, k in enumerate(rows_):
                lb, lc = k.find(class_="lb"), k.find(class_="lc")
                c0, c1 = t.cell(i, 0), t.cell(i, 1)
                clear_first(c0)
                clear_first(c1)
                shade(c0, "EEF2FF")
                sm = lb.find("small") if lb else None
                smt = sm.extract().get_text(strip=True) if sm else ""
                para(c0, inline(lb).strip(), bold=True, size=11)
                if smt:
                    para(c0, smt, size=9, color="6B7280")
                buf = []
                for x in (lc.children if lc else []):
                    if has(x, "line"):
                        if "".join(buf).strip():
                            para(c1, "".join(buf).strip(), size=11)
                        buf = []
                        para(c1, "＿" * 26, size=11)
                    elif has(x, "chips"):
                        if "".join(buf).strip():
                            para(c1, "".join(buf).strip(), size=11)
                        buf = []
                        para(c1, inline(x), size=9.5)
                    else:
                        buf.append(inline(x))
                if "".join(buf).strip():
                    para(c1, "".join(buf).strip(), size=11)
            return
        if has(el, "core"):
            t = table(target, 1, 1)
            c = t.cell(0, 0)
            clear_first(c)
            shade(c, "FDF2F8")
            para(c, inline(el).strip(), size=11)
            return
        if has(el, "mflow"):
            cols_ = [k for k in el.children if isinstance(k, Tag)]
            t = table(target, 1, len(cols_), [70, 30, 70][:len(cols_)] if len(cols_) == 3 else None)
            for i, k in enumerate(cols_):
                c = t.cell(0, i)
                clear_first(c)
                cells = k.find_all(class_="cell")
                if cells:
                    for cc in cells:
                        b = cc.find("b")
                        if b:
                            para(c, b.extract().get_text(strip=True), bold=True, size=10, color="D97706")
                        para(c, inline(cc).strip() + "＿＿＿", size=11)
                else:
                    shade(c, "FFF7ED")
                    para(c, inline(k).strip(), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
            return
        if has(el, "bubble"):
            kids = [k for k in el.children if isinstance(k, Tag)]
            t = table(target, 1, len(kids))
            for i, k in enumerate(kids):
                c = t.cell(0, i)
                clear_first(c)
                if has(k, "center"):
                    shade(c, "F3E8FF")
                    para(c, k.get_text(strip=True), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
                else:
                    para(c, "（　　　　　）", align=WD_ALIGN_PARAGRAPH.CENTER)
            return
        if has(el, "ringrow"):
            for k in el.children:
                if isinstance(k, Tag):
                    if has(k, "chips"):
                        para(target, "　　" + inline(k), size=10)
                    else:
                        block(target, k)
            return
        if has(el, "ring"):
            kids = [k for k in el.children if isinstance(k, Tag)]
            t = table(target, 3, 3, [50, 50, 50])
            for i, k in enumerate(kids[:9]):
                c = t.cell(i // 3, i % 3)
                clear_first(c)
                if has(k, "mid"):
                    shade(c, "ECFDF5")
                    para(c, k.get_text(strip=True), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
                else:
                    para(c, "\n", size=11)
            return
        if has(el, "imgbox") and el.find("img"):
            if not add_img(target, el.find("img"), 70):
                para(target, "（圖片）" + (el.find("img").get("alt") or ""))
            return
        if has(el, "pics") and el.find("img"):
            pic_cards(target, el)
            return
        if has(el, "bank") or has(el, "imgbox"):
            t = table(target, 1, 1)
            c = t.cell(0, 0)
            clear_first(c)
            shade(c, "FFFDF7")
            for k in el.children:
                if isinstance(k, Tag) and k.name in ("h4", "p", "div"):
                    para(c, inline(k).strip(), bold=k.name == "h4", size=11)
                elif str(k).strip():
                    para(c, inline(k).strip(), size=11)
            return
        if has(el, "q"):
            first = []
            subs = []
            for k in el.children:
                if isinstance(k, Tag) and (has(k, "opts") or has(k, "pics") or k.name in ("div", "table")):
                    subs.append(k)
                else:
                    first.append(inline(k))
            para(target, "".join(first).strip())
            for k in subs:
                if any(has(k, c) for c in ("flow", "mflow", "bubble", "ring", "ringrow", "layers")) or k.name == "table":
                    block(target, k)
                    continue
                if has(k, "ways"):
                    ways_table(target, k)
                    continue
                wrapped = k.find(class_="ways", recursive=False) if k.name == "div" and not k.get("class") else None
                if wrapped is not None:
                    ways_table(target, wrapped)
                    continue
                if has(k, "pics") and k.find("img"):
                    pic_cards(target, k)
                    continue
                inner = k.find(class_="pics") if k.name == "div" else None
                if inner is not None and inner.find("img"):
                    pic_cards(target, inner)
                    continue
                if has(k, "pics") or has(k, "opts"):
                    para(target, "　　" + inline(k), size=12)
                else:
                    para(target, "　　" + inline(k).strip())
            return
        if has(el, "line"):
            para(target, "　　" + "＿" * 30)
            return
        if el.name in ("table",):
            rows = el.find_all("tr")
            # 先算出格位（處理 rowspan／colspan）
            taken, place = {}, []
            for ri, r in enumerate(rows):
                ci = 0
                for td in r.find_all(["td", "th"]):
                    while (ri, ci) in taken:
                        ci += 1
                    rs, cs = int(td.get("rowspan", 1)), int(td.get("colspan", 1))
                    for a in range(rs):
                        for b in range(cs):
                            taken[(ri + a, ci + b)] = True
                    place.append((ri, ci, rs, cs, td))
                    ci += cs
            ncol = max(c for _, c in taken) + 1
            nrow = max(r for r, _ in taken) + 1
            import re as _re
            pct = []
            for th in rows[0].find_all(["td", "th"]):
                m = _re.search(r"width:\s*(\d+)%", th.get("style", ""))
                pct.append(int(m.group(1)) if m else None)
            widths = None
            if len(pct) == ncol and any(pct):
                rest = 100 - sum(x for x in pct if x)
                n_none = sum(1 for x in pct if not x) or 1
                widths = [186 * (x or rest / n_none) / 100 for x in pct]
            t = table(target, nrow, ncol, widths)
            for ri, ci, rs, cs, td in place:
                c = t.cell(ri, ci)
                if rs > 1 or cs > 1:
                    c = c.merge(t.cell(ri + rs - 1, ci + cs - 1))
                c.text = td.get_text(" ", strip=True)
                if td.name == "th":
                    shade(c, "F3F4F6")
                    for run in c.paragraphs[0].runs:
                        run.bold = True
            return
        if el.name in ("ul", "ol"):
            for i, li in enumerate(el.find_all("li", recursive=False), 1):
                para(target, (f"{i}. " if el.name == "ol" else "• ") + inline(li).strip(), size=11)
            return
        if el.name in ("h3", "h4"):
            para(target, inline(el).strip(), bold=True, size=13 if el.name == "h3" else 11)
            return
        # 一般容器：有區塊子元素就遞迴，否則當一段文字
        blocks = [c for c in el.children if isinstance(c, Tag) and c.name in ("div", "ol", "ul", "table", "h3", "h4", "p", "section")]
        if blocks:
            for c in el.children:
                block(target, c)
        else:
            txt = inline(el).strip()
            if txt:
                para(target, txt)

    sheets = soup.select(".sheet")
    for si, sh in enumerate(sheets):
        if si:
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        for el in sh.children:
            if not isinstance(el, Tag):
                continue
            if has(el, "head"):
                para(doc, "　".join(s.get_text(strip=True) for s in el.find_all("span")), size=11)
            elif has(el, "title"):
                extra = "（教師版）" if has(sh, "answer") else ""
                ver = el.select_one(".ver")
                vtxt = ""
                if ver:
                    vtxt = "【" + ver.get_text(strip=True) + "】"
                    ver.extract()
                para(doc, inline(el).strip() + vtxt + extra, size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
            elif has(el, "subtitle"):
                para(doc, inline(el).strip(), align=WD_ALIGN_PARAGRAPH.CENTER)
            elif has(el, "top"):
                kids = [c for c in el.children if isinstance(c, Tag)]
                t = table(doc, 1, len(kids))
                for i, k in enumerate(kids):
                    c = t.cell(0, i)
                    clear_first(c)
                    if has(k, "tag"):
                        for line in k.children:
                            if isinstance(line, Tag):
                                para(c, inline(line).strip(), size=11, bold=line.name == "h3")
                    else:
                        block(c, k)
            elif has(el, "goal-line"):
                para(doc, "學習目標：" + "　".join(f"{i}. " + x.get_text(strip=True) for i, x in enumerate(el.find_all("span"), 1)), size=10.5)
            elif has(el, "choose") or has(el, "star"):
                t = table(doc, 1, 1)
                c = t.cell(0, 0)
                clear_first(c)
                shade(c, "F0F9FF" if has(el, "choose") else "FEFCE8")
                lines = [x for x in el.children if has(x, "line")]
                for x in lines:
                    x.extract()
                para(c, inline(el).strip() if has(el, "star") else "　".join(x.get_text(strip=True) for x in el.find_all(["b", "span"])), size=10.5)
                for _ in lines:
                    para(c, "＿" * 40, size=10)
            elif has(el, "how"):
                t = table(doc, 1, 1)
                c = t.cell(0, 0)
                c.text = inline(el).strip()
                shade(c, "F3F4F6")
            elif has(el, "sec"):
                cls = next((c for c in el.get("class", []) if c in COLORS), "s1")
                t = table(doc, 2, 1)
                h = t.cell(0, 0)
                h.text = inline(el.select_one(".sec-h")).strip()
                shade(h, COLORS[cls])
                for run in h.paragraphs[0].runs:
                    run.bold = True
                    run.font.size = Pt(13)
                b = t.cell(1, 0)
                clear_first(b)
                body = el.select_one(".sec-b")
                if body:
                    block(b, body)
                gap = doc.add_paragraph()
                gap.paragraph_format.space_after = Pt(0)
                gap.add_run(" ").font.size = Pt(4)
            elif has(el, "check"):
                para(doc, "我完成了：" + "　".join("☐ " + s.get_text(strip=True) for s in el.find_all("span")), size=11)
            elif has(el, "teacher"):
                kids = [c for c in el.children if isinstance(c, Tag)]
                t = table(doc, 1, len(kids))
                for i, k in enumerate(kids):
                    c = t.cell(0, i)
                    clear_first(c)
                    shade(c, "F9FAFB")
                    block(c, k)
            elif has(el, "text"):
                for p in el.find_all("p"):
                    para(doc, inline(p).strip())
            else:
                block(doc, el)
    doc.save(str(out))
    print(f"DOCX：{out}")
    return True


DOCX_FONT = "標楷體"


def main():
    global DOCX_FONT
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    html = Path(sys.argv[1])
    flags = set(sys.argv[2:])
    if "--font=芫荽" in flags or "--iansui" in flags:
        DOCX_FONT = "Iansui"
    want_pdf = "--docx" not in flags or "--pdf" in flags
    want_docx = "--pdf" not in flags or "--docx" in flags
    if want_pdf:
        to_pdf(html, html.with_suffix(".pdf"))
    if want_docx:
        to_docx(html, html.with_suffix(".docx"))


if __name__ == "__main__":
    main()
