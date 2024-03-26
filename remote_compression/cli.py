"""Console script for remote-compression."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for remote-compression."""
    click.echo("Replace this message by putting your code into "
               "remote_compression.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

"""Console script for remote_compression."""
import sys
import click
from pathlib import Path

from remote_compression.video import VideoSettings
from remote_compression.explore import recurse, single_compression


def setting_option(att, shortcuts=None):
    if shortcuts is None:
        shortcuts = list()
    name = f"--{att}"
    settings = VideoSettings()
    default = settings.__getattribute__(att)
    found = False
    h = ""
    for l in settings.__doc__.splitlines():
        if l.strip().startswith(att):
            found = True
            continue
        if found:
            h = l.strip()
            break
    return [name, *shortcuts], {'default': default, 'help': h, 'show_default': True}


c_args, c_kwargs = setting_option('codec', ['-C'])
m_args, m_kwargs = setting_option('map', ['-M'])
r_args, r_kwargs = setting_option('replace', ['-R'])
h_args, h_kwargs = setting_option('height')

presets = {'soft': VideoSettings(),
           'hard': VideoSettings(map=False, replace=True),
           'hard4': VideoSettings(map=False, replace=True, codec='libx264')}


@click.command()
@click.option('--preset', '-P', type=click.Choice([k for k in presets]),
              help=f'Pre-defined settings (other flags are ignored)', )
@click.option(*c_args, type=click.Choice(list({s.codec for s in presets.values()})), **c_kwargs)
@click.option(*m_args, **m_kwargs)
@click.option(*h_args, **h_kwargs)
@click.option(*r_args, **r_kwargs)
@click.argument('target', default='.')
def main(args=None, **kwargs):
    """Console script for remote_compression."""
    dest = Path(kwargs.pop('target'))
    if not dest.exists():
        click.echo(f'{dest} does not exist!')
        return 1

    preset = kwargs.pop('preset', None)
    if preset is not None:
        settings = presets[preset]
    else:
        settings = VideoSettings(**kwargs)
    if dest.is_dir():
        recurse(dest, settings)
    else:
        single_compression(dest, settings)
    # core(settings)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

