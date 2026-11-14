from collections.abc import Callable, Generator
from contextlib import contextmanager

import click
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from pyvideokit_libs import FFmpegError, parse_time_to_seconds


@contextmanager
def track_progress(label: str) -> Generator[Callable[[float], None], None, None]:
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold]{task.description}"),
        BarColumn(),
        TextColumn("{task.percentage:>5.1f}%"),
        TimeElapsedColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task(label, total=100.0)

        def on_progress(pct: float) -> None:
            progress.update(task, completed=pct)

        yield on_progress


@contextmanager
def handle_errors() -> Generator[None, None, None]:
    try:
        yield
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        raise click.ClickException(str(e))
    except FFmpegError as e:
        click.echo(f"FFmpeg failed (exit {e.returncode}):", err=True)
        for line in e.error_lines:
            click.echo(f"  {line}", err=True)
        raise click.exceptions.Exit(e.returncode)


class TimeParam(click.ParamType):
    name = "TIME"

    def convert(self, value, param, ctx):
        try:
            result = parse_time_to_seconds(str(value))
        except ValueError as e:
            self.fail(str(e), param, ctx)
        if result is None:
            self.fail("Empty time value", param, ctx)
        return result


TIME = TimeParam()
