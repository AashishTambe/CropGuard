"""Disease/pest image analysis with a real-model hook and labelled demo fallback."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from utils.helpers import ROOT, class_kind, crop_catalog

MODEL_PATH = Path(os.environ.get("CROP_GUARD_MODEL_PATH", ROOT / "models" / "cropguard.pt"))


class DiseaseDetector:
    def __init__(self) -> None:
        self.mode = "demo"
        self.model = None
        self.device = "cpu"
        self._try_load()

    def _try_load(self) -> None:
        if not MODEL_PATH.exists():
            self.mode = "demo"
            return
        try:
            import torch
            from torchvision import models

            checkpoint = torch.load(MODEL_PATH, map_location="cpu")
            num_classes = checkpoint.get("num_classes")
            state = checkpoint["state_dict"] if isinstance(checkpoint, dict) and "state_dict" in checkpoint else checkpoint
            if num_classes is None and isinstance(state, dict):
                # Infer from last layer if possible
                for k, v in reversed(list(state.items())):
                    if hasattr(v, "shape") and len(v.shape) == 2:
                        num_classes = int(v.shape[0])
                        break
            if not num_classes:
                self.mode = "demo"
                return
            net = models.mobilenet_v2(weights=None)
            net.classifier[1] = torch.nn.Linear(net.last_channel, int(num_classes))
            net.load_state_dict(state, strict=False)
            net.eval()
            self.model = net
            self.labels = checkpoint.get("labels") if isinstance(checkpoint, dict) else None
            self.mode = "model"
        except Exception:
            self.mode = "demo"
            self.model = None

    def status_label(self) -> str:
        return "Ready (trained model)" if self.mode == "model" else "Ready (demo predictor)"

    def predict(self, image: Image.Image, crop_key: str) -> dict[str, Any]:
        crop_key = crop_key.lower()
        classes = crop_catalog()["crops"].get(crop_key, {}).get("classes", [])
        if not classes:
            classes = [{"id": "unknown", "name": "Unknown", "kind": "disease"}]
        if self.mode == "model" and self.model is not None:
            try:
                return self._infer(image, crop_key, classes)
            except Exception:
                pass
        return self._demo_predict(image, crop_key, classes)

    def _infer(self, image: Image.Image, crop_key: str, classes: list[dict[str, Any]]) -> dict[str, Any]:
        import torch
        from torchvision import transforms

        tfm = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )
        tensor = tfm(image.convert("RGB")).unsqueeze(0)
        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1)[0].cpu().numpy()
        labels = self.labels or [c["id"] for c in classes]
        # If model label count mismatches crop classes, fall back to demo rather than invent mapping.
        if len(probs) != len(labels):
            return self._demo_predict(image, crop_key, classes)
        order = np.argsort(probs)[::-1][:3]
        top = []
        for i in order:
            cid = labels[int(i)]
            name = next((c["name"] for c in classes if c["id"] == cid), str(cid))
            top.append({"id": cid, "name": name, "confidence": float(probs[int(i)])})
        best = top[0]
        return {
            "disease_id": best["id"],
            "disease": best["name"],
            "kind": class_kind(crop_key, best["id"]),
            "confidence": best["confidence"],
            "top3": top,
            "mode": "model",
            "note": "",
        }

    def _demo_predict(self, image: Image.Image, crop_key: str, classes: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Deterministic demo scores from crop + simple image statistics.
        Clearly labelled — not a trained disease model.
        Tomato + typical leaf photos bias toward Early Blight so the SIH demo script is repeatable.
        """
        arr = np.array(image.convert("RGB").resize((96, 96)), dtype=np.float32)
        digest = hashlib.md5(arr.tobytes() + crop_key.encode()).hexdigest()
        rng = np.random.default_rng(int(digest[:8], 16))

        names = [c["name"] for c in classes]
        ids = [c["id"] for c in classes]
        healthy_idx = next((i for i, c in enumerate(classes) if c.get("kind") == "healthy"), len(classes) - 1)

        mean_r, mean_g, mean_b = arr.mean(axis=(0, 1))
        # More brown/yellow than green → disease-like; green-dominant → healthier
        brownish = (mean_r + 10 > mean_g) and mean_g < 140
        scores = rng.normal(0.18, 0.04, size=len(classes))
        scores = np.clip(scores, 0.05, None)

        if crop_key == "tomato":
            # Hackathon walkthrough: Early Blight ~87%
            prefer = next((i for i, c in enumerate(classes) if "early" in c["id"]), 0)
            scores[prefer] = 0.87
            for i, c in enumerate(classes):
                if "late" in c["id"]:
                    scores[i] = 0.09
                elif c.get("kind") == "healthy":
                    scores[i] = 0.04
        elif brownish:
            disease_ids = [i for i, c in enumerate(classes) if c.get("kind") != "healthy"]
            pick = int(disease_ids[int(digest[8:10], 16) % max(len(disease_ids), 1)]) if disease_ids else 0
            scores[pick] = 0.72 + (int(digest[10:12], 16) % 12) / 100.0
            scores[healthy_idx] = 0.08
        else:
            scores[healthy_idx] = 0.62 + (int(digest[8:10], 16) % 15) / 100.0

        scores = scores / scores.sum()
        order = np.argsort(scores)[::-1][:3]
        top = [
            {"id": ids[int(i)], "name": names[int(i)], "confidence": float(scores[int(i)])}
            for i in order
        ]
        best = top[0]
        return {
            "disease_id": best["id"],
            "disease": best["name"],
            "kind": class_kind(crop_key, best["id"]),
            "confidence": best["confidence"],
            "top3": top,
            "mode": "demo",
            "note": "Demo prediction — replace with trained/open model for production.",
        }


_DETECTOR: DiseaseDetector | None = None


def get_detector() -> DiseaseDetector:
    global _DETECTOR
    if _DETECTOR is None:
        _DETECTOR = DiseaseDetector()
    return _DETECTOR
