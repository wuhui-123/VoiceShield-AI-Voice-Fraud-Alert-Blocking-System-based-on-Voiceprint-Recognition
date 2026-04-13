import tempfile
import shutil
import os
import stat
from pathlib import Path
from pydub import AudioSegment
from temp_file_registery import TempFileRegistery

class AudioProcess():

    def __init__(self, temp_file_registery: TempFileRegistery) -> None:
        self.temp_file_registery = temp_file_registery

    def convert_to_wav(self, file_name: str) -> None:
        file_path = self.temp_file_registery.files[file_name].file_path

        with open(file_path, 'rb') as f:
            audio = AudioSegment.from_file(f)

        audio = audio.set_channels(1).set_frame_rate(16000)

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
            audio.export(temp_path, format="wav")
        
        new_path = Path(file_path).with_suffix(".wav")

        # 删除旧文件前，先移除只读属性
        if os.path.exists(file_path):
            os.chmod(file_path, stat.S_IWRITE)

        self.temp_file_registery.unregister(file_name)
        self.temp_file_registery.register(
                                        file_name=new_path.name,
                                        file_path=new_path,
                                        file_size=0,
                                        file_type='wav',
                                        expire_interval=300
                                    )

        shutil.move(temp_path, new_path)

if __name__ == '__main__':
    temp_file_registery = TempFileRegistery(100)
    temp_file_registery.register(
                                file_name=r'云音乐@7105217@STYX HELIX@Myth&Roid.mp3', 
                                file_path=r'D:\python\VoiceShield-AI-Voice-Fraud-Alert-Blocking-System-based-on-Voiceprint-Recognition-main' \
                                r'\temp_files\云音乐@7105217@STYX HELIX@Myth&Roid.mp3',
                                file_size=0,
                                file_type='mp3',
                                expire_interval=300
                            )
    
    audio_process = AudioProcess(temp_file_registery)
    audio_process.convert_to_wav('云音乐@7105217@STYX HELIX@Myth&Roid.mp3')

    audio = AudioSegment.from_file(r'D:\python\VoiceShield-AI-Voice-Fraud-Alert-Blocking-System-based-on-Voiceprint-Recognition-main' \
                                r'\temp_files\云音乐@7105217@STYX HELIX@Myth&Roid.wav')
    print(f"声道数: {audio.channels}")
    print(f"采样率: {audio.frame_rate}")
    print(f"时长: {len(audio)/1000} 秒")