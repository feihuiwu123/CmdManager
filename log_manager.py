import os
from datetime import datetime

class LogManager:
    def __init__(self, log_file="execution.log", language_manager=None):
        self.log_file = log_file
        self.language_manager = language_manager
        self._ensure_log_file()

    def _ensure_log_file(self):
        """确保日志文件存在"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                if self.language_manager:
                    title = self.language_manager.get_text("log_title")
                    create_time = self.language_manager.get_text("messages.create_time")
                else:
                    title = "=== BAT Task Manager Log ==="
                    create_time = "Create Time"
                f.write(f"{title}\n{create_time}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    def write_log(self, message):
        """写入日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            if self.language_manager:
                print(self.language_manager.get_text("messages.write_log_failed").format(str(e)))

    def get_recent_logs(self, lines=100):
        """获取最近的日志记录"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = f.readlines()
                return logs[-lines:] if len(logs) > lines else logs
        except Exception as e:
            if self.language_manager:
                print(self.language_manager.get_text("messages.read_log_failed").format(str(e)))
            return []

    def clear_logs(self):
        """清空日志文件"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                if self.language_manager:
                    title = self.language_manager.get_text("log_title")
                    clear_time = self.language_manager.get_text("messages.clear_time")
                else:
                    title = "=== BAT Task Manager Log ==="
                    clear_time = "Clear Time"
                f.write(f"{title}\n{clear_time}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        except Exception as e:
            if self.language_manager:
                print(self.language_manager.get_text("messages.clear_log_failed").format(str(e)))