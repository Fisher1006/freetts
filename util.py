import json


def load_json(config_file):
    """"读取配置"""
    with open(config_file) as json_file:
        config = json.load(json_file)
    return config


def read_file(file_name):
    with open(file_name) as file:
        content = file.read()
    return content


def gen_ssml_text(language, voice_id, style, styledegree, role, rate, pitch, content):
    format_str = read_file("./tts.xml")
    return format_str % (language, voice_id, style, styledegree, role, rate, pitch, content)


def gen_filename(*args):
    file_name = ""
    for arg in args:
        file_name = file_name + "-" + arg
    return file_name[1:]
