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
bark:    
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
  tailoring:    #optional
    - title: "example title 1"    #optional
      group: "group1"    #optional
      icon: "http://<your-host>/<your-icon-1.png>"    #optional
      sound: "calypso"    #optional
      automaticallyCopy: 0    #optional
      isArchive: 1    #optional    #optional
      url: "http://<your-url-1>/"    #optional
      level: active    #optional    #optional
    - title: ["example title 2-1","example title 2-2"]    #optional
      group: "group2"    #optional
      icon: "http://<your-host>/<your-icon-2.png>"    #optional
      sound: "bell"    #optional
      automaticallyCopy: 0    #optional
      isArchive: 1    #optional
      url: "http://<your-url-2>/"    #optional
      level: active    #optional
    - title: [["your-regexp"]]
      group: "group3"    #optional
      icon: "http://<your-host>/<your-icon-3.png>"    #optional
      sound: "bell"    #optional
      automaticallyCopy: 0    #optional
      isArchive: 1    #optional
      url: "http://<your-url-3/"    #optional
      level: active    #optional
```
**ServerChan**
```
serverchan:    
  sckey: <your-sckey>
```
**PushPlus**
```
pushplus:    
  token: <your-token>
  channel: wechat   #optional
  template: markdown    #optional
```
**Iyuu**
```
iyuu:    
  token: <your-token>
```
**SMTP**
```
smtp:    
  server: <smtp-server, e.g. smtp.qq.com>
  port: 465
  sender: <sender-email, e.g. xxxx@qq.com>
  authcode: <authorization-code>
  recipient: <recipient-email, e.g. xxxx@163.com>
```
**DingTalk**
```
dingtalk:    
  secret: <your-secret>
  url: <your-webhook-url>
```
**FeiShu**
```
feishu:    
  secret: <your-secret>
  url: <your-webhook-url>
```
**WxBot**
```
wxbot:    
  url: <your-webhook-url>
```
**WxApp**
```
wxapp:    
  corpid: <your-corp-id>
  secret: <your-app-secret>
  agentid: <your-app-agentid>
  touser: <to-user-id>
  type: <message type, e.g. text>
```
**Telegram**
```
telegram:    
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

## Cookbook:
1. Use sendmessage in other python code

Please refer to example code below:

```
# step 1 - import sendmessage module
import sendmessage

# step 2 - load config file
# - for windows: config = sendmessage.ConfigLoader().loadConfig(r"C:\Users\Username\myfolder\config.yml")
# - for linux: config = sendmessage.ConfigLoader().loadConfig("/home/username/myfolder/config.yml")
config = sendmessage.ConfigLoader().loadConfig()  # by default it will load config.yml in the same folder as sendmessage.py

# step 3 - send the message

# Bark example
resp = sendmessage.Bark().push(config['bark'], ["subject","ln1","ln2"]) # you can add more lines, it is flexible
print(str(resp)) #print output

# ServerChan example
resp = sendmessage.ServerChan().push(config['serverchan'], ["subject","ln1","ln2"]) # you can add more lines, it is flexible
print(str(resp)) #print output

# PushPlus example
resp = sendmessage.PushPlus().push(config['pushplus'], ["subject","ln1","ln2"]) # you can add more lines, it is flexible
print(str(resp)) #print output

# Iyuu example
resp = sendmessage.Iyuu().push(config['iyuu'], ["subject","ln1","ln2"]) # you can add more lines, it is flexible
print(str(resp)) #print output

# SMTP example
resp = sendmessage.SMTP().push(config['smtp'], ["subject","ln1","ln2"]) # you can add more lines, it is flexible
print(str(resp)) #print output

# DingTalk example
resp = sendmessage.DingTalk().push(config['dingtalk'], ["subject","ln1","ln2"]) # you can add more lines, it is flexible
print(str(resp)) #print output

# FeiShu example
resp = sendmessage.FeiShu().push(config['feishu'], ["subject","ln1","ln2"]) # you can add more lines, it is flexible
print(str(resp)) #print output

# WxBot example
resp = sendmessage.WxBot().push(config['wxbot'], ["subject","ln1","ln2"]) # you can add more lines, it is flexible
print(str(resp)) #print output

# WxApp example
resp = sendmessage.WxApp().push(config['wxapp'], ["subject","ln1","ln2"]) # you can add more lines, it is flexible
print(str(resp)) #print output

# Telegram example
resp = sendmessage.Telegram().push(config['telegram'], ["subject","ln1","ln2"]) # you can add more lines, it is flexible
print(str(resp)) #print output

```
2. Send message to multiple message channels

In config.yml file, you can put multiple message channels in any combination, for example, serverchan + iyuu + pushplus:

```
serverchan:    
  sckey: <your-sckey>
  
pushplus:    
  token: <your-token>
  channel: wechat   #optional
  template: markdown    #optional

iyuu:    
  token: <your-token>
  
```
