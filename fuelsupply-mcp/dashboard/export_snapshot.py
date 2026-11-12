"""Export the current saved dashboard as one offline, credential-free HTML file."""

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def export(output):
    page = (HERE / "index.html").read_text()
    css = (HERE / "styles.css").read_text()
    js = (HERE / "app.js").read_text()
    data = json.loads((HERE / "data/snapshot.json").read_text())
    payload = json.dumps(data).replace("</", "<\\/")
    page = page.replace(
        '<link rel="stylesheet" href="styles.css">', "<style>" + css + "</style>"
    )
    page = page.replace(
        '<script src="data/snapshot.js"></script>',
        "<script>window.FUELSUPPLY_DATA = " + payload + ";</script>",
    )
    page = page.replace('<script src="app.js"></script>', "<script>" + js + "</script>")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page)
    print("Saved offline dashboard:", output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    export(parser.parse_args().output)
