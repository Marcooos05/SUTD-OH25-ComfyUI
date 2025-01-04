## Set up ComfyUI server
```
python -m venv myenv #create virtual environment
myenv\Scripts\activate
pip install -r .\requirements.txt
python .\main.py
```

#If you get the "Torch not compiled with CUDA enabled" error, uninstall torch with:
```
pip uninstall torch
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu124
```

## Set up for event pass generation
1. Create workflow on ComfyUI interface & export as API
2. Replace "websockets_api_example.py" prompt with exported workflow
//"websockets_api_example.py" will generate avatar based on input prompt line 179, and seed line 182 -> listen to websocket -> generate event pass when websocket receives the avatar image
//Find event pass photo based on the image path

requirements
//fonts to be in same folder as generate_card.py
//PIL & qrcode library