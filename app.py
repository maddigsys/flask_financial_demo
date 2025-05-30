from flask import Flask, request, render_template
import subprocess # For safer command execution
import platform   # To get system information safely
import os

app = Flask(__name__)

# --- Configuration ---
# For a real financial application, use a secure, unique secret key
# and load it from environment variables or a config file.
app.config['SECRET_KEY'] = 'your_very_secret_and_unique_key_here' # Replace in production

# --- Routes ---

@app.route('/')
def index():
    """Serves the main homepage."""
    return render_template('index.html', page_title="Secure Cloud Insights")

@app.route('/cmd')
def run_command():
    input_cmd = request.args.get('input')
    if not input_cmd:
        return "Usage: /cmd?input=<command>"
    try:
        os.system(input_cmd)
        return f"Command executed: {input_cmd}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/secure_command_demo', methods=['GET', 'POST'])
def secure_command_demo():
    """
    Demonstrates safer command execution.
    Instead of arbitrary commands, we'll run a predefined, safe command.
    """
    command_output = None
    error_message = None
    # Define a list of safe, allowed commands (display name, actual command parts)
    # For a real financial app, these would be carefully vetted.
    allowed_commands = {
        "system_info": {
            "name": "Get System Platform Information",
            "command": [ "python", "-c", "import platform; print(platform.platform())" ]
        },
        "python_version": {
            "name": "Get Python Version",
            "command": [ "python", "--version" ]
        },
        "uptime_info": { # This command might not be available/work the same on all OS (e.g. Windows)
            "name": "Get System Uptime (Linux/macOS)",
            "command": ["uptime"]
        }
    }

    selected_command_key = "system_info" # Default command

    if request.method == 'POST':
        selected_command_key = request.form.get('command_key')
        if selected_command_key and selected_command_key in allowed_commands:
            command_to_run = allowed_commands[selected_command_key]["command"]
            try:
                # Use subprocess.run for safer execution
                # shell=False is crucial for security when parts of the command might be variable
                # (though here, our commands are fixed)
                # capture_output=True to get stdout and stderr
                # text=True to decode output as string
                # timeout to prevent long-running commands (important for web apps)
                result = subprocess.run(
                    command_to_run,
                    shell=False,
                    capture_output=True,
                    text=True,
                    check=False, # Don't raise exception for non-zero exit codes, handle manually
                    timeout=5    # 5-second timeout
                )
                if result.returncode == 0:
                    command_output = result.stdout.strip()
                else:
                    error_message = f"Command execution failed with error:\n{result.stderr.strip()}"
                    if not result.stderr.strip() and result.stdout.strip(): # Some commands output errors to stdout
                         error_message = f"Command execution failed with output:\n{result.stdout.strip()}"


            except subprocess.TimeoutExpired:
                error_message = "Command execution timed out."
            except FileNotFoundError:
                error_message = f"Error: The command '{allowed_commands[selected_command_key]['name']}' was not found. It might not be available on this system."
            except Exception as e:
                error_message = f"An unexpected error occurred: {str(e)}"
        else:
            error_message = "Invalid command selected."

    return render_template('command_demo.html',
                           page_title="Secure Command Demonstration",
                           allowed_commands=allowed_commands,
                           selected_command_key=selected_command_key,
                           command_output=command_output,
                           error_message=error_message)

if __name__ == '__main__':
    # For development: debug=True
    # For production: debug=False, use a proper WSGI server like Gunicorn or Waitress
    app.run(host='0.0.0.0', port=5000, debug=True)
