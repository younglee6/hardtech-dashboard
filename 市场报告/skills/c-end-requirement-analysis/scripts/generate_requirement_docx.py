#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import zipfile
from xml.sax.saxutils import escape


CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""


def p(text: str, style: str = "") -> str:
    text = escape(text or "")
    if style:
        return (
            f"<w:p><w:pPr><w:pStyle w:val=\"{style}\"/></w:pPr>"
            f"<w:r><w:t xml:space=\"preserve\">{text}</w:t></w:r></w:p>"
        )
    return f"<w:p><w:r><w:t xml:space=\"preserve\">{text}</w:t></w:r></w:p>"


def bullet(text: str) -> str:
    return p(f"- {text}")


def table(headers, rows) -> str:
    lines = [
        "<w:tbl><w:tblPr><w:tblBorders>"
        "<w:top w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:left w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:right w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:insideH w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:insideV w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "</w:tblBorders></w:tblPr>"
    ]

    def tr(cells):
        cell_xml = []
        for c in cells:
            cell_xml.append(
                "<w:tc><w:tcPr/><w:p><w:r><w:t xml:space=\"preserve\">"
                + escape(str(c))
                + "</w:t></w:r></w:p></w:tc>"
            )
        return "<w:tr>" + "".join(cell_xml) + "</w:tr>"

    lines.append(tr(headers))
    for r in rows:
        lines.append(tr(r))
    lines.append("</w:tbl>")
    return "".join(lines)


def build_document(data: dict) -> str:
    title = data.get("title", "需求分析文档")
    version = data.get("version", "v1.0")
    doc_date = data.get("date") or dt.date.today().isoformat()
    author = data.get("author", "产品经理")

    body = [p(title, "Title"), p(f"版本：{version}"), p(f"日期：{doc_date}"), p(f"作者：{author}"), p("")]

    summary = data.get("summary", [])
    if summary:
        body.append(p("关键结论", "Heading1"))
        for item in summary:
            body.append(bullet(str(item)))
        body.append(p(""))

    for section in data.get("sections", []):
        heading = section.get("heading", "未命名章节")
        body.append(p(heading, "Heading1"))
        for para in section.get("paragraphs", []):
            body.append(p(str(para)))
        for item in section.get("bullets", []):
            body.append(bullet(str(item)))
        tbl = section.get("table")
        if isinstance(tbl, dict):
            headers = tbl.get("headers", [])
            rows = tbl.get("rows", [])
            if headers and rows:
                body.append(table(headers, rows))
        body.append(p(""))

    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
        "<w:body>"
        + "".join(body)
        + "<w:sectPr/></w:body></w:document>"
    )


def main():
    parser = argparse.ArgumentParser(description="Generate requirement analysis DOCX from JSON")
    parser.add_argument("--input", required=True, help="Path to JSON input")
    parser.add_argument("--output", required=True, help="Path to output .docx")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    document_xml = build_document(data)
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
        zf.writestr("_rels/.rels", RELS_XML)
        zf.writestr("word/document.xml", document_xml)

    print(f"DOCX generated: {args.output}")


if __name__ == "__main__":
    main()
