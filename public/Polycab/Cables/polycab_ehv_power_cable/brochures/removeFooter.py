import os
import sys
from pypdf import PdfReader, PdfWriter

FOOTER_HEIGHT = 60  # points (adjust if needed)

FOOTER_KEYWORDS = [
    "1800 267 0008",
    "enquiry@polycab.com",
    "www.polycab.com"
]


def has_footer(reader: PdfReader) -> bool:
    """
    Check if any page contains expected footer text
    """
    for page in reader.pages:
        text = page.extract_text() or ""
        if any(keyword in text for keyword in FOOTER_KEYWORDS):
            return True
    return False


def remove_footer(input_path: str, output_path: str):
    reader = PdfReader(input_path)

    # 🔍 Footer validation
    if not has_footer(reader):
        print(f"⚠️  Footer NOT detected → Skipping: {input_path}")
        return False

    writer = PdfWriter()

    for page in reader.pages:
        media_box = page.mediabox
        media_box.lower_left = (0, FOOTER_HEIGHT)
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

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
    output = pdf.replace(".pdf", "_NO_FOOTER_TEST.pdf")

    print("🧪 TEST MODE")
    print(f"Checking footer in: {pdf}")

    if remove_footer(pdf, output):
        print(f"✅ Footer removed → {output}")
    else:
        print("❌ Footer not found. No output generated.")


def run_mode():
    pdfs = get_pdfs()
    if not pdfs:
        print("❌ No PDFs found")
        return

    print(f"🚀 RUN MODE — scanning {len(pdfs)} PDFs")

    for pdf in pdfs:
        temp = pdf + ".tmp"

        print(f"→ Processing {pdf}")
        updated = remove_footer(pdf, temp)

        if updated:
            os.replace(temp, pdf)
            print("  ✔ Updated")
        else:
            if os.path.exists(temp):
                os.remove(temp)
            print("  ⏭ Skipped (footer not found)")

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
        print("❌ Invalid mode. Use 'test' or 'run'")
