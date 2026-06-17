import os
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

class NetworkAppGUI(ctk.CTk):
    def __init__(self, start_callback, stop_callback):
        super().__init__()

        self.start_callback = start_callback
        self.stop_callback = stop_callback

        self.title('NCL - Network Command Logger')
        self.geometry('850x520')
        self.resizable(False, False)

        # main grid: 2 columns
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.setup_ui()

    def setup_ui(self):
        # =========================================
        # LEFT SIDE: connection parameters
        # =========================================
        left_frame = ctk.CTkFrame(self, fg_color='transparent')
        left_frame.grid(row=0, column=0, padx=30, py=20, sticky='nsew')

        ctk.CTkLabel(left_frame, text='Connection parameters', font=ctk.CTkFont(size=16, weight='bold')).pack(anchor='w', pady=(0, 15))

        # netmiko drop-down list
        ctk.CTkLabel(left_frame, text='Device type (netmiko):').pack(anchor='w')
        self.device_type_select = ctk.CTkOptionMenu(
            left_frame,
            values=['cisco_ios', 'mikrotik_routeros', 'eltex'],
            width=300
        )
        self.device_type_select.pack(anchor='w', pady=(0, 10))

        # ip address and port in one row
        ip_port_frame = ctk.CTkFrame(left_frame, fg_color='transparent')
        ip_port_frame.pack(anchor='w', fill='x', pady=(0, 10))

        ip_sub = ctk.CTkFrame(ip_port_frame, fg_color='transparent')
        ip_sub.pack(side='left', fill='x', expand=True)
        ctk.CTkLabel(ip_sub, text='IP-address:').pack(anchor='w')
        self.host_entry = ctk.CTkEntry(ip_sub, placeholder_text='192.168.1.1')
        self.host_entry.insert(0, '192.168.1.1')
        self.host_entry.pack(anchor='w', fill='x', pright=10)

        port_sub = ctk.CTkFrame(ip_port_frame, fg_color='transparent')
        port_sub.pack(side='right', width=80)
        ctk.CTkLabel(port_sub, text='Port:').pack(anchor='w')
        self.port_entry = ctk.CTkEntry(port_sub, placeholder_text='22')
        self.port_entry.insert(0, '22')
        self.port_entry.pack(anchor='w', fill='x')

        # login, password, secret, command
        ctk.CTkLabel(left_frame, text='User name:').pack(anchor='w')
        self.username_entry = ctk.CTkEntry(left_frame, width=300)
        self.username_entry.insert(0, 'admin')
        self.username_entry.pack(anchor='w', pady=(0, 10))

        ctk.CTkLabel(left_frame, text='Password:').pack(anchor='w')
        self.password_entry = ctk.CTkEntry(left_frame, width=300, show='*')
        self.password_entry.insert(0, 'password')
        self.password_entry.pack(anchor='w', pady=(0, 10))

        ctk.CTkLabel(left_frame, text='Enable password (if needed):').pack(anchor='w')
        self.secret_entry = ctk.CTkEntry(left_frame, width=300, show='*')
        self.secret_entry.pack(anchor='w', pady=(0, 10))

        ctk.CTkLabel(left_frame, text='The command to execute:').pack(anchor='w')
        self.command_entry = ctk.CTkEntry(left_frame, width=300)
        self.command_entry.insert(0, 'sh int desc')
        self.command_entry.pack(anchor='w', pady=(0, 10))

        # =========================================
        # RIGHT SIDE: Time settings (interval/duration)
        # =========================================
        right_frame = ctk.CTkFrame(self, fg_color='transparent')
        right_frame.grid(row=0, column=1, padx=30, py=20, sticky='nsew')

        ctk.CTkLabel(right_frame, text='Time settings', font=ctk.CTkFont(size=16, weight='bold')).pack(anchor='w', pady=(0, 15))

        # interval checkbox
        self.interval_var = tk.BooleanVar(value=True)
        self.interval_cb = ctk.CTkCheckBox(
            right_frame, text='Enable periodic polling (interval)',
            variable=self.interval_var, command=self.toggle_time_widgets
        )
        self.interval_cb.pack(anchor='w', pady=(0, 10))

        # gray container
        self.time_box = ctk.CTkFont(right_frame, border_width=1, border_color='gray40')
        self.time_box.pack(fill='x', ipady=10, ipadx=10, pady=(0, 20))

        self.lbl_int = ctk.CTkLabel(self.time_box, text='Polling interval (sec):')
        self.lbl_int.pack(anchor='w', padx=10, pady=(5, 0))
        self.interval_entry = ctk.CTkEntry(self,self.time_box, width=120)
        self.interval_entry.insert(0, '60')
        self.interval_entry.pack(anchor='w', padx=10, pady=(0, 10))

        # duration checkbox
        self.duration_var = tk.BooleanVar(value=False)
        self.duration_cb = ctk.CTkCheckBox(
            self.time_box, text='Limit the duration',
            variable=self.duration_var, command=self.toggle_time_widgets
        )
        self.duration_cb.pack(anchor='w', padx=10, pady=(5, 0))

        self.lbl_dur = ctk.CTkLabel(self.time_box, text='Working time/duration (sec):')
        self.lbl_dur.pack(anchor='w', padx=10, pady=(5, 0))
        self.duration_entry = ctk.CTkEntry(self.time_box, width=120)
        self.duration_entry.insert(0, '360')
        self.duration_entry.pack(anchor='w', padx=10, pady=(0, 10))

        # =========================================
        # BOTTOM SIDE: file, buttons, status
        # =========================================
        bottom_frame = ctk.CTkFrame(self, fg_color='transparent')
        bottom_frame.grid(row=1, column=0, columnspan=2, padx=30, py=(0, 20), sticky='ew')

        # selecting the log file
        ctk.CTkLabel(bottom_frame, text='Path to the file log:').pack(anchor='w')
        file_frame = ctk.CTkFrame(bottom_frame, fg_color='transparent')
        file_frame.pack(fill='x', pady=(0, 15))

        self.file_entry = ctk.CTkEntry(file_frame, placeholder_text='Choose a path...')
        self.file_entry.insert(0, os.path.abspath('network_log.txt'))
        self.file_entry.pack(side='left', fill='x', expand=True, pright=10)

        self.browse_btn = ctk.CTkButton(file_frame, text='Browse...', width=90, command=self.choose_file)
        self.browse_btn.pack(side='right')

        # dividing line
        separator = ctk.CTkFrame(bottom_frame, height=2, fg_color='gray30')
        separator.pack(fill='x', pady=(0, 15))

        # control buttons 
        buttons_frame = ctk.CTkFrame(bottom_frame, fg_color='transparent')
        buttons_frame.pack(fill='x')

        self.start_button = ctk.CTkButton(buttons_frame, text='Start', fg_color='green', hover_color='darkgreen', command=self.start_callback)
        self.start_button.pack(side='left', fill='x', expand=True, pright=10)

        self.stop_button = ctk.CTkButton(buttons_frame, text='Stop', fg_color='red', hover_color='darkred', state='disabled', command=self.stop_callback)
        self.stop_button.pack(side='right', fill='x', expand=True)

        # status
        self.status_label = ctk.CTkLabel(bottom_frame, text='Status: Waiting for the start', font=ctk.CTkFont(size=12, slant='italic'))
        self.status_label.pack(pady=(15, 0))

        # swutching the availability of fields for the current checkboxes
        self.toggle_time_widgets()

    def toggle_time_widgets(self):
        '''intelligently locks/unlocks time settings fields'''
        if self.interval_var.get():
            self.interval_entry.configure(state='normal')
            self.duration_cb.configure(state='normal')
            if self.duration_var.get():
                self.duration_entry.configure(state='normal')
            else:
                self.duration_entry.configure(state='disabled')
        else:
            self.interval_entry.configure(state='disabled')
            self.duration_cb.configure(state='disabled')
            self.duration_entry.configure(state='disabled')
    
    def choose_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('Text files', '*.txt'), ('All files', '*.*')],
            initialfile='network_log.txt',
            title='Select a location to save the log'
        )
        if file_path:
            self.file_entry.delete(0, 'end')
            self.file_entry.insert(0, os.path.normpath(file_path))

    def update_status(self, text):
        self.after(0, lambda: self.status_label.configure(text=f'Status: {text}'))

    def set_ui_state(self, running=True):
        '''switches the status of the buttons when starting/stopping the survey'''
        if running:
            self.start_button.configure(state='disabled')
            self.stop_button.configure(state='normal')
        else:
            self.start_button.configure(state='normal')
            self.stop_button.configure(state='disabled')