import pyaudio
import wave
import threading
import keyboard
import time
import tempfile
from dataclasses import dataclass
from file_registery import FileRegistery

@dataclass
class RecorderSettings():
    """
        音频录制设置类

        保存一些基本参数, 向用户端暴露接口, 允许用户进行部分调整

        参数:
            chunk(int): 块大小(将多少样本点作为一个块进行采集)
            format(int): 音频数据格式
            channels(int): 通道数(1为单声道, 2为双声道)
            rate(int): 采样率(每秒采集的样本点个数)
            auto_save_on_device_loss(bool): 设备突然缺失时是否自动保存
    """

    chunk: int = 1024
    format: int = pyaudio.paInt16
    channels: int = 1
    rate: int = 44100
    auto_save_on_device_loss: bool = True

class Recorder():
    """
        音频录制类

        主要实现音频的录制和缓存, 存储格式为.wav

        参数:
            recorder_settings(RecorderSettings): 音频录制设置
    """

    def __init__(self, recorder_settings: RecorderSettings, file_registery: FileRegistery) -> None:
        self.settings = recorder_settings
        self.CHUNK = self.settings.chunk
        self.FORMAT = self.settings.format
        self.CHANNELS = self.settings.channels
        self.RATE = self.settings.rate

        self.p = None                  # PyAudio对象
        self.recording = False         # 记录是否正在录音，用于自定义快捷键打断
        self.frames = []               # 用于存储块数据
        self.device_ready = False      # 检测是否有麦克风

        self.pause_event = threading.Event()    # 创建暂停事件
        self.pause_event.set()                  # 初始状态为运行

        self.file_registery = file_registery

    def pause_recording(self) -> None:
        """暂停录音"""
        self.pause_event.clear()
        print('已暂停录音')

    def resume_recording(self) -> None:
        """恢复录音"""
        self.pause_event.set()
        print('已恢复录音')

    def get_recording(self) -> None:
        """
            开始录音

            将录音数据存储到self.frames中
            
            无参数, 无返回值
        """

        self.recording = True
        
        # 主循环，用于处理设备中途缺失和插入的情况
        while self.recording:
            try:
                # 创建流通道，初始时可能会出现设备缺失的情况，等待设备接入
                stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
            except (OSError, AttributeError):
                self.device_ready = False
                self.wait_for_device()
                continue

            print('可以开始录音了')

            # 循环接收数据，每次从流中选出一个块的大小的数据存入frames中，在此过程中，可能会因为设备缺失而抛出异常
            try:
                while self.recording and self.device_ready:

                    #等待暂停事件运行
                    self.pause_event.wait()

                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                    self.frames.append(data)
            except OSError as e:

                #设备突然缺失时是否保存当前音频
                if self.settings.auto_save_on_device_loss:
                    self.save_recording()

                self.device_ready = False
                self.wait_for_device()
                continue

            stream.stop_stream()
            stream.close()
    
    def save_recording(self) -> None:
        """
            保存录音数据

            将self.frames中的数据写入到临时文件中

            无参数，无返回值
        """

        if self.frames:
            print('正在保存')

            # 使用临时文件缓存录音
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.wav',
                prefix='recording_',
                dir='.',                # 保存在当前目录下
                delete=False            # close时不自动删除文件
            )

            wf = wave.open(temp_file.name, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.frames))
            wf.close()

            temp_file.close()

            self.frames = []        # 清空数据，防止下次录音时重复写入

    def wait_for_device(self) -> None:
        """
            等待设备接入

            检测设备是否接入, 如果未接入, 则等待1秒后再次检测

            无参数，无返回值
        """

        while not self.device_ready and self.recording:
            try:
                # 每次循环时创建一个新的PyAudio对象用于检测设备状况
                print("正在检测设备...")
                self.p = pyaudio.PyAudio()

                # 采用open的方式进行尝试，因为会稳定报出OSError错误
                test_stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
                test_stream.close()
                self.device_ready = True
                print("设备检测成功")
            except OSError:
                print("未检测到麦克风", end='\n\n')
                self.device_ready = False
            finally:

                # 如果没有检测到设备，关闭PyAudio对象，防止内存泄漏
                if self.p and not self.device_ready:
                    self.p.terminate()

                time.sleep(1)

    def stop_recording(self) -> None:
        """停止录音"""
        self.recording = False

    def close(self) -> None:
        """关闭"""
        self.p.terminate()

if __name__ == '__main__':
    recorder_settings = RecorderSettings()
    recorder = Recorder(recorder_settings)

    # 添加快捷键
    keyboard.add_hotkey('ctrl+a+b', recorder.stop_recording)             # 停止录音
    keyboard.add_hotkey('shift+a+b+c', recorder.pause_recording)         # 暂停录音
    keyboard.add_hotkey('shift+b+c+d', recorder.resume_recording)        # 继续录音

    # 创建进程，防止阻塞
    thread_record = threading.Thread(target=recorder.get_recording)
    thread_record.start()
    thread_record.join()

    recorder.save_recording()

    recorder.close()

    # 消除快捷键
    keyboard.remove_hotkey('ctrl+a+b')
    keyboard.remove_hotkey('shift+a+b+c')
    keyboard.remove_hotkey('shift+b+c+d')