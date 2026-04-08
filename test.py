import numpy as np
import pyaudio

p = pyaudio.PyAudio()

device_count = p.get_device_count()

for i in range(device_count):
    device_info = p.get_device_info_by_index(i)

    if device_info['maxInputChannels'] > 0: #输出所有有通道的设备的相关信息
        print(f'设备索引:{i}')
        print(f'设备名称:{device_info["name"]}')
        print(f'设备输入通道数:{device_info["maxInputChannels"]}')
        print(f'设备输出通道数:{device_info["maxOutputChannels"]}')
        print(f'设备默认采样率:{device_info["defaultSampleRate"]}')
        print(f'设备默认输入延迟:{device_info["defaultLowInputLatency"]}')
        print('-' * 50, end='\n\n')

#获取默认设备的相关信息
try:
    default_info = p.get_default_input_device_info()
    print(f'默认输入设备索引:{default_info["index"]}')
    print(f'默认输入设备名称:{default_info["name"]}')
except:
    print("没有默认输入设备")