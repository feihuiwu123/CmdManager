import json
import os
import sys

class LanguageManager:
    def __init__(self, language_file="language.json"):
        self.language_file = language_file
        self.current_language = "zh_CN"  # 默认使用中文
        self.languages = {}
        self.load_languages()

    def load_languages(self):
        """加载语言配置文件"""
        try:
            # 获取可执行文件所在目录
            if getattr(sys, 'frozen', False):
                # 如果是打包后的环境
                base_path = sys._MEIPASS
            else:
                # 如果是开发环境
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            language_path = os.path.join(base_path, self.language_file)
            if os.path.exists(language_path):
                with open(language_path, 'r', encoding='utf-8') as f:
                    self.languages = json.load(f)
        except Exception as e:
            print(f"加载语言配置失败: {str(e)}")
            self.languages = {}

    def get_text(self, key, default=""):
        """获取指定键的文本"""
        try:
            # 支持多级键，如 'task_list.name'
            keys = key.split('.')
            value = self.languages.get(self.current_language, {})
            for k in keys:
                value = value.get(k, default)
            return value
        except Exception:
            return default

    def switch_language(self, language_code):
        """切换语言"""
        if language_code in self.languages:
            self.current_language = language_code
            return True
        return False

    def get_available_languages(self):
        """获取可用的语言列表"""
        return list(self.languages.keys())