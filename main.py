import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from task_manager import TaskManager
from log_manager import LogManager
from data_manager import DataManager
from language_manager import LanguageManager

class BatTaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.version = "0.0.1"  # 添加版本号
        self.language_manager = LanguageManager()
        self.root.title(f"{self.language_manager.get_text('title')} v{self.version}")
        self.root.geometry("800x600")

        # 初始化管理器
        self.data_manager = DataManager(language_manager=self.language_manager)
        self.task_manager = TaskManager(self.data_manager, self.language_manager)
        self.log_manager = LogManager(language_manager=self.language_manager)

        # 创建主界面
        self.create_widgets()
        
        # 加载已保存的任务
        self.load_tasks()

    def create_widgets(self):
        # 创建顶部菜单栏
        menu_frame = ttk.Frame(self.root)
        menu_frame.pack(fill=tk.X, padx=3, pady=2)

        # 隐藏语言选择，默认使用中文
        self.language_var = tk.StringVar(value="zh_CN")
        
        # 创建左右分栏
        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3, pady=3)

        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=3, pady=3)

        # 左侧：任务管理区域
        task_frame = ttk.Frame(left_frame)
        task_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # 区域1：任务添加区域
        add_frame = ttk.Frame(task_frame)
        add_frame.pack(fill=tk.X, padx=2, pady=2)

        self.task_name_label = ttk.Label(add_frame, text=self.language_manager.get_text("task_name"))
        self.task_name_label.pack(side=tk.LEFT, padx=5)
        self.task_name_entry = ttk.Entry(add_frame)
        self.task_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.add_task_button = ttk.Button(add_frame, text=self.language_manager.get_text("add_task"), command=self.add_task)
        self.add_task_button.pack(side=tk.LEFT, padx=5)

        # BAT指令输入区域
        cmd_frame = ttk.Frame(task_frame)
        cmd_frame.pack(fill=tk.X, padx=2, pady=2)
        self.bat_command_label = ttk.Label(cmd_frame, text=self.language_manager.get_text("bat_command"))
        self.bat_command_label.pack(side=tk.LEFT, padx=5)
        self.bat_command_entry = tk.Text(cmd_frame, height=3)
        self.bat_command_entry.pack(fill=tk.X, expand=True, padx=5)

        # 区域2：聚合指令区域
        aggregate_frame = ttk.Frame(task_frame)
        aggregate_frame.pack(fill=tk.X, padx=2, pady=2)
        self.aggregate_name_label = ttk.Label(aggregate_frame, text=self.language_manager.get_text("aggregate_name"))
        self.aggregate_name_label.pack(side=tk.LEFT, padx=5)
        self.aggregate_name_entry = ttk.Entry(aggregate_frame)
        self.aggregate_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.create_aggregate_button = ttk.Button(aggregate_frame, text=self.language_manager.get_text("create_aggregate"), command=self.create_aggregate)
        self.create_aggregate_button.pack(side=tk.LEFT, padx=5)

        # 区域3：搜索区域
        search_frame = ttk.Frame(task_frame)
        search_frame.pack(fill=tk.X, padx=2, pady=2)
        self.search_label = ttk.Label(search_frame, text=self.language_manager.get_text("search_task"))
        self.search_label.pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.clear_search_button = ttk.Button(search_frame, text=self.language_manager.get_text("clear_search"), command=self.clear_search)
        self.clear_search_button.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_tasks)

        # 区域4：任务列表和操作区域
        lists_frame = ttk.Frame(task_frame)
        lists_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=1)

        # 任务列表
        self.task_tree = ttk.Treeview(lists_frame, columns=("name", "type", "status", "frequent"), show="headings", height=15)
        self.task_tree.heading("name", text=self.language_manager.get_text("task_list.name"))
        self.task_tree.heading("type", text=self.language_manager.get_text("task_list.type"))
        self.task_tree.heading("status", text=self.language_manager.get_text("task_list.status"))
        self.task_tree.heading("frequent", text=self.language_manager.get_text("task_list.frequent"))
        self.task_tree.column("name", width=200, minwidth=150)
        self.task_tree.column("type", width=100, minwidth=80)
        self.task_tree.column("status", width=100, minwidth=80)
        self.task_tree.column("frequent", width=60, minwidth=50)
        self.task_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        # 添加滚动条，隐藏箭头并优化样式
        style = ttk.Style()
        style.layout('Vertical.TScrollbar', 
                     [('Vertical.Scrollbar.trough',
                       {'children': [('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})],
                        'sticky': 'ns'})])
        style.configure('Vertical.TScrollbar', width=8)
        scrollbar = ttk.Scrollbar(lists_frame, orient="vertical", command=self.task_tree.yview, style='Vertical.TScrollbar')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        # 添加任务悬停预览功能
        self.tooltip = None
        self.task_tree.bind('<Enter>', self.show_command_preview)
        self.task_tree.bind('<Leave>', self.hide_command_preview)
        self.task_tree.bind('<Motion>', self.update_command_preview)
        self.task_tree.bind('<Return>', self.execute_selected_tasks)  # 添加Enter键绑定

        # 操作按钮区域（作为任务列表区域的一部分）
        btn_frame = ttk.LabelFrame(lists_frame, text=self.language_manager.get_text("buttons.operations"))
        btn_frame.pack(fill=tk.X, padx=2, pady=2)

        # 第一排按钮组
        first_row_frame = ttk.Frame(btn_frame)
        first_row_frame.pack(fill=tk.X, padx=2, pady=2)

        # 所有操作按钮排列在一行
        self.execute_button = ttk.Button(first_row_frame, text=self.language_manager.get_text("buttons.execute_selected"), command=self.run_selected)
        self.execute_button.pack(side=tk.LEFT, padx=2)
        self.delete_button = ttk.Button(first_row_frame, text=self.language_manager.get_text("buttons.delete_selected"), command=self.delete_selected)
        self.delete_button.pack(side=tk.LEFT, padx=2)
        self.batch_execute_button = ttk.Button(first_row_frame, text=self.language_manager.get_text("buttons.batch_execute"), command=self.run_multiple)
        self.batch_execute_button.pack(side=tk.LEFT, padx=2)
        self.pause_var = tk.BooleanVar(value=False)
        self.pause_var_label = ttk.Checkbutton(first_row_frame, text=self.language_manager.get_text("buttons.pause_between"), variable=self.pause_var)
        self.pause_var_label.pack(side=tk.LEFT, padx=5)
        self.set_frequent_button = ttk.Button(first_row_frame, text=self.language_manager.get_text("buttons.set_frequent"), command=self.set_as_frequent)
        self.set_frequent_button.pack(side=tk.LEFT, padx=2)
        self.unset_frequent_button = ttk.Button(first_row_frame, text=self.language_manager.get_text("buttons.unset_frequent"), command=self.unset_as_frequent)
        self.unset_frequent_button.pack(side=tk.LEFT, padx=2)
        self.show_frequent_var = tk.BooleanVar(value=False)
        self.show_frequent_var_label = ttk.Checkbutton(first_row_frame, text=self.language_manager.get_text("buttons.show_frequent"), variable=self.show_frequent_var, command=self.filter_frequent_tasks)
        self.show_frequent_var_label.pack(side=tk.LEFT, padx=5)
        self.move_up_button = ttk.Button(first_row_frame, text=self.language_manager.get_text("buttons.move_up"), command=lambda: self.move_task_up(self.task_tree))
        self.move_up_button.pack(side=tk.LEFT, padx=2)
        self.move_down_button = ttk.Button(first_row_frame, text=self.language_manager.get_text("buttons.move_down"), command=lambda: self.move_task_down(self.task_tree))
        self.move_down_button.pack(side=tk.LEFT, padx=2)

        # 右侧：日志区域，优化布局
        log_frame = ttk.Frame(right_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # 日志标题和控制区域
        log_title_frame = ttk.Frame(log_frame)
        log_title_frame.pack(fill=tk.X, padx=2, pady=0)
        
        # 日志标题
        self.log_label = ttk.Label(log_title_frame, text=self.language_manager.get_text("log_title"))
        self.log_label.pack(side=tk.LEFT)
        
        # 显示编辑框控制
        self.show_edit_var = tk.BooleanVar(value=True)
        self.show_edit_checkbox = ttk.Checkbutton(log_title_frame, text=self.language_manager.get_text("show_edit_area"), variable=self.show_edit_var, command=self.toggle_edit_area)
        self.show_edit_checkbox.pack(side=tk.RIGHT, padx=5)
        
        # 移动导入导出按钮到日志标题区域
        self.import_button = ttk.Button(log_title_frame, text=self.language_manager.get_text("buttons.import_tasks"), command=self.import_tasks)
        self.import_button.pack(side=tk.RIGHT, padx=2)
        self.export_button = ttk.Button(log_title_frame, text=self.language_manager.get_text("buttons.export_tasks"), command=self.export_tasks)
        self.export_button.pack(side=tk.RIGHT, padx=2)
        
        # 日志文本框和滚动条
        log_content_frame = ttk.Frame(log_frame)
        log_content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.log_text = tk.Text(log_content_frame, height=20, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        log_scrollbar = ttk.Scrollbar(log_content_frame, orient="vertical", command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # 默认设置日志为只读
        self.log_text.configure(state="disabled")



    def add_task(self):
        name = self.task_name_entry.get().strip()
        command = self.bat_command_entry.get("1.0", tk.END).strip()

        if not name or not command:
            messagebox.showerror(self.language_manager.get_text("messages.empty_name_command"), self.language_manager.get_text("messages.empty_name_command"))
            return

        if self.task_manager.add_task(name, command):
            # 根据任务类型获取对应的语言文本
            task_type = self.language_manager.get_text("task_type.aggregate") if "&&" in command else self.language_manager.get_text("task_type.normal")
            self.task_tree.insert("", tk.END, values=(name, task_type, self.language_manager.get_text("task_status.waiting"), self.language_manager.get_text("task_list.no")))  # 使用语言文件中的否
            self.task_name_entry.delete(0, tk.END)
            self.bat_command_entry.delete("1.0", tk.END)
        else:
            messagebox.showerror(self.language_manager.get_text("messages.name_exists"), self.language_manager.get_text("messages.name_exists"))

    def load_tasks(self):
        tasks = self.task_manager.get_all_tasks()
        for task in tasks:
            task_type = self.language_manager.get_text("task_type.aggregate") if "&&" in task["command"] else self.language_manager.get_text("task_type.normal")
            frequent = self.language_manager.get_text("task_list.yes") if task.get("frequent", False) else self.language_manager.get_text("task_list.no")
            self.task_tree.insert("", tk.END, values=(task["name"], task_type, self.language_manager.get_text("task_status.waiting"), frequent))

    def run_selected(self):
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning(self.language_manager.get_text("messages.select_execute"), self.language_manager.get_text("messages.select_execute"))
            return

        task_name = self.task_tree.item(selection[0])["values"][0]
        self.task_manager.run_task(task_name, self.update_task_status, self.update_log)

    def delete_selected(self):
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning(self.language_manager.get_text("messages.select_delete"), self.language_manager.get_text("messages.select_delete"))
            return

        task_name = self.task_tree.item(selection[0])["values"][0]
        self.task_manager.delete_task(task_name)
        self.task_tree.delete(selection[0])

    def run_multiple(self):
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning(self.language_manager.get_text("messages.select_execute"), self.language_manager.get_text("messages.select_execute"))
            return

        task_names = [self.task_tree.item(item)["values"][0] for item in selection]
        self.task_manager.run_multiple_tasks(task_names, self.update_task_status, self.update_log, self.pause_var.get())

    def update_task_status(self, task_name, status):
        # 更新任务状态显示
        for item in self.task_tree.get_children():
            name = self.task_tree.item(item, "values")[0]
            if name == task_name:
                task = self.task_manager.get_task(task_name)
                if task:
                    task_type = self.language_manager.get_text("task_type.aggregate") if "&&" in task["command"] else self.language_manager.get_text("task_type.normal")
                    # 修改状态文本获取逻辑
                    status_text = self.language_manager.get_text(status)
                    frequent_text = self.language_manager.get_text("task_list.yes") if task.get("frequent", False) else self.language_manager.get_text("task_list.no")
                    self.task_tree.item(item, values=(name, task_type, status_text, frequent_text))
                    # 强制更新界面显示
                    self.task_tree.update()
                break

    def set_as_frequent(self):
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning(self.language_manager.get_text("messages.select_frequent"), self.language_manager.get_text("messages.select_frequent"))
            return

        task_name = self.task_tree.item(selection[0])["values"][0]
        task = self.task_manager.get_task(task_name)
        if task:
            task["frequent"] = True
            self.task_manager.update_task(task_name, task)
            # 根据当前语言设置常用标识
            frequent_text = self.language_manager.get_text("task_list.yes")
            self.task_tree.item(selection[0], values=(task_name, self.task_tree.item(selection[0])["values"][1], self.task_tree.item(selection[0])["values"][2], frequent_text))

    def unset_as_frequent(self):
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning(self.language_manager.get_text("messages.select_unfrequent"), self.language_manager.get_text("messages.select_unfrequent"))
            return

        task_name = self.task_tree.item(selection[0])["values"][0]
        task = self.task_manager.get_task(task_name)
        if task:
            task["frequent"] = False
            self.task_manager.update_task(task_name, task)
            # 根据当前语言设置常用标识
            frequent_text = self.language_manager.get_text("task_list.no")
            self.task_tree.item(selection[0], values=(task_name, self.task_tree.item(selection[0])["values"][1], self.task_tree.item(selection[0])["values"][2], frequent_text))

    def update_log(self, message):
        """更新日志内容"""
        # 临时启用编辑
        current_state = self.log_text.cget("state")
        self.log_text.configure(state="normal")
        
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        
        # 恢复原始状态
        self.log_text.configure(state=current_state)
        
        # 同时写入日志文件
        self.log_manager.write_log(message)

    def filter_frequent_tasks(self):
        show_frequent = self.show_frequent_var.get()
        # 获取所有任务项，包括被detach的项
        all_items = self.task_tree.get_children("")
        
        if show_frequent:
            # 显示常用任务时，只显示标记为常用的任务
            for item in all_items:
                task_name = self.task_tree.item(item)["values"][0]
                task = self.task_manager.get_task(task_name)
                if task and task.get("frequent", False):
                    self.task_tree.reattach(item, "", tk.END)
                else:
                    self.task_tree.detach(item)
        else:
            # 不显示常用任务时，显示所有任务
            tasks = self.task_manager.get_all_tasks()
            # 清空当前显示的任务
            for item in self.task_tree.get_children():
                self.task_tree.delete(item)
            # 重新加载所有任务
            for task in tasks:
                task_type = self.language_manager.get_text("task_type.aggregate") if "&&" in task["command"] else self.language_manager.get_text("task_type.normal")
                frequent = self.language_manager.get_text("task_list.yes") if task.get("frequent", False) else self.language_manager.get_text("task_list.no")
                self.task_tree.insert("", tk.END, values=(task["name"], task_type, self.language_manager.get_text("task_status.waiting"), frequent))

    def search_tasks(self, event=None):
        search_text = self.search_entry.get().strip().lower()
        for item in self.task_tree.get_children():
            task_name = self.task_tree.item(item)['values'][0].lower()
            if search_text in task_name:
                self.task_tree.reattach(item, '', tk.END)
            else:
                self.task_tree.detach(item)

    def import_tasks(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            if self.data_manager.import_tasks(file_path):
                self.refresh_task_list()
                messagebox.showinfo("Success", self.language_manager.get_text("messages.import_success"))
            else:
                messagebox.showerror("Error", self.language_manager.get_text("messages.import_failed"))

    def export_tasks(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            if self.data_manager.export_tasks(file_path):
                messagebox.showinfo("Success", self.language_manager.get_text("messages.export_success"))
            else:
                messagebox.showerror("Error", self.language_manager.get_text("messages.export_failed"))

    def create_aggregate(self):
        name = self.aggregate_name_entry.get().strip()
        selected = self.task_tree.selection()
        
        if not name:
            messagebox.showerror(self.language_manager.get_text("messages.empty_aggregate"), self.language_manager.get_text("messages.empty_aggregate"))
            return
            
        if not selected:
            messagebox.showwarning(self.language_manager.get_text("messages.select_aggregate"), self.language_manager.get_text("messages.select_aggregate"))
            return
            
        commands = []
        for item in selected:
            task_name = self.task_tree.item(item)["values"][0]
            task = self.task_manager.get_task(task_name)
            if task:
                commands.append(task["command"])
                
        if commands:
            aggregate_command = " && ".join(commands)
            if self.task_manager.add_task(name, aggregate_command):
                self.task_tree.insert("", tk.END, values=(name, self.language_manager.get_text("task_type.aggregate"), self.language_manager.get_text("task_status.waiting"), self.language_manager.get_text("task_list.no")))
                self.aggregate_name_entry.delete(0, tk.END)
            else:
                messagebox.showerror(self.language_manager.get_text("messages.aggregate_exists"), self.language_manager.get_text("messages.aggregate_exists"))

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        # 重新加载所有任务
        tasks = self.task_manager.get_all_tasks()
        # 清空当前显示的任务
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        # 重新显示所有任务
        for task in tasks:
            task_type = self.language_manager.get_text("task_type.aggregate") if "&&" in task["command"] else self.language_manager.get_text("task_type.normal")
            frequent = self.language_manager.get_text("task_list.yes") if task.get("frequent", False) else self.language_manager.get_text("task_list.no")
            self.task_tree.insert("", tk.END, values=(task["name"], task_type, self.language_manager.get_text("task_status.waiting"), frequent))
        # 如果当前是显示常用任务模式，则应用过滤
        if self.show_frequent_var.get():
            self.filter_frequent_tasks()

    def move_task_up(self, tree):
        selection = tree.selection()
        if not selection:
            return

        for item in selection:
            idx = tree.index(item)
            if idx > 0:
                tree.move(item, tree.parent(item), idx - 1)

    def move_task_down(self, tree):
        selection = tree.selection()
        if not selection:
            return

        for item in reversed(selection):
            idx = tree.index(item)
            if idx < len(tree.get_children()) - 1:
                tree.move(item, tree.parent(item), idx + 1)

    def refresh_task_list(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        self.load_tasks()

    def show_command_preview(self, event):
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry("+%d+%d" % (event.x_root + 10, event.y_root + 10))
        self.tooltip_label = ttk.Label(self.tooltip, justify=tk.LEFT, relief=tk.SOLID, borderwidth=1)
        self.tooltip_label.pack()
        self.update_command_preview(event)

    def hide_command_preview(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def update_command_preview(self, event):
        if self.tooltip:
            item = self.task_tree.identify('item', event.x, event.y)
            if item:
                task_name = self.task_tree.item(item)['values'][0]
                task = self.task_manager.get_task(task_name)
                if task:
                    self.tooltip_label.config(text=f"指令: {task['command']}")
                    self.tooltip.wm_geometry("+%d+%d" % (event.x_root + 10, event.y_root + 10))
            else:
                self.hide_command_preview(event)

    def execute_selected_tasks(self, event=None):
        """响应Enter键执行选中的任务"""
        selection = self.task_tree.selection()
        if not selection:
            return
        
        # 如果选中了多个任务，执行批量任务
        if len(selection) > 1:
            self.run_multiple()
        else:
            # 如果只选中了一个任务，执行单个任务
            self.run_selected()

    def toggle_edit_area(self):
        """控制编辑区域的显示和隐藏"""
        show_edit = self.show_edit_var.get()
        # 获取需要控制显示/隐藏的区域组件
        add_frame = self.task_name_label.master
        cmd_frame = self.bat_command_label.master
        aggregate_frame = self.aggregate_name_label.master
        search_frame = self.search_label.master
        lists_frame = self.task_tree.master
        btn_frame = self.execute_button.master.master

        # 先移除所有组件
        add_frame.pack_forget()
        cmd_frame.pack_forget()
        aggregate_frame.pack_forget()
        search_frame.pack_forget()
        lists_frame.pack_forget()
        btn_frame.pack_forget()

        # 先设置按钮区域固定在底部
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5, anchor=tk.S)

        if show_edit:
            # 显示所有编辑区域组件，确保它们在正确的位置
            add_frame.pack(fill=tk.X, padx=5, pady=5)
            cmd_frame.pack(fill=tk.X, padx=5, pady=5)
            aggregate_frame.pack(fill=tk.X, padx=5, pady=5)
            search_frame.pack(fill=tk.X, padx=5, pady=5)
            lists_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        else:
            # 隐藏编辑区域时，只显示列表区域
            lists_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

    def switch_language(self, event=None):
        """切换界面语言"""
        if self.language_manager.switch_language(self.language_var.get()):
            # 更新界面文本
            self.root.title(self.language_manager.get_text("title"))
            self.refresh_ui_text()

    def refresh_ui_text(self):
        """刷新界面文本"""
        # 更新任务列表标题
        self.task_tree.heading("name", text=self.language_manager.get_text("task_list.name"))
        self.task_tree.heading("type", text=self.language_manager.get_text("task_list.type"))
        self.task_tree.heading("status", text=self.language_manager.get_text("task_list.status"))
        self.task_tree.heading("frequent", text=self.language_manager.get_text("task_list.frequent"))

        # 更新任务列表中的文本
        for item in self.task_tree.get_children():
            values = self.task_tree.item(item)["values"]
            if values:
                name = values[0]
                task = self.task_manager.get_task(name)
                if task:
                    # 根据任务类型获取对应的语言文本
                    task_type = self.language_manager.get_text("task_type.aggregate") if "&&" in task["command"] else self.language_manager.get_text("task_type.normal")
                    
                    # 获取当前状态对应的语言文本
                    status = values[2].lower() if values[2] else "waiting"
                    status_key = status.split('.')[-1] if '.' in status else status
                    status_text = self.language_manager.get_text(f"task_status.{status_key}")
                    
                    # 获取常用标识对应的语言文本
                    frequent_text = self.language_manager.get_text("task_list.yes") if task.get("frequent", False) else self.language_manager.get_text("task_list.no")
                    
                    # 更新列表项的显示文本
                    self.task_tree.item(item, values=(name, task_type, status_text, frequent_text))

        # 自适应调整列宽
        for col in ("name", "type", "status", "frequent"):
            self.task_tree.column(col, width=0)  # 先将宽度设为0
            self.task_tree.update()
            
            # 获取列中所有值的最大宽度
            content_widths = []
            for item in self.task_tree.get_children():
                col_idx = ("name", "type", "status", "frequent").index(col)
                value = str(self.task_tree.item(item)["values"][col_idx])
                content_widths.append(len(value) * 15)
            
            width = max(
                self.task_tree.column(col, "width"),  # 当前宽度
                len(self.task_tree.heading(col)["text"]) * 15,  # 标题宽度
                max(content_widths, default=50)  # 内容最大宽度
            )
            self.task_tree.column(col, width=width + 20)  # 添加一些padding

        # 更新按钮文本
        self.execute_button.config(text=self.language_manager.get_text("buttons.execute_selected"))
        self.delete_button.config(text=self.language_manager.get_text("buttons.delete_selected"))
        self.batch_execute_button.config(text=self.language_manager.get_text("buttons.batch_execute"))
        self.pause_var_label.config(text=self.language_manager.get_text("buttons.pause_between"))
        self.import_button.config(text=self.language_manager.get_text("buttons.import_tasks"))
        self.export_button.config(text=self.language_manager.get_text("buttons.export_tasks"))
        self.move_up_button.config(text=self.language_manager.get_text("buttons.move_up"))
        self.move_down_button.config(text=self.language_manager.get_text("buttons.move_down"))
        self.set_frequent_button.config(text=self.language_manager.get_text("buttons.set_frequent"))
        self.unset_frequent_button.config(text=self.language_manager.get_text("buttons.unset_frequent"))
        self.show_frequent_var_label.config(text=self.language_manager.get_text("buttons.show_frequent"))

        # 更新标签文本
        self.task_name_label.config(text=self.language_manager.get_text("task_name"))
        self.bat_command_label.config(text=self.language_manager.get_text("bat_command"))
        self.add_task_button.config(text=self.language_manager.get_text("add_task"))
        self.aggregate_name_label.config(text=self.language_manager.get_text("aggregate_name"))
        self.create_aggregate_button.config(text=self.language_manager.get_text("create_aggregate"))
        self.search_label.config(text=self.language_manager.get_text("search_task"))
        self.clear_search_button.config(text=self.language_manager.get_text("clear_search"))
        self.log_label.config(text=self.language_manager.get_text("log_title"))
        # 更新显示编辑复选框和语言标签文本的代码
        self.show_edit_checkbox.config(text=self.language_manager.get_text("show_edit_area"))
        # 更新语言标签文本
        self.language_label.config(text=self.language_manager.get_text("language"))
        ttk.Label(menu_frame, text=self.language_manager.get_text("language")).pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    import sys
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe运行，隐藏控制台窗口
        import win32gui
        import win32con
        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
    
    root = tk.Tk()
    app = BatTaskManagerApp(root)
    root.mainloop()