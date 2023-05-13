import subprocess
import os
import sys
import platform

python = sys.executable
index_url = os.environ.get('INDEX_URL', "")

def print_error_explanation(message):
    lines = message.strip().split("\n")
    max_len = max([len(x) for x in lines])

    print('=' * max_len, file=sys.stderr)
    for line in lines:
        print(line, file=sys.stderr)
    print('=' * max_len, file=sys.stderr)

def check_python_version():
    is_windows = platform.system() == "Windows"
    major = sys.version_info.major
    minor = sys.version_info.minor
    micro = sys.version_info.micro

    if is_windows:
        supported_minors = [10]
    else:
        supported_minors = [7, 8, 9, 10, 11]

    if not (major == 3 and minor in supported_minors):
        print_error_explanation(f"""
        INCOMPATIBLE PYTHON VERSION

        This program is tested with 3.10.6 Python, but you have {major}.{minor}.{micro}.
        If you encounter an error with "RuntimeError: Couldn't install ..." message,
        or any other error regarding unsuccessful package (library) installation,
        please downgrade (or upgrade) to the latest version of 3.10 Python
        and delete current Python and "venv" folder in WebUI's directory.
        """)

def run(command, desc=None, errdesc=None, custom_env=None, live=False):
    if desc is not None:
        print(desc)

    if live:
        result = subprocess.run(command, shell=True, env=os.environ if custom_env is None else custom_env)
        if result.returncode != 0:
            raise RuntimeError(f"""{errdesc or 'Error running command'}.
            Command: {command}
            Error code: {result.returncode}""")

        return ""

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=os.environ if custom_env is None else custom_env)

    if result.returncode != 0:

        message = f"""{errdesc or 'Error running command'}.
                Command: {command}
                Error code: {result.returncode}
                stdout: {result.stdout.decode(encoding="utf8", errors="ignore") if len(result.stdout)>0 else '<empty>'}
                stderr: {result.stderr.decode(encoding="utf8", errors="ignore") if len(result.stderr)>0 else '<empty>'}
                """
        raise RuntimeError(message)

    return result.stdout.decode(encoding="utf8", errors="ignore")

def run_pip(command, desc=None, live=False):
    index_url_line = f' --index-url {index_url}' if index_url != '' else ''
    return run(f'"{python}" -m pip {command} --prefer-binary{index_url_line}', desc=f"Installing {desc}", errdesc=f"Couldn't install {desc}", live=live)

def prepare_environment():
    check_python_version()
    run_pip("install -r \"requirements.txt\"", "requirements")

def start():
    import main
    main.webui().queue().launch()

if __name__ == "__main__":
    prepare_environment()
    start()