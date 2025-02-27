import panda_py
from pynput import keyboard

# 机器人参数
hostname = "172.16.0.2"
username = "franka"
password = "franka123"

# 初始化机器人
desk = panda_py.Desk(hostname, username, password)
desk.unlock()
desk.activate_fci()
panda = panda_py.Panda(hostname)

p = panda.get_state().q
print(p)

# q = [-0.0005593634298675808, -0.2931886632241168, 0.002818433728889926, -2.5869446936824865, 0.0036498803788848613, 2.273655532757441, 0.7796194068846911]
# panda.move_to_joint_position(q)
# panda.move_to_start()
# p2 = panda.get_state().q
# print (p2)
