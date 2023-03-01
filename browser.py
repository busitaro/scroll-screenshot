import time
import os
import signal
import math
from urllib.parse import urlparse

import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


class Browser:
    """
    Seleniumの機能をラップしたクラス

    """
    def __init__(self, width: int, height: int):
        self.__driver = None
        self.__wait = None
        self.__width = width
        self.__height = height

    def start(self):
        """
        ブラウザを起動する

        """
        # WebDriver のオプションを設定する
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('no-sandbox')
        options.add_argument('--start-maximized')
        options.add_argument(f'--window-size={self.__width},{self.__height}')

        capabilities = DesiredCapabilities.CHROME.copy()
        capabilities['acceptInsecureCerts'] = True

        self.__driver = \
            webdriver.Chrome(
                options=options, desired_capabilities=capabilities
            )
        self.__wait = WebDriverWait(self.__driver, 10)

    def open(self, url: str):
        """
        指定されたURLを開く

        Params
        -----------
        url: str
            URL
        """
        self.__driver.get(url)

    def page_down(self) -> bool:
        """
        １ページ進める

        Returns
        -------
        0: bool
            True: 最下部に達した
            False: 最下部に未達
        """
        # page_downキーを送出
        el_html = self.__driver.find_element(By.TAG_NAME, 'html')
        el_html.send_keys(Keys.PAGE_DOWN)

        return self.is_bottom()

    def page_down_by_arrow(self, count):
        """
        矢印キーでページをスクロールする

        """
        for _ in range(count):
            # page_downキーを送出
            el_html = self.__driver.find_element(By.TAG_NAME, 'html')
            el_html.send_keys(Keys.DOWN)
            self.wait(0.1)

        return self.is_bottom()

    def page_up_by_arrow(self):
        """
        矢印キーでページをスクロールする

        """
        # page_downキーを送出
        el_html = self.__driver.find_element(By.TAG_NAME, 'html')
        el_html.send_keys(Keys.UP)

        return self.is_bottom()

    def is_bottom(self):
        """
        スクロールバーが最下部まで来ているか判定する

        Returns
        -------
        0: bool
            True: 最下部に達した
            False: 最下部に未達
        """
        now = \
            math.ceil(
                self.__driver.execute_script("return $(this).scrollTop();")
            )
        bottom = \
            self.__driver.execute_script(
                "return $(document).innerHeight() - $(window).innerHeight();"
            )

        return now >= bottom

    def save_screenshot(self, file_path: str):
        self.__driver.save_screenshot(file_path)

    def find_by_id(self, key: str):
        """
        idで要素を探す

        Params
        -----------
        key: str
            id
        """
        return self.__driver.find_element(By.ID, key)

    def find_by_xpath(self, key: str):
        """
        XPATHで要素を探す

        Params
        -----------
        key: str
            XPATH
        """
        return self.__driver.find_element(By.XPATH, key)

    def wait(self, seconds: int):
        """
        指定秒数待機する

        Params
        -----------
        seconds: int
            待機秒数
        """
        time.sleep(seconds)

    def wait_for_element(self, xpath: str):
        """
        要素が表示されるのを待つ

        Params
        -------
        xpath: str
            表示を待つ要素のXPATH
        """
        timeout = 10
        element = EC.presence_of_element_located((By.XPATH, xpath))
        WebDriverWait(self.__driver, timeout).until(element)

    def capture(self, filename: str):
        """
        現在ページのキャプチャをpngで取得する

        """
        self.__driver.save_screenshot(filename)

    def print_src(self):
        """
        現在ページのソースを標準出力する

        """
        print(self.__driver.page_source)

    def click(self, element):
        """
        指定された要素をクリックする

        Params
        -----------
        element
            要素

        Memo
        -----------
        a要素は直接hrefの値を取得し、リンクを踏む
        非a要素は
        seleniumでは表示されていない要素はクリックできない
        その為、指定要素を画面内に入れるスクリプトを実行する
        """
        if element.tag_name == 'a':
            href = element.get_attribute('href')
            parsed_url = urlparse(self.current_url)
            if 'http' in href:
                link = href
            else:
                link = \
                    '{}://{}/{}'.format(
                        parsed_url.scheme,
                        parsed_url.netloc,
                        href
                    )
            self.__driver.get(link)
        else:
            self.__driver.execute_script(
                "arguments[0].scrollIntoView(false);",
                element
            )
            element.click()

    def input_text(self, xpath: str, text: str):
        target = self.find_by_xpath(xpath)
        target.send_keys(text)

    def accept_alert(self):
        self.__wait.until(expected_conditions.alert_is_present())
        Alert(self.__driver).accept()

    def keep(self):
        """
        seleniumへkillシグナルを送り、
        ブラウザウィンドウを閉じないようにする

        """
        if self.__driver:
            os.kill(
                self.__driver.service.process.pid,
                signal.SIGTERM
            )
