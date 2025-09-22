import os
import PIL.Image
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

class geminiModel:
    def __init__(self, key, model):
        self.key = key
        self.client = genai.Client(api_key=self.key)
        self.model = model
    
    def generateDefaultText(self, userInput) -> str:
       response = self.client.models.generate_content(
           model = self.model,
           contents = [userInput],
           config = types.GenerateContentConfig(
               max_output_tokens=500, 
               temperature=0.7,
           )
       )

       return response.text
    
    def inputImage(self, ins, path) -> str:
        image = Image.open(path)
        instruction = ins
        response = self.client.models.generate_content(
            model=self.model,
            contents=[image, instruction]
        )
        return response.text

    def GenerateImage(self, instruction):
        response = self.client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents= instruction,
        config=types.GenerateContentConfig(
              response_modalities=['Text', 'Image']
            )
        )
        
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)

            elif part.inline_data is not None:
                image = Image.open(BytesIO((part.inline_data.data)))
                image.save('C:\\Users\\USER\\Desktop\\projects\\Yoimiya3.0\\static\\geneated.png')
                image.show()

    def EditImage(self, path, content):
        image = PIL.Image.open(path)
        
        response = self.client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=[content, image],
            config=types.GenerateContentConfig(
              response_modalities=['Text', 'Image']
            )
        )

        for part in response.candidates[0].content.parts:
          if part.text is not None:
            print(part.text)
          elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save('C:\\Users\\USER\\Desktop\\projects\\Yoimiya3.0\\static\\edited.png')
            image.show()