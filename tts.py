import re
import uuid

from datetime import datetime
import requests
import websockets


# 文本转语音核心代码
async def transferMsTTSData(config, ssml_text, output_path):
    auth_token = get_auth_token(config.get_tts_endpoint())
    req_id = uuid.uuid4().hex.upper()
    print(req_id)

    websocket_endpoint = get_websocket_url(config.get_websocket_endpoint(), auth_token, req_id)
    async with websockets.connect(websocket_endpoint, ping_interval=None, ping_timeout=None) as websocket:
        await websocket.send(get_websocket_message1(req_id))
        await websocket.send(get_websocket_message2(req_id))
        await websocket.send(get_websocket_message3(req_id, ssml_text))

        end_resp_path = re.compile('Path:turn.end')
        audio_stream = b''
        while True:
            response = await websocket.recv()
            if re.search(end_resp_path, str(response)) is None:
                if isinstance(response, type(bytes())):
                    try:
                        start_ind = str(response).find('Path:audio')
                        audio_stream += response[start_ind - 2:]
                    except:
                        pass
            else:
                break
        with open(f'{output_path}.mp3', 'wb') as audio_out:
            audio_out.write(audio_stream)


def get_auth_token(endpoint):
    r = requests.get(endpoint)
    main_web_content = r.text
    token_expr = re.compile('token: \"(.*?)\"', re.DOTALL)
    auth_token = re.findall(token_expr, main_web_content)[0]
    return auth_token


def get_websocket_url(endpoint, auth_token, req_id):
    return endpoint + auth_token + "&X-ConnectionId=" + req_id


def get_websocket_message1(req_id):
    payload = '{"context":{"system":{"name":"SpeechSDK","version":"1.12.1-rc.1","build":"JavaScript",' \
              '"lang":"JavaScript","os":{"platform":"Browser/Linux x86_64","name":"Mozilla/5.0 (X11; Linux x86_64; ' \
              'rv:78.0) Gecko/20100101 Firefox/78.0","version":"5.0 (X11)"}}}} '
    message = 'Path : speech.config\r\nX-RequestId: ' + req_id + '\r\nX-Timestamp: ' + getXTime() + \
              '\r\nContent-Type: application/json\r\n\r\n' + payload
    return message


def get_websocket_message2(req_id):
    payload = '{"synthesis":{"audio":{"metadataOptions":{"sentenceBoundaryEnabled":false,' \
              '"wordBoundaryEnabled":false},"outputFormat":"audio-16khz-32kbitrate-mono-mp3"}}} '
    message = 'Path : synthesis.context\r\nX-RequestId: ' + req_id + '\r\nX-Timestamp: ' + \
              getXTime() + '\r\nContent-Type: application/json\r\n\r\n' + payload
    return message


def get_websocket_message3(req_id, payload):
    message = 'Path: ssml\r\nX-RequestId: ' + req_id + '\r\nX-Timestamp: ' + \
              getXTime() + '\r\nContent-Type: application/ssml+xml\r\n\r\n' + payload
    return message


def getXTime():
    now = datetime.now()
    return fr(str(now.year)) + '-' + fr(str(now.month)) + '-' + fr(str(now.day)) + 'T' + fr(
        hr_cr(int(now.hour))) + ':' + fr(str(now.minute)) + ':' + fr(str(now.second)) + '.' + str(now.microsecond)[
                                                                                              :3] + 'Z'


def hr_cr(hr):
    corrected = (hr - 1) % 24
    return str(corrected)


def fr(input_string):
    corr = ''
    i = 2 - len(input_string)
    while i > 0:
        corr += '0'
        i -= 1
    return corr + input_string
