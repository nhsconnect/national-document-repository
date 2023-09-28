from pypdf import PdfWriter


def stitch_pdf(filenames: list[str]) -> str:
    merger = PdfWriter()
    for filename in filenames:
        merger.append(filename)
    output_filename = '/tmp/stitched_lg.pdf'
    merger.write(output_filename)
    return output_filename
