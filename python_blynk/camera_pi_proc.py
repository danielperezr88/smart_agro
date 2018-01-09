import io
import time
import picamera
from picamera.array import PiRGBArray
from base_camera import BaseCamera
from PIL import Image

from matplotlib.colors import rgb_to_hsv as r2h
from matplotlib.colors import hsv_to_rgb as h2r


class Camera(BaseCamera):
    @staticmethod
    def frames():
        with picamera.PiCamera() as camera:

            highResCap = PiRGBArray(camera)

            # let camera warm up
            time.sleep(2)

            for foo in camera.capture_continuous(highResCap, 'rgb',
                                                 use_video_port=True):
                # return current frame
                highResCap.seek(0)
                highResCap.flush()
                arr = highResCap.array
                arr = r2h(arr)
                arr[:, :, :][0.4 < arr[:, :, 0]] = 0
                arr = h2r(arr)
                res = io.BytesIO()
                Image.fromarray(arr.astype('uint8')).save(res, 'jpeg')
                yield res.getvalue()

                # reset stream for next frame
                highResCap.seek(0)
                highResCap.truncate()
