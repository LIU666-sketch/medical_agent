import gradio as gr
from PIL import Image
from ocr_task import send_file, receive_result
from audio_module import audio_process, voice_advice
from medical_record_module import generate_medical_record, create_template_record

def ocr_handler(image, source):
    """处理OCR图像识别"""
    try:
        if source == "手动上传" or source == "实时拍摄":
            image_path = "captured_avatar.jpg"
            if source == "实时拍摄":
                # 保存并翻转图像
                image.save(image_path)
                with Image.open(image_path) as img:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                    img.save(image_path)
            else:
                image.save(image_path)
                
        # 发送处理后的图像文件并获取结果
        send_file(image_path)
        return receive_result()
    except Exception as e:
        return f"图像处理出错：{str(e)}"

def audio_handler(audio_file):
    """处理音频输入"""
    try:
        if not audio_file:
            return "请先录制音频", "无法提供建议"
        question, response = audio_process(audio_file)
        return question, response
    except Exception as e:
        return f"音频处理出错：{str(e)}", "无法提供建议"

def generate_medical_record_handler(info, answer):
    """生成病历图片"""
    try:
        if not info or not answer:
            # 如果没有信息，返回模板
            return create_template_record()
            
        record_path = generate_medical_record(info, answer)
        return record_path
    except Exception as e:
        print(f"病历生成出错：{str(e)}")
        return create_template_record()  # 发生错误时返回模板

def play_voice_advice():
    """播放语音建议"""
    try:
        return voice_advice()
    except Exception as e:
        print(f"语音建议生成出错：{str(e)}")
        return None

# GUI界面构建
with gr.Blocks() as demo:
    with gr.Tab("智慧医疗系统"):
        # 标题部分
        gr.Button("-----大连理工大学未来技术学院智慧医疗系统-----", variant="primary")
        
        # 第一行：欢迎信息和图像上传
        with gr.Row():
            with gr.Column(scale=4):
                gr.Textbox(
                    "欢迎来到智慧医疗系统！\n在这里我们的AI医生会竭尽全力答疑解惑\n让病魔无处遁形\n让健康伴您身边",
                    label="欢迎信息",
                    lines=6
                )
                source_choice = gr.Dropdown(
                    ["手动上传", "实时拍摄"],
                    label="选择图像来源",
                    value="手动上传"
                )
            
            with gr.Column(scale=8):
                image_input = gr.Image(
                    label="请上传您的就诊信息",
                    type="pil",
                    sources=["webcam", "upload"]
                )
                
            with gr.Column(scale=6):
                info_output = gr.Textbox(
                    label="就诊信息确认",
                    lines=10
                )
                submit_ocr = gr.Button("确认信息")

        # 分隔线
        gr.Button("-----就诊咨询-----", variant="primary")

        # 第二行：语音交互和病历显示
        with gr.Row():
            # 左侧语音交互区
            with gr.Column(scale=4):
                audio_input = gr.Audio(
                    type="filepath",
                    label="请说出您的问题"
                )
                submit_audio = gr.Button("开始语音咨询")
                
                question_output = gr.Textbox(
                    label="您的问题",
                    lines=3
                )
                answer_output = gr.Textbox(
                    label="AI医生建议",
                    lines=8
                )
                # 添加音频输出组件
                audio_output = gr.Audio(label="语音建议", visible=True)
                play_advice = gr.Button("收听语音建议")
            
            # 右侧病历显示区
            with gr.Column(scale=5):
                show_record = gr.Button("查看电子病历")
                record_display = gr.Image(
                    label="电子病历",
                    type="filepath",
                    value=create_template_record()  # 设置初始值为模板
                )

        # 底部
        gr.Button("-----感谢使用-----", variant="primary")

        # 事件绑定
        submit_ocr.click(
            ocr_handler,
            inputs=[image_input, source_choice],
            outputs=info_output
        )
        
        submit_audio.click(
            audio_handler,
            inputs=[audio_input],
            outputs=[question_output, answer_output]
        )
        
        show_record.click(
            generate_medical_record_handler,
            inputs=[info_output, answer_output],
            outputs=record_display
        )
        
        play_advice.click(
            play_voice_advice,
            inputs=None,
            outputs=audio_output  # 添加输出组件
        )

demo.launch(share=True)
