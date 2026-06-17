import datetime
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException, NetMikoAuthenticationException

def fetch_network_data(device_config, command, filename):
    '''
    executes the command on a network device via netmiko and writes the result to a file
    returns a tuple: (success_status: bool, message_for_interface: str)
    '''
    try:
        with ConnectHandler(**device_config) as ssh:
            if device_config.get('secret') and ssh.check_enable_mode():
                ssh.enable()

            output = ssh.send_command(command)

            log_entry = f'\n{"="*20} {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {"="*20}\n{output}\n'
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(log_entry)

            return True, 'The data has been successfully recorded!'
    except NetMikoTimeoutException:
        msg = f'Error: Connection timeout to {device_config["host"]}'
        _write_error_to_log(filename, msg)
        return False, msg
    except NetMikoAuthenticationException:
        msg = f'Error: Invalid username/password for {device_config["host"]}'
        _write_error_to_log(filename, msg)
        return False, msg
    except Exception as e:
        msg = f'Eror: {str(e)}'
        _write_error_to_log(filename, msg)
        return False, msg
    
def _write_error_to_log(filename, error_message):
    '''auxiliary function for recording system errors in a log file'''
    if filename:
        try:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f'[{timestamp}] {error_message}\n')
        except Exception:
            pass