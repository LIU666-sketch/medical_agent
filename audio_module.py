import os
from gtts import gTTS
import pyttsx3
import time
from medical_ai import create_medical_ai
from config import TEMP_DIR
import shutil

# 创建项目目录下的temp文件夹
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# 创建MedicalAI实例
medical_ai = create_medical_ai(
    provider_type="deepseek",
    enable_search=True,
    serper_api_key="填入你的搜索引擎api",
    api_key="sk-填入你的deepseekapi
)

def process_audio_file(audio_file_path):
    """处理音频文件并获取识别结果"""
    from soundreg_task import send_audiofile, receive_result
    
    # 复制音频文件到临时目录
    temp_audio = os.path.join(TEMP_DIR, "temp_audio.wav")
    shutil.copy(audio_file_path, temp_audio)
    
    # 发送音频文件并获取识别结果
    send_audiofile(temp_audio)
    recognized_text = receive_result()
    
    return recognized_text

def audio_process(audio_file_path):
    """处理音频输入并返回问答结果"""
    try:
        # 获取语音识别结果
        raw_text = process_audio_file(audio_file_path)
        
        if not raw_text:
            return "语音识别失败", "无法提供建议"
        
        # 清理识别文本
        question = raw_text.strip()
        if question.endswith('。。。') or question.endswith('...'):
            question = question[:-2]
        if not any(question.endswith(p) for p in ['。', '？', '！', '.', '?', '!']):
            question += '。'
            
        print(f"处理后的语音识别结果: {question}")
        
        # 获取医疗建议
        response = medical_ai.get_medical_advice(question)
        print(f"AI回复: {response}")
        
        return question, response
            
    except Exception as e:
        print(f"错误详情: {str(e)}")
        return f"音频处理出错：{str(e)}", "无法提供建议"

def text_process(text):
    """处理文本输入"""
    if not text or text.strip() == "":
        return "请输入您的问题"
    try:
        response = medical_ai.get_medical_advice(text)
        return response
    except Exception as e:
        print(f"文本处理出错：{str(e)}")
        return f"处理出错：{str(e)}"

def voice_advice():
    """生成语音建议"""
    try:
        text = "感谢您使用AI医疗助手，请记得按时服药，保持良好的作息习惯。如果症状持续，建议及时就医。"
        
        try:
            # 首先尝试使用 gTTS
            tts = gTTS(text=text, lang='zh-cn')
            temp_mp3_path = os.path.join(TEMP_DIR, f"temp_advice_{int(time.time())}.mp3")
            tts.save(temp_mp3_path)
            return temp_mp3_path
            
        except Exception as e:
            print(f"gTTS失败，尝试使用本地引擎: {str(e)}")
            
            # 如果 gTTS 失败，使用 pyttsx3 作为备选
            engine = pyttsx3.init()
            temp_mp3_path = os.path.join(TEMP_DIR, f"temp_advice_{int(time.time())}.mp3")
            engine.save_to_file(text, temp_mp3_path)
            engine.runAndWait()
            return temp_mp3_path
            
    except Exception as e:
        print(f"语音生成出错：{str(e)}")
        return None

def clean_temp_files():
    """清理temp文件夹中的临时文件"""
    for file in os.listdir(TEMP_DIR):
        try:
            os.remove(os.path.join(TEMP_DIR, file))
        except:
            pass

# 启动时清理临时文件
clean_temp_files()
