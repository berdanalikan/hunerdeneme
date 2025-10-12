import sys

print("Python:", sys.version)

try:
    import paddle
    print("Paddle:", paddle.__version__)
    try:
        use_gpu = paddle.device.is_compiled_with_cuda()
        print("CUDA available:", use_gpu)
    except Exception as e:
        print("CUDA check failed:", repr(e))
except Exception as e:
    print("Paddle import failed:", repr(e))
    raise

try:
    import numpy as np
    import cv2  # type: ignore
    print("NumPy:", np.__version__)
    print("OpenCV:", cv2.__version__)
except Exception as e:
    print("Deps check failed:", repr(e))
    raise

print("Env verification completed successfully.")

