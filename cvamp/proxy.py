import logging
import os
import random

logger = logging.getLogger(__name__)


class ProxyGetter:
    def __init__(self, proxy_file_name="proxy_list.txt"):
        self.proxy_list = []
        self.pathed_file_name = os.path.join(os.getcwd(), "proxy", proxy_file_name)
        self.build_proxy_list()

    def build_proxy_list(self):
        try:
            if self.pathed_file_name.endswith(".txt"):
                self.build_proxy_list_txt()
            else:
                print("File type not supported")
        except Exception as e:
            logger.exception(e)
            raise FileNotFoundError(f"Unable to find {self.pathed_file_name}")

    def build_proxy_list_txt(self):
        with open(self.pathed_file_name, "r") as fp:
            proxy_list = [line.strip() for line in fp if line.strip()]

        for proxy in proxy_list:
            # Handle socks5://user:pass@host:port format
            if proxy.startswith("socks5://") and "@" in proxy:
                try:
                    # Extract the server part after 'socks5://'
                    server_part = proxy[9:]  # Remove 'socks5://' prefix
                    auth_part, addr_part = server_part.split("@", 1)
                    username, password = auth_part.split(":", 1)
                    ip, port = addr_part.split(":", 1)
                    
                    self.proxy_list.append({
                        "server": f"socks5://{ip}:{port}",
                        "username": username,
                        "password": password,
                    })
                except ValueError:
                    logger.warning(f"Invalid socks5://user:pass@host:port format: {proxy}")
            # Handle socks5://host:port format (no auth)
            elif proxy.startswith("socks5://"):
                server_part = proxy.replace("socks5://", "")
                try:
                    ip, port = server_part.split(":", 1)
                    self.proxy_list.append({
                        "server": f"socks5://{ip}:{port}",
                        "username": "",
                        "password": "",
                    })
                except ValueError:
                    logger.warning(f"Invalid socks5://host:port format: {proxy}")
            # Handle regular HTTP/HTTPS proxy formats
            else:
                proxy_parts = proxy.split(":")
                if len(proxy_parts) == 4:
                    ip, port, username, password = proxy_parts
                    if username.lower() != "username":
                        self.proxy_list.append(
                            {
                                "server": f"http://{ip}:{port}",
                                "username": username,
                                "password": password,
                            }
                        )
                    else:
                        logger.warning(f"Skipping proxy with placeholder username: {proxy}")
                elif len(proxy_parts) == 2:
                    ip, port = proxy_parts
                    self.proxy_list.append(
                        {
                            "server": f"http://{ip}:{port}",
                            "username": "",
                            "password": "",
                        }
                    )
                else:
                    # Try to parse custom format like "socks5:ip:port:user:pass"
                    custom_parts = proxy.split(":")
                    if len(custom_parts) >= 4 and custom_parts[0] in ["socks5", "socks4"]:
                        protocol = custom_parts[0]
                        ip = custom_parts[1]
                        port = custom_parts[2]
                        if len(custom_parts) == 4:  # socks5:ip:port:password (no username)
                            self.proxy_list.append({
                                "server": f"{protocol}://{ip}:{port}",
                                "username": "",
                                "password": custom_parts[3],
                            })
                        elif len(custom_parts) == 5:  # socks5:ip:port:user:password
                            self.proxy_list.append({
                                "server": f"{protocol}://{ip}:{port}",
                                "username": custom_parts[3],
                                "password": custom_parts[4],
                            })
                        else:
                            logger.warning(f"Invalid custom proxy format: {proxy}")
                    else:
                        logger.warning(f"Invalid proxy format: {proxy}")

    def get_proxy_as_dict(self) -> dict:
        if not self.proxy_list:
            return {}

        proxy = self.proxy_list.pop(-1)
        self.proxy_list.insert(0, proxy)
        return proxy
