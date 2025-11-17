import datetime
import logging
import threading

from playwright.sync_api import sync_playwright
from abc import ABC


from . import utils
from .anti_detect import get_random_user_agent, get_anti_detection_script
from .ad_tracker import get_ad_tracker
from .ad_detector import detect_ads_on_page

logger = logging.getLogger(__name__)


class Instance(ABC):
    site_name = "BASE"
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
        browser_type="chromium",  # Add browser_type parameter
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
        self.browser_type = browser_type.lower()  # "chromium" or "firefox"

        # Store reference to SOCKS5 proxy server if created
        self.socks5_proxy_server = None

        # Ad tracking
        self.ad_tracker = get_ad_tracker()
        self.last_ad_check_time = None
        self.ads_detected_count = 0

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
        if cls.site_name != "UNKNOWN":
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
        
        # Clean up SOCKS5 proxy server if it was created
        if hasattr(self, 'socks5_proxy_server') and self.socks5_proxy_server:
            try:
                self.socks5_proxy_server.shutdown()
            except:
                pass
            self.socks5_proxy_server = None

    def start(self):
        try:
            self.spawn_page()
            self.todo_after_spawn()
            self.loop_and_check()
        except Exception as e:
            message = e.args[0][:25] if e.args else ""
            logger.exception(f"{e} died at page {self.page.url if self.page else None}")
            print(f"{self.site_name} Instance {self.id} died: {type(e).__name__}:{message}... Please see cvamp.log.")
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
        proxy_dict = self.proxy_dict

        if not proxy_dict:
            proxy_dict = None

        self.status = utils.InstanceStatus.RESTARTING if restart else utils.InstanceStatus.STARTING

        # Check if we have a SOCKS5 proxy with authentication (which requires local proxy workaround)
        has_socks5_auth = proxy_dict and "socks5://" in proxy_dict.get("server", "") and proxy_dict.get("username", "")

        # Generate random user agent for anti-detection
        user_agent = get_random_user_agent(self.browser_type)

        if has_socks5_auth:
            try:
                from .proxy_forwarder import create_socks5_forwarding_proxy
                
                # Construct the full SOCKS5 URL
                socks_url = f"socks5://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['server'].replace('socks5://', '')}"
                
                # Create the local proxy server that forwards to SOCKS5 with auth
                proxy_server, local_proxy_url = create_socks5_forwarding_proxy(socks_url)
                
                # Store references so we can clean them up later
                self.socks5_proxy_server = proxy_server
                
                logger.info(f"Created local proxy server for SOCKS5 authentication: {local_proxy_url}")
                
                # Now launch the browser with the local proxy
                self.playwright = sync_playwright().start()
                if self.browser_type == "firefox":
                    FF_ARGS = []
                    if self.headless:
                        FF_ARGS.append("--headless")
                    self.browser = self.playwright.firefox.launch(
                        proxy={"server": local_proxy_url},
                        headless=self.headless,
                        args=FF_ARGS,
                    )
                    browser_name = "firefox"
                    
                    self.context = self.browser.new_context(
                        viewport={"width": 800, "height": 600},
                        user_agent=user_agent,  # Use random user agent
                        proxy={"server": local_proxy_url},
                    )
                else:  # chromium
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
                        proxy={"server": local_proxy_url},
                        channel="chrome",
                        headless=False,
                        args=CHROMIUM_ARGS,
                    )
                    browser_name = "chromium"

                    context_params = {
                        "viewport": {"width": 800, "height": 600},
                        "proxy": {"server": local_proxy_url},
                        "user_agent": user_agent,  # Use random user agent
                    }
                    self.context = self.browser.new_context(**context_params)

            except ImportError as e:
                logger.warning(f"Failed to create SOCKS5 forwarder for instance {self.id}: {e}")
                logger.warning(f"Falling back to no-proxy mode.")
                
                # Fall back to no proxy
                self.playwright = sync_playwright().start()
                if self.browser_type == "firefox":
                    FF_ARGS = []
                    if self.headless:
                        FF_ARGS.append("--headless")
                    self.browser = self.playwright.firefox.launch(
                        headless=self.headless,
                        args=FF_ARGS,
                    )
                    browser_name = "firefox"
                    
                    context_params = {
                        "viewport": {"width": 800, "height": 600},
                        "user_agent": user_agent  # Use random user agent
                    }
                    self.context = self.browser.new_context(**context_params)
                else:  # chromium
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
                        channel="chrome",
                        headless=False,
                        args=CHROMIUM_ARGS,
                    )
                    browser_name = "chromium"

                    context_params = {
                        "viewport": {"width": 800, "height": 600},
                        "user_agent": user_agent  # Use random user agent
                    }
                    self.context = self.browser.new_context(**context_params)
        else:
            # Regular proxy handling (HTTP proxies or SOCKS5 without auth)
            self.playwright = sync_playwright().start()
            if self.browser_type == "firefox":
                FF_ARGS = []
                if self.headless:
                    FF_ARGS.append("--headless")

                self.browser = self.playwright.firefox.launch(
                    proxy=proxy_dict,
                    headless=self.headless,
                    args=FF_ARGS,
                )
                browser_name = "firefox"
                
                self.context = self.browser.new_context(
                    viewport={"width": 800, "height": 600},
                    user_agent=user_agent,  # Use random user agent
                    proxy=proxy_dict,
                )
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

                # Create context with proxy
                context_params = {
                    "viewport": {"width": 800, "height": 600},
                    "proxy": proxy_dict,
                    "user_agent": user_agent,  # Use random user agent
                }

                self.context = self.browser.new_context(**context_params)

        self.page = self.context.new_page()

        # Add comprehensive anti-detection script
        anti_detect_script = get_anti_detection_script()
        self.page.add_init_script(anti_detect_script)

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

    def check_for_ads(self):
        """
        Check if ads are currently playing and update tracking if needed
        """
        if not self.page:
            return False
        
        try:
            # Determine platform from target URL
            platform = "unknown"
            if "twitch.tv" in self.target_url:
                platform = "twitch"
            elif "youtube.com" in self.target_url or "youtu.be" in self.target_url:
                platform = "youtube"
            elif "kick.com" in self.target_url:
                platform = "kick"
            elif "chzzk.naver.com" in self.target_url:
                platform = "chzzk"
            
            # Check for ads on the current platform
            ad_detected = detect_ads_on_page(self.page, platform)
            
            if ad_detected:
                current_time = datetime.datetime.now()
                
                # Only record if enough time has passed since last check to avoid duplicates
                if (not self.last_ad_check_time or 
                    (current_time - self.last_ad_check_time).seconds > 5):
                    
                    self.ad_tracker.record_ad_detected(self.id)
                    self.ads_detected_count += 1
                    self.last_ad_check_time = current_time
                    logger.info(f"Ad detected for instance {self.id}. Total ads for this instance: {self.ads_detected_count}")
                
                return True
            return False
        except Exception as e:
            logger.warning(f"Error checking for ads on instance {self.id}: {e}")
            return False

    def update_status(self) -> None:
        """
        Mechanism is called every loop. Figure out if it is watching and working and updated status.
        Also check for ads and track them.
        """
        # Check for ads first
        self.check_for_ads()
        
        # The rest of the logic depends on the specific site implementation
        # For the base class, we just pass - specific site classes override this
        pass