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

    def remove_prompt(self, tags_:[str]) -> [str]:
        targets_ = [
            'hair',
            'eye',
            'skin',
            'nipple',
        ]

        filter_tags = []
        for tag in tags_:
            filter = False
            for target in targets_:
                if target in tag:
                    filter = True
                    break
            
            if not filter:
                filter_tags.append(tag)

        return filter_tags

    def download(self, text:str):
        response = requests.get(url_)
        soup = bs.BeautifulSoup(response.text ,'lxml')

        elem_ul = soup.find("ul", {"class": "general-tag-list"})
        elem_img = soup.find('section', {'id': 'post-options'})
        elem_info = soup.find('section', {'id': 'post-information'})
        
        #get tags
        tags = []
        for sub in elem_ul.find_all('li', recursive=False):
            tags.append(sub.attrs['data-tag-name'])
            
        tags_rm = self.remove_prompt(tags)

        prompt_str = ', '.join(tags_rm)

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