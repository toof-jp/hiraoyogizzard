#!/usr/bin/env python3
"""Upload TEI XML documents as JSON payloads using the upload_json_document.sh format."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shlex
import subprocess
import sys
import typing as t
import xml.etree.ElementTree as ET
from urllib.error import HTTPError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

TEI_NAMESPACE = "http://www.tei-c.org/ns/1.0"
NS = {"tei": TEI_NAMESPACE}
BASE_URL = "https://discoveryengine.googleapis.com/v1beta"


class UploadFailure(RuntimeError):
    """Raised when the Vertex AI Search API returns an unexpected response."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--download-dir",
        type=pathlib.Path,
        default=pathlib.Path("download"),
        help="Directory containing TEI XML files (default: download)",
    )
    parser.add_argument(
        "--url-list",
        type=pathlib.Path,
        default=pathlib.Path("urls.list"),
        help="Text file with one XML source URL per line (default: urls.list)",
    )
    parser.add_argument(
        "--project",
        default="hiraoyogizzard",
        help="Google Cloud project ID (default: hiraoyogizzard)",
    )
    parser.add_argument(
        "--location",
        default="global",
        help="Vertex AI Search location (default: global)",
    )
    parser.add_argument(
        "--collection",
        default="default_collection",
        help="Vertex AI Search collection ID (default: default_collection)",
    )
    parser.add_argument(
        "--data-store",
        default="mystore",
        help="Vertex AI Search data store ID (default: mystore)",
    )
    parser.add_argument(
        "--branch",
        default="0",
        help="Vertex AI Search branch ID (default: 0)",
    )
    parser.add_argument(
        "--access-token-command",
        default="gcloud auth print-access-token",
        help=(
            "Command executed to obtain an access token (default: 'gcloud auth print-access-token')"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse XML and display payloads without calling the API",
    )
    return parser.parse_args(argv)


def ensure_url_list(path: pathlib.Path) -> pathlib.Path:
    if path.exists():
        return path
    alternatives = (path.with_name("url.list"),)
    for candidate in alternatives:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"URL list file not found: {path}")


def iter_urls(source: pathlib.Path) -> t.Iterable[str]:
    text = source.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            yield stripped


def build_url_map(source: pathlib.Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for url in iter_urls(source):
        parsed = urlparse(url)
        name = pathlib.PurePosixPath(parsed.path).name
        if not name:
            continue
        mapping[name] = url
    return mapping


def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_title(root: ET.Element) -> str | None:
    title = root.findtext(".//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title", namespaces=NS)
    if title:
        return collapse_whitespace(title)
    return None


def gather_body_text(body: ET.Element) -> str:
    parts: list[str] = []
    for paragraph in body.findall(".//tei:p", namespaces=NS):
        text = collapse_whitespace(" ".join(segment for segment in paragraph.itertext()))
        if text:
            parts.append(text)
    if not parts:
        lines: list[str] = []
        for line in body.findall(".//tei:l", namespaces=NS):
            text = collapse_whitespace(" ".join(segment for segment in line.itertext()))
            if text:
                lines.append(text)
        if lines:
            parts.append("\n".join(lines))
    if not parts:
        raw = collapse_whitespace(" ".join(segment for segment in body.itertext()))
        if raw:
            parts.append(raw)
    if not parts:
        raise ValueError("TEI body contained no textual content")
    return "\n\n".join(parts)


def extract_body(xml_path: pathlib.Path) -> tuple[str | None, str]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    body = root.find(".//tei:text/tei:body", namespaces=NS)
    if body is None:
        body = root.find(".//tei:body", namespaces=NS)
    if body is None:
        raise ValueError("TEI body element not found")
    title = extract_title(root)
    content = gather_body_text(body)
    return title, content


def fetch_access_token(command: str) -> str:
    parts = shlex.split(command)
    if not parts:
        raise RuntimeError("Access token command is empty")
    completed = subprocess.run(
        parts,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(
            f"Access token command failed with code {completed.returncode}: {stderr}"
        )
    token = completed.stdout.strip()
    if not token:
        raise RuntimeError("Access token command returned empty output")
    return token


def sanitize_document_id(path: pathlib.Path, root: pathlib.Path) -> str:
    relative = path.relative_to(root).as_posix()
    candidate = re.sub(r"[^A-Za-z0-9_-]+", "-", relative).strip("-")
    if not candidate:
        digest = hashlib.sha256(relative.encode("utf-8")).hexdigest()
        candidate = digest[:32]
    if len(candidate) > 100:
        digest = hashlib.sha256(relative.encode("utf-8")).hexdigest()[:16]
        candidate = f"{candidate[:84]}-{digest}"
    return candidate.lower()


def format_segment_document_id(base_id: str, index: int) -> str:
    suffix = f"-{index:03d}"
    if len(base_id) + len(suffix) > 100:
        base_id = base_id[: 100 - len(suffix)]
        base_id = base_id.rstrip("-") or "doc"
    return f"{base_id}{suffix}"


def split_content_segments(content: str) -> list[str]:
    segments = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped:
            segments.append(stripped)
    return segments


def build_json_payload(*, content: str, url: str, title: str | None) -> dict[str, str]:
    body: dict[str, str] = {"content": content, "uri": url}
    if title:
        body["title"] = title
    return {"jsonData": json.dumps(body, ensure_ascii=False)}


def post_document(
    *,
    token: str,
    parent_path: str,
    document_id: str,
    payload: dict[str, str],
) -> None:
    documents_url = f"{BASE_URL}/{parent_path}/documents"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
    }
    create_url = f"{documents_url}?documentId={quote(document_id, safe='')}"
    request = Request(create_url, data=data, headers=headers)
    try:
        with urlopen(request) as response:
            status = response.getcode()
            if status >= 300:
                body = response.read().decode("utf-8", errors="replace")
                raise UploadFailure(f"Create failed ({status}): {body}")
    except HTTPError as exc:
        if exc.code != 409:
            body = exc.read().decode("utf-8", errors="replace")
            raise UploadFailure(f"Create failed ({exc.code}): {body}") from exc
        document_name = f"{documents_url}/{quote(document_id, safe='')}"
        update_url = f"{document_name}?updateMask=jsonData"
        patch_request = Request(update_url, data=data, headers=headers, method="PATCH")
        with urlopen(patch_request) as response:
            status = response.getcode()
            if status >= 300:
                body = response.read().decode("utf-8", errors="replace")
                raise UploadFailure(f"Update failed ({status}): {body}")


def iter_xml_files(directory: pathlib.Path) -> t.Iterable[pathlib.Path]:
    yield from sorted(path for path in directory.iterdir() if path.suffix.lower() == ".xml")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    download_dir: pathlib.Path = args.download_dir
    if not download_dir.exists() or not download_dir.is_dir():
        print(f"Download directory not found: {download_dir}", file=sys.stderr)
        return 1

    url_list_path = ensure_url_list(args.url_list)
    url_map = build_url_map(url_list_path)

    documents = list(iter_xml_files(download_dir))
    if not documents:
        print(f"No XML files found in {download_dir}", file=sys.stderr)
        return 1

    parent_path = (
        f"projects/{args.project}/locations/{args.location}/collections/{args.collection}/"
        f"dataStores/{args.data_store}/branches/{args.branch}"
    )

    if args.dry_run:
        token = None  # type: ignore[assignment]
    else:
        try:
            token = fetch_access_token(args.access_token_command)
        except RuntimeError as exc:
            print(f"Failed to obtain access token: {exc}", file=sys.stderr)
            return 1

    failures = 0
    successes = 0
    for xml_path in documents:
        try:
            title, content = extract_body(xml_path)
        except Exception as exc:  # noqa: BLE001
            print(f"[skip] {xml_path}: failed to extract body ({exc})", file=sys.stderr)
            failures += 1
            continue
        url = url_map.get(xml_path.name)
        if url is None:
            print(f"[skip] {xml_path}: source URL not found in {url_list_path.name}", file=sys.stderr)
            failures += 1
            continue
        segments = split_content_segments(content)
        if not segments:
            print(f"[skip] {xml_path}: no content segments after splitting", file=sys.stderr)
            failures += 1
            continue
        base_document_id = sanitize_document_id(xml_path, download_dir)
        for index, segment in enumerate(segments, start=1):
            segment_id = format_segment_document_id(base_document_id, index)
            payload = build_json_payload(content=segment, url=url, title=title)
            if args.dry_run:
                print(
                    f"[dry-run] {xml_path.name} -> {segment_id}\n"
                    f"{json.dumps(payload, ensure_ascii=False)}"
                )
                continue
            try:
                post_document(
                    token=token,
                    parent_path=parent_path,
                    document_id=segment_id,
                    payload=payload,
                )
            except UploadFailure as exc:
                print(f"[error] {xml_path}:{segment_id} {exc}", file=sys.stderr)
                failures += 1
            else:
                successes += 1
                print(f"uploaded {xml_path.name} segment {index} as {segment_id}")

    if failures:
        print(f"Completed with {successes} successes and {failures} failures.", file=sys.stderr)
        return 1
    if args.dry_run:
        print("Dry run complete.")
        return 0
    print(f"All {successes} segments uploaded successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
