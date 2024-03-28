import os
import re
from pathlib import Path


HOME = Path.home()

IDM_USER = os.environ.get("IDM_USER", "myusername")

CLUSTER_EXECUTOR = "127.0.0.1"
CLUSTER_EXECUTOR_USER = "cloud-user"
CLUSTER_DIRECTORY = "/mnt/clusters"

GIT_GERRIT_ROOT = f"{HOME}/git/gerrit"
SSH_KEY = f"{HOME}/.ssh/ssh_key.key"
SSH_USER = ""
REMOTE_HOME = f"~/{IDM_USER}"

LOCAL_SSH_KEY = f"{HOME}/.ssh/id_ed25519.pub"

TMUX_SESSION = "myuniquename"
TMUX_SESSION_LIMIT = 100000

HOST_MATRIX = [
    {
        "compiled_regex": re.compile(r"^(prefix)-[-a-z0-9]*41[23456][-a-z0-9]*$"),
        "hostname_format": CLUSTER_EXECUTOR,
        "username": CLUSTER_EXECUTOR_USER,
        "executor": False,
    },
    {
        "compiled_regex": re.compile(r"^(prefix)-[-a-z0-9]+$"),
        "hostname_format": "executor.{cluster_name}.clusterdomain.example.test",
    },
]
