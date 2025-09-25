#!/usr/bin/env python3
"""Upload files in a directory to a Vertex AI Search data store via the REST API."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
from typing import Iterable, Sequence
from urllib.parse import quote

try:
    import google.auth
    from google.auth.transport.requests import AuthorizedSession
    from google.oauth2 import service_account
except ImportError as exc:  # pragma: no cover - makes failure mode explicit for users
    raise SystemExit(
        "This script requires the google-auth package. Install it with 'pip install google-auth'."
    ) from exc

SCOPES: Sequence[str] = ("https://www.googleapis.com/auth/cloud-platform",)
BASE_URL = "https://discoveryengine.googleapis.com/v1"
DEFAULT_COLLECTION = "default_collection"
DEFAULT_BRANCH = "default_branch"


def iter_files(root: pathlib.Path, recursive: bool) -> Iterable[pathlib.Path]:
    if recursive:
        yield from (path for path in root.rglob("*") if path.is_file())
    else:
        yield from (path for path in root.iterdir() if path.is_file())


def build_session(service_account_file: pathlib.Path | None) -> AuthorizedSession:
    if service_account_file is not None:
        credentials = service_account.Credentials.from_service_account_file(
            str(service_account_file), scopes=SCOPES
        )
    else:
        credentials, _ = google.auth.default(scopes=SCOPES)
    return AuthorizedSession(credentials)


def sanitize_document_id(path: pathlib.Path, root: pathlib.Path) -> str:
    relative = path.relative_to(root).as_posix()
    candidate = re.sub(r"[^A-Za-z0-9_-]+", "-", relative).strip("-")
    if not candidate:
        candidate = hashlib.sha256(relative.encode("utf-8")).hexdigest()[:32]
    if len(candidate) > 100:
        digest = hashlib.sha256(relative.encode("utf-8")).hexdigest()[:16]
        candidate = f"{candidate[:84]}-{digest}"
    return candidate.lower()


def read_text(path: pathlib.Path, encoding: str, errors: str) -> str:
    return path.read_text(encoding=encoding, errors=errors)


def build_document_payload(
    file_path: pathlib.Path,
    root: pathlib.Path,
    content: str,
    content_type: str,
    source_uri: str | None,
) -> dict[str, object]:
    relative = file_path.relative_to(root).as_posix()
    stats = file_path.stat()
    metadata = {
        "relative_path": relative,
        "size_bytes": stats.st_size,
        "modified_at": dt.datetime.utcfromtimestamp(stats.st_mtime).isoformat() + "Z",
    }
    if source_uri:
        metadata["source_uri"] = source_uri

    json_data = {
        "content": content,
        "mimeType": content_type,
    }

    return {
        "structData": metadata,
        "jsonData": json.dumps(json_data),
    }


def post_document(
    session: AuthorizedSession,
    parent_path: str,
    document_id: str,
    payload: dict[str, object],
) -> None:
    documents_url = f"{BASE_URL}/{parent_path}/documents"
    response = session.post(f"{documents_url}?documentId={quote(document_id, safe='')}", json=payload)
    if response.status_code == 409:
        # Document already exists: update it.
        document_name = f"{documents_url}/{quote(document_id, safe='')}"
        params = {"updateMask": "jsonData,structData"}
        update_response = session.patch(document_name, params=params, json=payload)
        if update_response.status_code >= 300:
            raise RuntimeError(
                f"Update failed ({update_response.status_code}): {update_response.text.strip()}"
            )
    elif response.status_code >= 300:
        raise RuntimeError(f"Create failed ({response.status_code}): {response.text.strip()}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=pathlib.Path, help="Directory containing downloaded files")
    parser.add_argument("project", help="Google Cloud project ID")
    parser.add_argument("data_store", help="Vertex AI Search data store ID")
    parser.add_argument("--location", default="global", help="Vertex AI Search location (default: global)")
    parser.add_argument("--collection", default=DEFAULT_COLLECTION, help="Collection ID (default: default_collection)")
    parser.add_argument("--branch", default=DEFAULT_BRANCH, help="Branch ID (default: default_branch)")
    parser.add_argument(
        "--service-account",
        type=pathlib.Path,
        help="Path to a service account key JSON file (uses ADC if omitted)",
    )
    parser.add_argument("--encoding", default="utf-8", help="File encoding to read (default: utf-8)")
    parser.add_argument(
        "--errors",
        default="strict",
        help="Decode error handling strategy passed to str.decode (default: strict)",
    )
    parser.add_argument(
        "--content-type",
        default="text/plain",
        help="Content type stored in the document (default: text/plain)",
    )
    parser.add_argument(
        "--source-uri",
        help="Optional logical source URI recorded in struct data",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively upload files from subdirectories",
    )
    args = parser.parse_args(argv)

    directory: pathlib.Path = args.directory
    if not directory.exists() or not directory.is_dir():
        parser.error(f"Directory not found: {directory}")

    session = build_session(args.service_account)

    parent_path = (
        f"projects/{args.project}/locations/{args.location}/collections/{args.collection}/"
        f"dataStores/{args.data_store}/branches/{args.branch}"
    )

    successes = 0
    failures: list[str] = []

    for file_path in iter_files(directory, recursive=args.recursive):
        document_id = sanitize_document_id(file_path, directory)
        try:
            content = read_text(file_path, args.encoding, args.errors)
        except UnicodeDecodeError as exc:
            failures.append(f"{file_path}: decode error ({exc})")
            continue
        payload = build_document_payload(
            file_path=file_path,
            root=directory,
            content=content,
            content_type=args.content_type,
            source_uri=args.source_uri,
        )
        try:
            post_document(session, parent_path, document_id, payload)
        except Exception as exc:  # noqa: BLE001 - report unexpected API errors and continue
            failures.append(f"{file_path}: {exc}")
        else:
            successes += 1
            print(f"uploaded {file_path} as {document_id}")

    if failures:
        print("\nSome uploads failed:", file=sys.stderr)
        for item in failures:
            print(f"  {item}", file=sys.stderr)
        print(f"Completed with {successes} successes and {len(failures)} failures.")
        return 1

    print(f"All {successes} files uploaded successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
