
import time
import hashlib
import hmac
import base64
import uuid
import json as j
#
import requests
import streamlit as st
import pandas as pd
import requests
#
import config 


# アクセス用のtimestamp/sign/nonceの生成
token=config.TOKEN
nonce = uuid.uuid4().int
t = int(round(time.time() * 1000))
string_to_sign = '{}{}{}'.format(token, t, nonce)
string_to_sign = bytes(string_to_sign, 'utf-8')
secret = bytes(config.SECRET, 'utf-8')
sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())

# リクエストヘッダの設定
header={}
header["Authorization"] = token
header["sign"] = sign
header["t"] = str(t)
header["nonce"] = str(nonce)

# デバイスステータスの取得
response = requests.get(config.API_SERVER + "/v1.1/devices/"+ config.DEVICE_ID +"/status", headers=header)
status = j.loads(response.text)

params = {}
params["commandType"] = "command"
params["parameter"] = "default"

st.markdown("### 以下はデバッグ用のステータス表示")
st.json(status)

if status["statusCode"] != 100:
  st.markdown('# スマートロックは オフライン です')
else:
  st.markdown('# スマートロックは オンライン です')
  if status["body"]["lockState"]=="locked":
    st.markdown("## 鍵の状態　→　locked")
    if st.button("解錠する"):
      params["command"] = "unlock"
      requests.post(config.API_SERVER+"/v1.1/devices/"+config.DEVICE_ID+"/commands", headers=header, json=params)
      time.sleep(1)
      response = requests.get(config.API_SERVER + "/v1.1/devices/"+ config.DEVICE_ID +"/status", headers=header)
  else:
    st.markdown("## 鍵の状態　→　unlocked")
    if st.button("施錠する"):
      params["command"] = "lock"
      requests.post(config.API_SERVER+"/v1.1/devices/"+config.DEVICE_ID+"/commands", headers=header, json=params)
      time.sleep(1)
      response = requests.get(config.API_SERVER + "/v1.1/devices/"+ config.DEVICE_ID +"/status", headers=header)

