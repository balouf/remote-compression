import tempfile
from pathlib import Path
from remote_compression.ssh import SSH


def compress(source, settings):
    """

    Parameters
    ----------
    source: :class:`~pathlib.Path`
        Video to compress
    settings: :class:`~remote_compression.settings.Settings`
        Settings object

    Returns
    -------
    :class:`set`
        Names to be added to the keep file

    Examples
    --------

    >>> big = Path('data/big.mp4')
    >>> from remote_compression.settings import Settings
    >>> with tempfile.TemporaryDirectory() as d: # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS +SKIP
    ...     big_copy = Path(d) / big.name
    ...     _ = big_copy.write_bytes(big.read_bytes())
    ...     compress(big_copy, Settings())
    big.mp4 Size: 628516 => 380885, new size: 60.60%
    {...}
    """
    source = Path(source)
    stats = settings.check(source)
    return_value = {source.name}
    if stats['todo'] is False:
        return return_value
    r_source = f".rcomp/{next(tempfile._get_candidate_names())}{source.suffix}"
    r_target = f".rcomp/{next(tempfile._get_candidate_names())}{source.suffix}"
    cmd = stats['cmd'] % {'r_target': r_target, 'r_source': r_source}
    comp = source.with_name(f"comp_{source.name}")
    ori = source.with_name(f"ori_{source.name}")
    with SSH(settings.hostname) as ssh, ssh.open_sftp() as ftp:
        ftp.put(str(source), r_source)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        try:
            ftp.get(r_target, str(comp))
            ssh.exec_command(f"rm {r_target}")
        except FileNotFoundError:
            print("Failed compression")

        ssh.exec_command(f"rm {r_source}")

    if comp.exists:
        old_s = source.stat().st_size
        new_s = comp.stat().st_size
        ratio = new_s / old_s
        print(f"{source.name} Size: {old_s} => {new_s}, new size: {100 * ratio:.2f}%")
        if settings.replace:
            if exit_status == 0 and .01 < ratio < 1:
                comp.replace(source)
            if comp.exists():
                comp.unlink()
        else:
            if comp.exists():
                source.rename(ori)
                comp.rename(source)
                return_value.add(ori.name)
    return return_value
