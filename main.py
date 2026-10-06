import cv2
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock


class VHSLiveCam(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 0 is usually the default camera. On Android with PyCamera2/OpenCV, try index 0 or 1.
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Dynamic control parameters
        self.chroma_shift = 3
        self.noise_amount = 20
        self.saturation = 0.8
        self.scanlines = True

        # Frame rate target (~30 FPS)
        Clock.schedule_interval(self.update_frame, 1.0 / 30.0)

    def apply_vhs_effect(self, frame):
        # 1. Downscale frame for retro resolution
        h, w, _ = frame.shape
        small = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_NEAREST)

        # 2. Chroma Shift (RGB Separation)
        b, g, r = cv2.split(small)
        shift = int(self.chroma_shift)
        if shift > 0:
            # Roll channels along the x-axis
            r = np.roll(r, shift, axis=1)
            b = np.roll(b, -shift, axis=1)

        shifted = cv2.merge([b, g, r])

        # 3. Adjust Saturation in HSV space
        if self.saturation != 1.0:
            hsv = cv2.cvtColor(shifted, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 1] *= self.saturation
            hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
            shifted = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        # 4. Tape Noise / Grain
        if self.noise_amount > 0:
            noise = np.random.randint(-self.noise_amount, self.noise_amount + 1, shifted.shape, dtype='int16')
            noisy_frame = cv2.add(shifted.astype('int16'), noise)
            shifted = np.clip(noisy_frame, 0, 255).astype('uint8')

        # 5. Scanlines
        if self.scanlines:
            shifted[::2, :, :] = (shifted[::2, :, :] * 0.75).astype(np.uint8)

        # Upscale back to output resolution using nearest-neighbor for sharp pixels
        return cv2.resize(shifted, (w, h), interpolation=cv2.INTER_NEAREST)

    def update_frame(self, dt):
        ret, frame = self.capture.read()
        if not ret:
            return

        # Process frame via OpenCV
        processed = self.apply_vhs_effect(frame)

        # Convert BGR (OpenCV) to RGB for Kivy Texture
        buf = cv2.flip(processed, 0).tobytes()
        texture = Texture.create(size=(processed.shape[1], processed.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        # Push texture to Kivy rendering surface
        self.texture = texture

    def release_camera(self):
        if self.capture and self.capture.isOpened():
            self.capture.release()


class AwesomeVHSApp(App):
    def build(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Live Camera Viewport
        self.camera_view = VHSLiveCam(size_hint_y=0.65)
        main_layout.add_widget(self.camera_view)

        # Interactive Controls
        controls = GridLayout(cols=2, spacing=5, size_hint_y=0.35)

        # Chroma Shift Slider
        controls.add_widget(Label(text="Chroma Shift (px):"))
        self.shift_slider = Slider(min=0, max=10, value=3, step=1)
        self.shift_slider.bind(value=self.on_shift_change)
        controls.add_widget(self.shift_slider)

        # Tape Noise Slider
        controls.add_widget(Label(text="Tape Grain Intensity:"))
        self.noise_slider = Slider(min=0, max=50, value=20, step=1)
        self.noise_slider.bind(value=self.on_noise_change)
        controls.add_widget(self.noise_slider)

        # Saturation Slider
        controls.add_widget(Label(text="Color Saturation:"))
        self.sat_slider = Slider(min=0.0, max=2.0, value=0.8, step=0.1)
        self.sat_slider.bind(value=self.on_sat_change)
        controls.add_widget(self.sat_slider)

        # Scanline Toggle Button
        controls.add_widget(Label(text="CRT Scanlines:"))
        self.scanline_btn = Button(text="Toggle Scanlines")
        self.scanline_btn.bind(on_release=self.toggle_scanlines)
        controls.add_widget(self.scanline_btn)

        main_layout.add_widget(controls)
        return main_layout

    def on_shift_change(self, instance, value):
        self.camera_view.chroma_shift = int(value)

    def on_noise_change(self, instance, value):
        self.camera_view.noise_amount = int(value)

    def on_sat_change(self, instance, value):
        self.camera_view.saturation = float(value)

    def toggle_scanlines(self, instance):
        self.camera_view.scanlines = not self.camera_view.scanlines

    def on_stop(self):
        # Free camera hardware when app closes
        self.camera_view.release_camera()


if __name__ == '__main__':
    AwesomeVHSApp().run()
