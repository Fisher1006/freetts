import os

import util


# 获取当前文件所在的目录
def _get_current_dir():
    return os.path.dirname(__file__)


class Config(object):
    def __init__(self):
        self.config_file = os.path.join(_get_current_dir(), "config.json")
        self.config = util.load_json(self.config_file)

        # 反转 StyleMaps
        self.reverse_style_maps_data = dict()
        self._reverse_style_maps()

        self.voice_config_file = os.path.join(_get_current_dir(), "voice_config.json")
        self.voice_config = util.load_json(self.voice_config_file)

    def get_tts_endpoint(self):
        return self.config['TTSEndPoint']

    def get_websocket_endpoint(self):
        return self.config['WebSocketEndPoint']

    def get_voice_rate(self):
        return self.config['MinRate'], self.config['MaxRate']

    def get_voice_pitch(self):
        return self.config['MinPitch'], self.config['MaxPitch']

    def get_voice_degree(self):
        return self.config['MinDegree'], self.config['MaxDegree']

    def get_style_maps(self):
        return self.config['StyleMaps']

    def get_roles(self):
        return self.config['Roles']

    def get_languages(self):
        return self.voice_config['Locale']

    def get_voice_groups(self, language):
        voices = self.voice_config['Voice']
        return list(voices[language].keys())

    def get_voices(self, language, group):
        language_config = self.voice_config['Voice']
        group_config = language_config.get(language, "")
        if group_config == "":
            return {}
        else:
            voices = group_config.get(group, "")
            if voices == "":
                return {}
            else:
                return voices

    def get_voice(self, language, group, voice_name):
        language_config = self.voice_config['Voice']
        group_config = language_config.get(language, "")
        if group_config == "":
            return {}
        else:
            voices = group_config.get(group, "")
            if voices == "":
                return {}
            else:
                voice = voices.get(voice_name, "")
                if voice == "":
                    return {}
                return voice

    def get_style_names(self, style_ids):
        style_maps = self.get_style_maps()
        style_names = ["默认"]
        for style_id in style_ids:
            if style_maps.get(style_id, "") != "":
                style_names.append(style_maps[style_id])
        return style_names

    def get_style_id(self, style_name):
        data = self.reverse_style_maps_data
        return data.get(style_name, "")

    def get_role_names(self):
        role_names = ["默认"]
        for role_name in self.get_roles():
            role_names.append(role_name)
        return role_names

    def get_role_id(self, role_name):
        roles = self.get_roles()
        return roles.get(role_name, "")

    def _reverse_style_maps(self):
        style_map = self.get_style_maps()
        for style_id, style_name in style_map.items():
            self.reverse_style_maps_data[style_name] = style_id
        return
