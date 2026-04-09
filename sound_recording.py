import pyaudio
import wave
import threading
import keyboard

class Recorder():
    """
        音频录制类

        主要实现音频的录制和缓存, 存储格式为.wav

        参数:
            chunk(int): 块大小(将多少样本点作为一个块进行采集)
            format(int): 音频数据格式
            channels(int): 通道数(1为单声道, 2为双声道)
            rate(int): 采样率(每秒采集的样本点个数)
    """

    def __init__(self, chunk: int = 1024, format: int = pyaudio.paInt16, channels: int = 1, rate: int = 44100) -> None:
        self.CHUNK = chunk
        self.FORMAT = format
        self.CHANNELS = channels
        self.RATE = rate
        self.p = pyaudio.PyAudio()     #PyAudio对象
        self.recording = False         #记录是否正在录音，用于自定义快捷键打断
        self.frames = []               #用于存储块数据

    def get_recording(self) -> None:
        """
            开始录音

            将录音数据存储到self.frames中
            
            无参数, 无返回值
        """

        self.recording = True

        try:
            stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        
        #异常处理(未完成)
        except OSError as e:
            return

        #循环接收数据，即使录音无内容也不会主动停止
        while self.recording:
            data = stream.read(self.CHUNK, exception_on_overflow=False)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()
    
    def save_recording(self) -> None:
        """
            保存录音数据

            将self.frames中的数据写入到recording.wav文件中

            无参数，无返回值
        """

        if self.frames:
            wf = wave.open("recording.wav", 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            self.frames = []        #清空数据，防止下次录音时重复写入

    def stop_recording(self) -> None:
        """停止录音"""
        self.recording = False

    def close(self) -> None:
        """关闭"""
        self.p.terminate()

if __name__ == '__main__':
    recorder = Recorder()

    #添加快捷键
    keyboard.add_hotkey('ctrl+a+b', recorder.stop_recording)

    #创建进程，防止阻塞
    thread_record = threading.Thread(target=recorder.get_recording)
    thread_record.start()
    thread_record.join()

    recorder.save_recording()

    recorder.close()

    #消除快捷键
    keyboard.remove_hotkey('ctrl+a+b')