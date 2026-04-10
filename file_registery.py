import time
import threading
import os
from dataclasses import dataclass

@dataclass
class FileInfo():
    """
    待注册文件的相关信息

    参数:
        file_name(str): 文件名
        file_path(str): 文件路径
        file_type(str): 文件类型
        file_size(str): 文件大小(字节)
        create_time(float): 文件创建时间(无需输入)
        expire_interval(float): 文件过期时间(秒)
    """

    file_name: str
    file_path: str
    file_type: str
    file_size: int
    create_time: float = time.time()
    expire_interval: float

class FileRegistery():
    """
        文件注册表

        主要实现文件的注册和删除
    """

    def __init__(self, auto_cleanup_expire_interval: int = 300, search_path: str = '.') -> None:
        """
            初始化

            参数：
                auto_cleanup_expire_interval(int): 自动清理过期文件的时间间隔(秒)
                search_path(str): 搜索路径

            无返回值
        """

        self.search_path = search_path
        self.auto_cleanup_expired_interval = auto_cleanup_expire_interval

        self.files = {}                      # 存储所有注册的文件
        self.auto_cleanup_expired = False    # 自动清理过期文件
        self.cleanup_thread = None           # 清理线程
        self.iter_index = 0                  # 迭代索引

        self.cleanup_event = threading.Event()

    def __iter__(self):
        pass

    def __next__(self):
        pass

    def set_auto_cleanup_interval(self, interval: int) -> bool:
        """
            设置自动清理过期文件的间隔

            参数:
                interval(int): 间隔(秒)

            返回值:
                bool: 设置是否成功
        """

        if interval > 0:
            self.auto_cleanup_expired_interval = interval
            return True
        else:
            print('间隔必须大于0')
            return False

    def register(self, file_name: str, file_path: str, file_type: str, file_size: int, expire_interval: int = 300) -> bool:
        """
            注册单个文件

            参数:
                file_name(str): 文件名
                file_path(str): 文件路径
                file_type(str): 文件类型
                file_size(int): 文件大小(字节)
                expire_interval(int): 文件过期时间(秒)

            返回值:
                bool: 注册是否成功
        """

        try:
            self.files[file_name] = FileInfo(file_name, file_path, file_type, file_size, expire_interval=expire_interval)
            return True
        except Exception as e:
            print(f'文件注册失败，失败原因: {e}')
            return False
        
    def unregister(self, file_name: str) -> bool:
        """
            注销单个文件

            参数:
                file_name(str): 文件名

            返回值:
                bool: 注销是否成功
        """
        
        try:

            # 判断文件是否存在，先删除文件
            if os.path.exists(self.files[file_name].file_path):
                os.unlink(self.files[file_name].file_path)

            # 从字典中删除
            del self.files[file_name]

            return True
        except Exception as e:
            print(f'文件删除失败，失败原因: {e}')
            return False
        
    def cleanup(self) -> None:
        """注销文件"""
        for file_name, file_info in list(self.files.items()):
            if file_info.create_time + file_info.expire_interval < time.time():
                self.unregister(file_name)
    
    def auto_cleanup(self) -> None:
        """自动清理过期文件"""
        while self.auto_cleanup_expired:
            self.cleanup_event.wait(timeout=self.auto_cleanup_expired_interval)
            self.cleanup_event.clear()

            self.cleanup()

    def start_cleanup(self) -> None:
        """启动自动清理过期文件"""
        if not self.cleanup_thread:
            self.auto_cleanup_expired = True
            self.cleanup_thread = threading.Thread(target=self.auto_cleanup)
            self.cleanup_thread.start()

    def stop_cleanup(self) -> None:
        """停止自动清理过期文件"""
        self.auto_cleanup_expired = False
        self.cleanup_event.set()

        if self.cleanup_thread:
            self.cleanup_thread.join()

    def close(self) -> None:
        """关闭文件注册表"""
        self.stop_cleanup()
        self.files = {}

    def start(self) -> None:
        """启动文件注册表"""
        self.register_dictionary()
        self.start_cleanup()

    def register_dictionary(self, path: str = None) -> None:
        """注册指定目录下的所有文件"""
        pass
