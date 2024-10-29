import os
import shlex

from hey_clipy.exceptions import HelpCLIUnsupportedRemoteHost
from hey_clipy.utils import get_executor_hostname


class SSH:
    def __init__(self, config, cluster_name):
        self.config = config
        self.cluster_name = cluster_name

        self.remote_host, self.ssh_user = get_executor_hostname(host_matrix=self.config.HOST_MATRIX, cluster_name=self.cluster_name)
        assert self.remote_host, f"Remote host is {self.remote_host!r}"

        self.ssh_key_path = self.config.SSH_KEY
        if not self.ssh_user:
            self.ssh_user = self.config.SSH_USER

        self.remote_base_dir = os.path.join("~", self.config.IDM_USER)

    @staticmethod
    def remote_bash(remote_dir, command):
        _bash_command = "/usr/bin/env bash -l -c"
        return f"cd {remote_dir} && {_bash_command} \"{command}\""

    def get_command(self, remote_commands=None):
        if self.remote_host == "no-executor":
            raise HelpCLIUnsupportedRemoteHost(f"Unsupported host: {self.remote_host}")

        if not remote_commands:
            remote_commands = (
                f"mkdir -p {self.config.REMOTE_HOME} "
                f"&& cd ~/{self.config.IDM_USER} "
                r"&& export PS1='exit $?: $(date -u)\n\n${USER} \w\n($(git rev-parse --abbrev-ref HEAD 2>/dev/null))$ ' "
                f"&& tmux set-option -g history-limit {self.config.TMUX_SESSION_LIMIT} \\; "
                f"new-session -A -s {self.config.TMUX_SESSION} -t {self.config.TMUX_SESSION}"
            )
        remote_commands = shlex.quote(remote_commands)

        ssh_cmd_fmt = "ssh -t -i {ssh_key_path} {ssh_user}@{remote_host} {remote_commands}"
        return ssh_cmd_fmt.format(
            ssh_key_path=self.ssh_key_path,
            ssh_user=self.ssh_user,
            remote_host=self.remote_host,
            remote_commands=remote_commands,
        )


class SCP(SSH):
    def get_command(self, remote_commands=None):
        scp_cmd_fmt = "scp -i {ssh_key_path} {ssh_user}@{remote_host}:{remote_commands}"
        return scp_cmd_fmt.format(
            ssh_key_path=self.ssh_key_path,
            ssh_user=self.ssh_user,
            remote_host=self.remote_host,
            remote_commands=remote_commands,
        )


class SSHCopyID(SSH):
    def get_command(self, remote_commands=None):
        cmd_fmt = "ssh-copy-id -i {ssh_key_path} {ssh_user}@{remote_host}"
        return cmd_fmt.format(
            ssh_key_path=self.config.LOCAL_SSH_KEY,
            ssh_user=self.ssh_user,
            remote_host=self.remote_host,
        )
