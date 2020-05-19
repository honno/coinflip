from weasyprint import HTML


def write_report(markup, outfile):
    html = HTML(string=markup)
    html.write_pdf(outfile)
