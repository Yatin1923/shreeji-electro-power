import fitz  # PyMuPDF
import os

# ---- ADJUST THESE ONCE ----
LOGO_RECT_RATIO = {
    "x0": 0.55,   # start from 55% width
    "y0": 0.00,   # from top
    "x1": 1.00,   # till right edge
    "y1": 0.18    # top 18% height
}
# --------------------------


def remove_bals_logo(input_pdf: str, output_pdf: str):
    doc = fitz.open(input_pdf)

    for page in doc:
        r = page.rect

        logo_rect = fitz.Rect(
            r.width * LOGO_RECT_RATIO["x0"],
            r.height * LOGO_RECT_RATIO["y0"],
            r.width * LOGO_RECT_RATIO["x1"],
            r.height * LOGO_RECT_RATIO["y1"],
        )

        # Draw white rectangle over logo
        page.draw_rect(
            logo_rect,
            color=(1, 1, 1),
            fill=(1, 1, 1),
            overlay=True
        )

    doc.save(output_pdf)
    doc.close()


if __name__ == "__main__":
    input_pdf = "2199%20-%20Copy.pdf"
    output_pdf = "2199_NO_BALS_LOGO.pdf"

    remove_bals_logo(input_pdf, output_pdf)
    print("✅ Bals logo removed safely")
