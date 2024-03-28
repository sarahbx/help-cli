from help_cli.ssh import SSH


class BastionProxy(SSH):
    def get_command(self, remote_commands=None):
        cmd_fmt = "ssh -i {ssh_key_path} -D 8083 -N {ssh_user}@{remote_host}"
        return cmd_fmt.format(
            ssh_key_path=self.ssh_key_path,
            ssh_user=self.ssh_user,
            remote_host=self.remote_host,
        )
