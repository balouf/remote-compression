from pathlib import Path
import paramiko
import time


def get_config(hostname, config_path=None):
    """
    Parameters
    ----------
    hostname: :class:`str`
        Destination
    config_path: :class:`str`, optional
        Location of the openSSH config file if different from ~/.ssh/config.

    Returns
    -------
    :class:`dict`
        Parameters for destination

    Examples
    --------

    >>> get_config('my_machine')  # doctest: +NORMALIZE_WHITESPACE
    {'hostname': 'my_machine'}
    """
    if config_path is None:
        config_path = str(Path.home() / ".ssh/config")
    try:
        config = paramiko.SSHConfig.from_path(config_path)
    except FileNotFoundError:
        config = paramiko.SSHConfig()
    return config.lookup(hostname)


def auto_retry(client, attempts=0, **kwargs):
    if attempts > 10:
        raise paramiko.ssh_exception.SSHException
    try:
        client.connect(**kwargs)
    except paramiko.ssh_exception.SSHException:
        time.sleep(10)
        auto_retry(client, attempts=attempts + 1, **kwargs)


class SSH(paramiko.SSHClient):
    """
    Context manager for making a paramiko connection with possible proxyjump.

    Parameters
    ----------
    hostname: :class:`str`
        Destination. `~/.ssh/config` will be used to retrieve extra parameters.

    Examples
    --------

    >>> with SSH('remote_host') as ssh:  # doctest: +NORMALIZE_WHITESPACE +SKIP
    ...     _stdin, _stdout,_stderr = ssh.exec_command("pwd")
    ...     print(_stdout.read().decode())
    /home/fmathieu
    """

    def __init__(self, hostname):
        self.cfg = get_config(hostname)
        self.gw = paramiko.SSHClient()
        self.ssh = paramiko.SSHClient()

    def __enter__(self):
        dest = self.cfg.get('hostname')
        key = self.cfg.get('identityfile')
        user = self.cfg.get('user')
        jump = self.cfg.get('proxyjump')
        if jump is None:
            sock = None
        else:
            if "@" in jump:
                gw_user, gw_dest = jump.split('@')
            else:
                gw_user, gw_dest = user, jump
            self.gw.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            auto_retry(self.gw, hostname=gw_dest, username=gw_user, key_filename=key,
                       banner_timeout=100, timeout=100, auth_timeout=100, allow_agent=False)
            transport = self.gw.get_transport()
            transport.set_keepalive(60)
            dest_addr = (dest, 22)
            local_addr = ('127.0.0.1', 22)
            sock = transport.open_channel("direct-tcpip", dest_addr, local_addr)
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        auto_retry(self.ssh, hostname=dest, username=user, key_filename=key, sock=sock,
                   banner_timeout=100, timeout=100, auth_timeout=100, allow_agent=False)
        return self.ssh

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ssh.close()
        self.gw.close()
