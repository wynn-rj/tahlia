import subprocess
from pathlib import Path

controllable_args = [
    'autozoom',
    'autoup',
    'noautoup',
    'autodown',
    'noautodown',
    'fitwidth',
    'nofitwidth',
]

def display_on_window(image=None, **kwargs):
    kwargs.setdefault('autozoom', True)
    absimage = str(Path(image).absolute().name)
    if absimage != image or absimage.startswith('.'):
        return
    image = Path(Path(__file__).parent, "..", "images", absimage).resolve()
    if not image.exists():
        return

    cmd = ['fbi', '-T', '2', '-noverbose']
    for arg in controllable_args:
        if arg in kwargs:
            cmd.append(f'-{arg}')
    cmd.append(str(image))
    subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)