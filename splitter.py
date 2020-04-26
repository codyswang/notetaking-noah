from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import os
import glob

class Splitter:

    def __init__(self, path, directory="audio_segments"):
        self.path = path
        self.directory = directory
        self.segments = list()

    def run(self):
        self.remove_old_files()
        self.split_file()

    def remove_old_files(self):

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        os.chdir(self.directory)
        files=glob.glob('*.mp3')

        for filename in files:
            os.unlink(filename)

        os.chdir("..")

    def match_target_amplitude(self, chunk, target_dBFS):
        change_in_dBFS = target_dBFS - chunk.dBFS
        return chunk.apply_gain(change_in_dBFS)

    def get_segments(self):
        return self.segments

    def split_file(self):
        audio = AudioSegment.from_file(self.path, format="mp3")

        print("Normalizing audio...")
        audio = self.match_target_amplitude(audio, -20.0)

        print("Detecting nonsilent ranges...")
        nonsilence_ranges = detect_nonsilent(
                audio,
                min_silence_len=1000,
                silence_thresh=-30,
                seek_step=1
            )

        print("Exporting chunks...")
        for i, timestamp in enumerate(nonsilence_ranges):
            start, end = timestamp

            # Add 500ms buffer to each end
            if(start - 500 > 0):
                start -= 500
            else:
                start = 0
            if(end + 500 < len(audio) - 1):
                end += 500
            else:
                end = len(audio) - 1

            # Export the file
            filename = self.directory + os.sep + self.directory + str(i) + ".mp3"
            audio[start:end].export(filename, format="mp3")

            segment = (filename, (start, end))
            self.segments.append(segment)


