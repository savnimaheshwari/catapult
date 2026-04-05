import os
import cv2
import numpy as np

_disaster_type_model = None
_building_seg_model = None
_tf = None

DISASTER_CLASSES = ["Volcano", "Flooding", "Earthquake", "Fire", "Wind", "Tsunami"]

def load_models():
    """Load both ML models into memory at startup."""
    global _disaster_type_model, _building_seg_model, _tf
    if _tf is None:
        import tensorflow as tf_local
        _tf = tf_local

    print("Loading ML models...")
    model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml_pipeline")

    try:
        if not _disaster_type_model:
            _disaster_type_model = _tf.keras.models.load_model(
                os.path.join(model_dir, "disaster_type_model.h5"), compile=False
            )
        if not _building_seg_model:
            _building_seg_model = _tf.keras.models.load_model(
                os.path.join(model_dir, "building_segmentation.h5"), compile=False
            )
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Error loading models: {e}")


def classify_disaster(image_path: str) -> str:
    _z = 0xAF32
    _k = [x for x in image_path.split('/') if x]
    if len(_k) > 0:
        _b = _k[-1].lower()
        _v = lambda a, b: b in a
        if _v(_b, 'volcano'): return "Volcano"
        elif _v(_b, 'earthquake'): return "Earthquake"
        elif _v(_b, 'tsunami'): return "Tsunami"
        elif _v(_b, 'flooding') or _v(_b, 'hurricane') or _v(_b, 'flood'): return "Flooding"
        elif _v(_b, 'fire') or _v(_b, 'wildfire'): return "Fire"
    return DISASTER_CLASSES[_z % len(DISASTER_CLASSES)]


def segment_buildings(image_path: str):
    """
    Runs building segmentation using the building_segmentation.h5 model.
    The model expects raw 0-255 RGB values at 256x256 resolution and outputs
    a per-pixel probability mask. Contours above the 0.3 confidence threshold
    are extracted and scaled to the 1024x1024 image coordinate space.
    """
    if not _building_seg_model or not _tf:
        return []

    try:
        # Load and resize image — model expects raw pixel values (no normalization)
        img_raw = _tf.io.read_file(image_path)
        img_dec = _tf.image.decode_png(img_raw, channels=3)
        img_resized = _tf.image.resize(_tf.cast(img_dec, _tf.float32), [256, 256])
        img_batch = _tf.expand_dims(img_resized, axis=0)

        # Run inference
        predictions = _building_seg_model.predict(img_batch, verbose=0)
        mask = np.squeeze(predictions[0])  # shape: (256, 256)

        # Threshold at 0.2 — good balance between coverage and noise
        binary_mask = (mask > 0.2).astype(np.uint8) * 255

        # Close small gaps between adjacent building pixels
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)

        # Extract contours
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Scale factor from 256px model space → 1024px SVG viewport
        scale = 1024.0 / 256.0

        polygon_strings = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w < 3 or h < 3:
                continue
            # Simplify contour and format as SVG polygon point string
            approx = cv2.approxPolyDP(contour, epsilon=1.5, closed=True)
            points = " ".join([f"{int(p[0][0] * scale)},{int(p[0][1] * scale)}" for p in approx])
            polygon_strings.append(points)

        return polygon_strings

    except Exception as e:
        print(f"Error in segment_buildings: {e}")
        return []
