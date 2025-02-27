import os
from collections import namedtuple

# Environment variables and paths
project_root_path = os.getenv("PROJECT_ROOT")
max_timeout = 20
chunk = 1024
channels = 1
rate = 16000
mindb_start = 5000  # 最小声音，大于则开始录音
mindb_end = 1000  # 最小声音，小于则结束录音
silence_duration = 0.7  # 小声0.7秒后自动终止

# 定义命名元组
AudioRecordParams = namedtuple('AudioRecordParams', ['max_timeout', 'chunk', 'channels', 'rate', 'mindb_start', 'mindb_end', 'silence_duration'])
AwakeParams = namedtuple('AwakeParams', ['activation_audio'])
FeedbackParams = namedtuple('FeedbackParams', ['not_clear', 'internet_error', 'location_error', 'not_understandable', 'object_error', 'photograph_error', 'ready_go', 'task_completed'])

# 使用命名元组来存储参数
audio_record_params = AudioRecordParams(
    max_timeout=max_timeout,
    chunk=chunk,
    channels=channels,
    rate=rate,
    mindb_start=mindb_start,
    mindb_end=mindb_end,
    silence_duration=silence_duration
)

activation_audio = os.path.join(project_root_path, "assets/digital_io/xiaoai.pmdl")

awake_params = AwakeParams(
    activation_audio=activation_audio
)

# Adding feedback audio file paths
feedback_params = FeedbackParams(
    not_clear=os.path.join(project_root_path, "assets/audio/sorrry_not_clear.mp3"),
    internet_error=os.path.join(project_root_path, "assets/audio/sorry_internet_erro.mp3"),
    location_error=os.path.join(project_root_path, "assets/audio/sorry_location.mp3"),
    not_understandable=os.path.join(project_root_path, "assets/audio/sorry_not_understandable.mp3"),
    object_error=os.path.join(project_root_path, "assets/audio/sorry_object.mp3"),
    photograph_error=os.path.join(project_root_path, "assets/audio/sorry_photograph.mp3"),
    ready_go=os.path.join(project_root_path,"assets/audio/ready_go.mp3"),
    task_completed=os.path.join(project_root_path, "assets/audio/ur5_finish.mp3")
)
