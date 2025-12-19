import os
import sys
import fitz  # PyMuPDF

# ============================================================
# CONFIG (tune once if needed)
# ============================================================

# Area where Bals logo appears (top-right)
LOGO_RECT_RATIO = {
    "x0": 0.55,   # start from 55% width
    "y0": 0.00,   # top
    "x1": 1.00,   # right edge
    "y1": 0.18    # top 18% height
}

# ============================================================
# DETECTION LOGIC
# ============================================================

def has_datasheet_header(page: fitz.Page) -> bool:
    """
    Detect 'Data sheet' text in top-left region
    """
    r = page.rect
    header_rect = fitz.Rect(
        0,
        0,
        r.width * 0.45,    # left 45%
        r.height * 0.20    # top 20%
    )

    for w in page.get_text("words"):
        word_rect = fitz.Rect(w[:4])
        word_text = w[4].lower()

        if "data" in word_text and header_rect.intersects(word_rect):
            return True

    return False


# ============================================================
# MODIFICATION LOGIC
# ============================================================

def remove_bals_logo_if_needed(doc: fitz.Document) -> bool:
    """
    Removes Bals logo ONLY if 'Data sheet' is detected
    """
    modified = False

    for page in doc:
        if not has_datasheet_header(page):
            continue

        r = page.rect
        logo_rect = fitz.Rect(
            r.width * LOGO_RECT_RATIO["x0"],
            r.height * LOGO_RECT_RATIO["y0"],
            r.width * LOGO_RECT_RATIO["x1"],
            r.height * LOGO_RECT_RATIO["y1"],
        )

        page.draw_rect(
            logo_rect,
            color=(1, 1, 1),
            fill=(1, 1, 1),
            overlay=True
        )

        modified = True

    return modified


# ============================================================
# PIPELINE
# ============================================================

def process_pdf(input_pdf: str, output_pdf: str) -> bool:
    doc = fitz.open(input_pdf)

    print(f"  🔍 Checking: {input_pdf}")
    modified = remove_bals_logo_if_needed(doc)

    if modified:
        doc.save(output_pdf)
        print("  ✔ Bals logo removed")
    else:
        print("  ⏭ No Datasheet header found")

    doc.close()
    return modified


# ============================================================
# MODES
# ============================================================

def get_pdfs():
    return sorted(
        f for f in os.listdir(".")
        if f.lower().endswith(".pdf") and os.path.isfile(f)
    )


def test_mode():
    pdfs = get_pdfs()
    if not pdfs:
        print("❌ No PDFs found")
        return

    pdf = pdfs[0]
    out = pdf.replace(".pdf", "_TEST.pdf")

    print("🧪 TEST MODE")
    process_pdf(pdf, out)


def run_mode():
    pdfs = get_pdfs()
    print(f"🚀 RUN MODE — scanning {len(pdfs)} PDFs")

    for pdf in pdfs:
        tmp = pdf + ".tmp"
        print(f"→ Processing {pdf}")

        if process_pdf(pdf, tmp):
            os.replace(tmp, pdf)
        else:
            if os.path.exists(tmp):
                os.remove(tmp)

    print("✅ Run completed")


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python removeFooter.py test")
        print("  python removeFooter.py run")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "test":
        test_mode()
    elif mode == "run":
        run_mode()
    else:
        print("❌ Invalid mode (use test or run)")
