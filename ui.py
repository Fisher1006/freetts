import asyncio
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QRadioButton, QLineEdit,
                             QLabel, QSlider, QComboBox, QTextEdit, QGroupBox, QFileDialog, QButtonGroup, QMessageBox)
from playsound import playsound

import tts
import util


class FreeTTS(QWidget):
    def __init__(self, config):
        super(FreeTTS, self).__init__()
        self.logger = logging.getLogger()

        # init vars
        self.voice_language = ""  # 语言
        self.voice_group = ""  # 语音分组
        self.voice_text = ""  # 待转换文本
        self.voice_id = ""  # 语音
        self.voice_rate = 100  # 语速
        self.voice_pitch = 0  # 音调
        self.voice_degree = 1  # 强度
        self.voice_style = ""  # 语音风格
        self.voice_role = ""  # 角色
        self.voice_feature = "常规"  # 语音特点

        self.config = config
        self.init_ui()
        self.setAcceptDrops(True)

    # 鼠标拖入事件
    def dragEnterEvent(self, evn):
        file = evn.mimeData().urls()[0].toLocalFile()
        path = ''
        if file not in path:
            path += file
            with open(path, 'r', encoding='utf-8') as f:
                self.voice_text = f.read()
                f.close()
            self.line_select_file.setText(path)
        evn.accept()

    # 鼠标放开执行
    def dropEvent(self, evn):
        pass

    # 移动鼠标执行
    def dragMoveEvent(self, evn):
        pass

    def init_ui(self):
        # 最左侧参数
        vbox_left = QVBoxLayout()
        self.init_box_left(vbox_left)

        # 中间声音
        self.vbox_middle = QVBoxLayout()
        self.init_box_middle(self.vbox_middle)

        # 右侧展示
        vbox_right = QVBoxLayout()
        self.init_box_right(vbox_right)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox_left)
        hbox.addStretch(1)
        hbox.addLayout(self.vbox_middle)
        hbox.addStretch(1)
        hbox.addLayout(vbox_right)
        hbox.addStretch(1)

        self.setLayout(hbox)

        self.setGeometry(300, 300, 800, 500)
        self.setWindowTitle('FreeTTS by fisher1008')
        self.show()

    def init_box_left(self, vbox):
        # 源文件选择按钮和选择编辑框
        self.btn_select_file = QPushButton('选择文本', self)
        self.btn_select_file.clicked.connect(self.select_file)
        self.line_select_file = QLineEdit(self)
        hbox_select = self.gen_hbox(self.btn_select_file, self.line_select_file)

        # 语速设置
        min_rate, max_rate = self.config.get_voice_rate()
        self.label_rate, self.line_rate, self.slider_rate = \
            self.gen_slider_widget('语速：', str(min_rate), min_rate, max_rate, self.line_rate_change,
                                   self.slider_rate_change)
        hbox_rate = self.gen_hbox(self.label_rate, self.slider_rate, self.line_rate)

        # 音调
        min_pitch, max_pitch = self.config.get_voice_pitch()
        self.label_pitch, self.line_pitch, self.slider_pitch = \
            self.gen_slider_widget('音调：', str(min_pitch), min_pitch, max_pitch, self.line_pitch_change,
                                   self.slider_pitch_change)
        hbox_pitch = self.gen_hbox(self.label_pitch, self.slider_pitch, self.line_pitch)

        # 强度 0.01~2 这里扩大 100 倍
        min_degree, max_degree = self.config.get_voice_degree()
        self.label_degree, self.line_degree, self.slider_degree = \
            self.gen_slider_widget('强度：', str(min_degree), min_degree, max_degree, self.line_degree_change,
                                   self.slider_degree_change)
        hbox_degree = self.gen_hbox(self.label_degree, self.slider_degree, self.line_degree)

        # 风格
        self.label_style, self.combox_style = self.gen_combox_widget('风格：', [], self.combox_style_change)
        hbox_style = self.gen_hbox(self.label_style, self.combox_style)

        # 角色
        role_names = self.config.get_role_names()
        self.label_role, self.combox_role = self.gen_combox_widget('角色：', role_names, self.combox_role_change)
        hbox_role = self.gen_hbox(self.label_role, self.combox_role)

        # 特点
        self.label_feature, self.text_feature = self.gen_label_widget('特点：', self.voice_feature)
        hbox_feature = self.gen_hbox(self.label_feature, self.text_feature)

        vbox.addLayout(hbox_select)
        vbox.addLayout(hbox_rate)
        vbox.addLayout(hbox_pitch)
        vbox.addLayout(hbox_degree)
        vbox.addLayout(hbox_style)
        vbox.addLayout(hbox_role)
        vbox.addLayout(hbox_feature)
        vbox.addStretch(1)

    def init_box_middle(self, vbox):
        # 语言
        languages = self.config.get_languages()
        if len(languages) == 0:
            self.logger.error("init_box_middle Locale config is empty")
            exit(-1)
        self.label_language, self.combox_language = \
            self.gen_combox_widget("语言", languages, self.combox_language_change)
        hbox_language = self.gen_hbox(self.label_language, self.combox_language)

        # set default language
        first_language = languages[0]
        self.combox_language.setCurrentText(first_language)
        self.voice_language = first_language

        # 声音分组
        voice_groups = self.config.get_voice_groups(first_language)
        if len(voice_groups) == 0:
            self.logger.error("init_box_middle Voice Group config is empty")
            exit(-1)
        self.label_voice_group, self.combox_voice_group = \
            self.gen_combox_widget("声音", voice_groups, self.combox_voice_group_change)
        hbox_voice_group = self.gen_hbox(self.label_voice_group, self.combox_voice_group)

        # set default voice group
        first_group = voice_groups[0]
        self.combox_voice_group.setCurrentText(first_group)
        self.voice_group = first_group

        # 声音列表
        self.combox_voice = QGroupBox('', self)
        self.vbox_voice = QVBoxLayout()
        self.btn_group_voice = QButtonGroup()
        self.init_voices_ui()

        vbox.addLayout(hbox_language)
        vbox.addLayout(hbox_voice_group)
        vbox.addWidget(self.combox_voice)

    def init_box_right(self, vbox):
        # 测试文本
        content = util.read_file("./example/test_text.txt")
        self.text_example = QTextEdit(self)  # 设置输入框
        self.text_example.setText(content)  # 设置初始值
        self.text_example.setReadOnly(True)

        # 测试按钮
        self.btn_test = self.gen_button_widget('测试声音', self.btn_test_onclick)

        # 转换按钮
        self.btn_start = self.gen_button_widget('开始转换', self.btn_start_onclick)

        vbox.addWidget(self.text_example)
        vbox.addWidget(self.btn_test)
        vbox.addWidget(self.btn_start)

    # 声音列表
    def init_voices_ui(self):
        # 清除旧的
        if self.vbox_voice is not None:
            count = self.vbox_voice.count()
            while count > 0:
                item = self.vbox_voice.takeAt(count - 1)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                count -= 1

        language = self.combox_language.currentText()
        group = self.combox_voice_group.currentText()
        voice_config = self.config.get_voices(language, group)
        if len(voice_config) == 0:
            self.logger.error("init_voices_ui voice config empty")
            exit(-1)

        i = 0
        first_btn = None
        for key, voice in voice_config.items():
            btn = QRadioButton(key, self)
            # btn.clicked.connect(lambda: self.btn_voice_checked(btn))
            self.btn_group_voice.addButton(btn)
            self.vbox_voice.addWidget(btn)

            # 记录第一个语音信息，为了不记录 btn 句柄
            if i == 0:
                first_btn = btn
                i += 1

        self.btn_group_voice.buttonClicked[int].connect(self.btn_voice_checked)
        self.vbox_voice.addStretch(1)
        self.combox_voice.setLayout(self.vbox_voice)

        # set default voice
        first_btn.setChecked(True)
        self.btn_voice_checked()

    def gen_slider_widget(self, lb_name, init_val, min_val, max_val, line_func, pitch_func):
        label_widget = QLabel(lb_name, self)
        line_widget = QLineEdit(self)  # 设置输入框
        line_widget.setMaximumWidth(70)
        line_widget.setText(init_val)  # 设置初始值
        line_widget.setValidator(QIntValidator(min_val, max_val))  # 设置输入框的可输入范围
        line_widget.cursorPositionChanged.connect(line_func)  # 输入框输入内容发生变化时，触发该函数
        # 设置滑块
        slider_widget = QSlider(Qt.Horizontal, self)
        slider_widget.setMinimum(min_val)  # 设置滑块最小值
        slider_widget.setMaximum(max_val)  # 设置滑块最大值
        slider_widget.valueChanged.connect(pitch_func)  # 滑块值发生变化时，触发该函数

        return label_widget, line_widget, slider_widget

    def gen_combox_widget(self, lb_name, items, onchange):
        label_widget = QLabel(lb_name, self)
        combox_widget = QComboBox(self)
        combox_widget.addItems(items)
        combox_widget.activated[str].connect(onchange)
        return label_widget, combox_widget

    def gen_label_widget(self, lb_name, init_val):
        label_widget = QLabel(lb_name, self)
        lable_widget2 = QLabel(init_val, self)
        lable_widget2.adjustSize()
        lable_widget2.setWordWrap(True)
        return label_widget, lable_widget2

    def gen_button_widget(self, btn_txt, onclick):
        btn_widget = QPushButton(btn_txt, self)
        btn_widget.clicked.connect(onclick)
        return btn_widget

    def gen_hbox(self, *widgets):
        hbox = QHBoxLayout()
        for widget in widgets:
            hbox.addStretch(1)
            hbox.addWidget(widget)
        hbox.addStretch(1)
        return hbox

    # 选择文本
    def select_file(self):
        target, file_type = QFileDialog.getOpenFileName(self, "选择要转换的文本文件", "C:/")
        with open(target, 'r', encoding='utf-8') as f:
            self.voice_text = f.read()
            f.close()
        self.line_select_file.setText(str(target))

    # 语速输入框变化
    def line_rate_change(self):
        rate_str = self.line_rate.text()
        if rate_str == "" or rate_str == "-":
            rate = 0
        else:
            rate = int(rate_str)
        self.logger.debug("line_rate_change rate_str:%s, rate:%d", rate_str, rate)
        self.voice_rate = rate
        self.slider_rate.setValue(rate)

    # 语速滑块变化
    def slider_rate_change(self):
        rate = self.slider_rate.value()
        self.logger.debug("line_rate_change rate:%d", rate)
        self.voice_rate = rate
        self.line_rate.setText(str(rate))

    # 音调输入框变化
    def line_pitch_change(self):
        pitch_str = self.line_pitch.text()
        if pitch_str == "" or pitch_str == "-":
            pitch = 0
        else:
            pitch = int(pitch_str)
        self.logger.debug("line_rate_change pitch_str:%s, pitch:%d", pitch_str, pitch)
        self.voice_pitch = pitch
        self.slider_pitch.setValue(pitch)

    # 音调滑块变化
    def slider_pitch_change(self):
        pitch = self.slider_pitch.value()
        self.logger.debug("line_rate_change pitch:%d", pitch)
        self.voice_pitch = pitch
        self.line_pitch.setText(str(pitch))

    # 强度输入框变化
    def line_degree_change(self):
        degree_str = self.line_degree.text()
        if degree_str == "" or degree_str == "-":
            degree = 0
        else:
            degree = int(degree_str)
        self.logger.debug("line_rate_change degree_str:%s, degree:%d", degree_str, degree)
        self.voice_degree = degree / 100
        self.slider_degree.setValue(degree)

    # 强度滑块变化
    def slider_degree_change(self):
        degree = self.slider_degree.value()
        self.logger.debug("line_rate_change degree:%d", degree)
        self.voice_degree = degree / 100
        self.line_degree.setText(str(degree))

    # 风格选择变化
    def combox_style_change(self):
        style_name = self.combox_style.currentText()
        style_id = self.config.get_style_id(style_name)
        self.logger.debug("line_rate_change style_name:%s, style_id:%s", style_name, style_id)
        self.voice_style = style_id

    # 角色选择变化
    def combox_role_change(self):
        role_name = self.combox_role.currentText()
        role_id = self.config.get_role_id(role_name)
        self.logger.debug("line_rate_change role_name:%s, role_id:%s", role_name, role_id)
        self.voice_role = role_id

    # 语言变化
    def combox_language_change(self):
        # save language
        self.voice_language = self.combox_language.currentText()
        # init voice group combox
        voice_groups = self.config.get_voice_groups(self.voice_language)
        if len(voice_groups) == 0:
            self.logger.error("combox_language_change Voice Group config is empty")
            exit(-1)

        # reset voice group
        self.combox_voice_group.clear()
        self.combox_voice_group.addItems(voice_groups)

        # set default voice group
        first_group = voice_groups[0]
        self.combox_voice_group.setCurrentText(first_group)
        self.voice_group = first_group

        # reset voice ui
        self.init_voices_ui()

    # 声音组合变化
    def combox_voice_group_change(self):
        # save group
        self.voice_group = self.combox_voice_group.currentText()
        # reset voice ui
        self.init_voices_ui()

    # 选中声音
    def btn_voice_checked(self):
        # save voice id
        voice_name = self.btn_group_voice.checkedButton().text()
        self.logger.debug("btn_voice_checked btn:%s, language:%s, group:%s",
                          voice_name, self.voice_language, self.voice_group)

        voice = self.config.get_voice(self.voice_language, self.voice_group, voice_name)
        if voice is None:
            self.logger.error("btn_voice_checked language:%s, voice_group:%s, voice_name:%s config empty",
                              self.voice_language, self.voice_group, voice_name)
            exit(-1)

        # self.logger.debug("btn_voice_checked voice:%s", voice)
        self.voice_id = voice['id']

        # update style combox
        style_names = self.config.get_style_names(voice.get("styles", []))
        self.combox_style.clear()
        self.combox_style.addItems(style_names)

        # update role combox
        if voice.get("role", False):
            self.combox_role.setEnabled(True)
        else:
            self.combox_role.setEnabled(False)

        # update degree label
        if voice.get("styledegree", False):
            self.line_degree.setEnabled(True)
            self.slider_degree.setEnabled(True)
        else:
            self.line_degree.setEnabled(False)
            self.slider_degree.setEnabled(False)

        # update featrue label
        self.text_feature.setText(voice.get("comments", self.voice_feature))

    # 测试声音
    def btn_test_onclick(self):
        output_path = util.gen_filename("./example/test_text", self.voice_id)
        mp3_file_name = output_path + ".mp3"
        # 由于参数不同生成的内容不同，所以这里每次都重新生成
        # if not os.path.exists(mp3_file_name):
        content = util.read_file("./example/test_text.txt")
        voice_rate, voice_pitch, voice_degree = self.get_voice_args()
        ssml_text = util.gen_ssml_text(self.voice_language, self.voice_id, self.voice_style, voice_degree,
                                       self.voice_role, voice_rate, voice_pitch, content)
        asyncio.get_event_loop().run_until_complete(self.run(ssml_text, output_path))

        # 输出完成提示框
        playsound(mp3_file_name)

    # 开始转换
    def btn_start_onclick(self):
        if len(self.voice_text) == 0:
            QMessageBox.information(None, "提示", "请选择要转换的文件！")
            return

        voice_rate, voice_pitch, voice_degree = self.get_voice_args()
        ssml_text = util.gen_ssml_text(self.voice_language, self.voice_id, self.voice_style, voice_degree,
                                       self.voice_role, voice_rate, voice_pitch, self.voice_text)
        file_name = self.line_select_file.text()
        output_path = util.gen_filename(file_name.split(".")[0], self.voice_id)
        asyncio.get_event_loop().run_until_complete(self.run(ssml_text, output_path))
        # 输出完成提示框
        QMessageBox.information(None, "提示", "语音合成完成！")

    # 运行转换
    async def run(self, ssml_text, output_path):
        await tts.transferMsTTSData(self.config, ssml_text, output_path)

    def get_voice_args(self):
        return self.voice_rate - 100, self.voice_pitch - 50, self.voice_degree / 100
