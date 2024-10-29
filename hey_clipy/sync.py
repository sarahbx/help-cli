import os

from hey_clipy.exceptions import HelpCLIUnsupportedRemoteHost
from hey_clipy.utils import get_executor_hostname


EXCLUDE_FROM_SYNC = [".git", ".tox", "venv", ".idea", "__pycache__", "containers"]

# rsync -a == rsync -rlptgoD, dont use -a due to
# https://github.blog/2022-04-18-highlights-from-git-2-36/#stricter-repository-ownership-checks
_CMD_SYNC_GERRIT_CWD = (
    f"rsync -rlptDvz --delete-after --exclude {' --exclude '.join(EXCLUDE_FROM_SYNC)} "
    "-e 'ssh -i {SSH_KEY}' {cwd}/ "
    "{ssh_user}@{remote_host}:{REMOTE_HOME}/{cwd_name}"
)

_CMD_SYNC_FILE = (
    "rsync -avz -e 'ssh -i {SSH_KEY}' {hey_file_path} "
    "{ssh_user}@{remote_host}:{remote_home}/{file_basename}"
)


def sync(config, cluster_name):
    remote_host, ssh_user = get_executor_hostname(host_matrix=config.HOST_MATRIX, cluster_name=cluster_name)
    assert remote_host, f"Remote host is {remote_host!r}"

    if remote_host == "localhost":
        raise HelpCLIUnsupportedRemoteHost(remote_host)

    if not ssh_user:
        ssh_user = config.SSH_USER

    cwd = os.getcwd()
    assert cwd.startswith(os.path.join(config.HOME, "git")), "Unsupported path to sync"

    cwd_name = os.path.basename(cwd)

    return _CMD_SYNC_GERRIT_CWD.format(
        remote_host=remote_host,
        ssh_user=ssh_user,
        cwd=cwd,
        cwd_name=cwd_name,
        **config.__dict__,
    )


def sync_help_cli_file(config, cluster_name, file_path, remote_home):
    hey_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), file_path)
    assert os.path.isfile(hey_file_path)

    remote_host, ssh_user = get_executor_hostname(host_matrix=config.HOST_MATRIX, cluster_name=cluster_name)
    assert remote_host, f"Remote host is {remote_host!r}"

    if remote_host == "localhost":
        raise HelpCLIUnsupportedRemoteHost(remote_host)

    if not ssh_user:
        ssh_user = config.SSH_USER

    file_basename = os.path.basename(file_path)
    return _CMD_SYNC_FILE.format(
        hey_file_path=hey_file_path,
        remote_host=remote_host,
        ssh_user=ssh_user,
        file_basename=file_basename,
        remote_home=remote_home,
        **config.__dict__,
    )