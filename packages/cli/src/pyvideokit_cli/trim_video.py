from pathlib import Path

import click

from pyvideokit_libs import trim_video

from ._helpers import TIME, handle_errors, track_progress


@click.command("trim-video")
@click.argument("input", type=click.Path(exists=True))
@click.option("--start", required=True, type=TIME, help="Start time (seconds or HH:MM:SS).")
@click.option("--end", required=True, type=TIME, help="End time (seconds or HH:MM:SS).")
@click.option("-o", "--output", default=None, help="Output file or directory.")
def cmd(input, start, end, output):
    """Cut a segment from a video (stream copy, no re-encoding)."""
    with handle_errors():
        with track_progress("Trimming") as on_progress:
            out = trim_video(Path(input), start=start, end=end, output=output, on_progress=on_progress)
    click.echo(str(out))


main = cmd
