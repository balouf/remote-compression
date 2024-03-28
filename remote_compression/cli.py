"""Console script for remote_compression."""
import sys
import click
from pathlib import Path


from remote_compression.settings import Settings
from remote_compression.recurse import recurse
from remote_compression.compression import compress


def setting_option(att, shortcuts=None):
    if shortcuts is None:
        shortcuts = list()
    name = f"--{att}"
    settings = Settings()
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
d_args, d_kwargs = setting_option('hostname', ['-D'])


presets = {'soft': Settings(),
           'hard': Settings(map=False, replace=True),
           'hard4': Settings(map=False, replace=True, codec='libx264')}


@click.command()
@click.option('--preset', '-P', type=click.Choice([k for k in presets]),
              help=f'Pre-defined settings (other video flags are ignored)', )
@click.option(*c_args, type=click.Choice( list({s.codec for s in presets.values()}) ), **c_kwargs)
@click.option(*m_args, **m_kwargs)
@click.option(*h_args, **h_kwargs)
@click.option(*r_args, **r_kwargs)
@click.option(*d_args, **d_kwargs)
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
        if 'hostname' in kwargs:
            settings.hostname = kwargs['hostname']
    else:
        settings = Settings(**kwargs)
    if dest.is_dir():
        recurse(dest, settings)
    else:
        compress(dest, settings)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover


