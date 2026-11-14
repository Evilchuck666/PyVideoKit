import click
from importlib.metadata import version

from .apply_vhs_effect import cmd as cmd_apply
from .concat_videos import cmd as cmd_concat
from .convert_to_ffv1 import cmd as cmd_convert
from .extract_audio import cmd as cmd_extract
from .fade_video import cmd as cmd_fade
from .prepare_youtube import cmd as cmd_prepare
from .trim_video import cmd as cmd_trim


@click.group()
@click.version_option(version("PyVideoKit-CLI"))
def cli():
    """PyVideoKit CLI — FFmpeg-based video processing tools."""


cli.add_command(cmd_apply, "apply-vhs-effect")
cli.add_command(cmd_concat, "concat-videos")
cli.add_command(cmd_convert, "convert-to-ffv1")
cli.add_command(cmd_extract, "extract-audio")
cli.add_command(cmd_fade, "fade-video")
cli.add_command(cmd_prepare, "prepare-youtube")
cli.add_command(cmd_trim, "trim-video")
