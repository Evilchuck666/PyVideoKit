from pathlib import Path

import click

from pyvideokit_libs import prepare_youtube

from ._helpers import handle_errors, track_progress


@click.command("prepare-youtube")
@click.argument("input", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, help="Output file or directory.")
def cmd(input, output):
    """Encode FFV1 master to ProRes 422 HQ MOV for YouTube upload."""
    with handle_errors():
        with track_progress("Encoding for YouTube") as on_progress:
            out = prepare_youtube(Path(input), output=output, on_progress=on_progress)
    click.echo(str(out))


main = cmd
