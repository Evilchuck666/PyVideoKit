from pathlib import Path

import click

from pyvideokit_libs import apply_vhs_effect

from ._helpers import handle_errors, track_progress


@click.command("apply-vhs-effect")
@click.argument("input", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, help="Output file or directory.")
def cmd(input, output):
    """Apply VHS visual and audio effect to a video."""
    with handle_errors():
        with track_progress("Applying VHS effect") as on_progress:
            out = apply_vhs_effect(Path(input), output=output, on_progress=on_progress)
    click.echo(str(out))


main = cmd
