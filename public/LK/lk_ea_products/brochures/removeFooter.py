import os
import sys
import fitz  # PyMuPDF

# ============================================================
# KEYWORD SETS (GENERIC)
# ============================================================

CONTACT_KEYWORDS = [
    # "Electrical Standard Products","Electrical","Products","Standard","(ESP)"
    "india", "uae", "qatar", "oman", "dubai",
    "mumbai", "chennai", "bangalore", "hyderabad",
    "kolkata", "noida", "pune","training","switchgear"
]

DATA_KEYWORDS = [
    # "specification", "specifications",
    # "features", "feature",
    # "technical", "mechanical", "electrical",
    # "rating", "ratings", "model", "models",
    # "dimensions", "capacity", "voltage", "current",
    # "frequency", "power", "kva", "kw", "hp"
]

FOOTER_HINT_KEYWORDS = [
    "email", "phone", "www", "address"
]

# ============================================================
# CLASSIFICATION LOGIC
# ============================================================
def is_switchgear_training_page(page: fitz.Page) -> bool:
    text = page.get_text("text").lower()

    keywords = [
        "switchgear training",
        "switchgear training center",
    ]

    hits = sum(1 for k in keywords if k in text)
    return hits >= 1

def classify_last_page(page: fitz.Page) -> str:
    text = page.get_text("text").lower()
    words = text.split()

    contact_hits = sum(1 for k in CONTACT_KEYWORDS if k in text)
    data_hits = sum(1 for k in DATA_KEYWORDS if k in text)

    # Strong contact page
    if contact_hits >= 3 and data_hits == 0:
        return "CONTACT_ONLY"

    # Data present → keep page
    if data_hits >= 1:
        return "DATA_PAGE"

    # Very little content → contact page
    if len(words) < 120:
        return "CONTACT_ONLY"

    return "DATA_PAGE"


def find_footer_start_y(page: fitz.Page):
    y_positions = []

    for w in page.get_text("words"):
        if any(k in w[4].lower() for k in FOOTER_HINT_KEYWORDS):
            y_positions.append(w[1])  # y0

    return min(y_positions) if y_positions else None

# ============================================================
# CORE PROCESSOR
# ============================================================

def process_pdf(input_pdf: str, output_pdf: str) -> bool:
    doc = fitz.open(input_pdf)

    if len(doc) == 0:
        doc.close()
        return False
    pages_to_delete = []
    for i, page in enumerate(doc):
        if is_switchgear_training_page(page):
            pages_to_delete.append(i)

    for i in reversed(pages_to_delete):
        print(f"  🗑 Removing Switchgear Training Center page: {i + 1}")
        doc.delete_page(i)
        modified = True

    last_page = doc[-1]
    page_type = classify_last_page(last_page)

    print(f"  🔍 Last page classified as: {page_type}")
    modified = False

    if page_type == "CONTACT_ONLY":
        print("  🗑 Removing entire last page",len(doc))
        doc.delete_page(len(doc) - 1)
        modified = True

    else:
        footer_y = find_footer_start_y(last_page)
        if footer_y:
            r = last_page.rect
            print("  ✂ Cropping footer only")
            last_page.set_cropbox(
                fitz.Rect(0, 0, r.width, footer_y - 35)
            )
            modified = True
        else:
            print("  ⏭ No footer detected")

    if modified:
        doc.save(output_pdf)

    doc.close()
    return modified

# ============================================================
# MODES (TEST / RUN)
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
    print(f"→ Processing {pdf}")
    process_pdf(pdf, out)


def run_mode():
    pdfs = get_pdfs()
    print(f"🚀 RUN MODE — scanning {len(pdfs)} PDFs")

    for pdf in pdfs:
        tmp = pdf + ".tmp"
        print(f"→ Processing {pdf}")

        if process_pdf(pdf, tmp):
            os.replace(tmp, pdf)
            print("  ✔ Updated")
        else:
            if os.path.exists(tmp):
                os.remove(tmp)
            print("  ⏭ Skipped")

    print("✅ Run completed")

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python last_page_smart_cleanup.py test")
        print("  python last_page_smart_cleanup.py run")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode == "test":
        test_mode()
    elif mode == "run":
        run_mode()
    else:
        print("❌ Invalid mode (use test or run)")
