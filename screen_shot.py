from browser import Browser


class ScreenShot:
    """
    指定URLのスクリーンショットを取る

    """

    def __init__(
        self,
        url: str,
        screen_shot_base_name: str,
        width: int,
        height: int,
    ):
        self.url = url
        self.screen_shot_base_name = screen_shot_base_name
        self.__browser = Browser(width, height)

    def screen_shot(self):
        # ページを開く
        self.__browser.start()
        self.__browser.open(self.url)

        # スクロールしながら、スクリーンショットを取る
        idx = 1
        while True:
            self.__browser.wait(2)
            self.__browser.save_screenshot(
                f'{self.screen_shot_base_name}{idx}.png'
            )
            idx = idx + 1

            if self.__browser.page_down_by_arrow(13):
                break
