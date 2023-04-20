#!/usr/bin/python3
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
import json
import re
import sys
from decimal import Decimal
from decimal import InvalidOperation as DecimalInvalidOperation
from typing import Tuple
from xml.dom import minidom
from xml.parsers.expat import ExpatError

import clipboard
from PIL import Image, ImageDraw
from PyQt5 import QtGui, QtWidgets, uic

import easingslist as easings  # to avoid conflicts


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.
    Examples
    --------
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)
    """
    if a == b:
        return a
    return (1 - t) * a + t * b


ease_options = [
    {"name": "Linear", "func": easings.LinearInOut().func},
    {"name": "Sine In", "func": easings.SineEaseIn().func},
    {"name": "Sine Out", "func": easings.SineEaseOut().func},
    {"name": "Sine In Out", "func": easings.SineEaseInOut().func},
    {"name": "Quad In", "func": easings.QuadEaseIn().func},
    {"name": "Quad Out", "func": easings.QuadEaseOut().func},
    {"name": "Quad In Out", "func": easings.QuadEaseInOut().func},
    {"name": "Cubic In", "func": easings.CubicEaseIn().func},
    {"name": "Cubic Out", "func": easings.CubicEaseOut().func},
    {"name": "Cubic In Out", "func": easings.CubicEaseInOut().func},
    {"name": "Quart In", "func": easings.QuarticEaseIn().func},
    {"name": "Quart Out", "func": easings.QuarticEaseOut().func},
    {"name": "Quart In Out", "func": easings.QuarticEaseInOut().func},
    {"name": "Quint In", "func": easings.QuinticEaseIn().func},
    {"name": "Quint Out", "func": easings.QuinticEaseOut().func},
    {"name": "Quint In Out", "func": easings.QuinticEaseInOut().func},
    {"name": "Expo In", "func": easings.ExponentialEaseIn().func},
    {"name": "Expo Out", "func": easings.ExponentialEaseOut().func},
    {"name": "Expo In Out", "func": easings.ExponentialEaseInOut().func},
    {"name": "Circ In", "func": easings.CircularEaseIn().func},
    {"name": "Circ Out", "func": easings.CircularEaseOut().func},
    {"name": "Circ In Out", "func": easings.CircularEaseInOut().func},
    {"name": "Back In", "func": easings.BackEaseIn().func},
    {"name": "Back Out", "func": easings.BackEaseOut().func},
    {"name": "Back In Out", "func": easings.BackEaseInOut().func},
    {"name": "Elastic In", "func": easings.ElasticEaseIn().func},
    {"name": "Elastic Out", "func": easings.ElasticEaseOut().func},
    {"name": "Elastic In Out", "func": easings.ElasticEaseInOut().func},
    {"name": "Bounce In", "func": easings.BounceEaseIn().func},
    {"name": "Bounce Out", "func": easings.BounceEaseOut().func},
    {"name": "Bounce In Out", "func": easings.BounceEaseInOut().func},
]


def generate_values(easetype, duration, data, fps):
    t = []
    max_range = int(duration * fps)

    for i in range(0, max_range + 1):
        value01 = i / max_range
        value = easetype(value01)
        rect = (
            str(int(lerp(data["start"]["x"], data["end"]["x"], value)))
            + " "
            + str(int(lerp(data["start"]["y"], data["end"]["y"], value)))
        )
        rect += " " + str(
            int(lerp(data["start"]["width"], data["end"]["width"], value))
        )
        rect += " " + str(
            int(lerp(data["start"]["height"], data["end"]["height"], value))
        )
        rect += " " + str(
            lerp(data["start"]["opacity"], data["end"]["opacity"], value)
        )
        t.append(str(i) + "=" + rect)
        print(t[len(t) - 1])
    return ";".join(t)


def generate_json(easetype, duration, data, fps):
    return [
        {
            "DisplayName": "Generated easing for " + easetype["name"],
            "in": 0,
            "max": 0,
            "min": 0,
            "name": "rect",
            "opacity": True,
            "out": int(duration * fps),
            "type": 7,
            "value": generate_values(easetype["func"], duration, data, fps),
        }
    ]


class ClipWidget:
    def __init__(self, wid):
        self.wid = wid
        uic.loadUi("ui/clip.ui", self.wid)

        self.wid.btnPasteFps.clicked.connect(self.paste_fps)
        self.wid.btnPasteDuration.clicked.connect(self.paste_duration)

    def parse_clip_xml(self) -> Tuple[Decimal, int]:
        root = minidom.parseString(clipboard.paste()).documentElement
        fps = Decimal(root.attributes['fps'].value)
        total_frames = int(root.attributes['duration'].value)

        return fps, total_frames

    def on_paste_error(self, field_name, e):
        assert e, False
        template = 'Error parsing clip data for \'{0}\'.  Message:\n{1}'

        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle('Inference Failed')
        msgbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msgbox.setText(template.format(field_name, e))
        msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgbox.exec()

        print('error parsing clip:\n' + str(e))


    def on_paste(self, field_name):
        try:
            fps, total_frames = self.parse_clip_xml()
        except ExpatError as e:
            self.on_paste_error(field_name, e)

            return None, None

        return fps, total_frames

    def paste_duration(self):
        fps, total_frames = self.on_paste('duration')
        # for `SS.FF` notation
        # minor_frames = total_frames % fps
        # full_seconds = (total_frames - minor_frames) / fps
        # duration = full_seconds * fps + minor_frames

        if fps is not None and total_frames is not None:
            duration = total_frames / fps

            self.wid.numDuration.setValue(duration)

    def paste_fps(self):
        fps, _ = self.on_paste('FPS')

        if fps is not None:
            self.wid.numFps.setValue(int(fps))


class RectWidget:
    def __init__(self, wid):
        self.wid = wid
        uic.loadUi("ui/rect.ui", self.wid)
        self.wid.show()

    def get_data(self):
        return {
            "x": self.wid.numPosX.value(),
            "y": self.wid.numPosY.value(),
            "width": self.wid.numSizeX.value(),
            "height": self.wid.numSizeY.value(),
            "opacity": self.wid.numOpacity.value() / 100,
        }

    def set_data(self, position, size, opacity):
        self.wid.numPosX.setValue(position['x'])
        self.wid.numPosY.setValue(position['y'])
        self.wid.numSizeX.setValue(size['x'])
        self.wid.numSizeY.setValue(size['y'])
        self.wid.numOpacity.setValue(opacity)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/window.ui', self)
        self.show()
        for i in ease_options:
            self.cbEaseType.addItem(i["name"])
        self.btnGenerate.clicked.connect(self.on_generate_click)
        self.btnPasteStart.clicked.connect(self.on_paste_start)
        self.btnPasteEnd.clicked.connect(self.on_paste_end)
        self.startrect = self.load_rect(self.widStartRect)
        self.endrect = self.load_rect(self.widEndRect)
        self.create_easepreview()
        self.cbEaseType.currentIndexChanged.connect(self.create_easepreview)

        self.clip = self.load_clip(self.widClip)

    def load_clip(self, wid):
        cw = ClipWidget(wid)

        return cw

    def load_rect(self, wid):
        rw = RectWidget(wid)

        return rw

    def create_easepreview(self):
        easefunc = ease_options[self.cbEaseType.currentIndex()]["func"]

        plt = self.palette()

        scale = 4
        img = Image.new(
            "RGB", (170 * scale, 130 * scale), plt.window().color().getRgb()
        )
        imgdraw = ImageDraw.ImageDraw(img)
        lastpixel = (0, img.height - 1)
        for i in range(img.width):
            try:
                val = easefunc(i / img.width)
                xy = (i, int((1 - val) * (img.height - 1)))
                imgdraw.line(
                    lastpixel + xy,
                    plt.windowText().color().getRgb(),
                    3 * scale,
                )
                lastpixel = xy
            except Exception:
                pass
        img = img.resize(
            (img.width // scale, img.height // scale), resample=Image.ANTIALIAS
        )
        img.save("preview.png")
        """img = img.convert("RGB")
        data = img.tobytes("raw","RGB")
        qim = QtGui.QImage(data, img.width,img.height, QtGui.QImage.Format_RGB888)"""
        pix = QtGui.QPixmap("preview.png")
        self.imgEasePreview.setPixmap(pix)

    def parse_keyframe(self, json_str):
        keyframe = json.loads(clipboard.paste())
        SIZE_OFFSET=2
        position = {}
        size = {}

        for item in keyframe:
            if item.get('DisplayName', '') != 'Rectangle':
                continue

            try:
                fields = re.split(r'[\s=]', item['value'])[1:]
                for axis, idx in {'x': 0, 'y': 1}.items():
                    position[axis] = int(fields[idx])
                    size[axis] = int(fields[idx + SIZE_OFFSET])

                opacity = Decimal(fields[4])

                return position, size, opacity

            except (IndexError, DecimalInvalidOperation):
                break

        raise SyntaxError('Invalid rectangle data in clipboard')

    def on_paste_point_error(self, point, e):
        assert e, False
        template = 'Error parsing clip data for \'{0}\'.  Message:\n{1}'

        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle('Inference Failed')
        msgbox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msgbox.setText(template.format(point, e))
        msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgbox.exec()

        print('error parsing clip:\n' + str(e))

    def on_paste_point(self, point, widget):
        try:
            position, size, opacity = self.parse_keyframe(clipboard.paste())
        except (json.JSONDecodeError, SyntaxError) as e:
            self.on_paste_point_error(point, e)

            return

        widget.set_data(position, size, int(opacity * 100))


    def on_paste_start(self):
        self.on_paste_point('start', self.startrect)

    def on_paste_end(self):
        self.on_paste_point('end', self.endrect)


    def on_generate_click(self):
        easetype = ease_options[self.cbEaseType.currentIndex()]

        tocopy = json.dumps(
            generate_json(
                easetype,
                self.clip.wid.numDuration.value(),
                {
                    "start": self.startrect.get_data(),
                    "end": self.endrect.get_data(),
                },
                self.clip.wid.numFps.value(),
            )
        )
        clipboard.copy(tocopy)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
