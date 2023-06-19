import base64
from io import BytesIO

from potassium import Potassium, Request, Response
from PIL import Image
from diffusion import ImageGenerationOptions
from model import DiffusersModel
import numpy as np
# import torch
from diffusers.pipelines.stable_diffusion import StableDiffusionSafetyChecker
from transformers import CLIPFeatureExtractor

print('run handler')

pipe = DiffusersModel("")

app = Potassium("my_app")

#print('run handler')
@app.init
def init():

    pipe = DiffusersModel("")

    pipe.activate()
    context = {
        "model": pipe
    }
    return context

def handler(event):
    model_inputs = event['input']
    prompt = model_inputs.get('prompt', "Pepe")
    height = model_inputs.get('height', 512)
    negative = model_inputs.get('negative_prompt', "(deformed, distorted, disfigured:1.3), poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers:1.4), disconnected limbs, mutation, mutated, ugly, disgusting")
    batch_count = model_inputs.get('batch_count', 4)
    width = model_inputs.get('width', 512)
    steps = model_inputs.get('steps', 36)
    model = model_inputs.get('model', "Liberty")
    guidance_scale = model_inputs.get('guidance_scale', 7.5)
    seed = model_inputs.get('seed', -1)
    sampler = model_inputs.get('sampler', "dpm++")
    strength = model_inputs.get('strength', 1.0)
    initimg = model_inputs.get('image', None)

    opts = ImageGenerationOptions(image=None, strength=strength, scheduler_id=sampler, prompt=prompt, height=height, negative_prompt=negative, width=width, num_inference_steps=steps, guidance_scale=guidance_scale, seed=seed, batch_count=batch_count)

    pipe.activate(model)

    if initimg is not None:
        opts.image = Image.open(BytesIO(base64.b64decode(initimg)))

    for data in pipe(opts):
        if type(data) == tuple:
            pass
        else:
            image = data

    results = []
    for images, opts in image:
        results.extend(images)

    # do the things
    image1 = results[0]
    image1_np = np.array(image1)
    buffered1 = BytesIO()
    image1.save(buffered1, format="PNG")
    image_b1 = base64.b64encode(buffered1.getvalue()).decode('utf-8')

    image2 = results[1]
    image2_np = np.array(image2)
    buffered2 = BytesIO()
    image2.save(buffered2, format="PNG")
    image_b2 = base64.b64encode(buffered2.getvalue()).decode('utf-8')

    image3 = results[2]
    image3_np = np.array(image3)
    buffered3 = BytesIO()
    image3.save(buffered3, format="PNG")
    image_b3 = base64.b64encode(buffered3.getvalue()).decode('utf-8')

    image4 = results[3]
    image4_np = np.array(image4)
    buffered4 = BytesIO()
    image4.save(buffered4, format="PNG")
    image_b4 = base64.b64encode(buffered4.getvalue()).decode('utf-8')

    feature_extractor = CLIPFeatureExtractor.from_pretrained("./models/feature_extractor")

    safety_checker = StableDiffusionSafetyChecker.from_pretrained("./models/safety_checker")

    safety_checker_input = feature_extractor(image1, return_tensors="pt").to(torch.float32)
    _, has_nsfw_concept1 = safety_checker(images=image1_np, clip_input=safety_checker_input.pixel_values.to(torch.float32))

    safety_checker_input = feature_extractor(image2, return_tensors="pt").to(torch.float32)
    _, has_nsfw_concept2 = safety_checker(images=image2_np, clip_input=safety_checker_input.pixel_values.to(torch.float32))

    safety_checker_input = feature_extractor(image3, return_tensors="pt").to(torch.float32)
    _, has_nsfw_concept3 = safety_checker(images=image3_np, clip_input=safety_checker_input.pixel_values.to(torch.float32))

    safety_checker_input = feature_extractor(image4, return_tensors="pt").to(torch.float32)
    _, has_nsfw_concept4 = safety_checker(images=image4_np, clip_input=safety_checker_input.pixel_values.to(torch.float32))

    return Response(json={'images_base64': [[image_b1, has_nsfw_concept1], [image_b2, has_nsfw_concept2], [image_b3, has_nsfw_concept3], [image_b4, has_nsfw_concept4]]}, status=200)


if __name__ == "__main__":
    app.serve()