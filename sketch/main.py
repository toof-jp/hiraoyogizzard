"""Command-line helper for testing Vertex AI Search responses."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from google.cloud import discoveryengine_v1
from google.protobuf.json_format import MessageToDict

ENV_PROJECT = "VERTEX_AI_PROJECT_ID"
ENV_LOCATION = "VERTEX_AI_LOCATION"
ENV_DATA_STORE = "VERTEX_AI_DATA_STORE_ID"


def build_request(
    *,
    project: str,
    location: str,
    data_store: str,
    serving_config_id: str,
    query: str,
    page_size: int,
    page_token: str | None,
    filter_: str | None,
) -> discoveryengine_v1.SearchRequest:
    """Create the Discovery Engine request with the provided configuration."""

    serving_config = discoveryengine_v1.SearchServiceClient.serving_config_path(
        project=project,
        location=location,
        data_store=data_store,
        serving_config=serving_config_id,
    )

    request = discoveryengine_v1.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=page_size,
    )

    if page_token:
        request.page_token = page_token

    if filter_:
        request.filter = filter_

    return request


def execute_search(request: discoveryengine_v1.SearchRequest) -> discoveryengine_v1.SearchResponse:
    """Run the search request and return the service response."""

    client = discoveryengine_v1.SearchServiceClient()
    return client.search(request)


def response_to_json(response: discoveryengine_v1.SearchResponse) -> str:
    """Convert the search response to a formatted JSON string."""

    response_dict: dict[str, Any] = MessageToDict(
        response._pb,  # pylint: disable=protected-access
        preserving_proto_field_name=True,
    )
    return json.dumps(response_dict, indent=2, ensure_ascii=False)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query Vertex AI Search and print the raw response")
    parser.add_argument("query", help="Search query string to send to Vertex AI Search")
    parser.add_argument(
        "--project",
        default=os.environ.get(ENV_PROJECT),
        help=f"Google Cloud project ID (defaults to ${ENV_PROJECT} if set)",
    )
    parser.add_argument(
        "--location",
        default=os.environ.get(ENV_LOCATION),
        help=f"Vertex AI Search location (defaults to ${ENV_LOCATION} if set)",
    )
    parser.add_argument(
        "--data-store",
        default=os.environ.get(ENV_DATA_STORE),
        help=f"Vertex AI Search data store ID (defaults to ${ENV_DATA_STORE} if set)",
    )
    parser.add_argument(
        "--serving-config",
        default="default_config",
        help="Serving config ID to use (default: default_config)",
    )
    parser.add_argument(
        "-n",
        "--page-size",
        type=int,
        default=10,
        help="Number of documents to request (default: 10)",
    )
    parser.add_argument(
        "--page-token",
        default=None,
        help="Optional page token for continuing a previous query",
    )
    parser.add_argument(
        "--filter",
        dest="filter_",
        default=None,
        help="Optional filter expression",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    missing = [
        flag
        for flag, value in {
            "--project": args.project,
            "--location": args.location,
            "--data-store": args.data_store,
        }.items()
        if not value
    ]

    if missing:
        joined = ", ".join(missing)
        print(
            f"Missing required parameter(s): {joined}. "
            f"Pass them as CLI flags or set the matching environment variables.",
            file=sys.stderr,
        )
        return 1

    if args.page_size <= 0:
        print("--page-size must be a positive integer", file=sys.stderr)
        return 1

    try:
        request = build_request(
            project=args.project,
            location=args.location,
            data_store=args.data_store,
            serving_config_id=args.serving_config,
            query=args.query,
            page_size=args.page_size,
            page_token=args.page_token,
            filter_=args.filter_,
        )
        response = execute_search(request)
        print(response_to_json(response))
        return 0
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Vertex AI Search request failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
