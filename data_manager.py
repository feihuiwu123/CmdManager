import json
import os

class DataManager:
    def __init__(self, tasks_file="tasks.json", language_manager=None):
        self.tasks_file = tasks_file
        self.language_manager = language_manager
        self._ensure_tasks_file()

    def _ensure_tasks_file(self):
        """确保任务文件存在"""
        if not os.path.exists(self.tasks_file):
            self.save_tasks({})

    def load_tasks(self):
        """从文件加载任务列表"""
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            if self.language_manager:
                print(self.language_manager.get_text("messages.load_failed").format(str(e)))
            return {}

    def save_tasks(self, tasks):
        """保存任务列表到文件"""
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=4)
        except Exception as e:
            if self.language_manager:
                print(self.language_manager.get_text("messages.save_failed").format(str(e)))

    def export_tasks(self, file_path):
        """导出任务列表到指定文件"""
        try:
            tasks = self.load_tasks()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            if self.language_manager:
                print(self.language_manager.get_text("messages.export_failed").format(str(e)))
            return False

    def import_tasks(self, file_path):
        """从指定文件导入任务列表"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            self.save_tasks(tasks)
            return True
        except Exception as e:
            if self.language_manager:
                print(self.language_manager.get_text("messages.import_failed").format(str(e)))
            return False