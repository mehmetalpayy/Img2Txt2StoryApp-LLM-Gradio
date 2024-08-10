import gradio as gr
import numpy as np
from PIL import Image
import os
from imagetostory import ImageToStoryApp
from dotenv import load_dotenv

load_dotenv()

app = ImageToStoryApp()


def process_image(image, style, num_stories):

    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)

    return app.process(image, style, num_stories)


with gr.Blocks() as demo:
    gr.Markdown("<h1 style='text-align: center;'>Image to Story APP</h1>")

    with gr.Row():
        with gr.Column():
            image = gr.Image(label="Your Image", type="pil")

            style = gr.Dropdown(
                label="Story Style",
                choices=[
                    ("Romance", "romance"),
                    ("Adventure", "adventure"),
                    ("Mystery & detective", "mystery-&-detective"),
                    ("Fantasy", "fantasy"),
                    ("Humor & comedy", "humor-&-comedy"),
                    ("Paranormal", "paranormal"),
                    ("Science fiction", "science-fiction")
                ],
                value="romance"
            )

            num_stories = gr.Slider(
                label="Number of Stories",
                minimum=1,
                maximum=5,
                step=1,
                value=1
            )

            btn = gr.Button("Generate Story")

        with gr.Column():
            text_output = gr.Textbox(label="Image Description")
            story_output = gr.Textbox(label="Story")
            file_output = gr.File(label="Download Story")

    with gr.Row():
        btn.click(fn=process_image,
                  inputs=[image, style, num_stories],
                  outputs=[text_output, story_output, file_output],
                  show_progress="full")

if __name__ == "__main__":
    demo.launch(debug=True, share=True)
