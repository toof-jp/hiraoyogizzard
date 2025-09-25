#!/usr/bin/env python3
"""Download TEI XML files from URL list and optionally upload their text to Vertex AI Search."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import shlex
import subprocess
import sys
import typing as t
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

CHUNK_SIZE = 8192
TEI_NAMESPACE = "http://www.tei-c.org/ns/1.0"
NS = {"tei": TEI_NAMESPACE}
BASE_URL = "https://discoveryengine.googleapis.com/v1"
DEFAULT_COLLECTION = "default_collection"
DEFAULT_BRANCH = "default_branch"


@dataclass
class DownloadResult:
    url: str
    path: pathlib.Path


@dataclass
class SimpleResponse:
    status_code: int
    text: str


@dataclass
class GcloudSession:
    access_token: str

    def post(self, url: str, *, json: dict[str, t.Any] | None = None) -> SimpleResponse:
        return self._request("POST", url, payload=json)

    def patch(self, url: str, *, json: dict[str, t.Any] | None = None) -> SimpleResponse:
        return self._request("PATCH", url, payload=json)

    def _request(self, method: str, url: str, *, payload: dict[str, t.Any] | None) -> SimpleResponse:
        data = json_dumps(payload)
        request = Request(url, data=data, method=method)
        request.add_header("Authorization", f"Bearer {self.access_token}")
        request.add_header("Accept", "application/json")
        if data is not None:
            request.add_header("Content-Type", "application/json; charset=utf-8")
        try:
            with urlopen(request) as response:
                body = response.read().decode("utf-8")
                status = response.getcode()
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            return SimpleResponse(status_code=exc.code, text=body)
        return SimpleResponse(status_code=status, text=body)


def json_dumps(payload: dict[str, t.Any] | None) -> bytes | None:
    if payload is None:
        return None
    return json.dumps(payload).encode("utf-8")


def fetch_access_token(command: str) -> str:
    parts = shlex.split(command)
    if not parts:
        raise RuntimeError("gcloud access-token command is empty")
    try:
        completed = subprocess.run(
            parts,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"Failed to execute '{parts[0]}': {exc}") from exc
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(
            f"Access token command failed with exit code {completed.returncode}: {stderr}"
        )
    token = completed.stdout.strip()
    if not token:
        raise RuntimeError("Access token command returned empty output")
    return token


def build_gcloud_session(command: str) -> GcloudSession:
    token = fetch_access_token(command)
    return GcloudSession(access_token=token)


def iter_urls(source: pathlib.Path) -> t.Iterable[str]:
    for line in source.read_text(encoding="utf-8").splitlines():
        url = line.strip()
        if url and not url.startswith("#"):
            yield url


def pick_filename(url: str) -> str:
    parsed = urlparse(url)
    candidate = pathlib.PurePosixPath(parsed.path).name
    if not candidate:
        candidate = f"download-{hashlib.sha256(url.encode()).hexdigest()[:8]}"
    return candidate


def ensure_unique(path: pathlib.Path) -> pathlib.Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def download(url: str, dest_dir: pathlib.Path) -> pathlib.Path:
    name = pick_filename(url)
    target = ensure_unique(dest_dir / name)
    with urlopen(url) as response, target.open("wb") as fh:
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                break
            fh.write(chunk)
    return target


def download_all(url_file: pathlib.Path, output_dir: pathlib.Path) -> tuple[list[DownloadResult], list[str]]:
    downloads: list[DownloadResult] = []
    failures: list[str] = []
    for url in iter_urls(url_file):
        try:
            saved = download(url, output_dir)
            downloads.append(DownloadResult(url=url, path=saved))
            print(f"saved {url} -> {saved}")
        except (HTTPError, URLError) as exc:
            failures.append(f"{url}: {exc}")
            print(f"failed {url}: {exc}", file=sys.stderr)
    return downloads, failures


def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_title(root: ET.Element) -> str | None:
    title = root.findtext(".//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title", namespaces=NS)
    return collapse_whitespace(title) if title else None


def gather_paragraphs(body: ET.Element) -> list[str]:
    paragraphs: list[str] = []
    for paragraph in body.findall(".//tei:p", namespaces=NS):
        text = collapse_whitespace(" ".join(part for part in paragraph.itertext()))
        if text:
            paragraphs.append(text)
    if not paragraphs:
        lines: list[str] = []
        for line in body.findall(".//tei:l", namespaces=NS):
            text = collapse_whitespace(" ".join(part for part in line.itertext()))
            if text:
                lines.append(text)
        if lines:
            paragraphs.append("\n".join(lines))
    if not paragraphs:
        text = collapse_whitespace(" ".join(part for part in body.itertext()))
        if text:
            paragraphs.append(text)
    return paragraphs


def extract_body_text(xml_path: pathlib.Path) -> tuple[str | None, str]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    body = root.find(".//tei:text/tei:body", namespaces=NS)
    if body is None:
        body = root.find(".//tei:body", namespaces=NS)
    if body is None:
        raise ValueError("TEI body element not found")
    paragraphs = gather_paragraphs(body)
    if not paragraphs:
        raise ValueError("No textual content found in TEI body")
    title = extract_title(root)
    if title:
        content = title + "\n\n" + "\n\n".join(paragraphs)
    else:
        content = "\n\n".join(paragraphs)
    return title, content


def sanitize_document_id(path: pathlib.Path, root: pathlib.Path) -> str:
    relative = path.relative_to(root).as_posix()
    candidate = re.sub(r"[^A-Za-z0-9_-]+", "-", relative).strip("-")
    if not candidate:
        candidate = hashlib.sha256(relative.encode("utf-8")).hexdigest()[:32]
    if len(candidate) > 100:
        digest = hashlib.sha256(relative.encode("utf-8")).hexdigest()[:16]
        candidate = f"{candidate[:84]}-{digest}"
    return candidate.lower()


def build_document_payload(
    *,
    file_path: pathlib.Path,
    root: pathlib.Path,
    title: str | None,
    content: str,
    source_url: str | None,
    content_type: str,
) -> dict[str, t.Any]:
    stats = file_path.stat()
    metadata: dict[str, t.Any] = {
        "relative_path": file_path.relative_to(root).as_posix(),
        "size_bytes": stats.st_size,
        "modified_at": dt.datetime.utcfromtimestamp(stats.st_mtime).isoformat() + "Z",
        "content_type": "tei+xml",
    }
    if title:
        metadata["title"] = title
    if source_url:
        metadata["source_url"] = source_url
    return {
        "structData": metadata,
        "content": {
            "mimeType": content_type,
            "rawText": content,
        },
    }


def post_document(
    session: GcloudSession,
    *,
    parent_path: str,
    document_id: str,
    payload: dict[str, t.Any],
) -> None:
    documents_url = f"{BASE_URL}/{parent_path}/documents"
    create_url = f"{documents_url}?documentId={quote(document_id, safe='')}"
    response = session.post(create_url, json=payload)
    if response.status_code == 409:
        document_name = f"{documents_url}/{quote(document_id, safe='')}"
        update_mask = "content.mimeType,content.rawText,structData"
        update_url = f"{document_name}?updateMask={quote(update_mask, safe=',.')}"
        update_response = session.patch(update_url, json=payload)
        if update_response.status_code >= 300:
            raise RuntimeError(
                f"Update failed ({update_response.status_code}): {update_response.text.strip()}"
            )
    elif response.status_code >= 300:
        raise RuntimeError(f"Create failed ({response.status_code}): {response.text.strip()}")


def upload_documents(
    *,
    session: GcloudSession,
    output_dir: pathlib.Path,
    documents: list[DownloadResult],
    parent_path: str,
    content_type: str,
) -> tuple[int, list[str]]:
    successes = 0
    failures: list[str] = []
    for item in documents:
        file_path = item.path
        if file_path.suffix.lower() != ".xml":
            continue  # Skip non-XML files by default
        try:
            title, content = extract_body_text(file_path)
        except Exception as exc:  # noqa: BLE001 - capture parsing errors for reporting
            failures.append(f"{file_path}: {exc}")
            continue
        payload = build_document_payload(
            file_path=file_path,
            root=output_dir,
            title=title,
            content=content,
            source_url=item.url,
            content_type=content_type,
        )
        document_id = sanitize_document_id(file_path, output_dir)
        try:
            post_document(session, parent_path=parent_path, document_id=document_id, payload=payload)
        except Exception as exc:  # noqa: BLE001 - report API failures without aborting
            failures.append(f"{file_path}: {exc}")
        else:
            successes += 1
            print(f"uploaded {file_path} as {document_id}")
    return successes, failures


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url_file", type=pathlib.Path, help="Text file containing one URL per line")
    parser.add_argument("output_dir", type=pathlib.Path, help="Directory to save downloaded files")
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload downloaded XML content to Vertex AI Search",
    )
    parser.add_argument("--project", help="Google Cloud project ID (required with --upload)")
    parser.add_argument("--data-store", help="Vertex AI Search data store ID (required with --upload)")
    parser.add_argument("--location", default="global", help="Vertex AI Search location (default: global)")
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION,
        help="Vertex AI Search collection ID (default: default_collection)",
    )
    parser.add_argument(
        "--branch",
        default=DEFAULT_BRANCH,
        help="Vertex AI Search branch ID (default: default_branch)",
    )
    parser.add_argument(
        "--access-token-command",
        default="gcloud auth print-access-token",
        help=(
            "Command executed to obtain an access token when uploading "
            "(default: 'gcloud auth print-access-token')"
        ),
    )
    parser.add_argument(
        "--content-type",
        default="text/plain",
        help="Content type stored in Vertex AI Search documents (default: text/plain)",
    )
    args = parser.parse_args(argv)

    if args.upload:
        missing = [name for name in ("project", "data_store") if getattr(args, name) is None]
        if missing:
            parser.error(f"Missing required arguments for --upload: {', '.join(missing)}")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.url_file.exists():
        print(f"URL list file not found: {args.url_file}", file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)

    downloads, download_failures = download_all(args.url_file, args.output_dir)

    exit_code = 0
    if download_failures:
        print("\nSome downloads failed:", file=sys.stderr)
        for item in download_failures:
            print(f"  {item}", file=sys.stderr)
        exit_code = 1

    if args.upload and downloads:
        try:
            session = build_gcloud_session(args.access_token_command)
        except RuntimeError as exc:
            print(f"Failed to obtain access token: {exc}", file=sys.stderr)
            return 1
        parent_path = (
            f"projects/{args.project}/locations/{args.location}/collections/{args.collection}/"
            f"dataStores/{args.data_store}/branches/{args.branch}"
        )
        successes, failures = upload_documents(
            session=session,
            output_dir=args.output_dir,
            documents=downloads,
            parent_path=parent_path,
            content_type=args.content_type,
        )
        if failures:
            print("\nSome uploads failed:", file=sys.stderr)
            for item in failures:
                print(f"  {item}", file=sys.stderr)
            print(f"Completed with {successes} successes and {len(failures)} failures.")
            exit_code = 1
        else:
            print(f"All {successes} files uploaded successfully.")
    elif args.upload:
        print("No files were downloaded successfully; skipping upload.")
        exit_code = max(exit_code, 1)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
