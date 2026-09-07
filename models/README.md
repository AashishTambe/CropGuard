# CropGuard AI models

Place a trained crop-disease classifier here for production use.

## Expected file

- `cropguard.pt` — PyTorch `state_dict` for a MobileNetV2 classifier

## How to plug in a real model

1. Train or download an **open** PlantVillage-compatible classifier (document license and classes).
2. Save weights as `models/cropguard.pt`.
3. Put class names in `data/diseases.json` under each crop (`classes` list, same order as model outputs) **or** provide a `models/labels.json` mapping.
4. Set `CROP_GUARD_MODEL_PATH` if the file is stored elsewhere.

The detector in `services/disease_detection.py` will automatically leave **Demo Mode** when a valid checkpoint loads.

## Demo Mode

If no checkpoint is present, CropGuard uses a clearly labelled demo predictor. It does **not** run ImageNet labels as crop diseases.

## Dataset note

PlantVillage is a common public research dataset. Do not download copyrighted data automatically. Do not claim government or field accuracy from a lab-leaf model without local validation.

## License reminder

Document model name, source, license, input size, and class list before any demo that claims real inference.
