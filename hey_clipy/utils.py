import shlex
import subprocess
import sys


def _exit(return_code=1, reason=None):
    if reason:
        sys.stderr.write(f"\n{reason}\n")
    sys.exit(return_code)


def bash(command, timeout=None, cwd=None, command_verify=True, command_print=True, env=None):
    if command_verify:
        try:
            prompt_options = "Please type [yes] to continue, [skip] to skip this step, [^C] to exit: "
            input_prompt = f"Do you wish to run the following command:\n{command!r}\n{prompt_options}"
            response = input(input_prompt)
            while (
                response not in ["yes", "skip"]
            ):
                response = input(input_prompt)

            if response == "skip":
                return
        except KeyboardInterrupt:
            _exit(return_code=-1, reason="Interrupt, exiting")
    elif command_print:
        print(f"Running: {command!r}")

    args = shlex.split(f"/usr/bin/env bash -e -c {shlex.quote(command)}")
    with subprocess.Popen(args=args, stdout=sys.stdout, stderr=sys.stderr, cwd=cwd, env=env) as proc:
        proc.wait(timeout=timeout)

    if proc.returncode:
        _exit(return_code=proc.returncode)


def get_executor_hostname(host_matrix, cluster_name):
    for entry in host_matrix:
        if entry["compiled_regex"].match(cluster_name):
            if entry.get("executor", True) or entry.get("hostname_format"):
                return entry["hostname_format"].format(cluster_name=cluster_name), entry.get("username")
            else:
                return "no-executor", None

    return None, None


def get_cluster_directory(host_matrix, cluster_name):
    for entry in host_matrix:
        if entry["compiled_regex"].match(cluster_name):
            if entry.get("cluster_directory"):
                return entry["cluster_directory"]
            break

    return None
