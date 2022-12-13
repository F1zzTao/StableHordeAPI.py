from typing import Optional, Sequence

import msgspec


class ModelGenerationInputStable(msgspec.Struct):
    sampler_name: str | None = None
    cfg_scale: float | None = None
    denoising_strength: float | None = None
    height: int | None = None
    weight: int | None = None
    seed_variation: int | None = None
    post_processing: Sequence[str] | None = None
    karras: bool | None = None
    steps: int | None = None
    n: int | None = None

    def to_dict(self):
        return {f: getattr(self, f) for f in self.__struct_fields__}


class GenerationInput(msgspec.Struct):
    prompt: str
    params: ModelGenerationInputStable | None = None
    nsfw: bool | None = None
    trusted_workers: bool | None = None
    censor_nsfw: bool | None = None
    workers: Sequence[str] | None = None
    models: Sequence[str] | None = None
    source_image: str | None = None
    source_processing: str | None = None
    source_mask: str | None = None
    r2: bool | None = None

    def to_dict(self):
        return {f: getattr(self, f) for f in self.__struct_fields__ if getattr(self, f) is not None}


class RequestAsync(msgspec.Struct):
    id: str
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
