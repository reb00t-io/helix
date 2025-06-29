import os
import pty
import subprocess
import sys
from typing import Tuple
from threading import Thread

def run_and_capture(cmd: list, **kwargs) -> Tuple[int, str, str]:
    """
    Runs a command, streaming output to the terminal in real-time (color preserved),
    and also captures the output to return as a string.
    Returns (exit_code, stdout, stderr).
    """
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # line buffered
        **kwargs
    )

    stdout_buf = []
    stderr_buf = []

    # Print output as it arrives, while saving it
    def reader(pipe, out_stream, buf):
        for line in iter(pipe.readline, ''):
            print(line, end='', file=out_stream)
            buf.append(line)
        pipe.close()

    threads = [
        Thread(target=reader, args=(process.stdout, sys.stdout, stdout_buf)),
        Thread(target=reader, args=(process.stderr, sys.stderr, stderr_buf)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return_code = process.wait()
    return return_code, ''.join(stdout_buf), ''.join(stderr_buf)

def run_and_capture_pty(cmd) -> Tuple[int, str, str]:
    """
    Runs a command in a pseudo-terminal (pty), streaming output to the terminal in real-time
    with color preserved, and captures the combined output.
    Returns (exit_code, output).
    """
    pid, master_fd = pty.fork()
    if pid == 0:
        # Child process
        os.execvp(cmd[0], cmd)
    else:
        # Parent process
        output = []
        while True:
            try:
                data = os.read(master_fd, 1024)
                if not data:
                    break
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()
                output.append(data)
            except OSError:
                break
        _, status = os.waitpid(pid, 0)
        exit_code = os.WEXITSTATUS(status)
        return exit_code, b''.join(output).decode(errors='replace')
