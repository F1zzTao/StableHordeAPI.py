## Discontinued, use [pyAIHorde](https://github.com/lapismyt/pyAIHorde) instead :warning:

<h1 align="center">
StableHordeAPI.py
</h1>
<h2 align="center">Simple wrapper around Stable Horde API</h2>

# :warning: StableHordeAPI.py is obsolete. Consider using [horde-sdk by Haidra-Org](https://github.com/Haidra-Org/horde-sdk) instead :warning:

# Content
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [License](#license)

# Installation
```
pip install git+https://github.com/lapismyt/StableHordeAPI.py
```

# Usage
```python
import asyncio

from stablehorde_api import StableHordeAPI

async def main():
    client = StableHordeAPI("Your Stable Horde token here")
    prompt = "Futuristic cyberpunk landscape, 8k, hyper realistic, cinematic"
    negative_prompt = "lowres, bad quality, low quality, text, username, error"
    await client.generate_from_txt(
        prompt + " ### " + negative_prompt
    )

asyncio.run(main())
```
This code will generate an image based on your prompt and save it as "{unix timestamp}\_0.webp" in your current directory.

Additionally, you can specify file name:
```python
await client.generate_from_txt(
    "Your prompt...",
    filename="my_image"
)
```
In that case, your file will be saved as "my\_image.webp"

However, you'll probably want more control over how image is generated. So, for example, you can do this:
```python
import asyncio
from stablehorde_api import GenerationInput, ModelGenerationInputStable

async def main():
    client = StableHordeAPI("Your Stable Horde token here")
    payload = GenerationInput(
        "masterpiece, best quality, ((Hu Tao)), brown hair, long hair, flower-shaped pupils",
	params=ModelGenerationInputStable(
	    height=512,
	    width=768,
	    steps=50,
	    post_processing=['RealESRGAN_x4plus']
	),
	nsfw=True,
	censor_nsfw=False,
	models=['Anything Diffusion'],
	n=5
    )
    # payload can also be a dict, which is useful, if something new added
    txt2img_rsp = await client.txt2img_request(payload)
    img_uuid = txt2img_rsp.id

    done = False
    while not done:
        # Checking every second if image is generated
        await asyncio.sleep(1)
        generate_check = await client.generate_check(img_uuid)
	if generate_check.done == 1:
	    done = True

    # Generating a status which has all generations (in our case,
    # there should be 5 generations, because n is set to 5)
    generate_status = await client.generate_status(img_uuid)
    generations = generate_status.generations
```
After that, all generations will be in `generations` variable. To access first image, use `generations[0].img`

# Examples
This example will generate 3 Hu Tao images using Anything Diffusion model.
```python
import asyncio
import base64

import aiofiles
from stablehorde_api import GenerationInput, ModelGenerationInputStable

async def main():
    client = StableHordeAPI("Your Stable Horde token here")
    payload = GenerationInput(
        "masterpiece, best quality, ((Hu Tao)), brown hair, long hair, flower-shaped pupils",
	models=['Anything Diffusion'],
	n=3
    )
    txt2img_rsp = await client.txt2img_request(payload)
    img_uuid = txt2img_rsp.id

    done = False
    while not done:
        await asyncio.sleep(1)
        generate_check = await client.generate_check(img_uuid)
	if generate_check.done == 1:
	    done = True

    generate_status = await client.generate_status(img_uuid)
    generations = generate_status.generations
    for num, generation in enumerate(generations):
        new_filename = f'{filename}_{num}.webp'
        async with aiofiles.open(new_filename, 'wb') as file:
            b64_bytes = generation.img.encode('utf-8')
            img_bytes = base64.b64decode(b64_bytes)
            await file.write(img_bytes)
```
You can use LoRA's from CivitAI, by setting `loras`:
```
from stablehorde_api import ModelPayloadLorasStable, ModelGenerationInputStable

lora = '14479' # Model Version ID
strength = 0.9 # Model Strength
clip = 1 # CLIP Strength, not necessary
trigger = "Hu Tao" # Trigger tag, not necessary

loras = [ModelPayloadLorasStable(lora, model=strength, clip=clip_strength, inject_trigger=trigger)]
params = ModelGenerationInputStable(loras=loras)

prompt = ""masterpiece, best quality, ((Hu Tao)), brown hair, long hair, flower-shaped pupils"
model = 'Anything Diffusion'
payload = GenerationInput(prompt, models=[model], params=params)
...
```
If you set `r2` to true, then you will need to request content from the link in generations. You can do that by using aiohttp:
```python
import aiohttp
...

aiohttp_client = aiohttp.ClientSession()
...

img_rsp = (await aiohttp_client.request(url=generation.img)).content
img_bytes = await img_rsp.read()
```

# License
[MIT License](./LICENSE)

