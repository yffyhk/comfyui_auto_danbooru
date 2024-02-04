import numpy as np
import torch
import requests
import bs4 as bs
import re
import io

from PIL import Image

def to_tensor(image: Image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0) 

class GetDanbooru:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'url': ('STRING', {'multiline': False}),
                "zoom": ("INT", {"default": 512, "min": 64, "max": 2048}), 
            }
        }

    RETURN_TYPES = ('IMAGE', 'STRING', 'INT', 'INT')
    RETURN_NAMES = ('IMAGE', 'TAG', 'IMG_WIDTH', 'IMG_HEIGHT')
    FUNCTION = 'download'
    CATEGORY = 'Danbooru'

    def download(self, url, zoom):
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

        #get size and resize the output image size to same radio
        size_info = elem_info.find('li', {'id': 'post-info-size'}).text
        sizes = re.search("([0-9]+)x([0-9]+)", size_info).group().split('x')
        img_width = int(sizes[0])
        img_height = int(sizes[1])

        #check image size is | or  - 
        img_max_length = max(img_width, img_height)
        img_zoom = zoom / img_max_length

        img_width = int(img_width * img_zoom)
        img_height = int(img_height * img_zoom)

        #download image
        img_data = requests.get(elem_img_url).content

        #bytes to PIL image
        img_stream = io.BytesIO(img_data)
        image_ = Image.open(img_stream)

        #PIL image to tensor
        img_tensor = to_tensor(image_)

        return (img_tensor, prompt_str, img_width, img_height)
    
class TagPrompt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tags": ("STRING", {"forceInput": True}), 
                "basic": ("STRING", {"multiline": True}), 
                "remove": ("STRING", {"multiline": True}), 
            }
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "to_prompt"

    CATEGORY = "Danbooru"

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

    def to_prompt(self, tags, basic, remove):
        remove_tags = self.remove(tags, remove)
        prompt_str = f'{basic}, {remove_tags}'

        return (prompt_str,)
