import time
import pygame
import numpy as np


def object_position_cam2base(target_x_3d, target_y_3d, target_z_3d, camera2base_rotation, camera2base_translation):
    object_position_camera = np.array([target_x_3d, target_y_3d, target_z_3d])
    object_position_base = camera2base_rotation @ object_position_camera + camera2base_translation
    try:
        x_base, y_base, z_base = object_position_base[0][0], object_position_base[0][1], \
        object_position_base[0][2]
    except IndexError as e:
        x_base, y_base, z_base = object_position_base[0], object_position_base[1], object_position_base[2]
    return x_base, y_base, z_base

def make_radian_in_range(radian):
    """Ensure the radian is within the range (-π/2, π/2]."""
    while radian <= -np.pi / 2 or radian > np.pi / 2:
        radian += np.pi if radian <= -np.pi / 2 else -np.pi
    return radian

def play_audio_file(audio_file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.05)
    pygame.mixer.music.stop()