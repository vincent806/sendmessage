#
# Author: vincent806
# Date: 22Feb2022
# Description:
#   This script aims to build a generic kit to push message to various message channels.
# Supported message channels:
#   1. iOS - Bark
#   2. ServerChan
#   3. PushPlus
#   4. Iyuu
#   5. SMTP
#   6. DingTalk
#   7. FeiShu
#   8. WxBot - Robot for Chatgroup in Enterprise Wechat
#   9. WxApp - App message for Enterpise Wechat
#  10. Telegram - Bot
# Usage:
#   1. Refer to config-example.yml and create your own config.yml
#   2. Call this script like this:
#       python3 sendmessage.py 'title','line 1 in the body', 'line 2 in the body', 'line 3 in the body'[..., 'line x in the body']
#   3. If your config file is stored somewhere else, try to call as below and make sure --config or -c is the first parameter
#       python3 sendmessage.py --config='otherconfig.yml' 'title','line 1 in the body', 'line 2 in the body', 'line 3 in the body'[..., 'line x in the body']
# Environment:
#   This script is developed under python version 3.10.  Ideally it works in most of the python 3.x version but the latest version is always recommended.
#   Packages that you may need to install if you have not:
#       pip3 install pyyaml
#
# Disclaimer:
# The author assumes no responsibility or liability for any errors or omissions in this script.
#

import yaml # pip3 install pyyaml
import json, sys
import os
from urllib import request
from urllib import parse
from urllib.error import URLError, HTTPError
import ssl
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import time
import hmac
import hashlib
import base64
import getopt

class ConfigLoader():

    def loadConfig(self,configpath="config.yml"):
        configpath = configpath.strip()
        basename = os.path.basename(configpath)
        if(configpath == basename):
            scriptdir = os.path.dirname(sys.argv[0])
            configpath = os.path.join(scriptdir,configpath)
        
        print('reading config from: ' + configpath)
    
        with open(configpath, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
    
        return(config)
    
class MessageFormatter():

    def __init__(self):
        self.rounddigit = 2
    
    def convertBytes(self,inputstr):
        # convert size in bytes into readable format
        # criteria
        # 1. only if 'nnnnnnnnnnnbytes' is in the string, where 'nnnnnnnnnnn' is integer
        # 2. be careful that there is no space in between the 'nnnnnnnnnnn' and 'bytes'
        # 3. be careful that it is 'bytes', not 'byte/Byte/Bytes/BYTE/BYTES'.
        outputstr = inputstr
        pattern = re.compile(r'\d*bytes')
        match = pattern.search(inputstr)
        if match:
            matchstr = match.group()
            size = int(matchstr.replace('bytes',''))
            t = size
            u = "B"
            if t>1024:
                t = t / 1024
                u = "K"
            if t>1024:
                t = t / 1024
                u = 'M'
            if t>1024:
                t = t / 1024
                u = "G"
            if t>1024:
                t = t / 1024
                u = "T"
            if u != "B":
                t = str(round(t,self.rounddigit))
            else:
                t = str(t)
            replacestr = t + u
            outputstr = inputstr.replace(matchstr,replacestr)
        return(outputstr)

    def getHostLocation(self,inputstr):
        outputstr = inputstr
        if inputstr.startswith("http://") or inputstr.startswith("https://"):  #extract host location rather than exposing the entire url where sensitive data might be in place
            parsedurl = parse.urlparse(inputstr)
            outputstr = parsedurl.netloc
        return(outputstr)

#
# Bark service
#
class Bark():
    #
    # Bark instructions: https://github.com/Finb/Bark
    #
    def __init__(self):
        self.delimiter = '\n'

    def push(self,config,content):
        #handle message
        if(len(content)<2):
            title = "参数个数不对!"
            body = "null"
        else:
            title = content[0]
            body = ""
            for i in range(1,len(content)):
                v = content[i]
                v = MessageFormatter().convertBytes(v)
                v = MessageFormatter().getHostLocation(v)
                body = body + v + self.delimiter
            if (len(body)>5000):  #bark has limitation of 5000 characters in body
                body = body[0:5000]

        #load config
        endpoint = config.get('endpoint')
        #default config
        group = config.get('group')
        icon = config.get('icon')
        sound = config.get('sound')
        automaticallyCopy = config.get('automaticallyCopy')
        isArchive = config.get('isArchive')
        url = config.get('url')
        level = config.get('level')

        #get tailor made config
        tailoring = config.get('tailoring')
        if tailoring is not None:
            for t in config.get('tailoring'):
                t_title = t.get('title')
                matchtitle = False
                if isinstance(t_title, str):
                    if title == t.get('title'):
                        matchtitle = True
                if isinstance(t_title,list):
                    for e in t_title:
                        if title == e:
                            matchtitle = True
                if matchtitle:
                    t_group = t.get('group')
                    t_icon = t.get('icon')
                    t_sound = t.get('sound')
                    t_automaticallyCopy = t.get('automaticallyCopy')
                    t_isArchive = t.get('isArchive')
                    t_url = t.get('url')
                    t_level = t.get('level')
                    if t_group is not None:
                        group = t_group
                    if t_icon is not None:
                        icon = t_icon
                    if t_sound is not None:
                        sound = t_sound
                    if t_automaticallyCopy is not None:
                        automaticallyCopy = t_automaticallyCopy
                    if t_isArchive is not None:
                        isArchive = t_isArchive
                    if t_url is not None:
                        url = t_url
                    if t_group is not None:
                        level = t_level
                    break

        parameters = {}
        if group is not None:
            parameters['group'] = group
        if icon is not None:
            parameters['icon'] = icon
        if sound is not None:
            parameters['sound'] = sound
        if automaticallyCopy is not None:
            parameters['automaticallyCopy'] = automaticallyCopy
        if isArchive is not None:
            parameters['isArchive'] = isArchive
        if url is not None:
            parameters['url'] = url
        if group is not None:
            parameters['level'] = level

        #initialize endpoint
        if not endpoint.endswith("/"):
            endpoint = endpoint + "/"
        parameter = ''
        conchar = '?'
        for k,v in parameters.items():
            parameter = parameter + conchar + k + '=' + parse.quote_plus(str(v))
            conchar = '&'

        endpoint = endpoint + parse.quote_plus(title) + '/'
        endpoint = endpoint + parse.quote_plus(body) 
        endpoint = endpoint + parameter

        #send data to bark server
        try:
            resp = request.urlopen(endpoint) 
            return(resp.read().decode())
        except HTTPError as e:
            # do something
            return('Error code: ', e.code)
        except URLError as e:
            # do something
            return('Reason: ', e.reason)
        else:
            # do something
            return('Unknown exception!')

#
# ServerChan Service
#
class ServerChan():
    #
    # ServerChan instructions: https://sct.ftqq.com/
    #
    def __init__(self):
        self.delimiter = '\n\n'
        self.oldscurl = 'https://sc.ftqq.com/'
        self.newscurl = 'https://sctapi.ftqq.com/'

    def push(self,config,content):
        #handle message    
        if(len(content)<2):
            title = "参数个数不对!"
            body = "null"
        else:
            title = content[0]
            body = ""
            for i in range(1,len(content)):
                v = content[i]
                v = MessageFormatter().convertBytes(v)
                v = MessageFormatter().getHostLocation(v)
                body = body + v + self.delimiter

        #load config
        sckey = config.get('sckey')

        #initialize endpoint
        if sckey.startswith("SCU"):
            endpoint = self.oldscurl + sckey + ".send"
        else:
            endpoint = self.newscurl + sckey + ".send"


        #format posting data
        endpoint = endpoint + "?text=" + parse.quote(title) + "&desp=" + parse.quote(body)

        #send data to endpoint
        try:
            #print(endpoint)
            ssl._create_default_https_context = ssl._create_unverified_context
            resp = request.urlopen(endpoint)
            return(resp.read().decode())
        except HTTPError as e:
            # do something
            return('Error code: ', e.code)
        except URLError as e:
            # do something
            return('Reason: ', e.reason)
        else:
            # do something
            return('Unknown exception!')

#
# PushPlus Service
#
class PushPlus():
    #
    # PushPlus instructions: https://www.pushplus.plus/
    #
    def __init__(self):
        self.delimiter = '\n\n'
        self.endpoint = 'http://www.pushplus.plus/'

    def push(self,config,content):
        #handle message    
        if(len(content)<2):
            title = "参数个数不对!"
            body = "null"
        else:
            title = content[0]
            body = ""
            for i in range(1,len(content)):
                v = content[i]
                v = MessageFormatter().convertBytes(v)
                v = MessageFormatter().getHostLocation(v)
                body = body + v + self.delimiter

        #load config
        token = config.get('token')
        channel = config.get('channel')
        template = config.get('template')

        #initialize endpoint
        endpoint = self.endpoint + 'send?token=' + token
        if channel is not None:
            endpoint = endpoint + '&channel=' + channel
        if template is not None:
            endpoint = endpoint + '&template=' + template

        #format posting data
        endpoint = endpoint + "&title=" + parse.quote(title) + "&content=" + parse.quote(body)

        #send data to endpoint
        try:
            #print(endpoint)
            ssl._create_default_https_context = ssl._create_unverified_context
            resp = request.urlopen(endpoint)
            return(resp.read().decode())
        except HTTPError as e:
            # do something
            return('Error code: ', e.code)
        except URLError as e:
            # do something
            return('Reason: ', e.reason)
        else:
            # do something
            return('Unknown exception!')

#
# Iyuu Service
#
class Iyuu():
    #
    # Iyuu instructions: https://iyuu.cn/
    #
    def __init__(self):
        self.delimiter = '\n\n'
        self.endpoint = 'https://iyuu.cn/'

    def push(self,config,content):
        #handle message    
        if(len(content)<2):
            title = "参数个数不对!"
            body = "null"
        else:
            title = content[0]
            body = ""
            for i in range(1,len(content)):
                v = content[i]
                v = MessageFormatter().convertBytes(v)
                v = MessageFormatter().getHostLocation(v)
                body = body + v + self.delimiter

        #load config
        token = config.get('token')

        #initialize endpoint
        endpoint = self.endpoint + token + ".send"

        #format posting data
        endpoint = endpoint + "?text=" + parse.quote(title) + "&desp=" + parse.quote(body)

        #send data to endpoint
        try:
            #print(endpoint)
            ssl._create_default_https_context = ssl._create_unverified_context
            resp = request.urlopen(endpoint)
            return(resp.read().decode())
        except HTTPError as e:
            # do something
            return('Error code: ', e.code)
        except URLError as e:
            # do something
            return('Reason: ', e.reason)
        else:
            # do something
            return('Unknown exception!')

#
# SMTP Service
#
class SMTP():
    #
    # SMTP instructions: https://docs.python.org/3/library/smtplib.html
    #
    def __init__(self):
        self.delimiter = '\n\n'

    def push(self,config,content):
        #handle message    
        if(len(content)<2):
            title = "参数个数不对!"
            body = "null"
        else:
            title = content[0]
            body = ""
            for i in range(1,len(content)):
                v = content[i]
                v = MessageFormatter().convertBytes(v)
                v = MessageFormatter().getHostLocation(v)
                body = body + v + self.delimiter

        #load config
        server = config.get('server')
        port = config.get('port')
        sender = config.get('sender')
        authcode = config.get('authcode')
        recipient = config.get('recipient')

        #format posting data
        mailsubject = Header(title, 'utf-8').encode()
        mailbody = MIMEText(body, 'plain', 'utf-8')

        #send email via smtp server
        try:
            smtpcon = smtplib.SMTP_SSL(server, port)
            smtpcon.login(sender, authcode)
            smtpmsg = MIMEMultipart()
            smtpmsg['Subject'] = mailsubject
            smtpmsg['From'] = sender
            smtpmsg['To'] = recipient
            smtpmsg.attach(mailbody)
            smtpcon.sendmail(sender, recipient, smtpmsg.as_string())
            smtpcon.quit()
            return("successful!")
        except smtplib.SMTPException as e:
            #do something
            return('Error code: ', e.errno)
        else:
            # do something
            return('Unknown exception!')            

#
# DingTalk service
#
class DingTalk():
    #
    # DingTalk instructions: https://open.dingtalk.com/document/robots/custom-robot-access
    #
    def __init__(self):
        self.delimiter = '\n\n'

    def formatMessage(self,title, body):
        json_text = {
            "msgtype": "markdown",
            "markdown": {
            "title": title,
            "text": "#### **" + title + "** \n\n" + body
            },
            "at": {
                "isAtAll": True
            }
        }
        return json_text

    def push(self,config,content):
        #handle message    
        if(len(content)<2):
            title = "参数个数不对!"
            body = "null"
        else:
            title = content[0]
            body = ""
            for i in range(1,len(content)):
                v = content[i]
                v = MessageFormatter().convertBytes(v)
                v = MessageFormatter().getHostLocation(v)
                body = body + v + self.delimiter
            if (len(body)>5000):  #bark has limitation of 5000 characters in body
                body = body[0:5000]

        #load config
        secret = config.get('secret')
        endpoint = config.get('url')

        #initialize endpoint and sign
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode("utf-8")
        string_to_sign = "{}\n{}".format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = parse.quote_plus(base64.b64encode(hmac_code))
        endpoint = endpoint + "&timestamp={}&sign={}".format(timestamp, sign)
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }

        #format posting data
        message = self.formatMessage(title, body)

        #send data to dingtalk
        try:
            postdata = json.dumps(message)
            postdata = postdata.encode("utf-8")
            handler = request.Request(url=endpoint, data=postdata, headers=header) 
            resp = request.urlopen(handler) 
            return(resp.read().decode())
        except HTTPError as e:
            # do something
            return('Error code: ', e.code)
        except URLError as e:
            # do something
            return('Reason: ', e.reason)
        else:
            # do something
            return('Unknown exception!')

#
# FeiShu service
#
class FeiShu():
    #
    # FeiShu instructions: https://www.feishu.cn/hc/zh-CN/articles/360024984973
    #
    def __init__(self):
        self.delimiter = '\n\n'

    def formatMessage(self,title, body, timestamp, sign):
        json_text = {
            "timestamp": timestamp,
            "sign": sign,
            "msg_type": "text",
            "content": {
                "text": title + "\n\n" + body
            }
        } 
        return json_text

    def push(self,config,content):
        #handle message    
        if(len(content)<2):
            title = "参数个数不对!"
            body = "null"
        else:
            title = content[0]
            body = ""
            for i in range(1,len(content)):
                v = content[i]
                v = MessageFormatter().convertBytes(v)
                v = MessageFormatter().getHostLocation(v)
                body = body + v + self.delimiter
            if (len(body)>5000):  #bark has limitation of 5000 characters in body
                body = body[0:5000]

        #load config
        secret = config.get('secret')
        endpoint = config.get('url')

        #initialize endpoint and sign
        timestamp = str(round(time.time()))
        secret_enc = secret.encode("utf-8")
        string_to_sign = "{}\n{}".format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }

        #format posting data
        message = self.formatMessage(title, body, timestamp, sign)

        #send data to feishu
        try:
            postdata = json.dumps(message)
            postdata = postdata.encode("utf-8")
            handler = request.Request(url=endpoint, data=postdata, headers=header) 
            resp = request.urlopen(handler) 
            return(resp.read().decode())
        except HTTPError as e:
            # do something
            return('Error code: ', e.code)
        except URLError as e:
            # do something
            return('Reason: ', e.reason)
        else:
            # do something
            return('Unknown exception!')

#
# WxBot service
#
class WxBot():
    #
    # WxBot instructions: https://developer.work.weixin.qq.com/document/path/91770
    #
    def __init__(self):
        self.delimiter = '\n\n'

    def formatMessage(self,title, body):
        json_text = {
            "msgtype": "markdown",
            "markdown": {
                "content": "#### **" + title + "** \n\n" + body
            },
            "at": {
                "isAtAll": True
            }
        }
        return json_text

    def push(self,config,content):
        #handle message    
        if(len(content)<2):
            title = "参数个数不对!"
            body = "null"
        else:
            title = content[0]
            body = ""
            for i in range(1,len(content)):
                v = content[i]
                v = MessageFormatter().convertBytes(v)
                v = MessageFormatter().getHostLocation(v)
                body = body + v + self.delimiter
            if (len(body)>5000):  #bark has limitation of 5000 characters in body
                body = body[0:5000]

        #load config
        endpoint = config.get('url')

        #initialize header
        header = {
            "Content-Type": "application/json;charset=UTF-8"
        }

        #format posting data
        message = self.formatMessage(title, body)

        #send data to wxbot
        try:
            postdata = json.dumps(message)
            postdata = postdata.encode("utf-8")
            handler = request.Request(url=endpoint, data=postdata, headers=header) 
            resp = request.urlopen(handler) 
            return(resp.read().decode())
        except HTTPError as e:
            # do something
            return('Error code: ', e.code)
        except URLError as e:
            # do something
            return('Reason: ', e.reason)
        else:
            # do something
            return('Unknown exception!')

#
# WxApp service
#
class WxApp():
    #
    # WxApp instructions: https://developer.work.weixin.qq.com/document/path/90236
    #
    def __init__(self):
        self.delimiter = '\n\n'
        self.endpoint = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token='

    def formatMessage(self, touser, agentid, title, body, messagetype):
        json_md = {
            "touser": touser,
            "msgtype": "markdown",
            "agentid": agentid,
            "markdown": {
                "content": "#### **" + title + "** \n\n" + body
            },
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        json_text = {
           "touser" : touser,
           "msgtype" : "text",
           "agentid" : agentid,
           "text" : {
               "content" : title + "\n\n" + body
           },
           "safe":0,
           "enable_id_trans": 0,
           "enable_duplicate_check": 0,
           "duplicate_check_interval": 1800
        }
        if messagetype == "markdown":
            return json_md
        else:
            return json_text

    def getToken(self, corpid, secret):
        resp = request.urlopen("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=" + corpid + "&corpsecret=" + secret)
        json_resp = json.loads(resp.read().decode())
        token = json_resp["access_token"]
        return token

    def push(self,config,content):
        #handle message    
        if(len(content)<2):
            title = "参数个数不对!"
            body = "null"
        else:
            title = content[0]
            body = ""
            for i in range(1,len(content)):
                v = content[i]
                v = MessageFormatter().convertBytes(v)
                v = MessageFormatter().getHostLocation(v)
                body = body + v + self.delimiter
            if (len(body)>5000):  #bark has limitation of 5000 characters in body
                body = body[0:5000]

        #load config
        corpid = config.get('corpid')
        secret = config.get('secret')
        agentid = config.get('agentid')
        touser = config.get('touser')
        messagetype = config.get('type')

        #initialize header and endpoint
        header = {
            "Content-Type": "application/json;charset=UTF-8"
        }
        # 获取token
        token = self.getToken(corpid, secret)
        endpoint = self.endpoint + token

        #format posting data
        message = self.formatMessage(touser, agentid, title, body, messagetype)

        #send data to wxapp
        try:
            postdata = json.dumps(message)
            postdata = postdata.encode("utf-8")
            handler = request.Request(url=endpoint, data=postdata, headers=header) 
            resp = request.urlopen(handler) 
            return(resp.read().decode())
        except HTTPError as e:
            # do something
            return('Error code: ', e.code)
        except URLError as e:
            # do something
            return('Reason: ', e.reason)
        else:
            # do something
            return('Unknown exception!')

#
# Telegram service
#
class Telegram():
    #
    # Telegram instructions: https://core.telegram.org/bots/api#sendmessage
    #
    def __init__(self):
        self.delimiter = '\n\n'
        self.endpoint = 'https://api.telegram.org/bot'

    def push(self,config,content):
        #handle message    
        if(len(content)<2):
            title = "参数个数不对!"
            body = "null"
        else:
            title = content[0]
            body = ""
            for i in range(1,len(content)):
                v = content[i]
                v = MessageFormatter().convertBytes(v)
                v = MessageFormatter().getHostLocation(v)
                body = body + v + self.delimiter

        #load config
        token = config.get('token')
        chatid = config.get('chatid')

        #initialize endpoint
        endpoint = self.endpoint + token + "/sendMessage?chat_id=" + str(chatid)

        #format posting data
        endpoint = endpoint + "&text=" + parse.quote(title + "\n\n" + body)

        #send data to endpoint
        try:
            #print(endpoint)
            ssl._create_default_https_context = ssl._create_unverified_context
            resp = request.urlopen(endpoint)
            return(resp.read().decode())
        except HTTPError as e:
            # do something
            return('Error code: ', e.code)
        except URLError as e:
            # do something
            return('Reason: ', e.reason)
        else:
            # do something
            return('Unknown exception!')


if __name__ == '__main__':

    # load config
    opts,args = getopt.getopt(sys.argv[1:],'-c:',['config='])
    configpath = "config.yml"
    for optname,optvalue in opts:
        if optname in ('-c','--config'):
            configpath = optvalue # config from -c or --config parameter
            break
    config = ConfigLoader().loadConfig(configpath)
    for service in config:
        if service == 'bark':
            handler = Bark()
            resp = handler.push(config[service], args)
            print(service + ': ' + str(resp))
        if service == 'serverchan':
            handler = ServerChan()
            resp = handler.push(config[service], args)
            print(service + ': ' + str(resp))
        if service == 'pushplus':
            handler = PushPlus()
            resp = handler.push(config[service], args)
            print(service + ': ' + str(resp))
        if service == 'iyuu':
            handler = Iyuu()
            resp = handler.push(config[service], args)
            print(service + ': ' + str(resp))
        if service == 'smtp':
            handler = SMTP()
            resp = handler.push(config[service], args)
            print(service + ': ' + str(resp))
        if service == 'dingtalk':
            handler = DingTalk()
            resp = handler.push(config[service], args)
            print(service + ': ' + str(resp))
        if service == 'feishu':
            handler = FeiShu()
            resp = handler.push(config[service], args)
            print(service + ': ' + str(resp))
        if service == 'wxbot':
            handler = WxBot()
            resp = handler.push(config[service], args)
            print(service + ': ' + str(resp))
        if service == 'wxapp':
            handler = WxApp()
            resp = handler.push(config[service], args)
            print(service + ': ' + str(resp))
        if service == 'telegram':
            handler = Telegram()
            resp = handler.push(config[service], args)
            print(service + ': ' + str(resp))

