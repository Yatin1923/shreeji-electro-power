import os
import sys
import fitz  # PyMuPDF

# ============================================================
# CONFIG
# ============================================================

# ---- BALS LOGO (top-right) ----
BALS_LOGO_RECT_RATIO = {
    "x0": 0.55,
    "y0": 0.00,
    "x1": 1.00,
    "y1": 0.18
}

# ---- NEPTUNE FOOTER (last page only) ----
NEPTUNE_FOOTER_RATIO = {
    "x0": 0.00,
    "y0": 0.65,   # bottom 35%
    "x1": 1.00,
    "y1": 1.00
}

# ============================================================
# DETECTION
# ============================================================

def has_datasheet_header(page: fitz.Page) -> bool:
    """Detect 'Data sheet' in top-left"""
    r = page.rect
    header_rect = fitz.Rect(0, 0, r.width * 0.45, r.height * 0.20)

    for w in page.get_text("words"):
        if "data" in w[4].lower() and header_rect.intersects(fitz.Rect(w[:4])):
            return True
    return False


def has_neptune_footer(page: fitz.Page) -> bool:
    """Detect Neptune branding text"""
    text = page.get_text().lower()
    return (
        "neptune" in text or
        "neptuneindia.com" in text or
        "neptune india" in text
    )

# ============================================================
# MODIFICATIONS
# ============================================================

def remove_bals_logo(doc: fitz.Document) -> bool:
    modified = False

    for page in doc:
        if not has_datasheet_header(page):
            continue

        r = page.rect
        logo_rect = fitz.Rect(
            r.width * BALS_LOGO_RECT_RATIO["x0"],
            r.height * BALS_LOGO_RECT_RATIO["y0"],
            r.width * BALS_LOGO_RECT_RATIO["x1"],
            r.height * BALS_LOGO_RECT_RATIO["y1"],
        )

        page.draw_rect(
            logo_rect,
            fill=(1, 1, 1),
            color=(1, 1, 1),
            overlay=True
        )
        modified = True

    return modified


def remove_neptune_footer(doc: fitz.Document) -> bool:
    """
    Dynamically crop Neptune footer from the last page
    based on detected footer text position
    """
    last_page = doc[-1]
    words = last_page.get_text("words")

    footer_y_positions = []

    for w in words:
        text = w[4].lower()
        if (
            "neptune" in text or
            "neptuneindia.com" in text or
            "neptune india" in text
        ):
            footer_y_positions.append(w[1])  # y0 of word

    if not footer_y_positions:
        return False  # no Neptune footer found

    footer_start_y = min(footer_y_positions)

    r = last_page.rect

    # Crop everything below footer_start_y
    last_page.set_cropbox(
        fitz.Rect(
            0,
            0,
            r.width,
            footer_start_y - 5  # small safety padding
        )
    )

    return True

# ============================================================
# PIPELINE
# ============================================================

def process_pdf(input_pdf: str, output_pdf: str) -> bool:
    doc = fitz.open(input_pdf)
    modified = False

    print(f"  🔍 Checking: {input_pdf}")

    if remove_bals_logo(doc):
        print("  ✔ Bals logo removed")
        modified = True

    if remove_neptune_footer(doc):
        print("  ✔ Neptune footer removed (last page)")
        modified = True

    if modified:
        doc.save(output_pdf)
    else:
        print("  ⏭ No changes required")

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
        print("❌ Invalid mode")
