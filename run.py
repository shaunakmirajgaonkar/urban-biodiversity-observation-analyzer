import socket, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def free_port(start=8501, end=8599):
    for p in range(start, end+1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(('127.0.0.1', p)); return p
            except OSError:
                pass
    raise RuntimeError('No free local port found in 8501–8599.')

if __name__ == '__main__':
    port = free_port()
    print(f'UrbanBioTrack starting on http://localhost:{port}')
    subprocess.run([sys.executable,'-m','streamlit','run',str(ROOT/'app.py'),'--server.address','127.0.0.1','--server.port',str(port)],check=True)
