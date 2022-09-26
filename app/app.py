
import time
import hashlib
import hmac
import base64
import uuid
import json as j

import streamlit as st
import requests


# アクセス用のtimestamp/sign/nonceの生成
token=st.secrets["TOKEN"]
nonce = uuid.uuid4().int
t = int(round(time.time() * 1000))
string_to_sign = '{}{}{}'.format(token, t, nonce)
string_to_sign = bytes(string_to_sign, 'utf-8')
secret = bytes(st.secrets["SECRET"], 'utf-8')
sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())

# リクエストヘッダの設定
header={}
header["Authorization"] = token
header["sign"] = sign
header["t"] = str(t)
header["nonce"] = str(nonce)


API_SERVER = st.secrets["API_SERVER"]
DEVICE_ID = st.secrets["DEVICE_ID"]

params = {}
params["commandType"] = "command"
params["parameter"] = "default"


def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True


if check_password():
    # デバイスステータスの取得
    response = requests.get(API_SERVER + "/v1.1/devices/"+ DEVICE_ID +"/status", headers=header)
    status = j.loads(response.text)

    if status["statusCode"] != 100:
        st.markdown('# スマートロックは オフライン です')
    else:
        st.markdown('# スマートロックは オンライン です')
        st.session_state['lockState']=status["body"]["lockState"]
        st.markdown("## 鍵の状態　→ " + st.session_state['lockState'])

        if st.session_state['lockState']=="locked":
          if st.button("解錠する"):
            params["command"] = "unlock"
            requests.post(API_SERVER+"/v1.1/devices/"+DEVICE_ID+"/commands", headers=header, json=params)
            time.sleep(1)
            response = requests.get(API_SERVER + "/v1.1/devices/"+ DEVICE_ID +"/status", headers=header)
            status = j.loads(response.text)
            st.session_state['lockState']="unlocked"
        else:
          if st.button("施錠する"):
            params["command"] = "lock"
            requests.post(API_SERVER+"/v1.1/devices/"+DEVICE_ID+"/commands", headers=header, json=params)
            time.sleep(1)
            response = requests.get(API_SERVER + "/v1.1/devices/"+ DEVICE_ID +"/status", headers=header)
            status = j.loads(response.text)
            st.session_state['lockState']="locked"

        st.markdown("※ 解錠/施錠した後は↓のステータス更新後にもう一度ボタンを押して下さい")


    st.markdown("### 以下はデバッグ用のステータス表示")
    st.json(status)
