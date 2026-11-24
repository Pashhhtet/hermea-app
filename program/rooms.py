"""Определение типа комнаты на фото (локальная нейросеть CLIP, без интернета).

Используется, чтобы первым фото всегда шла кухня.
Если библиотека open_clip или файл модели не установлены — просто возвращает None,
и программа оставляет исходный порядок фото.
"""
import os

MODEL_FILE = "clip-rn50-cc12m.pt"
ARCH = "RN50-quickgelu"

LABELS = {
    "kitchen": ["a photo of a kitchen", "a kitchen with cabinets, a sink and a stove",
                "an open kitchen in a living room"],
    "living": ["a photo of a living room", "a living room with a sofa"],
    "bedroom": ["a photo of a bedroom with a bed"],
    "bathroom": ["a photo of a bathroom", "a bathroom with a shower and toilet"],
    "hall": ["a photo of a hallway with a door"],
    "balcony": ["a photo of a balcony", "a view from a window"],
    "plan": ["an architectural floor plan drawing"],
    "exterior": ["a photo of a building exterior"],
}


class RoomClassifier:
    def __init__(self, prog_dir):
        self.ok = False
        path = os.path.join(prog_dir, MODEL_FILE)
        if not os.path.exists(path):
            self.why = "нет файла модели " + MODEL_FILE
            return
        try:
            import torch
            import open_clip
            from PIL import Image  # noqa: F401
        except Exception as e:
            self.why = f"не установлена библиотека ({e})"
            return
        try:
            self.torch = torch
            self.model, _, self.pre = open_clip.create_model_and_transforms(ARCH, pretrained=path)
            self.model.eval()
            tok = open_clip.get_tokenizer(ARCH)
            self.names = list(LABELS)
            with torch.no_grad():
                feats = []
                for k in self.names:
                    e = self.model.encode_text(tok(LABELS[k]))
                    e = e / e.norm(dim=-1, keepdim=True)
                    feats.append(e.mean(0))
                t = torch.stack(feats)
                self.text = t / t.norm(dim=-1, keepdim=True)
            self.ok = True
        except Exception as e:
            self.why = f"модель не загрузилась ({e})"

    def classify(self, img_bgr):
        """-> (метка, вероятность кухни) или (None, 0.0)"""
        if not self.ok:
            return None, 0.0
        try:
            from PIL import Image
            import cv2
            im = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
            with self.torch.no_grad():
                e = self.model.encode_image(self.pre(im)[None])
                e = e / e.norm(dim=-1, keepdim=True)
                p = (100 * e @ self.text.T).softmax(-1)[0]
            best = int(p.argmax())
            return self.names[best], float(p[self.names.index("kitchen")])
        except Exception:
            return None, 0.0
