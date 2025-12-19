import os
import sys
from pypdf import PdfReader, PdfWriter

FOOTER_HEIGHT = 50  # adjust if needed (points)

def remove_footer(input_path: str, output_path: str):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        media_box = page.mediabox
        media_box.lower_left = (0, FOOTER_HEIGHT)
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)


def get_pdfs_in_current_folder():
    return sorted([
        f for f in os.listdir(".")
        if f.lower().endswith(".pdf") and os.path.isfile(f)
    ])


def test_mode():
    pdfs = get_pdfs_in_current_folder()

    if not pdfs:
        print("❌ No PDFs found in current folder")
        return

    input_pdf = pdfs[0]
    output_pdf = input_pdf.replace(".pdf", "_NO_FOOTER_TEST.pdf")

    print(f"🧪 TEST MODE")
    print(f"Processing: {input_pdf}")
    print(f"Output:     {output_pdf}")

    remove_footer(input_pdf, output_pdf)

    print("✅ Test PDF generated successfully")


def run_mode():
    pdfs = get_pdfs_in_current_folder()

    if not pdfs:
        print("❌ No PDFs found in current folder")
        return

    print(f"🚀 RUN MODE — Processing {len(pdfs)} PDFs (IN-PLACE)")

    for pdf in pdfs:
        temp_output = pdf + ".tmp"

        print(f" → Updating {pdf}")
        remove_footer(pdf, temp_output)

        # Replace original file
        os.replace(temp_output, pdf)

    print("✅ All PDFs updated successfully")


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
