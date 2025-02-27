import re
import time
import ctypes
import pyaudio
import threading

from dexterous_grasp.logger_module import LoggerValidator
from dexterous_grasp.utils.common import play_audio_file


class IFlytekInterface(LoggerValidator):
    def __init__(self, iflytek_config, logger_manager=None):
        super().__init__(logger_manager)
        self.iflytek_config = iflytek_config
        self._initialize_msc_library()

        # Initialize MSC login
        if not self._msc_login():
            raise Exception("Failed to login to MSC platform.")

    def __del__(self):
        self.msc.MSPLogout()

    def _initialize_msc_library(self):
        """Initializes MSC library and function prototypes."""
        self.msc = ctypes.cdll.LoadLibrary(self.iflytek_config.msc_lib_path)

        # Define MSC function argument and return types
        self.msc.MSPLogin.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        self.msc.MSPLogin.restype = ctypes.c_int

        self.msc.QISRSessionBegin.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
        self.msc.QISRSessionBegin.restype = ctypes.c_char_p

        self.msc.QISRAudioWrite.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
        self.msc.QISRAudioWrite.restype = ctypes.c_int

        self.msc.QISRGetResult.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_int)]
        self.msc.QISRGetResult.restype = ctypes.c_char_p

        self.msc.QISRSessionEnd.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.msc.QISRSessionEnd.restype = ctypes.c_int

        self.msc.MSPLogout.restype = ctypes.c_int

    def _msc_login(self):
        """Logs into the MSC platform."""
        login_params = f"appid = {self.iflytek_config.app_id}, work_dir = .".encode('utf-8')
        ret = self.msc.MSPLogin(None, None, login_params)
        if ret != 0:
            self.logger_manager.logger.error(f"MSPLogin failed, error code: {ret}")
        return ret == 0

    def audio_frame2text(self, pcm_data):
        """Converts PCM audio frames into text, returns False, None if takes more than 5 seconds."""
        result_container = {'success': False, 'text': None}

        def recognition():
            session_id = self._start_session()
            if not session_id:
                result_container['success'] = False
                result_container['text'] = None
                return

            if not self._write_audio_to_session(session_id, pcm_data):
                result_container['success'] = False
                result_container['text'] = None
                return

            full_result = self._get_recognition_result(session_id)
            self._end_session(session_id)

            # Remove punctuation
            text = re.sub(r'[^\w\s]', '', full_result)
            self.logger_manager.logger.info("Recognized text: %s", text)

            result_container['success'] = True
            result_container['text'] = text

        # Start the recognition in a separate thread
        recog_thread = threading.Thread(target=recognition)
        recog_thread.start()

        # Wait for the thread to finish with timeout
        recog_thread.join(timeout=5)

        if recog_thread.is_alive():
            # If thread is still alive after timeout, return False, None
            self.logger_manager.logger.error("Recognition timed out after 5 seconds")
            return False, None
        else:
            return result_container['success'], result_container['text']


    def _start_session(self):
        """Starts an MSC session."""
        errcode = ctypes.c_int(0)
        session_id = self.msc.QISRSessionBegin(None,
            b"sub = iat, domain = iat, language = zh_cn, accent = mandarin, sample_rate = 16000, result_type = plain, result_encoding = utf8",
            ctypes.byref(errcode))

        if not session_id:
            self.logger_manager.logger.error(f"QISRSessionBegin failed, error code: {errcode.value}")
        return session_id

    def _write_audio_to_session(self, session_id, pcm_data):
        """Writes audio data to the MSC session."""
        audio_status = ctypes.c_int(2)  # MSP_AUDIO_SAMPLE_FIRST
        ep_status = ctypes.c_int(0)
        rec_status = ctypes.c_int(0)

        ret = self.msc.QISRAudioWrite(session_id, ctypes.cast(pcm_data, ctypes.POINTER(ctypes.c_ubyte)), len(pcm_data),
                                      audio_status, ctypes.byref(ep_status), ctypes.byref(rec_status))
        if ret != 0:
            self.logger_manager.logger.error(f"QISRAudioWrite failed, error code: {ret}")
            self.msc.QISRSessionEnd(session_id, "QISRAudioWrite failed".encode('utf-8'))
            return False

        # Indicate end of audio
        ret = self.msc.QISRAudioWrite(session_id, None, 0, 4, ctypes.byref(ep_status), ctypes.byref(rec_status))
        if ret != 0:
            self.logger_manager.logger.error(f"QISRAudioWrite failed, error code: {ret}")
            self.msc.QISRSessionEnd(session_id, "QISRAudioWrite failed".encode('utf-8'))
            return False
        return True

    def _get_recognition_result(self, session_id):
        """Fetches the recognition result from the MSC session."""
        full_result = ""
        rec_status = ctypes.c_int(0)
        errcode = ctypes.c_int(0)

        while rec_status.value != 5:  # MSP_REC_STATUS_COMPLETE
            result = self.msc.QISRGetResult(session_id, ctypes.byref(rec_status), 0, ctypes.byref(errcode))
            if errcode.value != 0:
                self.logger_manager.logger.error(f"QISRGetResult failed, error code: {errcode.value}")
                break
            if result:
                full_result += result.decode('utf-8')
            time.sleep(0.1)

        return full_result

    def _end_session(self, session_id):
        """Ends the MSC session."""
        self.msc.QISRSessionEnd(session_id, "Normal end".encode('utf-8'))

    def voice_to_text(self, channels=1):
        """Captures voice input and converts it to text."""
        frames = self._record_audio(channels)
        text = self.audio_frame2text(b''.join(frames))
        if not text:
            self.logger_manager.logger.error(f"No valid voice input detected.")
            return None
        self.logger_manager.create_prompt_folder(text)
        return text

    def _record_audio(self, channels):
        """Records audio input using pyaudio."""
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=channels, rate=self.iflytek_config.sample_rate, input=True,
                        frames_per_buffer=1024)

        self.logger_manager.logger.info("Recording started.")
        play_audio_file(self.iflytek_config.start_recording_audio_path)

        frames = [stream.read(1024) for _ in range(0, int(self.iflytek_config.sample_rate / 1024 * self.iflytek_config.record_seconds))]

        self.logger_manager.logger.info("Recording finished.")
        play_audio_file(self.iflytek_config.stop_recording_audio_path)

        stream.stop_stream()
        stream.close()
        p.terminate()

        return frames
