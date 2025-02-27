from snowboy.examples.Python3 import snowboydecoder
from dexterous_grasp.config import awake_params
import signal
interrupted = False

def interrupt_callback():
    global interrupted
    return interrupted

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)

activation_audio = awake_params.activation_audio
detector = snowboydecoder.HotwordDetector(activation_audio, sensitivity=0.5)