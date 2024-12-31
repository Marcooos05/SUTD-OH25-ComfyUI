#This is an example that uses the websockets api to know when a prompt execution is done
#Once the prompt execution is done it downloads the images using the /history endpoint


import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse

from PIL import Image
import random
import io
import os

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    output = json.loads(urllib.request.urlopen(req).read())
    return output

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        # print("http://{}/view?{}".format(server_address, url_values))
        # print('output', response.read())
        content_type = response.info().get_content_type()  # Gets the MIME type
        print(f"Content-Type: {content_type}")
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            print('message', message) 
            if message['type'] == 'executed':
                data = message['data']
                if data['prompt_id'] == prompt_id:
                    filename = data['output']['images'][0]['filename'] #To retrieve the filename of the image
                    #To replace 0 with iteration if doing batch processing
                    # print('filename', filename)


            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            # If you want to be able to decode the binary stream for latent previews, here is how you can do it:
            # bytesIO = BytesIO(out[8:])
            # preview_image = Image.open(bytesIO) # This is your preview in PIL image format, store it in a global
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        images_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
        output_images[node_id] = images_output

    return output_images

def get_random_avatar(avatar_type, personal_interest=None):
    avatar_names = [
    "Innovative engineer",
    "Interdisciplinary architect",
    "Collaborative designer",
    "Design-centric creator",
    "Tech-savvy developer",
    "Hands-on builder",
    "Creative innovator",
    "Problem-solving analyst",
    "Sustainable-minded planner",
    "Entrepreneurial visionary",
    "Adaptive learner",
    "Human-centered designer",
    "Project-driven manager",
    "Critical-thinking researcher",
    "Resilient problem-solver",
    "Experimental thinker",
    "Globally-aware strategist",
    "Digitally-literate technologist",
    "Visionary futurist",
    "Holistic systems-thinker",
    "Inclusive leader"
    ]
    taglines = [
    "Building the future with innovation!",
    "Designing spaces that inspire!",
    "Crafting solutions with creativity!",
    "Bringing visionary ideas to life!",
    "Coding the blueprint of tomorrow!",
    "Constructing dreams with hands-on expertise!",
    "Pioneering breakthroughs in design and technology!",
    "Solving problems with precision and insight!",
    "Shaping sustainable futures with foresight!",
    "Leading the way with entrepreneurial spirit!",
    "Adapting to challenges with curiosity!",
    "Crafting solutions with creativity!",
    "Driving projects to success with leadership!",
    "Exploring new frontiers with critical thinking!",
    "Overcoming obstacles with resilience!",
    "Experimenting with bold ideas!",
    "Navigating global challenges with insight!",
    "Innovating with digital expertise!",
    "Envisioning tomorrow with creativity!",
    "Designing holistic solutions for complex problems!"
    "Trailblazing a better world by design!"]

    random_number = random.randint(0, 20)
    avatar_name = avatar_names[random_number]
    tagline = taglines[random_number]
    
    random_avatar_number = random.randint(1, 3)
    script_dir = os.path.dirname(__file__)
    avatar_base_path = os.path.join(script_dir, "Samples\\")
    avatar_path = avatar_base_path + f'{avatar_type}_Sample{random_avatar_number}.png'    

    return avatar_name, tagline, avatar_path

def get_custom_avatar(avatar_type, personal_interest):
    # call websocket to get custom avatar
    prompt_text = """
{
  "3": {
    "inputs": {
      "seed": 785790463864392,
      "steps": 30,
      "cfg": 7,
      "sampler_name": "euler_ancestral",
      "scheduler": "karras",
      "denoise": 1,
      "model": [
        "39",
        0
      ],
      "positive": [
        "6",
        0
      ],
      "negative": [
        "7",
        0
      ],
      "latent_image": [
        "40",
        0
      ]
    },
    "class_type": "KSampler"
  },
  "4": {
    "inputs": {
      "ckpt_name": "sdXL_v10VAEFix.safetensors"
    },
    "class_type": "CheckpointLoaderSimple"
  },
  "6": {
    "inputs": {
      "text": "anthropomorphic computer scientist character close up of upper body, character focus, young student, in action, simple, flat colors, stardew valley style, pixel art style",
      "clip": [
        "39",
        1
      ]
    },
    "class_type": "CLIPTextEncode"
  },
  "7": {
    "inputs": {
      "text": "low quality, blurry, deformed, watermark, text, signature, depth of field, photoreal, white background",
      "clip": [
        "39",
        1
      ]
    },
    "class_type": "CLIPTextEncode"
  },
  "25": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode"
  },
  "38": {
    "inputs": {
      "filename_prefix": "pixelbuildings128-v1-raw-",
      "images": [
        "25",
        0
      ]
    },
    "class_type": "SaveImage"
  },
  "39": {
    "inputs": {
      "lora_name": "pixel-art-xl-v1.1.safetensors",
      "strength_model": 1,
      "strength_clip": 1,
      "model": [
        "4",
        0
      ],
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "LoraLoader"
  },
  "40": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage"
  }
}
"""
    prompt = json.loads(prompt_text)
    #set the text prompt for our positive CLIPTextEncode
    prompt["6"]["inputs"]["text"] = f"anthropomorphic {personal_interest} character close up of upper body, character focus, young {avatar_type} student, in action, simple, flat colors, stardew valley style, pixel art style"

    #set the seed for our KSampler node
    seed = random.choice([1,2,3]) # TODO set a fixed set of seeds available
    prompt["3"]["inputs"]["seed"] = 785790463864390

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)
    ws.close()
    
    script_dir = os.path.dirname(__file__)
    avatar_folder = os.path.join(script_dir, "Avatars")
    os.makedirs(avatar_folder, exist_ok=True)
    for node_id in images:
        for image_data in images[node_id]:
            avatar_path = os.path.join(avatar_folder, f"{avatar_type}_{personal_interest}_avatar.png")
            image = Image.open(io.BytesIO(image_data))
            image.save(avatar_path)

    print('avatar_path',avatar_path)
    avatar_name = f"{personal_interest} {avatar_type}"
    tagline = f"Trailblazing a better world by design!"
    return avatar_name, tagline, avatar_path