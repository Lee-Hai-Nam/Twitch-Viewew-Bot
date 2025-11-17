import datetime
import logging
import threading

from playwright.sync_api import sync_playwright
from abc import ABC


from . import utils

logger = logging.getLogger(__name__)


class FirefoxInstance(ABC):
    """Firefox-specific instance implementation"""
    site_name = "FIREFOX_BASE"
    site_url = None
    instance_lock = threading.Lock()
    supported_sites = dict()

    def __init__(
        self,
        proxy_dict,
        target_url,
        status_reporter,
        location_info=None,
        headless=False,
        auto_restart=False,
        instance_id=-1,
        browser_type="firefox"
    ):
        self.playwright = None
        self.context = None
        self.browser = None
        self.status_info = {}
        self.status_reporter = status_reporter
        self.thread = threading.current_thread()

        self.id = instance_id
        self._status = "alive"
        self.proxy_dict = proxy_dict
        self.target_url = target_url
        self.headless = headless
        self.auto_restart = auto_restart
        self.browser_type = browser_type  # "firefox" or "chromium"

        self.last_restart_dt = datetime.datetime.now()

        self.location_info = location_info
        if not self.location_info:
            self.location_info = {
                "index": -1,
                "x": 0,
                "y": 0,
                "width": 500,
                "height": 300,
                "free": True,
            }

        self.command = None
        self.page = None

    def __init_subclass__(cls, **kwargs):
        if cls.site_name != "FIREFOX_UNKNOWN":
            cls.supported_sites[cls.site_url] = cls

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        if self._status == new_status:
            return

        self._status = new_status
        self.status_reporter(self.id, new_status)

    def clean_up_playwright(self):
        if any([self.page, self.context, self.browser]):
            try:
                self.page.close()
            except:
                pass
            try:
                self.context.close()
            except:
                pass
            try:
                self.browser.close()
            except:
                pass
            try:
                self.playwright.stop()
            except:
                pass

    def start(self):
        try:
            self.spawn_page()
            self.todo_after_spawn()
            self.loop_and_check()
        except Exception as e:
            message = e.args[0][:25] if e.args else ""
            logger.exception(f"{e} died at page {self.page.url if self.page else None}")
            print(f"{self.browser_type.upper()} Instance {self.id} died: {type(e).__name__}:{message}... Please see cvamp.log.")
        else:
            logger.info(f"ENDED: instance {self.id}")
            with self.instance_lock:
                print(f"Instance {self.id} shutting down")
        finally:
            self.status = utils.InstanceStatus.SHUTDOWN
            self.clean_up_playwright()
            self.location_info["free"] = True

    def loop_and_check(self):
        page_timeout_s = 10
        while True:
            self.page.wait_for_timeout(page_timeout_s * 1000)
            self.todo_every_loop()
            self.update_status()

            if self.command == utils.InstanceCommands.RESTART:
                self.clean_up_playwright()
                self.spawn_page(restart=True)
                self.todo_after_spawn()
            if self.command == utils.InstanceCommands.SCREENSHOT:
                print("Saved screenshot of instance id", self.id)
                self.save_screenshot()
            if self.command == utils.InstanceCommands.REFRESH:
                print("Manual refresh of instance id", self.id)
                self.reload_page()
            if self.command == utils.InstanceCommands.EXIT:
                return
            self.command = utils.InstanceCommands.NONE

    def save_screenshot(self):
        filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + f"_instance{self.id}.png"
        self.page.screenshot(path=filename)

    def spawn_page(self, restart=False):
        FF_ARGS = [
            "--width=500",
            "--height=300",
        ]

        if self.headless:
            FF_ARGS.append("--headless")

        proxy_dict = self.proxy_dict

        if not proxy_dict:
            proxy_dict = None

        self.status = utils.InstanceStatus.RESTARTING if restart else utils.InstanceStatus.STARTING

        self.playwright = sync_playwright().start()

        # Launch appropriate browser based on browser_type
        if self.browser_type.lower() == "firefox":
            self.browser = self.playwright.firefox.launch(
                proxy=proxy_dict,
                headless=False,  # Firefox in headless mode might not work with all features
                args=FF_ARGS,
            )
            browser_name = "firefox"
        else:  # Default to chromium
            CHROMIUM_ARGS = [
                "--window-position={},{}".format(self.location_info["x"], self.location_info["y"]),
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--no-first-run",
                "--disable-blink-features=AutomationControlled",
                "--mute-audio",
                "--webrtc-ip-handling-policy=disable_non_proxied_udp",
                "--force-webrtc-ip-handling-policy",
            ]

            if self.headless:
                CHROMIUM_ARGS.append("--headless")

            self.browser = self.playwright.chromium.launch(
                proxy=proxy_dict,
                channel="chrome",
                headless=False,
                args=CHROMIUM_ARGS,
            )
            browser_name = "chromium"

        major_version = self.browser.version.split(".")[0]
        
        # Create context with proxy
        context_params = {
            "viewport": {"width": 800, "height": 600},
            "proxy": proxy_dict,
        }
        
        # Set appropriate user agent for the browser type
        if browser_name == "firefox":
            context_params["user_agent"] = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{major_version}.0) Gecko/20100101 Firefox/{major_version}.0"
        else:
            context_params["user_agent"] = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{major_version}.0.0.0 Safari/537.36"

        self.context = self.browser.new_context(**context_params)

        self.page = self.context.new_page()
        
        # Add script to avoid detection (different for Firefox)
        if browser_name == "firefox":
            self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
        else:
            self.page.add_init_script("""navigator.webdriver = false;""")

    def goto_with_retry(self, url, max_tries=3, timeout=20000):
        """
        Tries to navigate to a page max_tries times. Raises the last exception if all attempts fail.
        """
        for attempt in range(1, max_tries + 1):
            try:
                self.page.goto(url, timeout=timeout)
                return
            except Exception:
                logger.warning(f"Instance {self.id} failed connection attempt #{attempt}.")
                if attempt == max_tries:
                    raise

    def todo_after_load(self):
        self.goto_with_retry(self.target_url)
        self.page.wait_for_timeout(1000)

    def reload_page(self):
        self.page.reload(timeout=30000)
        self.todo_after_load()

    def todo_after_spawn(self):
        """
        Basic behaviour after a page is spawned. Override for more functionality
        e.g. load cookies, additional checks before instance is truly called "initialized"
        :return:
        """
        self.status = utils.InstanceStatus.INITIALIZED
        self.goto_with_retry(self.target_url)

    def todo_every_loop(self):
        """
        Add behaviour to be executed every loop
        e.g. to fake page interaction to not count as inactive to the website.
        """
        pass

    def update_status(self) -> None:
        """
        Mechanism is called every loop. Figure out if it is watching and working and updated status.
        if X:
            self.status = utils.InstanceStatus.WATCHING
        """
        pass