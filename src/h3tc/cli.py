"""CLI entry point for H3 template converter."""

import sys
from pathlib import Path

import click

from h3tc.converters.sod_to_hota import sod_to_hota
from h3tc.converters.hota_to_sod import hota_to_sod
from h3tc.converters.hota_to_hota18 import hota_to_hota18
from h3tc.converters.hota18_to_hota import hota18_to_hota
from h3tc.formats import detect_format, get_parser
from h3tc.writers.sod import SodWriter
from h3tc.writers.hota import HotaWriter
from h3tc.writers.hota18 import Hota18Writer


@click.group()
def cli():
    """H3 Template Converter - Convert between SOD, HOTA 1.7.x, and HOTA 1.8.x template formats."""
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_file", type=click.Path(path_type=Path))
@click.option(
    "--from", "from_format",
    type=click.Choice(["sod", "hota", "hota18"], case_sensitive=False),
    help="Input format (auto-detected from extension if omitted).",
)
@click.option(
    "--to", "to_format",
    type=click.Choice(["sod", "hota", "hota18"], case_sensitive=False),
    required=True,
    help="Output format.",
)
@click.option(
    "--pack-name",
    default="",
    help="Pack name for SOD->HOTA conversion.",
)
def convert(input_file: Path, output_file: Path, from_format: str, to_format: str, pack_name: str):
    """Convert a template file between SOD and HOTA formats."""
    # Auto-detect input format
    if not from_format:
        parser = detect_format(input_file)
        from_format = parser.format_id
    else:
        from_format = from_format.lower()
        parser = get_parser(from_format)

    to_format = to_format.lower()

    pack = parser.parse(input_file)

    # Convert if needed
    if from_format != to_format:
        if from_format == "sod" and to_format == "hota":
            name = pack_name or input_file.stem
            pack = sod_to_hota(pack, pack_name=name)
        elif from_format == "sod" and to_format == "hota18":
            name = pack_name or input_file.stem
            pack = sod_to_hota(pack, pack_name=name)
            pack = hota_to_hota18(pack)
        elif from_format == "hota" and to_format == "sod":
            pack = hota_to_sod(pack)
        elif from_format == "hota" and to_format == "hota18":
            pack = hota_to_hota18(pack)
        elif from_format == "hota18" and to_format == "sod":
            pack = hota_to_sod(pack)
        elif from_format == "hota18" and to_format == "hota":
            pack = hota18_to_hota(pack)
    else:
        click.echo(f"Rewriting {from_format.upper()} -> {to_format.upper()}")

    # Write output
    if to_format == "sod":
        writer = SodWriter()
    elif to_format == "hota18":
        writer = Hota18Writer()
    else:
        writer = HotaWriter()

    writer.write(pack, output_file)
    click.echo(f"Written {output_file}")


@cli.command()
@click.argument("file", required=False, type=click.Path(path_type=Path))
def editor(file: Path | None):
    """Launch the visual SOD template editor."""
    try:
        from h3tc.editor import launch
    except ImportError:
        click.echo(
            "The editor requires PySide6. Install with: pip install h3tc[gui]",
            err=True,
        )
        sys.exit(1)
    launch(str(file) if file else None)


def main():
    cli()


if __name__ == "__main__":
    main()
