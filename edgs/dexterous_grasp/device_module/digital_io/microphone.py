import time
import pyaudio, wave
import numpy as np
from dexterous_grasp.logger_module.logger import LoggerValidator

class Microphone(LoggerValidator):

    def __init__(self, audio_record_params,awake_params, snowboydecoder, logger_manager):
        super(Microphone, self).__init__(logger_manager)

        #For awake
        self.models = awake_params.activation_audio
        self.detector = snowboydecoder.HotwordDetector(self.models, sensitivity=[0.5])
        #For the record
        self.chunk = audio_record_params.chunk
        self.channels = audio_record_params.channels
        self.rate = audio_record_params.rate
        self.mindb_start = audio_record_params.mindb_start  # 开始录音的音量阈值
        self.mindb_end = audio_record_params.mindb_end  # 结束录音的音量阈值
        self.silence_duration = audio_record_params.silence_duration  # 没有人说话后的静默时间
        self.max_timeout = audio_record_params.max_timeout  # 最大录音时间
        self.format = pyaudio.paInt16
        self.pyaudio_instance = None


    def listen(self):
        self.pyaudio_instance = pyaudio.PyAudio()
        stream = self.pyaudio_instance.open(format=self.format,
                                            channels=self.channels,
                                            rate=self.rate,
                                            input=True,
                                            frames_per_buffer=self.chunk)

        self.logger_manager.logger.info("开始录音等待...")
        audio_frames = []
        is_recording = False  # 是否正在录音
        is_silent = False  # 是否检测到静音
        silence_start_time = None  # 静音开始的时间戳
        record_start_time = None  # 录音开始的时间戳

        while True:
            # 从音频流中读取数据
            audio_data = stream.read(self.chunk, exception_on_overflow=False)
            audio_samples = np.frombuffer(audio_data, dtype=np.short)
            max_volume = np.max(audio_samples)
            current_time = time.time()  # 当前时间戳

            # 如果音量大于起始阈值并且未开始录音，开始录音
            if max_volume > self.mindb_start and not is_recording:
                is_recording = True
                record_start_time = current_time
                self.logger_manager.logger.info("检测到声音，开始录音...")
                audio_frames.append(audio_data)
                silence_start_time = None
                continue

            # 如果正在录音，将音频数据保存
            if is_recording:
                audio_frames.append(audio_data)

                # 检测是否小于结束音量阈值
                if max_volume < self.mindb_end:
                    if not is_silent:
                        self.logger_manager.logger.info("静音检测中...")
                        silence_start_time = current_time  # 记录静音开始时间
                    is_silent = True
                else:
                    is_silent = False
                    silence_start_time = None  # 取消静音状态

                # 如果静音时间超过设定的时间，停止录音
                if is_silent and silence_start_time and (current_time - silence_start_time) > self.silence_duration:
                    self.logger_manager.logger.info("静音超过设定时间，停止录音")
                    break

                # 如果录音时间超过最大超时时间，强制结束
                if (current_time - record_start_time) > self.max_timeout:
                    self.logger_manager.logger.info("录音超时，强制停止录音")
                    break

        # 结束音频流
        stream.stop_stream()
        stream.close()
        self.pyaudio_instance.terminate()

        self.logger_manager.logger.info("录音结束")
        return audio_frames



    def save_mp3(self, frames, map3_path):
        wf = wave.open(map3_path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.pyaudio_instance.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()


