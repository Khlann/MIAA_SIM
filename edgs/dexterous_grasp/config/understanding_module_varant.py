import os
from collections import namedtuple

# Define namedtuples for better organization
ProxySettings = namedtuple('ProxySettings', ['http', 'https'])
FilePaths = namedtuple('FilePaths', ['understanding_test_image', 'msc_lib', 'audio_file', 'start_recording_audio', 'stop_recording_audio'])
RequestInfo = namedtuple('RequestInfo', ['headers', 'single_en_prompt', 'model', 'api_url'])
IflytekConfig = namedtuple('IflytekConfig', ['app_id', 'msc_lib_path', 'audio_file', 'start_recording_audio_path', 'stop_recording_audio_path', 'record_seconds', 'sample_rate'])
DoubaoConfig = namedtuple('DoubaoConfig', ['api_key','model_config','single_en_prompt'])
# Proxy settings
proxy_settings = ProxySettings(
    http="http://localhost:7890",
    https="http://localhost:7890"
)

api_key = ""#

file_paths = FilePaths(
    understanding_test_image=os.path.join( "edgs/dexterous_grasp/config/unittest_assets/understanding/over.jpeg"),
    msc_lib=os.path.join( "edgs/dexterous_grasp/config/unittest_assets/understanding/libmsc.so"),
    audio_file=os.path.join( "edgs/dexterous_grasp/config/unittest_assets/understanding/mp3/command.wav"),
    start_recording_audio=os.path.join( "edgs/dexterous_grasp/config/unittest_assets/understanding/mp3/start_recording.mp3"),
    stop_recording_audio=os.path.join( "edgs/dexterous_grasp/config/unittest_assets/understanding/mp3/start.mp3")
)

command_token = "INSERT INSTRUCTION HERE"

request_info = RequestInfo(
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    },
    single_en_prompt=
       """
            ## Introduction:
            You are the semantic understanding module of a robot. Your task is to analyze an image and identify the object that best matches the user's description, focusing only on objects located on a black tablecloth. The description must be compatible with Grounded SAM2.
            ## Rules:
            1. **Filter**: Exclude action-related information. Describe only the object's characteristics.
            2. **Object Selection**: If multiple objects match, return the one that fits best.
            3. **Diversity**: Ensure variety in descriptions for different objects.
            4. **Detail**: Provide a consistent, single-sentence description (without punctuation) of the object's features (e.g., color, texture, shape) without mentioning its location or the black tablecloth.
            6. **Compatibility**: Ensure the description works for Grounded SAM2, focusing on object features.

            ## Restraints:
            - **Black Tablecloth Focus!!!**: Only return an object if it is on the black tablecloth. Otherwise, return "None"
            - **Unclear Input!!!**: If you cannot determine which object from the user's command please return "None"
            - **Output: The response must either be a valid target object description or "None"

            ## Examples:
            ```
            1. **User instruction**: "帮我拿一下苹果."
               **Image context**: A black tablecloth with a red apple and a banana on it.
               **Output**: "A round shiny red apple"

            2. **User instruction**: "帮我拿一下书本."
               **Image context**: A table with a red apple, a banana, and a cup, book is outside of a black tablecloth.
               **Output**: "None"

            3. **User instruction**: "今天天气怎么样"
               **Output**: "None"
            ```

            ## Query
            **User instruction**: "{}"
        """.format(command_token),
    model="chatgpt-4o-latest",
    api_url="https://az.gptplus5.com/v1/chat/completions"
)

iflytek_config = IflytekConfig(
    app_id="51c33305",
    msc_lib_path=file_paths.msc_lib,
    audio_file=file_paths.audio_file,
    start_recording_audio_path=file_paths.start_recording_audio,
    stop_recording_audio_path=file_paths.stop_recording_audio,
    record_seconds=7,
    sample_rate=16000
)

doubao_config = DoubaoConfig(
    # 配置信息
    api_key = "",
    model_config = {
        "model": "doubao-1-5-vision-pro-32k-250115",
        "max_tokens": 200,
        "temperature": 0.7,
        "stream": False,
        "stop": ["结束"]
    },
    single_en_prompt=
       """
            ## Introduction:
            You are the semantic understanding module of a robot. Your task is to analyze an image and identify the object that best matches the user's description, focusing only on objects located on a black tablecloth. The description must be compatible with Grounded SAM2.
            ## Rules:
            1. **Filter**: Exclude action-related information. Describe only the object's characteristics.
            2. **Object Selection**: If multiple objects match, return the one that fits best.
            3. **Diversity**: Ensure variety in descriptions for different objects.
            4. **Detail**: Provide a consistent, single-sentence description (without punctuation) of the object's features (e.g., color, texture, shape) without mentioning its location or the black tablecloth.
            6. **Compatibility**: Ensure the description works for Grounded SAM2, focusing on object features.

            ## Restraints:
            - **Black Tablecloth Focus!!!**: Only return an object if it is on the black tablecloth. Otherwise, return "None"
            - **Unclear Input!!!**: If you cannot determine which object from the user's command please return "None"
            - **Output: The response must either be a valid target object description or "None"

            ## Examples:
            ```
            1. **User instruction**: "帮我拿一下苹果."
               **Image context**: A black tablecloth with a red apple and a banana on it.
               **Output**: "A round shiny red apple"

            2. **User instruction**: "帮我拿一下书本."
               **Image context**: A table with a red apple, a banana, and a cup, book is outside of a black tablecloth.
               **Output**: "None"

            3. **User instruction**: "今天天气怎么样"
               **Output**: "None"
            ```

            ## Query
            **User instruction**: "{}"
        """.format(command_token),
)