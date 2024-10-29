import argparse
import logging
import os
from pathlib import Path

import kubernetes
from ocp_resources.resource import get_client

from hey_clipy.network import BastionProxy
from hey_clipy.openshift import OpenShiftCluster
from hey_clipy.sync import sync, sync_help_cli_file
from hey_clipy.ssh import SSH, SCP, SSHCopyID
from hey_clipy.utils import _exit, bash, get_cluster_directory


LOGGER = logging.getLogger(__name__)


def _assert(condition, message):
    if not condition:
        _exit(reason=message)


def _add_subparser(subparsers, parser_name, *additional_arguments):
    new_parser = subparsers.add_parser(parser_name)
    for arg in additional_arguments:
        new_parser.add_argument(arg)
    return new_parser


def _parse_arguments():
    parser = argparse.ArgumentParser(prog="h")
    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands',
        help='additional help',
        dest="command",
    )
    subparsers.add_parser("help")
    subparsers.add_parser("test")
    subparsers.add_parser("update")
    subparsers.add_parser("log")
    subparsers.add_parser("fix")

    _add_subparser(subparsers, "get-config", "cluster_name")
    _add_subparser(subparsers, "activate", "cluster_name")
    _add_subparser(subparsers, "ssh", "cluster_name")
    _add_subparser(subparsers, "ssh-bash", "cluster_name")
    _add_subparser(subparsers, "ssh-copy-id", "cluster_name")
    _add_subparser(subparsers, "ssh-tmux", "cluster_name")
    _add_subparser(subparsers, "sync", "cluster_name")
    _add_subparser(subparsers, "bastion", "cluster_name")

    return parser, parser.parse_args()


def get_cluster_name_kube_config_path(parsed_args):
    cluster_name = getattr(parsed_args, "cluster_name", None)
    kube_config_path = None
    if cluster_name:
        kube_config_path = os.path.join(Path.home(), f".kube/{cluster_name}/kubeconfig")
        if os.path.isfile(kube_config_path) and parsed_args.command not in ["activate"]:
            bash(
                command="echo \"KUBECONFIG=${KUBECONFIG}\"; oc get clusterversion || true",
                env={
                    "PATH": os.environ.get("PATH"),
                    "KUBECONFIG": kube_config_path,
                },
            )

    return cluster_name, kube_config_path


def main(config):
    parser, parsed_args = _parse_arguments()
    cluster_name, cluster_name_local_kube_config_path = get_cluster_name_kube_config_path(parsed_args)

    if parsed_args.command == "help":
        parser.print_help()
    elif parsed_args.command == "test":
        bash(command="echo 'hello there'", command_verify=False)
    elif parsed_args.command == "update":
        return
    elif parsed_args.command == "log":
        bash(command="git log -n 5 --oneline", command_verify=False)
    elif parsed_args.command == "fix":
        bash(command="git rebase -i HEAD~2", command_verify=False)
    elif parsed_args.command == "get-config":
        bash(command=f"mkdir -p ~/.kube/{cluster_name}", command_verify=False)

        cluster_directory = (
            get_cluster_directory(host_matrix=config.HOST_MATRIX, cluster_name=cluster_name)
            or config.CLUSTER_DIRECTORY
        )

        remote_commands = f"\"{cluster_directory}/{cluster_name}/auth/*\" ~/.kube/{cluster_name}/"

        bash(
            command=SCP(
                config=config,
                cluster_name=cluster_name,
            ).get_command(remote_commands=remote_commands)
        )
        print(f"Run:\nexport KUBECONFIG=~/.kube/{cluster_name}/kubeconfig\n\n")
    elif parsed_args.command == "activate":
        try:
            client = get_client(config_file=cluster_name_local_kube_config_path)
        except kubernetes.config.config_exception.ConfigException:
            LOGGER.warning("Missing or invalid configuration file, run 'h get-config <cluster_name>'")
            client = None

        cluster = OpenShiftCluster(
            config=config,
            cluster_name=cluster_name,
            client=client,
        )

        oc_command = None
        virtctl_command = None
        if client:
            oc_command = cluster.get_download_oc()
            virtctl_command = cluster.get_download_virtctl()

        print(
            "Run:\n"
            f"export KUBECONFIG={cluster_name_local_kube_config_path}\n"
            f"{oc_command}\n"
            f"{virtctl_command}\n\n"
        )
    elif parsed_args.command in ["ssh", "ssh-bash", "ssh-tmux"]:
        file_name = ".sarahbx_cli_bash_profile"
        if parsed_args.command in ["ssh", "ssh-tmux"]:
            bash(
                command=sync_help_cli_file(config=config, cluster_name=cluster_name, file_path=file_name, remote_home="~"),
                command_verify=False,
            )

        if parsed_args.command == "ssh":
            remote_commands = f"bash --init-file \"${{HOME}}/{file_name}\" -i"
        elif parsed_args.command == "ssh-bash":
            remote_commands = "/usr/bin/env bash -i"
        else:
            remote_commands = None

        bash(
            command=SSH(
                config=config,
                cluster_name=cluster_name
            ).get_command(remote_commands=remote_commands),
            command_verify=False,
        )
    elif parsed_args.command == "ssh-copy-id":
        bash(
            command=SSHCopyID(
                config=config,
                cluster_name=cluster_name
            ).get_command(),
            command_verify=True,
        )
    elif parsed_args.command == "sync":
        bash(
            command=sync(config=config, cluster_name=cluster_name),
            command_verify=True,
        )
    elif parsed_args.command == "bastion":
        bash(
            command=BastionProxy(config=config, cluster_name=cluster_name).get_command(),
            command_verify=False,
        )
