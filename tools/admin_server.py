from __future__ import annotations

import argparse
import csv
import difflib
import html
import json
import re
import shutil
import threading
import time
import unicodedata
import urllib.parse
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


HOST = "localhost"
PORT = 8765

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
JSON_PATH = DATA_DIR / "songs.json"
CSV_PATH = DATA_DIR / "songs_master.csv"
BACKUP_DIR = DATA_DIR / "backups"
STATIC_DIR = Path(__file__).resolve().parent / "admin_static"

FIELDS = [
    "id",
    "title",
    "translation",
    "artist",
    "artistKr",
    "language",
    "genre",
    "genre1",
    "genre2",
    "theme",
    "situation",
    "target",
    "emotion",
    "sourceNote",
    "media",
    "sourceType",
    "workTitle",
    "tags",
    "videoUrl",
    "lyricsUrl",
    "singCount",
    "pick",
    "thumbnailUrl",
    "songIntro",
]

TEXTAREA_FIELDS = {"songIntro", "sourceNote", "tags"}
PICK_TRUE = {"true", "1", "yes", "y", "예", "체크", "checked", "on"}
PICK_FALSE = {"", "false", "0", "no", "n", "아니오", "unchecked"}


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    auto_normalizations: list[str] = field(default_factory=list)
    deletion_candidates: list[dict] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass
class PreviewResult:
    rows: list[dict]
    json_rows: list[dict]
    prepared_rows: list[dict]
    rows_for_json: list[dict]
    additions: list[dict]
    updates: list[dict]
    validation: ValidationResult


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def normalize_key(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).lower()
    text = re.sub(r"[\s\-_·.,!?~'\"“”‘’()\[\]{}<>♡☆★♪♫/\\|:;]+", "", text)
    return text


def normalize_title_artist(row: dict) -> str:
    return f"{normalize_key(row.get('title'))}\0{normalize_key(row.get('artist'))}"


def read_json() -> list[dict]:
    with JSON_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("songs.json root must be a list")
    return [normalize_row(row) for row in data]


def write_json(rows: list[dict]) -> None:
    with JSON_PATH.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)
        file.write("\n")


def normalize_row(row: dict) -> dict:
    normalized = {}
    for field_name in FIELDS:
        value = row.get(field_name, "")
        if field_name == "singCount":
            normalized[field_name] = value if isinstance(value, int) else str(value)
        elif field_name == "pick":
            normalized[field_name] = value if isinstance(value, bool) else str(value)
        else:
            normalized[field_name] = "" if value is None else str(value)
    return normalized


def read_csv_master() -> list[dict]:
    ensure_master_csv()
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            return []
        missing = [field_name for field_name in FIELDS if field_name not in reader.fieldnames]
        if missing:
            raise ValueError(f"songs_master.csv missing fields: {', '.join(missing)}")
        return [normalize_row(row) for row in reader]


def write_csv_master(rows: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = CSV_PATH.with_suffix(".csv.tmp")
    with temp_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            csv_row = normalize_row(row)
            writer.writerow({field_name: csv_row.get(field_name, "") for field_name in FIELDS})
    temp_path.replace(CSV_PATH)


def ensure_master_csv() -> bool:
    if CSV_PATH.exists():
        return False
    rows = read_json()
    write_csv_master(rows)
    return True


def parse_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    normalized = unicodedata.normalize("NFKC", str(value or "")).strip().lower()
    if normalized in PICK_TRUE:
        return True
    if normalized in PICK_FALSE:
        return False
    raise ValueError(f"pick 값을 boolean으로 바꿀 수 없습니다: {value}")


def parse_sing_count(value: object) -> int:
    text = str(value if value is not None else "").strip()
    if text == "":
        return 0
    return int(text)


def extract_youtube_id(url: str) -> str:
    if not url:
        return ""
    try:
        parsed = urllib.parse.urlparse(url.strip())
    except ValueError:
        return ""

    host = parsed.netloc.lower()
    path_parts = [part for part in parsed.path.split("/") if part]
    if "youtu.be" in host:
        return path_parts[0] if path_parts else ""
    if "youtube.com" in host:
        query = urllib.parse.parse_qs(parsed.query)
        if query.get("v"):
            return query["v"][0]
        if path_parts and path_parts[0] in {"shorts", "embed", "live"} and len(path_parts) > 1:
            return path_parts[1]
    return ""


def canonical_youtube_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}" if video_id else ""


def thumbnail_url(video_id: str) -> str:
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id else ""


def next_id(rows: list[dict], json_rows: list[dict]) -> str:
    max_num = 0
    for row in [*rows, *json_rows]:
        match = re.fullmatch(r"S(\d+)", str(row.get("id", "")).strip())
        if match:
            max_num = max(max_num, int(match.group(1)))
    return f"S{max_num + 1:04d}"


def prepare_rows(rows: list[dict], json_rows: list[dict], result: ValidationResult) -> list[dict]:
    prepared = []
    used_ids = {str(row.get("id", "")).strip() for row in rows if str(row.get("id", "")).strip()}

    for index, row in enumerate(rows, start=1):
        prepared_row = normalize_row(row)
        if not prepared_row["id"].strip():
            generated_id = next_id([*prepared, *rows], json_rows)
            while generated_id in used_ids:
                generated_id = f"S{int(generated_id[1:]) + 1:04d}"
            prepared_row["id"] = generated_id
            used_ids.add(generated_id)
            result.auto_normalizations.append(f"{index}행: 빈 id를 {generated_id}(으)로 자동 생성")

        original_video = prepared_row["videoUrl"].strip()
        video_id = extract_youtube_id(original_video)
        if original_video and video_id:
            canonical = canonical_youtube_url(video_id)
            thumb = thumbnail_url(video_id)
            if prepared_row["videoUrl"] != canonical:
                result.auto_normalizations.append(f"{prepared_row['id']}: videoUrl 정규화")
                prepared_row["videoUrl"] = canonical
            if prepared_row["thumbnailUrl"] != thumb:
                result.auto_normalizations.append(f"{prepared_row['id']}: thumbnailUrl 재생성")
                prepared_row["thumbnailUrl"] = thumb
        elif original_video:
            result.warnings.append(f"{prepared_row['id'] or index}행: YouTube video id를 추출할 수 없습니다.")

        try:
            prepared_row["singCount"] = parse_sing_count(prepared_row["singCount"])
        except ValueError:
            result.errors.append(f"{prepared_row['id'] or index}행: singCount를 숫자로 변환할 수 없습니다.")

        try:
            prepared_row["pick"] = parse_bool(prepared_row["pick"])
        except ValueError as error:
            result.errors.append(f"{prepared_row['id'] or index}행: {error}")

        prepared.append(prepared_row)
    return prepared


def validate_rows(rows: list[dict], json_rows: list[dict] | None = None) -> tuple[list[dict], ValidationResult]:
    json_rows = json_rows or []
    result = ValidationResult()
    prepared = prepare_rows(rows, json_rows, result)

    ids = [str(row.get("id", "")).strip() for row in prepared]
    for song_id in sorted({song_id for song_id in ids if ids.count(song_id) > 1}):
        result.errors.append(f"중복 id가 있습니다: {song_id}")

    json_by_id = {str(row.get("id", "")).strip(): row for row in json_rows if str(row.get("id", "")).strip()}
    existing_title_artist = {
        normalize_title_artist(row)
        for row in json_rows
        if str(row.get("id", "")).strip()
    }

    seen_csv_title_artist = {}
    for index, row in enumerate(prepared, start=1):
        label = row.get("id") or f"{index}행"
        if not str(row.get("title", "")).strip():
            result.errors.append(f"{label}: title이 비어 있습니다.")
        if not str(row.get("artist", "")).strip():
            result.errors.append(f"{label}: artist가 비어 있습니다.")
        if not str(row.get("language", "")).strip():
            result.errors.append(f"{label}: language가 비어 있습니다.")

        key = normalize_title_artist(row)
        is_new = str(row.get("id", "")).strip() not in json_by_id
        if key in seen_csv_title_artist:
            result.errors.append(f"{label}: CSV 안에 동일 title+artist가 있습니다.")
        seen_csv_title_artist[key] = label
        if is_new and key in existing_title_artist:
            result.errors.append(f"{label}: 기존 곡과 동일한 title+artist입니다.")

        for field_name, message in [
            ("videoUrl", "videoUrl 없음"),
            ("lyricsUrl", "lyricsUrl 없음"),
            ("songIntro", "songIntro 없음"),
            ("genre1", "genre1 없음"),
            ("tags", "tags 없음"),
            ("sourceNote", "sourceNote 없음"),
        ]:
            if not str(row.get(field_name, "")).strip():
                result.warnings.append(f"{label}: {message}")

        video_id = extract_youtube_id(str(row.get("videoUrl", "")))
        thumb_id = extract_youtube_id_from_thumbnail(str(row.get("thumbnailUrl", "")))
        if video_id and thumb_id and video_id != thumb_id:
            result.warnings.append(f"{label}: videoUrl과 thumbnailUrl의 YouTube ID가 다릅니다.")

    add_similarity_warnings(prepared, result)
    return prepared, result


def extract_youtube_id_from_thumbnail(url: str) -> str:
    match = re.search(r"/vi/([^/]+)/", str(url or ""))
    return match.group(1) if match else ""


def add_similarity_warnings(rows: list[dict], result: ValidationResult) -> None:
    for left_index, left in enumerate(rows):
        left_title = normalize_key(left.get("title"))
        if not left_title:
            continue
        left_tokens = " ".join(
            normalize_key(left.get(field_name))
            for field_name in ("translation", "tags")
            if left.get(field_name)
        )
        for right in rows[left_index + 1 :]:
            right_title = normalize_key(right.get("title"))
            if not right_title:
                continue
            ratio = difflib.SequenceMatcher(None, left_title, right_title).ratio()
            if ratio >= 0.88 and left.get("artist") != right.get("artist"):
                result.warnings.append(
                    f"유사 제목 후보: {left.get('id')} {left.get('title')} / {right.get('id')} {right.get('title')}"
                )
            right_tokens = " ".join(
                normalize_key(right.get(field_name))
                for field_name in ("translation", "tags")
                if right.get(field_name)
            )
            if left_title and right_tokens and left_title in right_tokens:
                result.warnings.append(f"translation/tags 유사 후보: {left.get('title')} ↔ {right.get('title')}")
            if right_title and left_tokens and right_title in left_tokens:
                result.warnings.append(f"translation/tags 유사 후보: {right.get('title')} ↔ {left.get('title')}")


def preview_changes() -> PreviewResult:
    rows = read_csv_master()
    json_rows = read_json()
    prepared_rows, validation = validate_rows(rows, json_rows)
    json_by_id = {str(row.get("id", "")).strip(): row for row in json_rows if str(row.get("id", "")).strip()}
    prepared_by_id = {str(row.get("id", "")).strip(): row for row in prepared_rows if str(row.get("id", "")).strip()}

    additions = [row for row in prepared_rows if row["id"] not in json_by_id]
    updates = []
    for row in prepared_rows:
        old = json_by_id.get(row["id"])
        if old and json_ready_row(old) != json_ready_row(row):
            updates.append({"before": old, "after": row, "diffs": row_diffs(old, row)})

    deletion_candidates = [row for row in json_rows if row.get("id") not in prepared_by_id]
    for row in deletion_candidates:
        validation.deletion_candidates.append(row)

    rows_for_json = [json_ready_row(row) for row in prepared_rows]
    for row in deletion_candidates:
        rows_for_json.append(json_ready_row(row))

    return PreviewResult(
        rows=rows,
        json_rows=json_rows,
        prepared_rows=prepared_rows,
        rows_for_json=rows_for_json,
        additions=additions,
        updates=updates,
        validation=validation,
    )


def json_ready_row(row: dict) -> dict:
    ready = {}
    for field_name in FIELDS:
        value = row.get(field_name, "")
        if field_name == "singCount":
            ready[field_name] = parse_sing_count(value)
        elif field_name == "pick":
            ready[field_name] = parse_bool(value)
        else:
            ready[field_name] = "" if value is None else str(value)
    return ready


def row_diffs(before: dict, after: dict) -> list[tuple[str, object, object]]:
    diffs = []
    before_ready = json_ready_row(before)
    after_ready = json_ready_row(after)
    for field_name in FIELDS:
        if before_ready.get(field_name) != after_ready.get(field_name):
            diffs.append((field_name, before_ready.get(field_name), after_ready.get(field_name)))
    return diffs


def apply_build() -> PreviewResult:
    preview = preview_changes()
    if not preview.validation.ok:
        return preview

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = now_stamp()
    if CSV_PATH.exists():
        shutil.copy2(CSV_PATH, BACKUP_DIR / f"songs_master_{stamp}.csv")
    if JSON_PATH.exists():
        shutil.copy2(JSON_PATH, BACKUP_DIR / f"songs_{stamp}.json")

    write_csv_master(preview.prepared_rows)
    write_json(preview.rows_for_json)
    return preview_changes()


def form_row_from_params(params: dict[str, list[str]]) -> dict:
    row = {}
    for field_name in FIELDS:
        values = params.get(field_name, [""])
        row[field_name] = values[0]
    return normalize_row(row)


def find_row(rows: list[dict], song_id: str, row_index: str) -> tuple[int | None, dict | None]:
    if song_id:
        for index, row in enumerate(rows):
            if row.get("id") == song_id:
                return index, row
    if row_index.isdigit():
        index = int(row_index)
        if 0 <= index < len(rows):
            return index, rows[index]
    return None, None


def songs_return_url(params: dict[str, list[str]]) -> str:
    kept = {}
    for key in ("q", "language", "genre"):
        value = params.get(key, [""])[0].strip()
        if value:
            kept[key] = value
    query = urllib.parse.urlencode(kept)
    return f"/songs?{query}" if query else "/songs"


def safe_return_url(value: str) -> str:
    if not value:
        return "/songs"
    parsed = urllib.parse.urlparse(value)
    if parsed.path != "/songs":
        return "/songs"
    return parsed.path + (f"?{parsed.query}" if parsed.query else "")


def with_notice(return_to: str, message: str = "", warning: str = "") -> str:
    parsed = urllib.parse.urlparse(safe_return_url(return_to))
    query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    if message:
        query["message"] = [message]
    if warning:
        query["warning"] = [warning]
    encoded = urllib.parse.urlencode(query, doseq=True)
    return parsed.path + (f"?{encoded}" if encoded else "")


def layout(title: str, body: str) -> bytes:
    page = f"""<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(title)} - Kura Songbook Admin</title>
    <link rel="stylesheet" href="/static/admin.css">
  </head>
  <body>
    <header class="topbar">
      <a class="brand" href="/">쿠라's 노래책 Admin</a>
      <nav>
        <a href="/">대시보드</a>
        <a href="/songs">곡 목록</a>
        <a href="/add">새 곡 추가</a>
        <a href="/preview">변경 미리보기</a>
        <a href="/validate">검증</a>
      </nav>
    </header>
    <main class="wrap">
      {body}
    </main>
  </body>
</html>"""
    return page.encode("utf-8")


def message_box(kind: str, messages: list[str]) -> str:
    if not messages:
        return ""
    items = "".join(f"<li>{esc(message)}</li>" for message in messages[:80])
    overflow = "" if len(messages) <= 80 else f"<li>...외 {len(messages) - 80}건</li>"
    return f'<section class="box {kind}"><ul>{items}{overflow}</ul></section>'


class AdminHandler(BaseHTTPRequestHandler):
    server_version = "KuraSongbookAdmin/0.1"

    def do_GET(self) -> None:
        try:
            self.route_get()
        except Exception as error:  # pragma: no cover - server fallback
            self.respond(500, layout("오류", f"<h1>오류</h1><pre>{esc(error)}</pre>"))

    def do_POST(self) -> None:
        try:
            self.route_post()
        except Exception as error:  # pragma: no cover - server fallback
            self.respond(500, layout("오류", f"<h1>오류</h1><pre>{esc(error)}</pre>"))

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[admin] {self.address_string()} - {fmt % args}")

    def route_get(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)
        if path == "/":
            return self.dashboard()
        if path == "/songs":
            return self.song_list(params)
        if path == "/edit":
            return self.edit_form(params)
        if path == "/add":
            return self.add_form()
        if path == "/preview":
            return self.preview_page()
        if path == "/apply":
            return self.apply_confirm()
        if path == "/validate":
            return self.validate_page()
        if path == "/count/decrement":
            return self.decrement_confirm(params)
        if path == "/static/admin.css":
            return self.static_file("admin.css", "text/css; charset=utf-8")
        self.respond(404, layout("찾을 수 없음", "<h1>404</h1><p>페이지를 찾을 수 없습니다.</p>"))

    def route_post(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        params = urllib.parse.parse_qs(raw, keep_blank_values=True)
        if parsed.path == "/edit":
            return self.save_edit(params)
        if parsed.path == "/add":
            return self.save_add(params)
        if parsed.path == "/apply":
            return self.apply_page(params)
        if parsed.path == "/count/increment":
            return self.increment_count(params)
        if parsed.path == "/count/decrement":
            return self.decrement_count(params)
        self.respond(404, layout("찾을 수 없음", "<h1>404</h1><p>POST 대상이 없습니다.</p>"))

    def respond(self, status: int, body: bytes, content_type: str = "text/html; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def static_file(self, file_name: str, content_type: str) -> None:
        path = STATIC_DIR / file_name
        if not path.exists():
            return self.respond(404, b"not found", "text/plain; charset=utf-8")
        self.respond(200, path.read_bytes(), content_type)

    def dashboard(self) -> None:
        rows = read_csv_master()
        json_rows = read_json()
        _, validation = validate_rows(rows, json_rows)
        modified = datetime.fromtimestamp(JSON_PATH.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        body = f"""
<section class="hero">
  <p class="eyebrow">Local only</p>
  <h1>로컬 관리자 GUI</h1>
  <p>CSV master를 편집하고 미리보기 후 public songs.json으로 빌드합니다. 자동 commit/push는 하지 않습니다.</p>
</section>
<section class="grid">
  <article class="card"><strong>{len(rows)}</strong><span>CSV 곡 수</span></article>
  <article class="card"><strong>{len(json_rows)}</strong><span>JSON 곡 수</span></article>
  <article class="card"><strong>{len(validation.warnings)}</strong><span>경고</span></article>
  <article class="card"><strong>{esc(modified)}</strong><span>songs.json 수정 시간</span></article>
</section>
<section class="actions">
  <a class="button" href="/songs">곡 목록 보기</a>
  <a class="button" href="/add">새 곡 추가</a>
  <a class="button" href="/preview">변경 미리보기</a>
  <a class="button" href="/validate">검증만 실행</a>
</section>
<section class="box warn">
  <p><strong>안전 안내:</strong> 이 도구는 로컬 전용입니다. 삭제, git commit, git push, 원격 배포를 하지 않습니다.</p>
  <p>부른 횟수는 곡 목록에서 +1/-1로 빠르게 수정할 수 있습니다. JSON 반영은 적용/빌드 후 이루어집니다.</p>
  <p>백업 폴더: <code>{esc(BACKUP_DIR.relative_to(ROOT_DIR))}</code></p>
</section>
"""
        self.respond(200, layout("대시보드", body))

    def song_list(self, params: dict[str, list[str]]) -> None:
        rows = read_csv_master()
        query = params.get("q", [""])[0].strip()
        language = params.get("language", [""])[0].strip()
        genre = params.get("genre", [""])[0].strip()
        message = params.get("message", [""])[0]
        warning = params.get("warning", [""])[0]
        return_to = songs_return_url(params)
        encoded_return = urllib.parse.quote(return_to, safe="")

        filtered = []
        for index, row in enumerate(rows):
            haystack = " ".join(str(row.get(field_name, "")) for field_name in FIELDS)
            if query and normalize_key(query) not in normalize_key(haystack):
                continue
            if language and row.get("language") != language:
                continue
            if genre and genre not in {row.get("genre1"), row.get("genre2"), row.get("genre")}:
                continue
            filtered.append((index, row))

        languages = sorted({row.get("language", "") for row in rows if row.get("language")})
        genres = sorted({value for row in rows for value in [row.get("genre1"), row.get("genre2")] if value})
        language_options = option_list(languages, language)
        genre_options = option_list(genres, genre)
        table_rows = "".join(
            f"""<tr>
  <td><a href="/edit?id={urllib.parse.quote(row.get('id', ''))}&row={index}">{esc(row.get('id') or '(new)')}</a></td>
  <td>{esc(row.get('title'))}</td>
  <td>{esc(row.get('translation'))}</td>
  <td>{esc(row.get('artist'))}</td>
  <td>{esc(row.get('language'))}</td>
  <td>{esc(row.get('singCount'))}회</td>
  <td class="count-actions">
    <form class="inline-form" method="post" action="/count/increment">
      <input type="hidden" name="id" value="{esc(row.get('id', ''))}">
      <input type="hidden" name="row" value="{esc(index)}">
      <input type="hidden" name="return_to" value="{esc(return_to)}">
      <button type="submit">+1</button>
    </form>
    <a class="button ghost" href="/count/decrement?id={urllib.parse.quote(row.get('id', ''))}&row={index}&return_to={encoded_return}">-1</a>
    <a class="button ghost" href="/edit?id={urllib.parse.quote(row.get('id', ''))}&row={index}">수정</a>
  </td>
</tr>"""
            for index, row in filtered
        )
        body = f"""
<h1>곡 목록</h1>
{message_box('ok', [message] if message else [])}
{message_box('warn', [warning] if warning else [])}
<form class="filter-bar" method="get" action="/songs">
  <input type="search" name="q" value="{esc(query)}" placeholder="제목, 가수, 태그 검색">
  <select name="language"><option value="">언어 전체</option>{language_options}</select>
  <select name="genre"><option value="">장르 전체</option>{genre_options}</select>
  <button type="submit">검색</button>
  <a class="button ghost" href="/songs">초기화</a>
</form>
<p class="muted">표시: {len(filtered)}곡 / 전체 {len(rows)}곡</p>
<div class="table-wrap">
  <table>
    <thead><tr><th>ID</th><th>제목</th><th>번역명</th><th>가수</th><th>언어</th><th>부른 횟수</th><th>빠른 수정</th></tr></thead>
    <tbody>{table_rows or '<tr><td colspan="7">조건에 맞는 곡이 없습니다.</td></tr>'}</tbody>
  </table>
</div>
"""
        self.respond(200, layout("곡 목록", body))

    def edit_form(self, params: dict[str, list[str]], errors: list[str] | None = None, row_override: dict | None = None) -> None:
        rows = read_csv_master()
        song_id = params.get("id", [""])[0]
        row_index = params.get("row", [""])[0]
        index, row = find_row(rows, song_id, row_index)
        if row_override is not None:
            row = row_override
        if row is None:
            return self.respond(404, layout("곡 없음", "<h1>곡을 찾을 수 없습니다.</h1>"))
        message = params.get("message", [""])[0]
        warning = params.get("warning", [""])[0]
        body = f"""
<h1>곡 수정</h1>
{message_box('error', errors or [])}
{message_box('ok', [message] if message else [])}
{message_box('warn', [warning] if warning else [])}
<form class="song-form" method="post" action="/edit">
  <input type="hidden" name="original_id" value="{esc(song_id)}">
  <input type="hidden" name="row_index" value="{esc(index if index is not None else row_index)}">
  {form_fields(row)}
  <div class="form-actions">
    <button name="action" value="save" type="submit">CSV에 저장</button>
    <button name="action" value="increment" type="submit">부른 횟수 +1</button>
    <button name="action" value="decrement" type="submit">부른 횟수 -1</button>
    <button name="action" value="normalize_youtube" type="submit">YouTube URL 정규화</button>
    <button name="action" value="regen_thumb" type="submit">thumbnailUrl 재생성</button>
    <a class="button ghost" href="/preview">저장 후 미리보기</a>
  </div>
</form>
"""
        self.respond(200, layout("곡 수정", body))

    def add_form(self, row: dict | None = None, errors: list[str] | None = None) -> None:
        row = row or normalize_row({"singCount": "0", "pick": "false"})
        body = f"""
<h1>새 곡 추가</h1>
<p class="muted">id는 비워둘 수 있습니다. 적용/빌드 시 다음 id가 자동 생성됩니다.</p>
{message_box('error', errors or [])}
<form class="song-form" method="post" action="/add">
  {form_fields(row)}
  <div class="form-actions">
    <button type="submit">CSV에 추가</button>
    <a class="button ghost" href="/songs">취소</a>
  </div>
</form>
"""
        self.respond(200, layout("새 곡 추가", body))

    def preview_page(self) -> None:
        preview = preview_changes()
        body = render_preview(preview, show_apply=True)
        self.respond(200, layout("변경 미리보기", body))

    def apply_confirm(self) -> None:
        preview = preview_changes()
        body = render_preview(preview, show_apply=False)
        if preview.validation.ok:
            body += """
<section class="box danger">
  <h2>적용 확인</h2>
  <p>백업을 만든 뒤 CSV를 정리하고 songs.json을 재생성합니다. git commit/push는 하지 않습니다.</p>
  <form method="post" action="/apply">
    <input type="hidden" name="confirm" value="yes">
    <button class="danger-button" type="submit">백업 후 적용/빌드</button>
    <a class="button ghost" href="/preview">미리보기만 보기</a>
  </form>
</section>
"""
        self.respond(200, layout("적용 확인", body))

    def validate_page(self) -> None:
        rows = read_csv_master()
        json_rows = read_json()
        _, validation = validate_rows(rows, json_rows)
        body = f"""
<h1>검증 결과</h1>
{message_box('error', validation.errors)}
{message_box('warn', validation.warnings)}
{message_box('ok', ['에러가 없습니다.'] if validation.ok else [])}
"""
        self.respond(200, layout("검증", body))

    def save_edit(self, params: dict[str, list[str]]) -> None:
        rows = read_csv_master()
        original_id = params.get("original_id", [""])[0]
        row_index = params.get("row_index", [""])[0]
        index, _ = find_row(rows, original_id, row_index)
        if index is None:
            return self.respond(404, layout("곡 없음", "<h1>곡을 찾을 수 없습니다.</h1>"))
        row = form_row_from_params(params)
        action = params.get("action", ["save"])[0]
        warning = apply_form_action(row, action)
        rows[index] = row
        write_csv_master(rows)
        redirect_to = f"/edit?id={urllib.parse.quote(row.get('id', ''))}&row={index}"
        if warning:
            redirect_to += f"&warning={urllib.parse.quote(warning)}"
        elif action in {"increment", "decrement"}:
            redirect_to += "&message=CSV%EC%97%90%20%EC%A0%80%EC%9E%A5%EB%90%98%EC%97%88%EC%8A%B5%EB%8B%88%EB%8B%A4.%20%EB%B0%B0%ED%8F%AC%20%EB%B0%98%EC%98%81%EC%9D%80%20%EB%B3%80%EA%B2%BD%20%EB%AF%B8%EB%A6%AC%EB%B3%B4%EA%B8%B0%20%E2%86%92%20%EC%A0%81%EC%9A%A9%2F%EB%B9%8C%EB%93%9C%EC%97%90%EC%84%9C%20%EC%A7%84%ED%96%89%ED%95%98%EC%84%B8%EC%9A%94."
        self.redirect(redirect_to)

    def save_add(self, params: dict[str, list[str]]) -> None:
        row = form_row_from_params(params)
        if not row["singCount"].strip():
            row["singCount"] = "0"
        if not row["pick"].strip():
            row["pick"] = "false"
        errors = []
        for field_name in ("title", "artist", "language"):
            if not row[field_name].strip():
                errors.append(f"{field_name} 필드는 필수입니다.")
        if errors:
            return self.add_form(row, errors)
        rows = read_csv_master()
        rows.append(row)
        write_csv_master(rows)
        self.redirect("/songs")

    def apply_page(self, params: dict[str, list[str]]) -> None:
        if params.get("confirm", [""])[0] != "yes":
            return self.respond(400, layout("확인 필요", "<h1>확인 값이 없습니다.</h1>"))
        preview = apply_build()
        body = "<h1>적용/빌드 결과</h1>"
        if preview.validation.ok:
            body += message_box("ok", ["백업 생성 및 songs.json 빌드가 완료되었습니다."])
        body += render_preview(preview, show_apply=False)
        self.respond(200, layout("적용 결과", body))

    def increment_count(self, params: dict[str, list[str]]) -> None:
        return_to = safe_return_url(params.get("return_to", ["/songs"])[0])
        rows = read_csv_master()
        index, row = find_row(rows, params.get("id", [""])[0], params.get("row", [""])[0])
        if index is None or row is None:
            return self.redirect(with_notice(return_to, warning="곡을 찾을 수 없습니다."))
        try:
            row["singCount"] = str(parse_sing_count(row.get("singCount", "")) + 1)
        except ValueError:
            return self.redirect(with_notice(return_to, warning="singCount를 숫자로 변환할 수 없습니다."))
        rows[index] = row
        write_csv_master(rows)
        self.redirect(with_notice(return_to, message="CSV에 저장되었습니다. 배포 반영은 변경 미리보기 → 적용/빌드에서 진행하세요."))

    def decrement_confirm(self, params: dict[str, list[str]]) -> None:
        rows = read_csv_master()
        return_to = safe_return_url(params.get("return_to", ["/songs"])[0])
        index, row = find_row(rows, params.get("id", [""])[0], params.get("row", [""])[0])
        if index is None or row is None:
            return self.redirect(with_notice(return_to, warning="곡을 찾을 수 없습니다."))
        try:
            current = parse_sing_count(row.get("singCount", ""))
        except ValueError:
            return self.redirect(with_notice(return_to, warning="singCount를 숫자로 변환할 수 없습니다."))
        new_count = max(0, current - 1)
        warning = message_box("warn", ["이미 0회라 더 줄일 수 없습니다."] if current <= 0 else [])
        apply_button = "" if current <= 0 else '<button class="danger-button" type="submit">-1 적용</button>'
        body = f"""
<h1>부른 횟수 -1 확인</h1>
{warning}
<section class="box">
  <p>정말 이 곡의 부른 횟수를 1 줄일까요?</p>
  <dl class="confirm-list">
    <dt>ID</dt><dd>{esc(row.get('id'))}</dd>
    <dt>제목</dt><dd>{esc(row.get('title'))}</dd>
    <dt>가수</dt><dd>{esc(row.get('artist'))}</dd>
    <dt>현재 횟수</dt><dd>{current}회</dd>
    <dt>변경 후</dt><dd>{new_count}회</dd>
  </dl>
  <form method="post" action="/count/decrement" class="actions">
    <input type="hidden" name="id" value="{esc(row.get('id', ''))}">
    <input type="hidden" name="row" value="{esc(index)}">
    <input type="hidden" name="return_to" value="{esc(return_to)}">
    {apply_button}
    <a class="button ghost" href="{esc(return_to)}">취소</a>
  </form>
</section>
"""
        self.respond(200, layout("부른 횟수 -1 확인", body))

    def decrement_count(self, params: dict[str, list[str]]) -> None:
        return_to = safe_return_url(params.get("return_to", ["/songs"])[0])
        rows = read_csv_master()
        index, row = find_row(rows, params.get("id", [""])[0], params.get("row", [""])[0])
        if index is None or row is None:
            return self.redirect(with_notice(return_to, warning="곡을 찾을 수 없습니다."))
        try:
            current = parse_sing_count(row.get("singCount", ""))
        except ValueError:
            return self.redirect(with_notice(return_to, warning="singCount를 숫자로 변환할 수 없습니다."))
        if current <= 0:
            row["singCount"] = "0"
            rows[index] = row
            write_csv_master(rows)
            return self.redirect(with_notice(return_to, warning="이미 0회라 더 줄일 수 없습니다."))
        row["singCount"] = str(current - 1)
        rows[index] = row
        write_csv_master(rows)
        self.redirect(with_notice(return_to, message="CSV에 저장되었습니다. 배포 반영은 변경 미리보기 → 적용/빌드에서 진행하세요."))


def option_list(values: list[str], selected: str) -> str:
    return "".join(
        f'<option value="{esc(value)}"{" selected" if value == selected else ""}>{esc(value)}</option>'
        for value in values
    )


def apply_form_action(row: dict, action: str) -> str:
    if action == "increment":
        try:
            row["singCount"] = str(parse_sing_count(row.get("singCount", "")) + 1)
        except ValueError:
            row["singCount"] = "1"
    if action == "decrement":
        try:
            current = parse_sing_count(row.get("singCount", ""))
        except ValueError:
            row["singCount"] = "0"
            return "singCount를 숫자로 변환할 수 없어 0회로 두었습니다."
        if current <= 0:
            row["singCount"] = "0"
            return "이미 0회라 더 줄일 수 없습니다."
        row["singCount"] = str(current - 1)
    if action in {"normalize_youtube", "regen_thumb"}:
        video_id = extract_youtube_id(row.get("videoUrl", ""))
        if video_id and action == "normalize_youtube":
            row["videoUrl"] = canonical_youtube_url(video_id)
        if video_id:
            row["thumbnailUrl"] = thumbnail_url(video_id)
    return ""


def form_fields(row: dict) -> str:
    blocks = []
    for field_name in FIELDS:
        value = row.get(field_name, "")
        label = FIELD_LABELS.get(field_name, field_name)
        if field_name in TEXTAREA_FIELDS:
            control = f'<textarea name="{field_name}" rows="3">{esc(value)}</textarea>'
        elif field_name == "pick":
            text_value = str(value).lower()
            control = f"""<select name="pick">
  <option value="false"{' selected' if text_value in {'', 'false', '0', 'no', 'n'} else ''}>false</option>
  <option value="true"{' selected' if text_value in {'true', '1', 'yes', 'y', '예', '체크'} else ''}>true</option>
</select>"""
        else:
            control = f'<input name="{field_name}" value="{esc(value)}">'
        blocks.append(f'<label><span>{esc(label)}</span>{control}</label>')
    return "\n".join(blocks)


FIELD_LABELS = {
    "id": "ID",
    "title": "제목",
    "translation": "번역명",
    "artist": "가수",
    "artistKr": "가수 한국명",
    "language": "언어",
    "genre": "장르 표시",
    "genre1": "대표 장르",
    "genre2": "보조 장르",
    "theme": "테마",
    "situation": "상황",
    "target": "대상",
    "emotion": "분위기",
    "sourceNote": "출처/비고",
    "media": "미디어",
    "sourceType": "출처 유형",
    "workTitle": "작품명",
    "tags": "검색 태그",
    "videoUrl": "영상 URL",
    "lyricsUrl": "가사 URL",
    "singCount": "부른 횟수",
    "pick": "Pick",
    "thumbnailUrl": "썸네일 URL",
    "songIntro": "곡 소개",
}


def render_preview(preview: PreviewResult, show_apply: bool) -> str:
    additions = "".join(f"<li>{esc(row['id'])} {esc(row['title'])} / {esc(row['artist'])}</li>" for row in preview.additions)
    updates = "".join(render_update(update) for update in preview.updates)
    deletions = "".join(
        f"<li>{esc(row.get('id'))} {esc(row.get('title'))} / {esc(row.get('artist'))}</li>"
        for row in preview.validation.deletion_candidates
    )
    body = f"""
<h1>변경 미리보기</h1>
<section class="box warn">
  <p><strong>주의:</strong> 첫 적용 시 기존 YouTube URL과 썸네일이 정규화되어 많은 행이 수정될 수 있습니다.</p>
  <p>검토만 하려면 이 페이지에서 멈추세요. 실제 파일 반영은 아래 적용/빌드 확인 화면에서 한 번 더 확인한 뒤 진행됩니다.</p>
</section>
{message_box('error', preview.validation.errors)}
{message_box('warn', preview.validation.warnings)}
{message_box('info', preview.validation.auto_normalizations)}
<section class="box">
  <h2>추가 예정 ({len(preview.additions)})</h2>
  <ul>{additions or '<li>없음</li>'}</ul>
</section>
<section class="box">
  <h2>수정 예정 ({len(preview.updates)})</h2>
  <ul>{updates or '<li>없음</li>'}</ul>
</section>
<section class="box warn">
  <h2>삭제 후보 ({len(preview.validation.deletion_candidates)})</h2>
  <p>v0.1에서는 삭제를 자동 반영하지 않습니다. CSV에서 사라진 곡도 songs.json에는 유지됩니다.</p>
  <ul>{deletions or '<li>없음</li>'}</ul>
</section>
"""
    if show_apply:
        if preview.validation.ok:
            body += """
<p class="actions">
  <a class="button ghost" href="/preview">미리보기만 보기</a>
  <a class="button danger-link" href="/apply">적용/빌드 확인으로 이동</a>
</p>
"""
        else:
            body += '<p class="muted">에러가 있어 적용할 수 없습니다.</p>'
    return body


def render_update(update: dict) -> str:
    diffs = "".join(
        f"<li><code>{esc(field_name)}</code>: {esc(before)} → {esc(after)}</li>"
        for field_name, before, after in update["diffs"]
    )
    row = update["after"]
    return f"<li><strong>{esc(row.get('id'))} {esc(row.get('title'))}</strong><ul>{diffs}</ul></li>"


def run_server(no_browser: bool) -> None:
    created = ensure_master_csv()
    if created:
        print(f"created {CSV_PATH}")

    server = ThreadingHTTPServer((HOST, PORT), AdminHandler)
    url = f"http://{HOST}:{PORT}"
    print(f"Kura Songbook local admin: {url}")
    print("Press Ctrl+C to stop.")
    if not no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping admin server.")
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Kura Songbook local admin GUI")
    parser.add_argument("--no-browser", action="store_true", help="do not open browser automatically")
    args = parser.parse_args()
    run_server(no_browser=args.no_browser)


if __name__ == "__main__":
    main()
