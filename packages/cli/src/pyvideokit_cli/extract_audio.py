from pathlib import Path

import click

from pyvideokit_libs import extract_audio

from ._helpers import handle_errors, track_progress


@click.command("extract-audio")
@click.argument("input", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, help="Output file or directory.")
def cmd(input, output):
    """Extract audio track to WAV (pcm_s16le)."""
    with handle_errors():
        with track_progress("Extracting audio") as on_progress:
            out = extract_audio(Path(input), output=output, on_progress=on_progress)
    click.echo(str(out))


main = cmd
