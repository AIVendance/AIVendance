import cv2
import numpy as np

def read_image_from_bytes(file_content: bytes) -> np.ndarray:
    """Helper to convert uploaded bytes to an OpenCV image."""
    nparr = np.frombuffer(file_content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def resize_image(image: np.ndarray, width: int = 640) -> np.ndarray:
    """Resizes image while keeping aspect ratio."""
    h, w = image.shape[:2]
    if w > width:
        ratio = width / float(w)
        dim = (width, int(h * ratio))
        return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return image