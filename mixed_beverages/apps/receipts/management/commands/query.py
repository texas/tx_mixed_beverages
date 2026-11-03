import inspect
import json
from decimal import Decimal
from typing import Any, cast

from django.core.management.base import BaseCommand, CommandError

from mixed_beverages.apps.receipts.queries import QUERIES


def _signature(name: str) -> str:
    params = inspect.signature(QUERIES[name]).parameters.values()
    return " ".join(
        f"{p.name}=<{p.annotation.__name__}>"
        + ("" if p.default is p.empty else f" (default {p.default})")
        for p in params
    )


def _is_table(result: Any) -> bool:
    return (
        isinstance(result, list)
        and bool(result)
        and all(isinstance(row, dict) for row in result)
    )


LOCATION_KEYS = ("pk", "name", "lat", "lng", "url")


# Characters that would break a markdown table cell or link text
ESCAPES = str.maketrans(
    cast("dict[str, str | int | None]", {"|": r"\|", "[": r"\[", "]": r"\]"})
)


def _link(row: dict[str, Any]) -> str:
    """Markdown link: pk and name as text, the map url (with lat/lng) as target."""
    text = f"{row['pk']} {row['name']}".translate(ESCAPES)
    return f"[{text}]({row['url']})" if row["url"] else text


def _table(rows: list[dict[str, Any]]) -> str:
    if all(key in rows[0] for key in LOCATION_KEYS):
        # Replace the pk, name, lat, lng and url columns with one link column
        rest = [key for key in rows[0] if key not in LOCATION_KEYS]
        columns = ["location", *rest]
        cells = [[_link(row), *(str(row[key]) for key in rest)] for row in rows]
    else:
        columns = list(rows[0])
        cells = [[str(row.get(column, "")) for column in columns] for row in rows]
    lines = [
        "| " + " | ".join(columns) + " |",
        "|" + "|".join("---" for _ in columns) + "|",
        *("| " + " | ".join(row) + " |" for row in cells),
    ]
    return "\n".join(lines)


class Command(BaseCommand):
    help = """
    Run a canned read-only ORM query. A list of rows prints as a markdown
    table, anything else (or with --json) as JSON.
    Without a name, list the available queries.
    Example: ./manage.py query low_quality limit=5
    """

    def add_arguments(self, parser):
        parser.add_argument("name", nargs="?")
        parser.add_argument("params", nargs="*", help="key=value")
        parser.add_argument(
            "--json",
            action="store_true",
            help="Print JSON even when the result is a list of rows",
        )

    def handle(self, name, params, *args, **options):
        if name is None:
            for query_name, fn in QUERIES.items():
                self.stdout.write(f"{query_name}: {inspect.getdoc(fn)}")
                if signature := _signature(query_name):
                    self.stdout.write(f"    {signature}")
            return
        if name not in QUERIES:
            raise CommandError(f"Unknown query {name!r}. Run without a name to list.")

        fn = QUERIES[name]
        accepted = inspect.signature(fn).parameters
        kwargs: dict[str, Any] = {}
        for param in params:
            key, sep, value = param.partition("=")
            if not sep or key not in accepted:
                raise CommandError(
                    f"Bad parameter {param!r}. Expected: {_signature(name)}"
                )
            kind = accepted[key].annotation
            try:
                kwargs[key] = Decimal(value) if kind is Decimal else kind(value)
            except ValueError as e:
                raise CommandError(f"Bad value for {key}: {e}") from e
        result = fn(**kwargs)
        if options["json"] or not _is_table(result):
            self.stdout.write(json.dumps(result, indent=2, default=str))
        else:
            self.stdout.write(_table(result))
