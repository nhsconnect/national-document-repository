from pypdf import PdfWriter


def stitch_pdf(filenames: list[str], output_filename: str = "merged_file.pdf") -> str:
    merger = PdfWriter()
    for filename in filenames:
        merger.append(filename)

    merger.write(output_filename)
    return output_filename
