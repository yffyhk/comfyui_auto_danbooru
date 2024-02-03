import numpy as np
import torch
import requests
import bs4 as bs
import re
import io

from PIL import Image, ImageDraw, ImageFont

def to_tensor(image: Image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0) 

class GetDanbooru:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'url': ('STRING', {'multiline': False})
            }
        }

    RETURN_TYPES = ('IMAGE', 'STRING')
    RETURN_NAMES = ('IMAGE', 'TAG')
    FUNCTION = 'download'
    CATEGORY = 'Danbooru'

    def download(self, url):
        response = requests.get(url)
        soup = bs.BeautifulSoup(response.text ,'lxml')

        elem_ul = soup.find("ul", {"class": "general-tag-list"})
        elem_img = soup.find('section', {'id': 'post-options'})
        elem_info = soup.find('section', {'id': 'post-information'})
        
        #get tags
        tags = []
        for sub in elem_ul.find_all('li', recursive=False):
            tags.append(sub.attrs['data-tag-name'])

        prompt_str = ','.join(tags)

        #get image
        elem_img_url = elem_img.find('li', {'id': 'post-option-view-large'}).a.attrs['href']
        elem_img_url = re.sub(r'\?.+', '', elem_img_url)

        #download image
        img_data = requests.get(elem_img_url).content

        #bytes to PIL image
        img_stream = io.BytesIO(img_data)
        image_ = Image.open(img_stream)

        #PIL image to tensor
        img_tensor = to_tensor(image_)

        return (img_tensor, prompt_str)
    
class TagPrompt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tags": ("STRING", {"multiline": True}), 
                "basic": ("STRING", {"multiline": True}), 
                "remove": ("STRING", {"multiline": True}), 
            }
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "to_prompt"

    CATEGORY = "Prompt"

    def remove(self, tags:str, remove:str):
        tags = [t.strip() for t in tags.split(',')]
        remove = [r.strip() for r in remove.split(',')]

        remove_tags = []
        for t_ in tags:
            for r_ in remove:
                if r_ in t_:
                    remove_tags.append(t_)
                    break

        tag_set = set(tags) - set(remove_tags)
        tag_str = ', '.join(tag_set)
        return tag_str

    def to_prompt(self, tags, clip, basic, remove):
        remove_tags = self.remove(tags, remove)
        prompt_str = f'{basic}, {remove_tags}'

        return (prompt_str, )
