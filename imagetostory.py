from transformers import pipeline
from PIL import Image
import re
import os
import textwrap
import torch
from dotenv import load_dotenv

load_dotenv()

device = 0 if torch.cuda.is_available() else -1


def format_text(text, max_line_length=100):
    """ Format the text by inserting newline characters to ensure no line exceeds max_line_length."""

    return "\n".join(textwrap.wrap(text, width=max_line_length))


def save_story(self, stories):
    filename = "generated_story.txt"
    formatted_stories = [f"{self.format_text(story)}" for story in stories]

    with open(filename, "w") as file:
        file.write("\n\n".join(formatted_stories))

    return filename


class ImageToStoryApp:
    def __init__(self):
        self.image_to_text_pipeline = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base",
                                               device=device)
        self.text_to_story = pipeline("text-generation", model="aspis/gpt2-genre-story-generation", device=device)
        self.default_width = 512
        self.default_height = 512

    # Image to Text
    def img2text(self, image):
        """Create a text from the image to understand what is in the image."""

        try:
            text = self.image_to_text_pipeline(image)
            return text

        except Exception as e:
            return f"Error occurred while processing image: {e}"

    # Text to Story
    def txt2story(self, text, num_stories, style):
        """Generate a response with StoryGenerator LLM using user based parameters."""

        try:

            style_map = {
                "romance": "Romance",
                "adventure": "Adventure",
                "mystery-&-detective": "Mystery & detective",
                "fantasy": "Fantasy",
                "humor-&-comedy": "Humor & comedy",
                "paranormal": "Paranormal",
                "science-fiction": "Science fiction"
            }

            prompt = f"{text[0].get('generated_text')}, Create a {style_map.get(style, 'heartwarming')} story about the image."

            # Generate the story
            responses = self.text_to_story(
                prompt,
                max_new_tokens=200,
                truncation=True,
                num_return_sequences=num_stories,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7,
                repetition_penalty=2.0,
                return_full_text=True,
                pad_token_id=self.text_to_story.tokenizer.eos_token_id
            )

            stories = []
            pattern = re.escape(text[0].get('generated_text')) + r"\s*,\s*Create a.*?story about the image\."
            for i in range(num_stories):
                story_text = re.sub(pattern, "", responses[i]['generated_text']).strip()
                stories.append(f"{i + 1}. Story:\n{story_text}")

            return stories

        except Exception as e:
            return f"Error occurred while generating story: {e}"

    def resize_image(self, image):
        """Resize the image to the default dimensions."""

        resized_image = image.resize((self.default_width, self.default_height), Image.LANCZOS)

        return resized_image

    def process(self, image, style, num_stories):
        """Process all the functions to create a story."""

        image = self.resize_image(image)

        scenario = self.img2text(image)
        if scenario:
            stories = self.txt2story(scenario, num_stories, style)
            if isinstance(stories, list):
                filename = save_story(stories)
                if filename:
                    return scenario[0].get('generated_text'), "\n\n".join(stories), filename
                else:
                    return scenario[0].get('generated_text'), "\n\n".join(stories), "Error: File could not be saved."

        return (
            "Image processing failed or no text generated from the image.",
            "Story generation failed.",
            "Occured problem while creating txt file."
        )
