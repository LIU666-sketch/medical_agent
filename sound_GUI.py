import gradio as gr
from soundreg_task import send_audiofile, receive_result
import shutil

def audioreg(audio_file_path):
    # 指定保存文件的路径和名称
    save_path = "saved_audio.wav"
    # 复制录制的音频文件到目标路径
    shutil.copy(audio_file_path, save_path)

    # 发送处理后的图像文件
    send_audiofile(save_path)
    return receive_result()

with gr.Blocks() as demo:
    with gr.Tab() as tab1:
        with gr.Row():
            voice_get = gr.Audio(type="filepath", label="请说出您的病症")
            submit_button2 = gr.Button("询问", scale=3)
            inquiry_show = gr.Textbox(label="您的问题是：", lines=5, scale=1)

        submit_button2.click(audioreg, inputs=voice_get, outputs=inquiry_show)

demo.launch()