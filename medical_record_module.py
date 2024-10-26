from PIL import Image, ImageDraw, ImageFont
import datetime
import os
from config import FONT_PATH, TEMP_RECORD_PATH
import textwrap

def wrap_text(text, width=40):
    """将长文本按指定宽度换行"""
    return '\n'.join(textwrap.wrap(text, width=width))

def create_template_record():
    """创建空白的病历模板"""
    try:
        width = 800
        height = 1000  # 增加高度
        margin = 80    # 页面边距
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        font = ImageFont.truetype(FONT_PATH, 20)
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        
        template_content = f"""
电子病历
==================
就诊日期：{current_time}

患者信息：
等待输入...

主诉：
等待输入...

医生建议：
等待AI医生建议...

==================
注：本病历由AI辅助生成，仅供参考。
        """
        
        # 绘制文字，使用统一的左边距
        y_position = margin
        for line in template_content.split('\n'):
            draw.text((margin, y_position), line.strip(), font=font, fill='black')
            y_position += 30  # 行间距
        
        image.save(TEMP_RECORD_PATH)
        return TEMP_RECORD_PATH
    except Exception as e:
        print(f"创建模板出错：{str(e)}")
        return None

def generate_medical_record(info, answer):
    """生成带有内容的病历"""
    try:
        width = 800
        height = 1000  # 增加高度
        margin = 80    # 页面边距
        content_width = width - (margin * 2)  # 内容区域宽度
        char_width = 20  # 估计的单个字符宽度
        max_chars_per_line = int(content_width / char_width)  # 每行最大字符数
        
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        font = ImageFont.truetype(FONT_PATH, 20)
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # 处理患者信息
        info = info if info and info.strip() else "未提供患者信息"
        info = wrap_text(info, width=max_chars_per_line - 4)
        
        # 处理AI回答，移除参考链接部分
        answer = answer if answer and answer.strip() else "未提供诊断信息"
        # 如果回答中包含"参考："，只保留之前的内容
        if "参考：" in answer:
            answer = answer.split("参考：")[0].strip()
        answer = wrap_text(answer, width=max_chars_per_line - 4)
        
        # 构建内容
        header = f"""
电子病历
==================
就诊日期：{current_time}
"""
        
        body = f"""
患者信息：
{info}

主诉：
{answer}

医生建议：
请遵医嘱用药，保持良好作息。
如有不适请及时就医。

==================
注：本病历由AI辅助生成，仅供参考。
"""
        
        # 绘制文字
        y_position = margin
        
        # 绘制头部
        for line in header.strip().split('\n'):
            draw.text((margin, y_position), line.strip(), font=font, fill='black')
            y_position += 30
        
        y_position += 10  # 添加额外间距
        
        # 绘制主体内容
        for line in body.strip().split('\n'):
            draw.text((margin, y_position), line.strip(), font=font, fill='black')
            y_position += 30
        
        image.save(TEMP_RECORD_PATH)
        return TEMP_RECORD_PATH
    except Exception as e:
        print(f"病历生成出错：{str(e)}")
        return create_template_record()
