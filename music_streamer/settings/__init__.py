from music_streamer.settings.common import *

try:
    from music_streamer.settings.local import *
except ModuleNotFoundError:
    from music_streamer.settings.production import *
