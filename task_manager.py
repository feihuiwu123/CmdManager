import threading
import time
import subprocess
from queue import Queue
import platform

class TaskManager:
    def __init__(self, data_manager, language_manager):
        self.data_manager = data_manager
        self.language_manager = language_manager
        self.tasks = self.data_manager.load_tasks()
        self.running_tasks = set()
        self.task_queue = Queue()
        self.task_lock = threading.Lock()
        self.pause_between_tasks = False
        self.platform = platform.system().lower()

    def add_task(self, name, command):
        """添加新任务"""
        if name in self.tasks:
            return False
        
        task = {
            "name": name,
            "command": command
        }
        self.tasks[name] = task
        self.data_manager.save_tasks(self.tasks)
        return True

    def delete_task(self, name):
        """删除任务"""
        if name in self.tasks:
            del self.tasks[name]
            self.data_manager.save_tasks(self.tasks)

    def get_all_tasks(self):
        """获取所有任务"""
        return [task for task in self.tasks.values()]

    def get_task(self, name):
        """获取指定任务"""
        return self.tasks.get(name)

    def get_task_type(self, task_name):
        """获取任务类型"""
        task = self.tasks.get(task_name)
        if task:
            return "aggregate" if "&&" in task["command"] else "normal"
        return "normal"

    def update_task(self, name, task):
        """更新任务信息"""
        if name in self.tasks:
            self.tasks[name] = task
            self.data_manager.save_tasks(self.tasks)

    def run_task(self, task_name, status_callback, log_callback):
        """运行单个任务"""
        if task_name in self.running_tasks:
            log_callback(self.language_manager.get_text("messages.task_running").format(task_name))
            return

        task = self.tasks.get(task_name)
        if not task:
            log_callback(self.language_manager.get_text("messages.task_not_exist").format(task_name))
            return

        thread = threading.Thread(
            target=self._execute_task,
            args=(task, status_callback, log_callback)
        )
        thread.daemon = True
        thread.start()

    def run_multiple_tasks(self, task_names, status_callback, log_callback, pause_between=False):
        """运行多个任务"""
        self.pause_between_tasks = pause_between
        for task_name in task_names:
            if task_name not in self.tasks:
                log_callback(self.language_manager.get_text("messages.task_not_exist").format(task_name))
                continue

            self.task_queue.put(task_name)

        if not self.task_queue.empty():
            thread = threading.Thread(
                target=self._process_task_queue,
                args=(status_callback, log_callback)
            )
            thread.daemon = True
            thread.start()

    def _process_task_queue(self, status_callback, log_callback):
        """处理任务队列"""
        while not self.task_queue.empty():
            task_name = self.task_queue.get()
            task = self.tasks.get(task_name)
            if task:
                self._execute_task(task, status_callback, log_callback)
                if self.pause_between_tasks and not self.task_queue.empty():
                    log_callback(self.language_manager.get_text("messages.pause_3s"))
                    time.sleep(3)
            self.task_queue.task_done()

    def _execute_task(self, task, status_callback, log_callback):
        """执行任务"""
        task_name = task["name"]
        command = task["command"]

        with self.task_lock:
            if task_name in self.running_tasks:
                return
            self.running_tasks.add(task_name)
            # 添加初始状态回调
            status_callback(task_name, "task_status.waiting")

        try:
            # 更新为执行中状态
            status_callback(task_name, "task_status.running")
            log_callback(self.language_manager.get_text("messages.start_task").format(task_name))
            log_callback(self.language_manager.get_text("messages.execute_command").format(command))
            
            return_code = 0
            # 如果是聚合命令，分割并逐个执行
            if "&&" in command:
                commands = [cmd.strip() for cmd in command.split("&&")]
                for cmd in commands:
                    if not cmd:
                        continue
                    log_callback(f"执行子命令: {cmd}")
                    cmd_return_code = self._execute_single_command(cmd, log_callback)
                    if cmd_return_code != 0:
                        return_code = cmd_return_code
                        break
            else:
                return_code = self._execute_single_command(command, log_callback)

            # 根据返回码更新最终状态
            if return_code == 0:
                status_callback(task_name, "task_status.completed")
                log_callback(self.language_manager.get_text("messages.task_success").format(task_name))
            else:
                status_callback(task_name, "task_status.failed")
                log_callback(self.language_manager.get_text("messages.task_failed").format(task_name, return_code))

        except Exception as e:
            status_callback(task_name, "task_status.failed")
            log_callback(self.language_manager.get_text("messages.task_error").format(task_name, str(e)))

        finally:
            with self.task_lock:
                self.running_tasks.remove(task_name)

    def _execute_single_command(self, command, log_callback):
        """执行单个命令"""
        try:
            # 特殊处理pause命令
            if command.strip().lower().startswith('pause'):
                try:
                    # 提取暂停时间（秒数）
                    pause_time = int(command.strip().split()[1])
                    log_callback(f"暂停{pause_time}秒...")
                    time.sleep(pause_time)
                    return 0
                except (IndexError, ValueError):
                    # 如果没有指定时间或格式错误，默认暂停3秒
                    log_callback("暂停3秒...")
                    time.sleep(3)
                    return 0

            # 其他命令使用原有的处理逻辑
            shell = True if self.platform == "windows" else False
            process = subprocess.Popen(
                command,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )

            # 创建输出读取线程
            def read_output(pipe, callback_type):
                try:
                    for line in iter(pipe.readline, ''):
                        if line:
                            line = line.strip()
                            if line:
                                if callback_type == 'stdout':
                                    log_callback(line)
                                else:
                                    log_callback(self.language_manager.get_text("messages.error").format(line))
                except Exception as e:
                    log_callback(self.language_manager.get_text("messages.error").format(str(e)))

            stdout_thread = threading.Thread(target=read_output, args=(process.stdout, 'stdout'))
            stderr_thread = threading.Thread(target=read_output, args=(process.stderr, 'stderr'))
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()

            # 等待进程完成
            process.wait()
            stdout_thread.join()
            stderr_thread.join()

            return process.returncode

        except Exception as e:
            log_callback(self.language_manager.get_text("messages.error").format(str(e)))
            return -1