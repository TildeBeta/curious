# This file is part of curious.
#
# curious is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# curious is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with curious.  If not, see <http://www.gnu.org/licenses/>.

"""
A voice player that uses ffmpeg.
"""
import subprocess
import threading
import time
import typing

from curious.voice import voice_client


class VoicePlayer(threading.Thread):
    """
    A voice player object.
    """

    FFMPEG_NAME = "ffmpeg"

    def __init__(self, vc: 'voice_client.VoiceClient',
                 path: str, callback: typing.Callable[['VoicePlayer'], None] = None):
        """
        :param vc: The voice client this player is associated with.
        :param path: The path this player should play.
        :param callback: A callback to be ran after the voice player has finished playing.
        """
        threading.Thread.__init__(self, daemon=True)
        self.vc = vc
        self.path = path
        self.callable = callback

        # samples_per_frame * 4
        self.buf_amount = 20 * 48 * 4

        # delay - 20ms
        self.delay = 0.02

    def run(self):
        # Load ffmpeg, and begin encoding the frames.
        arg = "-i {} -f s16le -ar 48000 -ac 2 pipe:1".format(self.path).split()
        full = [self.FFMPEG_NAME, *arg]

        proc = subprocess.Popen(full, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        start_time = time.time()
        loops = 0

        while True:
            # Ensure the subprocess isn't ded
            try:
                proc.wait(timeout=0)
            except subprocess.TimeoutExpired:
                pass
            else:
                _, stderr = proc.communicate()
                if proc.returncode:
                    raise RuntimeError(stderr.decode())
                else:
                    break

            loops += 1

            # encode the packet and send it to discord
            data = proc.stdout.read(self.buf_amount)
            if not data:
                continue

            self.vc.send_voice_packet(data)

            # now we need to sleep
            # make sure to account for drift!
            delay = max(0, self.delay + ((start_time + self.delay * loops) + - time.time()))
            time.sleep(delay)

        if self.callable:
            self.callable(self)
