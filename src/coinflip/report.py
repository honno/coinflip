from pathlib import Path
from typing import Iterator

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2.exceptions import TemplateNotFound

templates_dir = Path(__file__).parents[2] / "templates"
templates_loader = FileSystemLoader(templates_dir)
templates_env = Environment(loader=templates_loader)


def write_report(results, outfile) -> Iterator[Exception]:
    report = templates_env.get_template("index.html")

    result_markups = []
    for randtest, result in results.items():
        template_file = f"randtests/{randtest}.html"
        try:
            template = templates_env.get_template(template_file)
            markup = template.render(result=result)
            result_markups.append(markup)
        except TemplateNotFound as e:
            yield e

    with open(outfile, "w") as f:
        report_html = report.render(result_markups=result_markups)
        f.write(report_html)
