import os
import sys
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

FOOTER_HEIGHT = 50  # slightly larger for OCR safety

FOOTER_KEYWORDS = [
    "1800 267 0008",
    "enquiry@polycab.com",
    "www.polycab.com",
    "TOLL FREE"
]


def footer_contains_keywords(pdf_path: str) -> bool:
    """
    OCR bottom part of page and check for footer keywords
    """
    doc = fitz.open(pdf_path)

    for page in doc:
        rect = page.rect

        footer_rect = fitz.Rect(
            0,
            rect.height - FOOTER_HEIGHT,
            rect.width,
            rect.height
        )

        pix = page.get_pixmap(clip=footer_rect, dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        text = pytesseract.image_to_string(img).lower()

        if any(keyword.lower() in text for keyword in FOOTER_KEYWORDS):
            doc.close()
            return True

    doc.close()
    return False


def remove_footer(input_pdf: str, output_pdf: str):
    if not footer_contains_keywords(input_pdf):
        print(f"⏭ Skipped (keywords not found): {input_pdf}")
        return False

    doc = fitz.open(input_pdf)

    for page in doc:
        r = page.rect
        page.set_cropbox(
            fitz.Rect(0, 0, r.width, r.height - FOOTER_HEIGHT)
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

    pdf = pdfs[17]
    out = pdf.replace(".pdf", "_NO_FOOTER_TEST.pdf")

    print("🧪 TEST MODE")
    print(f"Scanning footer keywords in: {pdf}")

    if remove_footer(pdf, out):
        print(f"✅ Footer removed → {out}")
    else:
        print("❌ Footer keywords not detected")


def run_mode():
    pdfs = get_pdfs()
    if not pdfs:
        print("❌ No PDFs found")
        return

    print(f"🚀 RUN MODE — scanning {len(pdfs)} PDFs")

    for pdf in pdfs:
        tmp = pdf + ".tmp"

        print(f"→ Processing {pdf}")
        if remove_footer(pdf, tmp):
            os.replace(tmp, pdf)
            print("  ✔ Updated")
        else:
            if os.path.exists(tmp):
                os.remove(tmp)
            print("  ⏭ Skipped")

    print("✅ Run completed")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python remove_footer.py test")
        print("  python remove_footer.py run")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode == "test":
        test_mode()
    elif mode == "run":
        run_mode()
    else:
        print("❌ Invalid mode")
