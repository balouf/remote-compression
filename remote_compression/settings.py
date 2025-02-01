import subprocess
import json
from dataclasses import dataclass
from pathlib import Path

default_fields = ['width', 'height', 'codec_name']

full_extensions = {".avi", ".mp4", ".flv", ".wmv", ".mkv", ".ts", ".webm"}

default_extensions = {".mkv", ".mp4", ".m4v"}


def probe(file, fields=None):
    """

    Parameters
    ----------
    file: :class:`~pathlib.Path` or :class:`str`
        File location
    fields: dict
        Fields to extract

    Returns
    -------
    :class:`dict`:
        Extracted fields.
    :class:`bool`:
        Success of parsing.

    Examples
    --------

    >>> probe('data/small.mp4') # doctest: +SKIP
    ({'width': 1280, 'height': 720, 'codec_name': 'h264'}, True)
    >>> probe('data/big.mp4') # doctest: +SKIP
    ({'width': 1920, 'height': 1080, 'codec_name': 'h264'}, True)
    >>> probe('data/ovnis.mp4') # doctest: +SKIP
    ({}, False)
    """
    if fields is None:
        fields = default_fields
    try:
        command = f"ffprobe -v quiet -print_format json -show_streams \"{file}\""
        ffprobe_output = subprocess.check_output(command).decode('utf-8')
        streams = json.loads(ffprobe_output)['streams']
        for stream in streams:
            if fields[0] in stream:
                return {field: stream.get(field, "") for field in fields}, True
        return dict(), False
    except subprocess.CalledProcessError:
        return dict(), False


def transcode(infos, codec):
    return codec == 'libx265' and (infos['codec_name'] != 'hevc')


def big_size(infos, max_height=720):
    if max_height is None:
        return False
    return infos['height'] > max_height


@dataclass
class Settings:
    """
    Attributes
    ----------

    codec: str
        Name of the encoding codec to use
    map: bool
        Enforce full channel redirection. Use it to avoid (a bit) silent conversion errors due to strange multi-channel streams.
    height: int, optional
        Maximal height (for resizing)
    replace: bool, optional
        Should the transcoded version overwrite the original (do it at your own risk!)
    hostname: `str`, optional
        Remote host. Details related to connection should lie in the ssh config file.
    stats: `dict`
        Result of last check.

    Examples
    --------

    >>> settings = Settings()
    >>> settings.check('data/big.mp4') # doctest: +SKIP
    {'file': 'big.mp4', 'success': True, 'codec': True, 'resize': True, 'todo': True, 'cmd': 'ffmpeg -y -i "%(r_source)s" -vf scale=-1280:720 -map 0 -c:v libx265 -c:a copy -c:s copy -max_muxing_queue_size 9999 "%(r_target)s"'}
    >>> settings.check('data/small.mp4') # doctest: +SKIP
    {'file': 'small.mp4', 'success': True, 'codec': True, 'resize': False, 'todo': True, 'cmd': 'ffmpeg -y -i "%(r_source)s"  -map 0 -c:v libx265 -c:a copy -c:s copy -max_muxing_queue_size 9999 "%(r_target)s"'}
    >>> settings.check('data/ovnis.mp4') # doctest: +SKIP
    Issue with ovnis.mp4
    {'file': 'ovnis.mp4', 'success': False, 'todo': False}
    >>> settings = Settings(height=None, codec='libx264')
    >>> settings.check('data/big.mp4') # doctest: +SKIP
    {'file': 'big.mp4', 'success': True, 'codec': False, 'resize': False, 'todo': False, 'cmd': 'ffmpeg -y -i "%(r_source)s"  -map 0 -c:v libx264 -c:a copy -c:s copy -max_muxing_queue_size 9999 "%(r_target)s"'}
    >>> settings.stats['file'] # doctest: +SKIP
    'big.mp4'
    """
    codec: str = 'libx265'
    map: bool = True
    height: int = 720
    replace: bool = False
    hostname: str = 'remote_host'
    stats: dict = None

    def check(self, file):
        file = Path(file)
        res = {'file': file.name}
        infos, success = probe(file)
        res['success'] = success
        if not success:
            print(f"Issue with {file.name}")
            res["todo"] = False
            return res
        res['codec'] = transcode(infos, self.codec)
        res['resize'] = big_size(infos, max_height=self.height)
        if res['resize']:

            w2 = 2 * int(infos['width'] * (self.height // 2) / infos['height'])
            resize = f"-vf scale=-{w2}:{self.height}"
        else:
            resize = ""
        if self.map:
            codec = f"-map 0 -c:v {self.codec} -c:a copy -c:s copy"
        else:
            codec = f"-c:v {self.codec} -c:a copy"
        res["todo"] = res['codec'] or res['resize']
        res['cmd'] = f"ffmpeg -y -i \"%(r_source)s\" {resize} {codec} -max_muxing_queue_size 9999 \"%(r_target)s\""
        self.stats = res
        return res
