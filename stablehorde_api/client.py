import asyncio
import base64
import time
from typing import Optional
import json
from io import BytesIO
import base64

import aiofiles
import aiohttp
import msgspec
from loguru import logger
from PIL import Image

from . import errors, models


class StableHordeAPI:
    def __init__(
        self, api_key: Optional[str] = None,
        api: Optional[str] = 'https://stablehorde.net/api/v2',
        session: Optional[str] = None,
    ):
        if session is None:
            self._session = aiohttp.ClientSession()
        else:
            self._session = session
        self.api_key: str = api_key
        self.api: str = api

    async def _request(
        self, url: str, method: str = 'GET', json=None, headers=None
    ) -> aiohttp.ClientResponse:
        """Request an url using choiced method"""
        response = await self._session.request(method, url, json=json, headers=headers)
        logger.debug(
            f"Requesting {url} with method {method}\n"
            f"JSON: {json}\n"
            f"Headers: {headers}"
        )
        return response

    async def get_models(
        self, payload: models.ActiveModelsRequest | dict, 
    ) -> list[models.ActiveModel]:
        if not isinstance(payload, dict):
            payload = payload.to_dict()

        response = await self._request(
            self.api+'/status/models', "GET", payload, {'apikey': self.api_key}
        )

        return msgspec.json.decode(
            (await response.content.read()),
            type=list[models.ActiveModel]
        )

    async def find_user(
            self, api_key: str | None = None
    ) -> models.FindUserResponse:
        if api_key is None:
            api_key = self.api_key
        response = await self._request(
            self.api+"/find_user", "GET", None, {"apikey": api_key}
        )
        return msgspec.json.decode(
            (await response.content.read()),
            type=models.FindUserResponse
        )

    async def txt2img_request(
        self, payload: models.GenerationInput | dict
    ) -> models.GenerationQueued | dict:
        """Create an asynchronous request to generate images"""
        if not isinstance(payload, dict):
            payload = payload.to_dict()

        response = await self._request(
            self.api+'/generate/async', "POST", payload, {'apikey': self.api_key}
        )
        if response.status == 202:
            return msgspec.json.decode(
                (await response.content.read()),
                type=models.GenerationQueued
            )
        elif response.status == 400:
            description = msgspec.json.decode(
                (await response.content.read()),
                type=models.ValidationErrorDescription
            )
            raise errors.ValidationError(description.message + "\nErrors:\n" + str(description.errors))
        elif response.status == 401:
            description = msgspec.json.decode(
                (await response.content.read()),
                type=models.InvalidAPIKeyDescription
            )
            raise errors.InvalidAPIKey(description.message)
        elif response.status == 429:
            description = msgspec.json.decode(
                (await response.content.read()),
                type=models.TooManyPromptsDescription
            )
            raise errors.TooManyPrompts(description.message)
        elif response.status == 503:
            description = msgspec.json.decode(
                (await response.content.read()),
                type=models.MaintenanceModeDescription
            )
            raise errors.MaintenanceMode(description.message)
        else:
            raise ValueError("Invalid status code: " + str(response.status))

    async def convert_image(self, jpg_path):
        jpg_image = Image.open(jpg_path)
        webp_image = jpg_image.convert("RGBA")
        webp_bytes = BytesIO()
        webp_image.save(webp_bytes, "WEBP", lossless=True)
        jpg_image.close()
        webp_base64 = base64.b64encode(webp_bytes.getvalue())
        return webp_base64.decode()

    async def generate_from_txt(
        self,
        payload: models.GenerationInput | dict | str,
        filename: str | None = f"{int(time.time())}"
    ) -> dict:
        """Full method to generate images and save them in a file"""
        if isinstance(payload, str):
            payload = models.GenerationInput(payload)

        # Request an image generation
        image_gen = await self.txt2img_request(payload)
        finished = False
        while not finished:
            img_check = await self.generate_check(image_gen.id)
            if img_check.done == 1:
                finished = True
            else:
                await asyncio.sleep(img_check.wait_time)

        # Request a status of the generation with images
        img_status = await self.generate_status(image_gen.id)

        if isinstance(payload, dict):
            r2 = payload.get('r2')
        else:
            r2 = payload.r2

        generations = img_status.generations
        generations_paths = []
        for num, generation in enumerate(generations):
            new_filename = f'{filename}_{num}.webp'
            generations_paths.append(new_filename)
            async with aiofiles.open(new_filename, 'wb') as file:
                if r2:
                    # When r2 is set to True, it will return link
                    # instead of base64 encoded image
                    img_rsp = (await self._request(generation.img)).content
                    img_bytes = await img_rsp.read()
                else:
                    b64_bytes = generation.img.encode('utf-8')
                    img_bytes = base64.b64decode(b64_bytes)

                # Save image
                await file.write(img_bytes)

        return {"images": generations_paths, "img_status": img_status}

    async def generate_check(
        self, uuid: str
    ) -> models.RequestStatusCheck | dict:
        """Check the status of generation without consuming bandwidth"""
        response = await self._request(
            self.api+f'/generate/check/{uuid}'
        )
        if response.status == 404:
            raise errors.StatusNotFound("You entered an UUID that is not found")

        return msgspec.json.decode(
            (await response.content.read()),
            type=models.RequestStatusCheck
        )

    async def generate_status(
        self, uuid: str
    ) -> models.RequestStatusStable | dict:
        """
        Same as `generate_check`, but will also include all already
        generated images in a base64 encoded .webp files (if r2 not set).
        You should not request this often. It's limited to 1 request per minute
        """
        response = await self._request(
            self.api+f'/generate/status/{uuid}'
        )
        if response.status == 404:
            raise errors.StatusNotFound("You entered an UUID that is not found")

        return msgspec.json.decode(
            (await response.content.read()),
            type=models.RequestStatusStable
        )
