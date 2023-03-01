# 概要

ブラウザをスクロールしつつ、スクリーンショットを取るツール  
画像の読込のディレイ等が設定されていて、Chrome のキャプチャ機能の使用が難しいページ向け

# 使い方

```
from screen_shot import ScreenShot


url = 'https://something'
capture_base_name = 'shot'

sc = ScreenShot(url, base_name, width=1366, height=768)

# store screenshot as shot1.png, shot2.png ...
sc.screen_shot()
```
