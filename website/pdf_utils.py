import fitz
from django.core.files.base import ContentFile

# 3x zoom matches the manual PyMuPDF renders used earlier for the ISO/GST/
# Udyam certificate images (595x842pt A4 page -> ~1785x2526px), sharp enough
# for the "View Full Certificate"-style click-through even though here it's
# only ever used as the on-page thumbnail (the PDF itself is what actually
# opens on click).
PDF_RENDER_ZOOM = 3


def render_pdf_first_page_to_png(pdf_file, base_name):
    """Renders page 1 of an uploaded PDF to a PNG ContentFile via PyMuPDF, so
    a Certification can show a real certificate-style thumbnail image even
    when the admin only has a PDF to upload. Raises ValueError if the bytes
    can't be opened as a PDF or the document has no pages — should only
    happen if validate_pdf_file's own magic-byte check was somehow bypassed
    (e.g. a corrupt file that still starts with '%PDF-')."""
    pdf_file.seek(0)
    data = pdf_file.read()
    pdf_file.seek(0)

    try:
        doc = fitz.open(stream=data, filetype='pdf')
    except Exception as exc:
        raise ValueError('Could not read PDF file.') from exc

    try:
        if doc.page_count < 1:
            raise ValueError('PDF has no pages.')
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(PDF_RENDER_ZOOM, PDF_RENDER_ZOOM))
        png_bytes = pix.tobytes('png')
    finally:
        doc.close()

    return ContentFile(png_bytes, name=f'{base_name}.png')
