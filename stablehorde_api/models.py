from typing import Optional, Sequence
import logging

import msgspec

class ModelPayloadLorasStable(msgspec.Struct):
    name: str # The exact name or CivitAI ID of the LoRa.
    model: int | None = None # The strength of the LoRa to apply to the SD model.
    clip: int | None = None # The strength of the LoRa to apply to the clip model.

    # If set, will try to discover a trigger for this LoRa which matches or
    # is similar to this string and inject it into the prompt.
    # If 'any' is specified it will be pick the first trigger.
    inject_trigger: str | None = None

    def to_dict(self):
        return {f: getattr(self, f) for f in self.__struct_fields__ if getattr(self, f) is not None}


class ModelPayloadTextualInversionsStable(msgspec.Struct):
    name: str
    inject_ti: str = "prompt" # prompt/negprompt
    strength: int | float | None = None

    def to_dict(self):
        return {f: getattr(self, f) for f in self.__struct_fields__ if getattr(self, f) is not None}


class ModelGenerationInputStable(msgspec.Struct):
    sampler_name: str | None = None
    cfg_scale: float | None = None
    denoising_strength: float | None = None
    height: int | None = None
    width: int | None = None
    seed_variation: int | None = None
    post_processing: Sequence[str] | None = ["GFPGAN"]
    karras: bool | None = None
    steps: int | None = None
    loras: Sequence[ModelPayloadLorasStable] | None = None
    n: int | None = None
    clip_skip: int | None = 2
    hires_fix: bool | None = None
    tis: Sequence[ModelPayloadTextualInversionsStable] | None = None
    control_type: str | None = None
    image_is_control: bool | None = None
    return_control_map: bool | None = None
    seed: int | str | None = None

    def to_dict(self):
        resp = {f: getattr(self, f) for f in self.__struct_fields__ if getattr(self, f) is not None}
        if "loras" in resp:
            loras = []
            for lora in self.loras:
                loras.append(lora.to_dict())
            resp["loras"] = loras
        if "tis" in resp:
            tis = []
            for ti in self.tis:
                tis.append(ti.to_dict())
            resp["tis"] = tis
        return resp


class FindUserResponse(msgspec.Struct):
    username: str = None
    id: int | None = None
    kudos: int | float | None = None
    concurrency: int | None = None
    worker_invited: int | None = None
    moderator: bool | None = None
    kudos_details: dict | None = None
    worker_count: int | None = None
    worker_ids: list | None = None
    sharedkey_ids: list | None = None
    trusted: bool | None = None
    flagged: bool | None = None
    vpn: bool | None = None
    special: bool | None = None
    pseudonymous: bool | None = None
    account_age: int | None = None


class GenerationInput(msgspec.Struct):
    prompt: str
    params: ModelGenerationInputStable | None = None
    nsfw: bool | None = None
    trusted_workers: bool | None = None
    censor_nsfw: bool | None = None
    workers: Sequence[str] | None = None
    models: Sequence[str] | None = None
    source_image: str | bytes | None = None
    source_processing: str | None = None
    source_mask: str | None = None
    r2: bool | None = None
    slow_workers: bool | None = None
    shared: bool | None = True
    replacement_filter: bool | None = False

    def to_dict(self):
        resp = {f: getattr(self, f) for f in self.__struct_fields__ if getattr(self, f) is not None}
        if "params" in resp:
            resp["params"] = self.params.to_dict()
        return resp


class GenerationQueued(msgspec.Struct):
    id: str
    kudos: int | float
    message: Optional[str] = None


class RequestStatusCheck(msgspec.Struct):
    finished: int
    processing: int
    restarted: int
    waiting: int
    done: bool
    faulted: bool
    wait_time: int
    queue_position: int
    kudos: float
    is_possible: bool


class GenerationStable(msgspec.Struct):
    worker_id: str
    worker_name: str
    model: str
    img: str
    seed: str


class RequestStatusStable(msgspec.Struct):
    finished: int
    processing: int
    restarted: int
    waiting: int
    done: bool
    faulted: bool
    wait_time: int
    queue_position: int
    kudos: float
    is_possible: bool
    generations: list[GenerationStable]
    gen_metadata: dict | list | None = None


class ValidationErrorDescription(msgspec.Struct):
    message: str
    errors: dict | None = {}


class InvalidAPIKeyDescription(msgspec.Struct):
    message: str


class TooManyPromptsDescription(msgspec.Struct):
    message: str


class MantenanceModeDescription(msgspec.Struct):
    message: str


class ActiveModelsRequest(msgspec.Struct):
    type: str | None = "image"
    min_count: int | None = None
    max_count: int | None = None

    def to_dict(self):
        return {f: getattr(self, f) for f in self.__struct_fields__ if getattr(self, f) is not None}


class ActiveModel(msgspec.Struct):
    name: str
    count: int
    performance: int | float
    queued: int | float
    jobs: int | float
    eta: int
    type: str
