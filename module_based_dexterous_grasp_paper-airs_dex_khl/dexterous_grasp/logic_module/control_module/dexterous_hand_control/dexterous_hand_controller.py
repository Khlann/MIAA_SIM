import time
import serial
from dexterous_grasp.logger_module import LoggerValidator


class DexterousHandController(LoggerValidator):
    def __init__(self, hand_motion_params, hand_device_params, logger_manager=None):
        super().__init__(logger_manager)
        self.speedSet = hand_motion_params.speedSet
        self.angleSet_execute1 = hand_motion_params.angleSet_execute1
        self.angleSet_execute2 = hand_motion_params.angleSet_execute2
        self.forceSet = hand_motion_params.forceSet
        self.tinyforceSet = hand_motion_params.tinyforceSet
        self.angleSet_abort = hand_motion_params.angleSet_abort
        self.regdict = hand_device_params.regdict
        self.port = hand_device_params.port
        self.baudrate = hand_device_params.baudrate
        self.ser = self.open_serial(self.port, self.baudrate)
        self.abort_grasp()
        
    def open_serial(self, port, baudrate):
        ser = serial.Serial()
        ser.port = port
        ser.baudrate = baudrate
        ser.open()
        return ser
    
    def write_register(self, id, add, num, val):
        bytes = [0xEB, 0x90]  # 通信帧头
        bytes.append(id)      # 设备ID
        bytes.append(num + 3) # 数据帧长度，包括命令字、地址、数据等
        bytes.append(0x12)    # 写寄存器的命令字
        bytes.append(add & 0xFF)  # 寄存器地址低字节
        bytes.append((add >> 8) & 0xFF)  # 寄存器地址高字节
        for i in range(num):
            bytes.append(val[i])
        checksum = 0x00
        for i in range(2, len(bytes)):
            checksum += bytes[i]
        checksum &= 0xFF
        bytes.append(checksum)
        self.ser.write(bytes)
        time.sleep(0.01)
        self.ser.read_all()
           
    def write6(self, id, str, val):
        if str in ['angleSet', 'forceSet', 'speedSet']:
            val_reg = []
            for i in range(6):
                val_reg.append(val[i] & 0xFF)
                val_reg.append((val[i] >> 8) & 0xFF)
            self.write_register(id, self.regdict[str], 12, val_reg)
        else:
            self.logger_manager.logger.error('函数调用错误，正确方式：str的值为\'angleSet\'/\'forceSet\'/\'speedSet\'，val为长度为6的list，值为0~1000，允许使用-1作为占位符')

    def execute_grasp(self):# 抓取
        time.sleep(0.2)
        # Implementation for executing the grasp based on the planned command
        self.write6(1, 'speedSet', self.speedSet)# 自定义灵巧手抓取动作：设置速度并实现小拇指和大拇指同时弯曲
        time.sleep(0.01)
        
        self.write6(1, 'angleSet', self.angleSet_execute1)# 设置小拇指和大拇指的关节角度
        time.sleep(0.25)

        self.write6(1, 'angleSet', self.angleSet_execute2)# 设置小拇指和大拇指的关节角度
        time.sleep(0.5)

        self.logger_manager.logger.info("自定义灵巧手抓取动作完成")

    def execute_regrasp(self):# 抓取
        time.sleep(0.925)
        # Implementation for executing the grasp based on the planned command
        self.write6(1, 'speedSet', self.speedSet)
        self.write6(1, 'forceSet', self.tinyforceSet)
        self.write6(1, 'angleSet', self.angleSet_execute2)# 设置小拇指和大拇指的关节角度
        self.logger_manager.logger.info("自定义灵巧手抓取动作完成")
    
    def abort_grasp(self):# 松开
        # Implementation for executing the grasp based on the planned command
        self.write6(1, 'speedSet', self.speedSet)  
        time.sleep(0.01)
        self.write6(1, 'forceSet', self.forceSet)
        time.sleep(0.01)
        self.write6(1, 'angleSet', self.angleSet_abort)  
        time.sleep(0.01)
