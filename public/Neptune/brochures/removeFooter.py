import os
import sys
import fitz  # PyMuPDF

# ---- ADJUST IF NEEDED ----
TOP_CROP = 60     # removes Bals logo + www.bals.com
BOTTOM_CROP = 70  # removes footer
# --------------------------

BALS_KEYWORDS = [
    "bals",
    "www.bals.com"
]


def is_bals_pdf(pdf_path: str) -> bool:
    """Lightweight safety check"""
    doc = fitz.open(pdf_path)
    for page in doc:
        text = page.get_text().lower()
        if any(k in text for k in BALS_KEYWORDS):
            doc.close()
            return True
    doc.close()
    return False


def clean_bals_pdf(input_pdf: str, output_pdf: str):
    if not is_bals_pdf(input_pdf):
        print(f"⏭ Skipped (not a Bals PDF): {input_pdf}")
        return False

    doc = fitz.open(input_pdf)

    for page in doc:
        r = page.rect

        page.set_cropbox(
            fitz.Rect(
                0,
                TOP_CROP,
                r.width,
                r.height - BOTTOM_CROP
            )
        )

    doc.save(output_pdf)
    doc.close()
    return True


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
    out = pdf.replace(".pdf", "_CLEAN_TEST.pdf")

    print("🧪 TEST MODE")
    if clean_bals_pdf(pdf, out):
        print(f"✅ Cleaned → {out}")


def run_mode():
    pdfs = get_pdfs()
    print(f"🚀 RUN MODE — scanning {len(pdfs)} PDFs")

    for pdf in pdfs:
        tmp = pdf + ".tmp"

        print(f"→ Processing {pdf}")
        if clean_bals_pdf(pdf, tmp):
            os.replace(tmp, pdf)
            print("  ✔ Updated")
        else:
            if os.path.exists(tmp):
                os.remove(tmp)

    print("✅ Run completed")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python clean_bals_pdf.py test")
        print("  python clean_bals_pdf.py run")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode == "test":
        test_mode()
    elif mode == "run":
        run_mode()
    else:
        print("❌ Invalid mode")
