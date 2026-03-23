import subprocess

controllable_args = [
    "autozoom",
    "autoup",
    "noautoup",
    "autodown",
    "noautodown",
    "fitwidth",
    "nofitwidth",
]


def display_on_window(image: str, **kwargs):
    kwargs.setdefault("autozoom", True)
    cmd = ["fbi", "-T", "2", "-noverbose"]
    for arg in controllable_args:
        if arg in kwargs:
            cmd.append(f"-{arg}")
    cmd.append(str(image))
    subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
