import argparse
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


DEFAULT_OUTPUT = Path("data/songs.json")
SOURCE_ARCHIVE = Path("source_archive")
PREFERRED_SHEETS = ("쿠라s 노래책~!", "쿠라's 노래책~!")

COLUMN_MAPPING = [
    ("A", "title"),
    ("B", "translation"),
    ("C", "artist"),
    ("D", "artistKr"),
    ("E", "language"),
    ("F", "genre"),
    ("G", "genre1"),
    ("H", "genre2"),
    ("I", "theme"),
    ("J", "situation"),
    ("K", "target"),
    ("L", "emotion"),
    ("M", "sourceNote"),
    ("N", "media"),
    ("O", "sourceType"),
    ("P", "workTitle"),
    ("Q", "tags"),
    ("R", "videoUrl"),
    ("S", "lyricsUrl"),
    ("T", "singCount"),
    ("U", "pick"),
    ("V", "thumbnailUrl"),
]
OPTIONAL_HEADER_MAPPING = {
    "곡 소개": "songIntro",
}

YOUTUBE_ID_PATTERN = re.compile(
    r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})"
)

NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkg_rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def find_default_xlsx() -> Path:
    files = sorted(SOURCE_ARCHIVE.glob("*.xlsx"))
    if not files:
        raise FileNotFoundError("No .xlsx file found in source_archive/.")
    if len(files) > 1:
        names = ", ".join(str(path) for path in files)
        raise ValueError(f"Multiple .xlsx files found. Pass --input explicitly: {names}")
    return files[0]


def normalize_cell(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return value


def stringify(value) -> str:
    value = normalize_cell(value)
    if value == "":
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def parse_sing_count(value) -> int:
    value = normalize_cell(value)
    if value == "":
        return 0
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def parse_pick(value) -> bool:
    value = stringify(value).lower()
    if value == "":
        return False
    return value not in {"false", "0", "no", "n", "없음", "x"}


def extract_youtube_id(url: str) -> str:
    match = YOUTUBE_ID_PATTERN.search(url or "")
    return match.group(1) if match else ""


def make_thumbnail_url(video_url: str, existing_thumbnail: str) -> str:
    youtube_id = extract_youtube_id(video_url)
    if youtube_id:
        return f"https://img.youtube.com/vi/{youtube_id}/mqdefault.jpg"
    return existing_thumbnail


def is_blank_source_row(values) -> bool:
    important_values = values[:19]
    return all(stringify(value) == "" for value in important_values)


def column_index(cell_ref: str) -> int:
    letters = re.match(r"([A-Z]+)", cell_ref).group(1)
    index = 0
    for letter in letters:
        index = index * 26 + ord(letter) - ord("A") + 1
    return index


def read_shared_strings(archive: zipfile.ZipFile):
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []

    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    strings = []
    for item in root.findall("main:si", NS):
        text_parts = [node.text or "" for node in item.findall(".//main:t", NS)]
        strings.append("".join(text_parts))
    return strings


def read_workbook_sheets(archive: zipfile.ZipFile):
    workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
    rels_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    rels = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels_root.findall("pkg_rel:Relationship", NS)
    }

    sheets = []
    for sheet in workbook_root.findall("main:sheets/main:sheet", NS):
        rel_id = sheet.attrib[f"{{{NS['rel']}}}id"]
        target = rels[rel_id].lstrip("/")
        path = target if target.startswith("xl/") else f"xl/{target}"
        sheets.append({"name": sheet.attrib["name"], "path": path})
    return sheets


def read_cell_value(cell, shared_strings):
    cell_type = cell.attrib.get("t", "")

    if cell_type == "inlineStr":
        text_parts = [node.text or "" for node in cell.findall(".//main:t", NS)]
        return "".join(text_parts)

    value_node = cell.find("main:v", NS)
    if value_node is None:
        return ""

    raw_value = value_node.text or ""
    if cell_type == "s":
        return shared_strings[int(raw_value)] if raw_value else ""
    if cell_type == "b":
        return raw_value == "1"
    if cell_type == "str":
        return raw_value

    try:
        number = float(raw_value)
    except ValueError:
        return raw_value
    return int(number) if number.is_integer() else number


def read_sheet_rows(archive: zipfile.ZipFile, sheet_path: str, shared_strings):
    root = ET.fromstring(archive.read(sheet_path))
    rows = []

    for row in root.findall(".//main:sheetData/main:row", NS):
        cell_values = {}
        max_column = 22
        for cell in row.findall("main:c", NS):
            ref = cell.attrib.get("r", "")
            if not ref:
                continue
            index = column_index(ref)
            max_column = max(max_column, index)
            cell_values[index - 1] = read_cell_value(cell, shared_strings)

        values = [""] * max_column
        for index, value in cell_values.items():
            values[index] = value
        rows.append(values)

    return rows


def build_header_map(header_row):
    return {stringify(value): index for index, value in enumerate(header_row)}


def get_optional_value(values, header_map, header_name):
    index = header_map.get(header_name)
    if index is None or index >= len(values):
        return ""
    return values[index]


def detect_db_sheet(sheets, sheet_rows_by_name):
    for sheet_name in PREFERRED_SHEETS:
        if sheet_name in sheet_rows_by_name:
            return sheet_name, sheet_rows_by_name[sheet_name]

    for sheet in sheets:
        rows = sheet_rows_by_name[sheet["name"]]
        headers = [stringify(value) for value in rows[0][:22]] if rows else []
        if headers[:5] == ["제목", "번역명", "가수", "한국명", "언어"]:
            return sheet["name"], rows

    raise ValueError("Could not find the DB sheet.")


def convert_workbook(input_path: Path):
    with zipfile.ZipFile(input_path) as archive:
        shared_strings = read_shared_strings(archive)
        sheets = read_workbook_sheets(archive)
        sheet_rows_by_name = {
            sheet["name"]: read_sheet_rows(archive, sheet["path"], shared_strings)
            for sheet in sheets
        }

    sheet_name, rows = detect_db_sheet(sheets, sheet_rows_by_name)
    songs = []
    header_map = build_header_map(rows[0]) if rows else {}

    for row in rows[1:]:
        values = list(row)
        if is_blank_source_row(values):
            continue

        raw = {field: values[position] for position, (_column, field) in enumerate(COLUMN_MAPPING)}
        optional_raw = {
            field: get_optional_value(values, header_map, header)
            for header, field in OPTIONAL_HEADER_MAPPING.items()
        }
        video_url = stringify(raw["videoUrl"])
        existing_thumbnail = stringify(raw["thumbnailUrl"])

        songs.append(
            {
                "id": f"S{len(songs) + 1:04d}",
                "title": stringify(raw["title"]),
                "translation": stringify(raw["translation"]),
                "artist": stringify(raw["artist"]),
                "artistKr": stringify(raw["artistKr"]),
                "language": stringify(raw["language"]),
                "genre": stringify(raw["genre"]),
                "genre1": stringify(raw["genre1"]),
                "genre2": stringify(raw["genre2"]),
                "theme": stringify(raw["theme"]),
                "songIntro": stringify(optional_raw["songIntro"]),
                "situation": stringify(raw["situation"]),
                "target": stringify(raw["target"]),
                "emotion": stringify(raw["emotion"]),
                "sourceNote": stringify(raw["sourceNote"]),
                "media": stringify(raw["media"]),
                "sourceType": stringify(raw["sourceType"]),
                "workTitle": stringify(raw["workTitle"]),
                "tags": stringify(raw["tags"]),
                "videoUrl": video_url,
                "lyricsUrl": stringify(raw["lyricsUrl"]),
                "singCount": parse_sing_count(raw["singCount"]),
                "pick": parse_pick(raw["pick"]),
                "thumbnailUrl": make_thumbnail_url(video_url, existing_thumbnail),
            }
        )

    return sheet_name, songs


def main():
    parser = argparse.ArgumentParser(
        description="Convert the Kura Songbook xlsx snapshot to data/songs.json."
    )
    parser.add_argument("--input", type=Path, default=None, help="Path to the xlsx snapshot.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSON path.")
    parser.add_argument("--dry-run", action="store_true", help="Print a preview without writing JSON.")
    args = parser.parse_args()

    input_path = args.input or find_default_xlsx()
    sheet_name, songs = convert_workbook(input_path)

    preview = {
        "input": str(input_path),
        "detectedSheetName": sheet_name,
        "columnMapping": {column: field for column, field in COLUMN_MAPPING},
        "totalSongCount": len(songs),
        "firstFiveRecords": songs[:5],
    }

    if args.dry_run:
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(songs, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(preview, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
