import PIL
import numpy as np
import torch
from diffusers.pipelines.stable_diffusion import StableDiffusionSafetyChecker
from transformers import CLIPFeatureExtractor

pilimage = PIL.Image.open("test1.png").convert("RGB")
image = np.array(pilimage)

feature_extractor = CLIPFeatureExtractor.from_pretrained("./models/feature_extractor")

safety_checker = StableDiffusionSafetyChecker.from_pretrained("./models/safety_checker")

safety_checker_input = feature_extractor(pilimage, return_tensors="pt").to(torch.float32)
image, has_nsfw_concept = safety_checker(images=image, clip_input=safety_checker_input.pixel_values.to(torch.float32))

print(has_nsfw_concept)

# from diffusion import ImageGenerationOptions
# from model import DiffusersModel
#
# opts = ImageGenerationOptions(
#     prompt="a cow",
#     negative_prompt="distorted",
#     image=None
#
# )
#
# pipe = DiffusersModel("")
#
# pipe.activate()
#
# for data in pipe(opts):
#     if type(data) == tuple:
#         pass
#     else:
#         image = data
#
# results = []
# for images, opts in image:
#     results.extend(images)
#
#
# results[0].save("haha.png", format="PNG")
# print(results)