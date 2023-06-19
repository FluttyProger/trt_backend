import gc
import os
import random
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import *

from lib.diffusers.scheduler import SCHEDULERS

import torch

from diffusion import ImageGenerationOptions


ModelMode = Literal["diffusers", "tensorrt"]
logged_trt_warning = False


class DiffusersModel:
    def __init__(self, model_id: str):
        self.model_id: str = model_id
        self.activated: bool = False
        self.pipe = None

    def activate(self, model_name: str):
        from tensorrt_pipe import TensorRTStableDiffusionPipeline

        model_dir = "models/"+model_name
        self.pipe = TensorRTStableDiffusionPipeline.from_pretrained(
            model_id="",
            engine_dir=os.path.join(model_dir, "engine"),
            device=torch.device("cuda"),
            max_batch_size=1
        )

    def create_scheduler(self, scheduler_name: str):
        return SCHEDULERS[scheduler_name].from_pretrained("models/Liberty", subfolder="scheduler")

    def __call__(self, opts: ImageGenerationOptions, plugin_data: Dict[str, List] = {}):
        # if not self.activated:
        #     raise RuntimeError("Model not activated")

        if opts.seed is None or opts.seed == -1:
            opts.seed = random.randrange(0, 4294967294, 1)

        self.pipe.scheduler = self.create_scheduler(opts.scheduler_id)

        queue = Queue()
        done = object()
        total_steps = 0

        results = []

        def callback(*args, **kwargs):
            nonlocal total_steps
            total_steps += 1
            queue.put((total_steps, results))

        def on_done(feature):
            queue.put(done)

        for i in range(opts.batch_count):
            manual_seed = int(opts.seed + i)

            generator = torch.Generator(device=self.pipe.device).manual_seed(manual_seed)

            with ThreadPoolExecutor() as executer:
                feature = executer.submit(
                    self.pipe,
                    opts=opts,
                    generator=generator,
                    callback=callback,
                    plugin_data=plugin_data,
                )
                feature.add_done_callback(on_done)

                while True:
                    item = queue.get()
                    if item is done:
                        break
                    yield item

                images = feature.result().images

            results.append(
                (
                    images,
                    ImageGenerationOptions.parse_obj(
                        {"seed": manual_seed, **opts.dict()}
                    ),
                )
            )

        yield results
