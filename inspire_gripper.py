#!/usr/bin/env python3

class inspire_gripper():
    def __init__(self) -> None:
        pass

    def dec_to_hex_string(self,dec_num:int,lenth=2):
        # 将10进制数转为16进制的字符串表示
        if lenth == 2:
            hex_str = hex(dec_num)[2:].zfill(4).upper()  # 转为16进制，高位补0，转为大写（此时低位在左，高位在右）
            byte1 = hex_str[2:]  # 取高8位
            byte2 = hex_str[:2]  # 取低8位
            return byte1 + ' ' + byte2  # 此时高位在左，低位在右
        elif lenth == 1:
            hex_str = hex(dec_num)[2:].zfill(2).upper()  # 转为16进制，高位补0，转为大写
            return hex_str

    def hex_string_sum(self,hex_string:str,only_low=True):
        # 输入含16进制元素的字符串，返回各元素相加后的8位16进制数，高位自动补0
        hex_list = hex_string.split()  # 将字符串按空格分割成列表
        hex_sum = 0
        for hex_num in hex_list:
            hex_sum += int(hex_num, 16)  # 将每个16进制数转换成10进制数并相加
        if only_low: hex_sum = hex_sum & 0xFF
        return hex(hex_sum)[2:].zfill(2).upper()

    def ToSerial(cls,data_cmd,port_vpid:str,baudrate=115200,bytesize=8,parity='N',stopbits=1,timeout=None,find=False,from_hex=False):
        # 通过串口发送有关数据；port_pid可以是端口号（Linux下比如是'/dev/ttyUSB0',Windows下比如是'COM8'），也可以是设备的vid和pid信息结合；
        # 如vid为6790，PID为29987，则写为'6790_29987'；
        # find=true时查找完直接函数直接返回；
        if not hasattr(cls.ToSerial,f'{port_vpid}'):
            from serial import Serial  # 要装pyserial
            import serial.tools.list_ports
            import atexit
            if find is True:
                port_list = list(serial.tools.list_ports.comports())
                device_list = [port.device for port in port_list]
                vid_list = [port.vid for port in port_list]
                pid_list = [port.pid for port in port_list]
                description_list = [port.description for port in port_list]
                print('共检测到这些设备：',device_list)
                print('设备的VID为：',vid_list)
                print('设备的PID为：',pid_list)
                print('设备的descriptio为：',description_list)
                print(type(pid_list[0]))
                return
            #继承串口类
            class MySerial(Serial):
                # 继承串口类，实现了可以在初始化时不用配置任何信息，通过新增加的comset函数进行配置，然后通过connect进行鲁棒的连接。
                # 初始化和comset可以都不指定端口号，而是在connect时再指定。
                # 配置串口参数（可以不包括端口号）
                def ComSet(self, baudrate, bytesize, parity, stopbits, timeout,port=None):
                    d={'baudrate': baudrate, 'bytesize': bytesize, 'parity':parity, 'stopbits':stopbits, 'timeout': timeout}
                    self.apply_settings(d)
                    self.port = port
                # 选择端口号并尝试连接
                def Connect(self,rs_port=None):
                    if self.is_open:
                        print(f'已成功连接串口{self.port}')
                        return
                    if rs_port is None:
                        if self.port is not None:
                            rs_port = self.port
                        else: raise Exception('缺少串口号，请检查串口配置')
                    # 没连接到串口则一直连接
                    while True:
                        port_list = list(serial.tools.list_ports.comports())
                        if len(port_list) == 0: exit("没有可用串口")
                        else:
                            port_list = [port.device for port in port_list]
                            port_list = ";".join(list(map(str,port_list)))  # 将字符串列表转换为一整个字符串
                            if rs_port in port_list:  # 判断选用的端口是否在其中
                                self.port = rs_port
                                self.open() # 开启串口
                                if self.is_open:
                                    print(f"成功连接串口{rs_port}")
                                    return
                                else: print(f"已找到目标端口号{rs_port}，但无法连接")
                            else: print("未找到目标端口号{}。找到的所有端口为：{}".format(rs_port,port_list))
            # 串口初始化与连接
            if '_' in port_vpid:
                vid, pid = port_vpid.split('_')
                port_list = list(serial.tools.list_ports.comports())
                device_list = [port.device for port in port_list]
                vid_list = [port.vid for port in port_list]
                pid_list = [port.pid for port in port_list]
                if (int(pid) in pid_list) and (int(vid) in vid_list):
                    port = device_list[pid_list.index(int(pid))]
                else: exit('错误：pid和vid与现连接所有设备不匹配')
            ser = MySerial(port,baudrate,bytesize,parity,stopbits,timeout)
            # ser.Connect()
            cls.ToSerial.__dict__[f'{port_vpid}'] = ser
            atexit.register(ser.close)  # 程序退出时关闭串口
        # 发送数据
        if data_cmd is not None:
            if from_hex: data_cmd = bytes.fromhex(data_cmd)
            cls.ToSerial.__dict__[f'{port_vpid}'].write(data_cmd)

    def two_finger_gripper(self,pp,sleep_time=0,speed=500,force=100,always=False,show_state=True,set_gap=None):
        # 二指夹爪（因时科技）常用控制接口：
        # 1抓取，0释放；sleep_time是执行动作后的延时
        # speed是从1 - 1000 的无量纲速度系数
        # force是从50 - 1000 单位为g(克)
        # always为True表示持续施加给定的夹取力
        # seek_pos为None时默认张开和闭合的开口度没有限制，不为None时取值为0-70mm。如果当前开口度小于设定开口度，以设定速度松开直到开口度达到目标开口度后停止运动；
        #     如果当前开口度大于设定开口度，以设定速度和力控阈值去夹取，当夹持力超过设定的力控阈值后，或者开口度达到目标开口度后停止运动。
        # set_gap为None时不重新设置夹爪的最大和最小开口参数，为一个二元组时为(min,max)值。
        VID_PID = '6790_29987'  # 因时二指夹爪的vid和pid（至少目前买的批次是这样）
        HEAD = 'EB 90 '
        if set_gap is not None:
            set_gap = list(set_gap)
            if set_gap[0] > 1000: set_gap[0] = 1000
            elif set_gap[0] < 0: set_gap[0] = 0
            if set_gap[1] > 1000: set_gap[1] = 1000
            elif set_gap[1] < 0: set_gap[1] = 0                
            min_gap=self.dec_to_hex_string(set_gap[0])
            max_gap=self.dec_to_hex_string(set_gap[1])
            cmd_temp = '01 05 12 '+max_gap+' '+min_gap
            SUM = self.hex_string_sum(cmd_temp)
            SET_GAP_CMD = HEAD+cmd_temp+' '+SUM
            self.ToSerial(SET_GAP_CMD,VID_PID,from_hex=True)
        if pp == 1:
            self.two_finger_gripper.__dict__['state'] = 'closed'
            if show_state: print("夹爪闭合")
            if speed > 1000: speed = 1000
            elif speed < 1: speed = 1
            if force > 1000: force = 1000
            elif force < 50: force = 50
            speed_str = self.dec_to_hex_string(speed)
            force_str = self.dec_to_hex_string(force)
            if not always:
                cmd_temp = '01 05 10 '+speed_str+' '+force_str
            else:
                cmd_temp = '01 05 18 '+speed_str+' '+force_str
            SUM = self.hex_string_sum(cmd_temp)
            CLOSE_CMD = HEAD+cmd_temp+' '+SUM
            self.ToSerial(CLOSE_CMD,VID_PID,from_hex=True)
        else:
            self.two_finger_gripper.__dict__['state'] = 'opened'
            if show_state: print("夹爪张开")
            speed_str = self.dec_to_hex_string(speed)
            cmd_temp = '01 03 11 '+speed_str
            SUM = self.hex_string_sum(cmd_temp)
            OPEN_CMD = HEAD+cmd_temp+' '+SUM
            self.ToSerial(OPEN_CMD,VID_PID,from_hex=True)
        # 提示：根据因时的相关协议说明，两次控制指令发送时间间隔最好至少5ms

if __name__ == '__main__':
    a = inspire_gripper()
    a.two_finger_gripper(pp=0)