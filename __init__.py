from .nodes.nodes import *

NODE_CLASS_MAPPINGS = { 
    'GetDanbooru': GetDanbooru,
    'TagEncode': TextEncode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    'GetDanbooru': 'Get Danbooru',
    'TagEncode': 'Tag Encode',
}