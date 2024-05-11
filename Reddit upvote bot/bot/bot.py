import contextlib
import time, enum, random, logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


from .ghost_logger import GhostLogger


class DefaultLinksEnum(enum.Enum):
    home = "https://www.reddit.com/"
    login = "https://www.reddit.com/login/"


class Timeouts:
    def srt() -> None:
        """short timeout"""
        time.sleep(random.random() + random.randint(0, 1))

    def med() -> None:
        """medium timeout"""
        time.sleep(random.random() + random.randint(1, 2))

    def lng() -> None:
        """long timeout"""
        time.sleep(random.random() + random.randint(3, 5))

class RedditBot:
    def __init__(self, verbose: bool = False):
        self.logger = GhostLogger
        if verbose:
            self.verbose = True
            # configure logging
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(logging.StreamHandler())
            formatter = logging.Formatter(
                "\033[93m[INFO]\033[0m %(asctime)s \033[95m%(message)s\033[0m"
            )
            self.logger.handlers[0].setFormatter(formatter)

        self.logger.info("Booting up webdriver")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("log-level=3")
        chrome_options.add_argument("--lang=en")
        chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}
        )
        self.dv = webdriver.Chrome(
            chrome_options=chrome_options, executable_path=r"chromedriver.exe"
        )
        self.logger.info("Webdriver booted up")

    def login(self, username: str, password: str):
        # clear data first
        self.logout()
        self.dv.get(DefaultLinksEnum.login.value)
        print(DefaultLinksEnum.login.value)
        self.logger.info(f"Logging in as \033[4m{username}\033[0m")
        self.dv.get(DefaultLinksEnum.login.value)

        # username
        try:
            username_field = self.dv.find_element(By.NAME, "username")
        except NoSuchElementException:
            WebDriverWait(self.dv, 20).until(
                EC.frame_to_be_available_and_switch_to_it(
                    (
                        By.XPATH,
                        '//*[@id="SHORTCUT_FOCUSABLE_DIV"]/div[3]/div[2]/div/iframe',
                    )
                )
            )
            username_field = self.dv.find_element(By.NAME, "username")

        for ch in username:
            username_field.send_keys(ch)
            Timeouts.srt()
        Timeouts.med()

        # password
        password_field = self.dv.find_element(By.NAME, "password")

        for ch in password:
            password_field.send_keys(ch)
            Timeouts.srt()
        Timeouts.med()

        # sign in
        with contextlib.suppress(Exception):
            password_field.send_keys(Keys.ENTER)
        Timeouts.med()

        assert "https://www.reddit.com/login" not in self.dv.current_url, "Login failed"

        self._popup_handler()
        self._cookies_handler()
        self.logger.info("Logged in successfully.")
        
    def logout(self) -> None:
        self.logger.info(f"Clearing browser data")
        Timeouts.med()
        self.dv.delete_all_cookies()

    def vote(self, link: str, action: bool, counter: int) -> None:
        """action: True to upvote, False to downvote"""
        if action:
            self.logger.info(f"Upvoting \033[4m{link}\033[0m")
        else:
            self.logger.info(f"Downvoting \033[4m{link}\033[0m")

        self._get_link(link, handle_nsfw=True)

        if action:
            if counter == 0:
                try:
                    button = self.dv.find_element(By.XPATH, "//*[@id='upvote-button-t3_1akdqfy']/span")
                    print("Clicked-----------------------------------------")
                except:
                    print("!!!!!!!Error!!!!!!!")
                    print("Address not found")
            if counter == 1:
                try:
                    button = self.dv.find_element(By.XPATH, "//*[@id='upvote-button-t3_1akdoli']")
                    print("Clicked-----------------------------------------")
                except:
                    print("!!!!!!!Error!!!!!!!")                    
                    print("Address not found")
        else:
            button = self.dv.find_element(By.XPATH,
                "//*//div[2]/span/span/button[1]/span/svg" 
            )
        try:
            button.click()
        except:
            print("!!!!!!!hata!!!!!!!")
            print("Button not found")
        Timeouts.med()



    def _get_link(self, link: str, handle_nsfw: bool = False) -> None:
        self.dv.get(link)
        Timeouts.med()

        if handle_nsfw:
            with contextlib.suppress(NoSuchElementException):
                nsfw_button = self.dv.find_element(By.XPATH,
                    "/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[2]/button"
                )
                nsfw_button.click()
            Timeouts.med()

    def _popup_handler(self) -> None:
        with contextlib.suppress(NoSuchElementException):
            close_button = self.dv.find_element(By.XPATH,
                "/html/body/div[1]/div/div[2]/div[1]/header/div/div[2]/div[2]/div/div[1]/span[2]/div/div[2]/button"
            )
            close_button.click()

    def _cookies_handler(self) -> None:
        with contextlib.suppress(NoSuchElementException):
            accept_button = self.dv.find_element(By.XPATH,
                "/html/body/div[1]/div/div/div/div[3]/div/form/div/button"
            )
            accept_button.click()

    def _dispose(self) -> None:
        self.logger.info("Disposing webdriver")
        self.dv.quit()
