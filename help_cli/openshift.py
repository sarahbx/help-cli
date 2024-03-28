from ocp_resources.console_cli_download import ConsoleCLIDownload


class OpenShiftCluster:
    def __init__(self, config, cluster_name, client):
        self.config = config
        self.cluster_name = cluster_name
        self.client = client

    def get_download_oc(self):
        oc_link = None
        console_cli_download = ConsoleCLIDownload(client=self.client, name="oc-cli-downloads")
        links = console_cli_download.instance.spec.links
        for link in links:
            if "amd64/linux" in link["href"]:
                oc_link = link["href"]
                break

        assert oc_link, f"Invalid links: {links}"
        return f"curl -k {oc_link} | tar -xvO oc > {self.config.HOME}/bin/oc"

    def get_download_virtctl(self):
        virtctl_link = None
        console_cli_download = ConsoleCLIDownload(client=self.client, name="virtctl-clidownloads-kubevirt-hyperconverged")
        if not console_cli_download.exists:
            return ""

        links = console_cli_download.instance.spec.links
        for link in links:
            if "amd64/linux" in link["href"]:
                virtctl_link = link["href"]
                break

        assert virtctl_link, f"Invalid links: {links}"
        return f"curl -k {virtctl_link} | tar -xzvO virtctl > {self.config.HOME}/bin/virtctl"

