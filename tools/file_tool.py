from pathlib import Path


def create_file(filename, content):
    file_path = Path("outputs") / filename

    file_path.parent.mkdir(exist_ok=True)

    file_path.write_text(content, encoding="utf-8")

    return f"File created successfully: {file_path}"