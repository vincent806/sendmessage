## Description:
This script aims to build a generic kit to push message to various message channels.
## Supported message channels:
  1. iOS - Bark
  2. ServerChan
  3. PushPlus
  4. Iyuu
  5. SMTP
  6. DingTalk
  7. FeiShu
  8. WxBot - Robot for Chatgroup in Enterprise Wechat
  9. WxApp - App message for Enterpise Wechat
 10. Telegram - Bot
## Usage:
1. Refer to config-example.yml and create your own config.yml
2. Call this script like this:
```
python3 sendmessage.py 'title','line 1', 'line 2', 'line 3'[..., 'line x']
```
3. If your config file is stored somewhere else, try to call as below and make sure --config or -c is the first parameter
```
python3 sendmessage.py --config='otherconfig.yml' 'title','line 1', 'line 2', 'line 3'[..., 'line x']
```
## Environment:
This script is developed under python version 3.10.  Ideally it works in most of the python 3.x version but the latest version is always recommended.
Packages that you may need to install if you have not:
```
pip3 install pyyaml
```
## Disclaimer:
The author assumes no responsibility or liability for any errors or omissions in this script.
