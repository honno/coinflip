import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import pandas as pd
from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2.exceptions import TemplateNotFound

from coinflip._randtests.common.result import BaseTestResult
from coinflip.cli.pprint import print_warning

__all__ = ["store_results", "load_results", "write_report_doc"]


@dataclass
class Report:
    series: pd.Series
    results: Dict[str, BaseTestResult]


def store_results(series: pd.Series, results: Dict[str, BaseTestResult], out: str):
    report = Report(series, results)

    pickle.dump(report, open(out, "wb"))


def load_results(results_path: Path) -> Report:
    report = pickle.load(open(results_path, "rb"))

    return report


templates_dir = Path(__file__).parents[3] / "templates"
templates_loader = FileSystemLoader(templates_dir)
templates_env = Environment(loader=templates_loader)


def write_report_doc(report: Report, out: Path):
    doc = templates_env.get_template("index.html")

    result_markups = []
    for randtest, result in report.results.items():
        template_file = f"randtests/{randtest}.html"
        try:
            template = templates_env.get_template(template_file)
            markup = template.render(result=result)
            result_markups.append(markup)
        except TemplateNotFound:
            print_warning(f"{template_file} not found")

    with open(out, "w") as f:
        report_html = doc.render(result_markups=result_markups)
        f.write(report_html)
