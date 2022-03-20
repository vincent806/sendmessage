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
1. Refer to section 'config.yml example' to create your own config.yml and place in the same folder as sendmessage.py
2. Call this script like this:
```
python3 sendmessage.py 'title','line 1', 'line 2', 'line 3'[..., 'line x']
```
3. If your config file is stored somewhere else, try to call as below and make sure --config or -c is the first parameter
```
python3 sendmessage.py --config='otherconfig.yml' 'title','line 1', 'line 2', 'line 3'[..., 'line x']
```

## config.yml example

**Bark**
```
bark:    #optional
  endpoint: https://<your-url>/<your-key/
  # default settings for other parameters
  group: "default"
  icon: "http://<your-host>/<your-default-icon.png>"
  sound: paymentsuccess
  automaticallyCopy: 0    #optional
  isArchive: 1    #optional
  url: "http://<your-url>/"    #optional
  level: active    #optional
  # tailor made parameters according to message title
  tailoring:
    - title: "example title 1"
      group: "group1"
      icon: "http://<your-host>/<your-icon-1.png>"
      sound: "calypso"
      automaticallyCopy: 0    #optional
      isArchive: 1    #optional
      url: "http://<your-url-1>/"    #optional
      level: active    #optional
    - title: ["example title 2-1","example title 2-2"]
      group: "group2"
      icon: "http://<your-host>/<your-icon-2.png>"
      sound: "bell"
      automaticallyCopy: 0    #optional
      isArchive: 1    #optional
      url: "http://<your-url-2>/"    #optional
      level: active    #optional
```
**ServerChan**
```
serverchan:    #optional
  sckey: <your-sckey>
```
**PushPlus**
```
pushplus:    #optional
  token: <your-token>
  channel: wechat   #optional
  template: markdown    #optional
```
**Iyuu**
```
iyuu:    #optional
  token: <your-token>
```
**SMTP**
```
smtp:    #optional
  server: <smtp-server, e.g. smtp.qq.com>
  port: 465
  sender: <sender-email, e.g. xxxx@qq.com>
  authcode: <authorization-code>
  recipient: <recipient-email, e.g. xxxx@163.com>
```
**DingTalk**
```
dingtalk:    #optional
  secret: <your-secret>
  url: <your-webhook-url>
```
**FeiShu**
```
feishu:    #optional
  secret: <your-secret>
  url: <your-webhook-url>
```
**WxBot**
```
wxbot:    #optional
  url: <your-webhook-url>
```
**WxApp**
```
wxapp:    #optional
  corpid: <your-corp-id>
  secret: <your-app-secret>
  agentid: <your-app-agentid>
  touser: <to-user-id>
  type: <message type, e.g. text>
```
**Telegram**
```
telegram:    #optional
  token: <your-token>
  chatid: <your-chatid>
```
## Environment:
This script is developed under python version 3.10.  Ideally it works in most of the python 3.x version but the latest version is always recommended.
Packages that you may need to install if you have not:
```
pip3 install pyyaml
```
## Disclaimer:
The author assumes no responsibility or liability for any errors or omissions in this script.
