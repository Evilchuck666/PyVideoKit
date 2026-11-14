from pathlib import Path

import click

from pyvideokit_libs import convert_to_ffv1

from ._helpers import handle_errors, track_progress


@click.command("convert-to-ffv1")
@click.argument("input", type=click.Path(exists=True))
@click.option("--fps", default=None, type=int, help="Output frame rate (default: preserve source fps).")
@click.option("-o", "--output", default=None, help="Output file or directory.")
def cmd(input, fps, output):
    """Convert video to lossless FFV1/MKV format."""
    with handle_errors():
        with track_progress("Converting to FFV1") as on_progress:
            out = convert_to_ffv1(Path(input), fps=fps, output=output, on_progress=on_progress)
    click.echo(str(out))


main = cmd
