# 微软tts音频下载工具
> 微软tts 使用 119 种语言和变体，超过 270 种神经语音来吸引全球观众。使用极具表现力和类似人类的声音将你的方案(如文本阅读器和支持语音的助手)变为现实。神经文本到语音转换功能支持若干种话语风格，包括聊天、新闻播报和客户服务，以及各种情感(如快乐和同情)。

## 官方的demo地址
```
https://azure.microsoft.com/zh-cn/services/cognitive-services/text-to-speech/#overview
```

# 项目目的和声明
- 本项目的目的是解决微软官方的网页版demo，不能直接下载转换后的MP3文件以及方便调试声音
- 本项目仅用于学习交流禁止用于商业用途
- 本项目核心代码来自：[skygongque/tts](https://github.com/skygongque/tts)

# 使用说明
1. config/config.json 可以配置速率、音调、强度、角色列表以及风格列表等参数
2. config/voice_config.json 可以配置语言列表和语音列表，方便动态添加自己想要调试的语音
3. 点击测试声音按钮，会使用选中的语音配置转换界面右侧的测试文本，然后自动播放
4. 点击开始转换，会使用选择的文本和选中的语音配置来转换并保存 mp3 文件到文本所在目录
5. 直接运行 main.py 即可，可以参考如下演示视频

# 演示视频
https://user-images.githubusercontent.com/9008110/166864052-507fd4dd-3143-4ab7-a423-4dec6124a11f.mov

