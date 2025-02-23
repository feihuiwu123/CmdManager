import json
import os

class LanguageManager:
    def __init__(self, language_file="language.json"):
        self.language_file = language_file
        self.current_language = "zh_CN"  # 默认使用中文
        self.languages = {}
        self.load_languages()

    def load_languages(self):
        """加载语言配置文件"""
        try:
            if os.path.exists(self.language_file):
                with open(self.language_file, 'r', encoding='utf-8') as f:
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