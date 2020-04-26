from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import os
import glob

class Splitter:
    '''
    Class meant to split audio by the
    silence in the provided *.mp3.

    Puts files in variable directory, default is
    audio_segments.
    '''
    def __init__(self, path, directory="audio_segments"):
        self.path = path
        self.directory = directory
        self.segments = list()

        # speakers often change slides while talking, and sometimes
        # the slide change is after they begin to talk again
        # so we can account for this using a 2s buffer
        self.buffer = 2000
    '''
    Runs the splitter in its entirety.
    Removes files previously created.
    '''
    def run(self):
        self.remove_old_files()
        self.split_file()

    '''
    Removes old files in the directory
    that the script uses to put audio segments.
    '''
    def remove_old_files(self):

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        os.chdir(self.directory)
        files=glob.glob('*.mp3')

        for filename in files:
            os.unlink(filename)

        os.chdir("..")

    '''
    Normalizes the passed in chunk to the target
    volume.
    '''
    def match_target_amplitude(self, chunk, target_dBFS):
        change_in_dBFS = target_dBFS - chunk.dBFS
        return chunk.apply_gain(change_in_dBFS)

    '''
    Getter for the segments in the format of
    a list of tuples (filename, (start_time, end_time)).
    '''
    def get_segments(self):
        return self.segments

    '''
    Function that splits the file into audio segments
    based off the volume. Default is -30dB after normalization
    to -20dB for 1 second long pauses.
    '''
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

            # Add 500ms buffer to each end to keep the full audio
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

            # Add the buffer for slide switching to the start
            # and add the 500ms back
            if(start + self.buffer < end):
                start += self.buffer
            else:
                start = end

            segment = (filename, (start/1000, end/1000))
            self.segments.append(segment)


