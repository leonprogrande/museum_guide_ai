import ctypes
import sys
from ctypes.util import find_library


_asound = None


@ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
def _alsa_error_handler(_filename, _line, _function, _err, _fmt):
    # Ignora logs internos de ALSA (e.g. "ALSA lib conf.c ...").
    return


def suppress_alsa_warnings() -> None:
    global _asound

    if not sys.platform.startswith("linux"):
        return

    try:
        lib_name = find_library("asound") or "libasound.so.2"
        _asound = ctypes.cdll.LoadLibrary(lib_name)
        _asound.snd_lib_error_set_handler(_alsa_error_handler)
    except Exception:
        # Si falla, continuamos sin suprimir para no romper audio.
        pass
