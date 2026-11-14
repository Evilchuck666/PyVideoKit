from pathlib import Path

import click

from pyvideokit_libs import fade_video

from ._helpers import handle_errors, track_progress


@click.command("fade-video")
@click.argument("input", type=click.Path(exists=True))
@click.option("--fade", default=None, type=float, help="Fade-in and fade-out duration in seconds (shorthand).")
@click.option("--fade-in", "fade_in", default=None, type=float, help="Fade-in duration in seconds.")
@click.option("--fade-out", "fade_out", default=None, type=float, help="Fade-out duration in seconds.")
@click.option("-o", "--output", default=None, help="Output file or directory.")
def cmd(input, fade, fade_in, fade_out, output):
    """Add fade-in and/or fade-out to an FFV1 video."""
    if fade is not None:
        fade_in = fade_in if fade_in is not None else fade
        fade_out = fade_out if fade_out is not None else fade
    with handle_errors():
        with track_progress("Applying fade") as on_progress:
            out = fade_video(
                Path(input),
                fade_in=fade_in,
                fade_out=fade_out,
                output=output,
                on_progress=on_progress,
            )
    click.echo(str(out))


main = cmd
