from pathlib import Path

import click

from pyvideokit_libs import join_videos

from ._helpers import handle_errors, track_progress


@click.command("concat-videos")
@click.argument("videos", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("-o", "--output", default=None, help="Output file or directory.")
def cmd(videos, output):
    """Concatenate two or more videos (lossless stream copy)."""
    if len(videos) < 2:
        raise click.UsageError("Provide at least two input videos.")
    with handle_errors():
        with track_progress("Concatenating") as on_progress:
            out = join_videos([Path(v) for v in videos], output=output, on_progress=on_progress)
    click.echo(str(out))


main = cmd
