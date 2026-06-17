import threading
import time
from gui import NetworkAppGUI
from backend import fetch_network_data

class NetworkAppController:
    def __init__(self):
        # creating a gui by passing links to the start and stop methods
        self.ui = NetworkAppGUI(
            start_callback=self.start_logging,
            stop_callback=self.stop_logging
        )
        self.is_running = False
        self.worker_thread = None

    def start_logging(self):
        self.is_running = True
        self.ui.set_ui_state(running=True)

        # creating and launching a survey stream
        self.worker_thread = threading.Thread(target=self.polling_loop, daemon=True)
        self.worker_thread.start()

    def stop_logging(self):
        self.is_running = False
        self.ui.update_status('Stopping the process by the user...')

    def polling_loop(self):
        # collecting the device configuration from the interface
        try:
            port_val = int(self.ui.port_entry.get())
        except ValueError:
            self.ui.update_status('Error: Incorrect port format')
            self.reset_ui_stop()
            return
        
        device_config = {
            'device_type': self.ui.device_type_select.get(),
            'host': self.ui.host_entry.get(),
            'username': self.ui.username_entry.get(),
            'password': self.ui.password_entry.get(),
            'secret': self.ui.secret_entry.get(),
            'port': port_val,
        }

        command = self.ui.command_entry.get()
        filename = self.ui.file_entry.get()

        # validation of time settings
        use_interval = self.ui.interval_var.get()
        try:
            interval_time = int(self.ui.interval_entry.get()) if use_interval else 0
            use_duration = self.ui.duration_var.get() if use_interval else False
            duration_time = int(self.ui.duration_entry.get()) if use_duration else 0
        except ValueError:
            self.ui.update_status('Error: The time interval/duration format incorrect')
            self.reset_ui.stop()
            return
        
        if not filename:
            self.ui.update_status('Error: The file for the log is not specified')
            self.reset_ui_stop()
            return
        
        start_time = time.time()

        # the main survey cycle
        while self.is_running:
            self.ui.update_status(f'Connecting to {device_config["host"]}:{device_config["port"]}...')

            # calling the network backend
            success, message = fetch_network_data(device_config, command, filename)
            self.ui.update_status(message)

            # if thr periodic survey is disabled - exit immediately (one-time collection)
            if not use_interval:
                break

            # if the total duration is enabled and the time is up - exit
            if use_duration and (time.time() - start_time) >= duration_time:
                self.ui.update_status('Completed after the end of the working time')
                break

            # smart one-second pause ( so than the 'stop' button works instantly)
            for _ in range(interval_time):
                if not self.is_running:
                    break
                time.sleep(1)
        
        self.reset_ui_stop()

    def reset_ui_stop(self):
        self.is_running = False
        self.ui.set_ui_state(running=False)
        if 'Error' not in self.ui.status_label.cget('text') and 'Completed' not in self.ui.status_label.cget('text'):
            self.ui.update_status('The survey is completed/stopped')

    def run(self):
        self.ui.mainloop()

if __name__ == '__main__':
    app = NetworkAppController()
    app.run()