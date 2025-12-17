import os
from pathlib import Path
from fpdf import FPDF
from io import BytesIO
from PIL import Image
import markdown
from bs4 import BeautifulSoup
from typing import Literal
import json
import tempfile


# small function for testing, converts prepared context into single pdf
def create_pdf(content_list, output_filename):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    temp_files = []
    ss = ""
    new_list = []
    for item in content_list:
        if isinstance(item, str):
            ss += "\n" + item
        else:
            new_list.append(ss)
            new_list.append(item)
            ss = ""

    try:
        for item in new_list:
            pdf.add_page()

            if isinstance(item, str):
                html = markdown.markdown(item)
                soup = BeautifulSoup(html, "html.parser")

                for elem in soup.find_all(["h1", "h2", "h3", "p", "code"]):
                    if elem.name == "h1":
                        pdf.set_font("helvetica", "B", 16)
                    elif elem.name == "h2":
                        pdf.set_font("helvetica", "B", 14)
                    elif elem.name == "h3":
                        pdf.set_font("helvetica", "B", 12)
                    else:
                        pdf.set_font("helvetica", "", 11)
                    pdf.multi_cell(0, 8, elem.get_text())
                    pdf.ln(2)
            else:
                img_bytes = item if isinstance(item, bytes) else item.data
                img = Image.open(BytesIO(img_bytes))
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                img.save(temp_file.name)
                temp_files.append(temp_file.name)
                pdf.image(temp_file.name, x=10, w=190)

        pdf.output(output_filename)

    finally:
        # Clean up all temp files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)


def save_analysis(
    run_id: str,
    context: list,
    analysis: str,
    analysis_json: str | None = None,
    agent_type: str = "eai",
    context_type: Literal["pdf", "str"] = "pdf",
):
    base_path = Path(f"analysis_context/{run_id}/{agent_type}")
    base_path.mkdir(parents=True, exist_ok=True)

    path_result = base_path / "analysis.md"
    with open(path_result, "w") as f:
        f.write(analysis)
    if context_type == "pdf":
        path_context = base_path / "context.pdf"
        create_pdf(context, path_context)
    elif context_type == "str":
        path_context = base_path / "context.md"
        with open(path_context, "w") as f:
            f.write(context[0])

    if analysis_json:
        path_result = base_path / "analysis.json"
        with open(path_result, "w") as f:
            json.dump(analysis_json, f)
