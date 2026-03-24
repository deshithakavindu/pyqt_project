# from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton,QLabel
# import sys
# from PyQt5.QtGui import QIcon,QFont,QPixmap
# from PyQt5.QtCore import Qt #  Qt for aligment


# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle(" App")
#         self.setWindowIcon(QIcon("download.jpeg"))
#         self.setGeometry(700, 300, 500, 500)


#         self.label = QLabel(self)
#         pixmap = QPixmap("about_the_eif.jpg")
#         self.label.setPixmap(pixmap)
#         self.label.setScaledContents(True)
#         self.label.setGeometry(0, 0, self.width(), self.height())
#         self.label.lower()





#     def resizeEvent(self, event):
#         self.label.setGeometry(0, 0, self.width(), self.height())

#         # label = QLabel("hiii",self)
#         # label.setFont(QFont("Arial",30))
#         # label.setGeometry(0,0,500,100)
#         # label.setStyleSheet("color: blue;"
#         #                     "background-color:green;"
#         #                     "font-weight:bold;"
#         #                     "font-style:italic;"
#         #                     "text-decoration:underline;")
    
        
#         # label.setAlignment(Qt.AlignCenter)
#         # Button
#         self.button = QPushButton("Click Me", self)
#         self.button.move(150, 120)

#         # Connect event
#         self.button.clicked.connect(self.on_click)

#     def on_click(self):
#         print("Button clicked 🚀")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)

#     window = MainWindow()
#     window.show()

#     sys.exit(app.exec_())



"""
╔══════════════════════════════════════════════╗
║   NOVA TERMINAL  v4  —  PyQt5 Command Suite  ║
║   Install:  pip install PyQt5 requests psutil║
║   (psutil optional — works without it too)   ║
╚══════════════════════════════════════════════╝
"""

import os
import sys, json, math, random, socket, platform
import datetime, urllib.request, urllib.parse
from dotenv import load_dotenv

# ── Optional: requests (fallback to urllib) ──
try:
    import requests as _req
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ── Optional: psutil ──
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *

# ═══════════════════════════════════════════════════════
#  COLOUR PALETTE  —  Deep Ocean / Electric Teal
# ═══════════════════════════════════════════════════════
B0  = "#03080f"   # void black-blue
B1  = "#060d18"   # base bg
B2  = "#0b1525"   # card bg
B3  = "#101e33"   # input bg
BB  = "#162640"   # border
BH  = "#1d3352"   # hover border

T0  = "#00e5cc"   # teal primary
T1  = "#00b8a0"   # teal mid
T2  = "#007a6b"   # teal dark
T3  = "#003d35"   # teal deep bg

BLU = "#2080ff"   # electric blue accent
BLU2= "#60a8ff"   # light blue
PUR = "#8060ff"   # purple accent
RED = "#ff3848"   # alert
GRN = "#30e060"   # success
YEL = "#ffc040"   # warning/yellow

FG  = "#c0d8f0"   # primary text
FG2 = "#4a6880"   # muted
FG3 = "#243040"   # very muted
load_dotenv()

# ── Free APIs (zero extra packages needed) ──
API_WEATHER = os.getenv("API_WEATHER_URL")
API_IP         = os.getenv("API_IP_lookup")
API_JOKE       = os.getenv("API_JOKE_key")
API_QUOTE      = os.getenv("API_QUOTE_key")
API_DICTIONARY = os.getenv("API_DICTIONARY_key")
API_NUMBERS    = os.getenv("API_NUMBERS_KEY")
API_COUNTRY    = os.getenv("API_COUNTRY_KEY")
API_CAT_FACT   = os.getenv("API_CAT_FACT_KEY")
API_BORED      = os.getenv("API_BORED_KEY")


# ═══════════════════════════════════════════════════════
#  Network helper — uses requests if available, else urllib
# ═══════════════════════════════════════════════════════
def fetch(url: str, timeout: int = 8):
    headers = {"User-Agent": "NovaTerminal/4.0"}
    try:
        if HAS_REQUESTS:
            r = _req.get(url, timeout=timeout, headers=headers)
            return r.json()
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"_error": str(e)}


class ApiWorker(QThread):
    done = pyqtSignal(object)
    def __init__(self, url):
        super().__init__()
        self.url = url
    def run(self):
        self.done.emit(fetch(self.url))


# ═══════════════════════════════════════════════════════
#  UI PRIMITIVE HELPERS
# ═══════════════════════════════════════════════════════
def make_card(title: str = ""):
    f = QFrame()
    f.setStyleSheet(f"""
        QFrame {{
            background : {B2};
            border     : 1px solid {BB};
            border-radius : 6px;
        }}
    """)
    vl = QVBoxLayout(f)
    vl.setContentsMargins(16, 14, 16, 14)
    vl.setSpacing(10)
    if title:
        row = QHBoxLayout()
        dot = QLabel("▸")
        dot.setStyleSheet(f"color:{T0}; font-size:9pt;")
        t = QLabel(title.upper())
        t.setStyleSheet(
            f"color:{FG2}; font-family:'Consolas'; font-size:8pt; letter-spacing:3px;"
        )
        row.addWidget(dot)
        row.addWidget(t)
        row.addStretch()
        vl.addLayout(row)
        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{BB}; max-height:1px;")
        vl.addWidget(sep)
    return f, vl


def teal_btn(text: str, color: str = T0):
    b = QPushButton(text)
    b.setCursor(Qt.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{
            background    : {color}18;
            color         : {color};
            border        : 1px solid {color}55;
            border-radius : 5px;
            padding       : 6px 18px;
            font-family   : Consolas;
            font-size     : 9pt;
            font-weight   : bold;
            letter-spacing: 1px;
        }}
        QPushButton:hover   {{ background:{color}30; border:1px solid {color}; }}
        QPushButton:pressed {{ background:{color}50; }}
        QPushButton:disabled{{ color:{FG3}; border-color:{BB}; background:transparent; }}
    """)
    return b


def field_input(placeholder: str = "", fixed_w: int = 0):
    e = QLineEdit()
    e.setPlaceholderText(placeholder)
    if fixed_w:
        e.setFixedWidth(fixed_w)
    e.setStyleSheet(f"""
        QLineEdit {{
            background    : {B3};
            color         : {FG};
            border        : 1px solid {BB};
            border-radius : 5px;
            padding       : 6px 10px;
            font-family   : Consolas;
            font-size      : 9pt;
        }}
        QLineEdit:focus {{ border:1px solid {T0}; }}
        QLineEdit::placeholder {{ color:{FG3}; }}
    """)
    return e


def styled_combo(items):
    c = QComboBox()
    c.addItems(items)
    c.setStyleSheet(f"""
        QComboBox {{
            background:{B3}; color:{FG}; border:1px solid {BB};
            border-radius:5px; padding:5px 10px;
            font-family:Consolas; font-size:9pt;
        }}
        QComboBox:hover  {{ border:1px solid {T1}; }}
        QComboBox::drop-down {{ border:none; width:20px; }}
        QComboBox QAbstractItemView {{
            background:{B2}; color:{FG}; border:1px solid {BB};
            font-family:Consolas; selection-background-color:{T2};
        }}
    """)
    return c


def mono_display():
    t = QTextEdit()
    t.setReadOnly(True)
    t.setStyleSheet(f"""
        QTextEdit {{
            background:{B1}; color:{FG}; border:1px solid {BB};
            border-radius:5px; font-family:Consolas;
            font-size:9pt; padding:10px;
        }}
    """)
    return t


# ═══════════════════════════════════════════════════════
#  CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════

class RingGauge(QWidget):
    """Smooth animated arc gauge."""
    def __init__(self, label: str, color: str = T0):
        super().__init__()
        self.setFixedSize(118, 118)
        self._target  = 0.0
        self._current = 0.0
        self._label   = label
        self._color   = color
        t = QTimer(self); t.timeout.connect(self._step); t.start(16)

    def set_value(self, v: float):
        self._target = max(0.0, min(100.0, v))

    def _step(self):
        self._current += (self._target - self._current) * 0.10
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy, r, t = w // 2, h // 2, 44, 9

        # Track
        p.setPen(QPen(QColor(BB), t, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(cx-r, cy-r, r*2, r*2, 225*16, -270*16)

        # Arc
        span = int(self._current / 100 * 270 * 16)
        grad = QConicalGradient(cx, cy, 225)
        grad.setColorAt(0.0, QColor(self._color).darker(140))
        grad.setColorAt(1.0, QColor(self._color))
        p.setPen(QPen(QBrush(grad), t, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(cx-r, cy-r, r*2, r*2, 225*16, -span)

        # Tip glow
        if span > 0:
            a   = math.radians(225 - self._current / 100 * 270)
            tx  = cx + r * math.cos(a)
            ty  = cy - r * math.sin(a)
            gc  = QColor(self._color); gc.setAlpha(140)
            p.setBrush(gc); p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(tx, ty), 5, 5)

        # Value
        p.setPen(QColor(self._color))
        p.setFont(QFont("Consolas", 16, QFont.Bold))
        p.drawText(QRect(0, cy-14, w, 22), Qt.AlignCenter, f"{int(self._current)}")
        p.setPen(QColor(FG2))
        p.setFont(QFont("Consolas", 7))
        p.drawText(QRect(0, cy+10, w, 14), Qt.AlignCenter, self._label)
        p.end()


class SparkLine(QWidget):
    """60-sample history sparkline."""
    def __init__(self, color: str = T0, label: str = ""):
        super().__init__()
        self.setFixedHeight(54)
        self._data  = [0.0] * 60
        self._color = QColor(color)
        self._label = label

    def push(self, v: float):
        self._data.append(max(0.0, min(100.0, v)))
        if len(self._data) > 60:
            self._data.pop(0)
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h, pad = self.width(), self.height(), 2
        n = len(self._data)
        if n < 2:
            p.end(); return

        pts = [
            QPointF(pad + i * (w - pad*2) / (n-1),
                    h - pad - (h - pad*2) * v / 100)
            for i, v in enumerate(self._data)
        ]

        # Fill
        path = QPainterPath()
        path.moveTo(pts[0])
        for pt in pts[1:]: path.lineTo(pt)
        path.lineTo(pts[-1].x(), h - pad)
        path.lineTo(pts[0].x(),  h - pad)
        path.closeSubpath()
        g = QLinearGradient(0, 0, 0, h)
        c1 = QColor(self._color); c1.setAlpha(55)
        c2 = QColor(self._color); c2.setAlpha(4)
        g.setColorAt(0, c1); g.setColorAt(1, c2)
        p.fillPath(path, g)

        # Line
        p.setPen(QPen(self._color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        path2 = QPainterPath()
        path2.moveTo(pts[0])
        for pt in pts[1:]: path2.lineTo(pt)
        p.drawPath(path2)

        # Labels
        p.setPen(QColor(self._color))
        p.setFont(QFont("Consolas", 10, QFont.Bold))
        p.drawText(QRect(w - 62, 2, 58, 20), Qt.AlignRight | Qt.AlignVCenter,
                   f"{self._data[-1]:.0f}%")
        p.setPen(QColor(FG3))
        p.setFont(QFont("Consolas", 7))
        p.drawText(4, h - 3, self._label)
        p.end()


class ScrollingTicker(QLabel):
    """Horizontally scrolling text ticker."""
    def __init__(self):
        super().__init__()
        self.setFixedHeight(26)
        self.setStyleSheet(f"background:{B0}; border-top:1px solid {BB};")
        self._text   = "  NOVA TERMINAL  ·  READY  "
        self._offset = 0
        t = QTimer(self); t.timeout.connect(self._scroll); t.start(30)

    def set_text(self, txt: str):
        self._text   = f"  {txt}  "
        self._offset = 0

    def _scroll(self):
        fm = self.fontMetrics()
        tw = fm.horizontalAdvance(self._text)
        self._offset = (self._offset + 1) % max(tw, 1)
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(B0))
        p.setPen(QColor(T2))
        p.setFont(QFont("Consolas", 8))
        fm    = p.fontMetrics()
        tw    = fm.horizontalAdvance(self._text)
        x     = -self._offset
        while x < self.width():
            p.drawText(x, 17, self._text)
            x += tw
        p.end()


# ═══════════════════════════════════════════════════════
#  TAB: DASHBOARD
# ═══════════════════════════════════════════════════════
class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(14)

        # ── Hero banner ──────────────────────────────
        banner = QFrame()
        banner.setFixedHeight(90)
        banner.setStyleSheet(
            f"background:{B2}; border:1px solid {BB}; border-radius:6px;"
            f"border-left:4px solid {T0};"
        )
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(22, 10, 22, 10)

        lv = QVBoxLayout()
        name = QLabel("NOVA TERMINAL")
        name.setFont(QFont("Consolas", 22, QFont.Bold))
        name.setStyleSheet(f"color:{T0}; letter-spacing:5px;")
        sub  = QLabel("COMMAND SUITE  ·  WEATHER  ·  TOOLS  ·  WORLD CLOCK  ·  AI CHAT")
        sub.setStyleSheet(f"color:{FG2}; font-family:Consolas; font-size:8pt; letter-spacing:2px;")
        lv.addWidget(name); lv.addWidget(sub)
        bl.addLayout(lv); bl.addStretch()

        rv = QVBoxLayout(); rv.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.hero_time = QLabel()
        self.hero_time.setFont(QFont("Consolas", 18, QFont.Bold))
        self.hero_time.setStyleSheet(f"color:{BLU2};")
        self.hero_date = QLabel()
        self.hero_date.setStyleSheet(f"color:{FG2}; font-family:Consolas; font-size:9pt;")
        rv.addWidget(self.hero_time); rv.addWidget(self.hero_date)
        bl.addLayout(rv)
        root.addWidget(banner)

        # ── Gauges + sparks ──────────────────────────
        gc, gl = make_card("LIVE SYSTEM METRICS")
        grow = QHBoxLayout(); grow.setSpacing(18)
        self.cpu_g  = RingGauge("CPU",  T0)
        self.ram_g  = RingGauge("RAM",  BLU)
        self.disk_g = RingGauge("DISK", PUR)
        for g in [self.cpu_g, self.ram_g, self.disk_g]:
            grow.addWidget(g, alignment=Qt.AlignCenter)

        sv = QVBoxLayout(); sv.setSpacing(6)
        self.cpu_spark  = SparkLine(T0,  "CPU HISTORY  60s")
        self.ram_spark  = SparkLine(BLU, "RAM HISTORY  60s")
        sv.addWidget(self.cpu_spark); sv.addWidget(self.ram_spark)
        grow.addLayout(sv); grow.addStretch()
        gl.addLayout(grow)
        root.addWidget(gc)

        # ── Two info columns ─────────────────────────
        cols = QHBoxLayout(); cols.setSpacing(14)

        # System info
        si, sil = make_card("SYSTEM INFO")
        for k, v in [
            ("OS",       f"{platform.system()} {platform.release()}"),
            ("MACHINE",  platform.machine()),
            ("HOSTNAME", socket.gethostname()),
            ("PYTHON",   platform.python_version()),
            ("ARCH",     platform.architecture()[0]),
            ("PSUTIL",   "installed ✓" if HAS_PSUTIL else "not found — pip install psutil"),
        ]:
            row = QHBoxLayout()
            kl = QLabel(k); kl.setFixedWidth(76)
            kl.setStyleSheet(f"color:{FG2}; font-family:Consolas; font-size:8pt;")
            vl = QLabel(v)
            vl.setStyleSheet(f"color:{FG}; font-family:Consolas; font-size:8pt;")
            row.addWidget(kl); row.addWidget(vl); row.addStretch()
            sil.addLayout(row)
        sil.addStretch()
        cols.addWidget(si)

        # Activity log
        lc, ll = make_card("ACTIVITY LOG")
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet(
            f"QTextEdit {{ background:{B1}; color:{GRN}; border:none;"
            f"font-family:Consolas; font-size:8pt; }}"
        )
        ll.addWidget(self.log_view)
        cols.addWidget(lc)
        root.addLayout(cols)

        # Timer
        t = QTimer(self); t.timeout.connect(self._tick); t.start(1000)
        self._tick()
        self.log("NOVA TERMINAL v4 READY")
        self.log(f"HOST: {socket.gethostname()}")

    def _tick(self):
        now = datetime.datetime.now()
        self.hero_time.setText(now.strftime("%H:%M:%S"))
        self.hero_date.setText(now.strftime("%A  %d %B %Y"))
        if HAS_PSUTIL:
            cpu  = psutil.cpu_percent()
            ram  = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
        else:
            cpu = ram = disk = 0.0
        self.cpu_g.set_value(cpu);  self.cpu_spark.push(cpu)
        self.ram_g.set_value(ram);  self.ram_spark.push(ram)
        self.disk_g.set_value(disk)

    def log(self, msg: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_view.append(f"[{ts}]  {msg}")
        self.log_view.verticalScrollBar().setValue(
            self.log_view.verticalScrollBar().maximum()
        )


# ═══════════════════════════════════════════════════════
#  TAB: WEATHER
# ═══════════════════════════════════════════════════════
class WeatherTab(QWidget):
    def __init__(self, log):
        super().__init__()
        self._log = log
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(14)

        # Search
        sc, sl = make_card("CITY LOOKUP")
        row = QHBoxLayout()
        self.city_in = field_input("Enter city name…  e.g. Tokyo, London, Colombo")
        self.city_in.returnPressed.connect(self._fetch)
        btn = teal_btn("▸  FETCH WEATHER")
        btn.clicked.connect(self._fetch)
        row.addWidget(self.city_in); row.addWidget(btn)
        sl.addLayout(row)
        root.addWidget(sc)

        # Current
        cc, cl = make_card("CURRENT CONDITIONS")
        top = QHBoxLayout(); top.setSpacing(24)

        tv = QVBoxLayout(); tv.setSpacing(2)
        self.temp_lbl = QLabel("—°C")
        self.temp_lbl.setFont(QFont("Consolas", 52, QFont.Bold))
        self.temp_lbl.setStyleSheet(f"color:{T0};")
        self.desc_lbl = QLabel("—")
        self.desc_lbl.setStyleSheet(f"color:{FG}; font-family:Consolas; font-size:13pt;")
        self.loc_lbl  = QLabel("—")
        self.loc_lbl.setStyleSheet(f"color:{FG2}; font-family:Consolas; font-size:9pt; letter-spacing:2px;")
        tv.addWidget(self.temp_lbl); tv.addWidget(self.desc_lbl); tv.addWidget(self.loc_lbl)
        top.addLayout(tv)

        div = QFrame(); div.setFrameShape(QFrame.VLine)
        div.setStyleSheet(f"background:{BB}; max-width:1px;")
        top.addWidget(div)

        self._det = {}
        dg = QGridLayout(); dg.setSpacing(8)
        for i,(lbl,key) in enumerate([
            ("FEELS LIKE","fl"),("HUMIDITY","hum"),
            ("WIND","wind"),("VISIBILITY","vis"),
            ("CLOUD COVER","cloud"),("HIGH / LOW","hl"),
            ("SUNRISE","rise"),("SUNSET","set"),
        ]):
            kl = QLabel(lbl)
            kl.setStyleSheet(f"color:{FG3}; font-family:Consolas; font-size:7pt; letter-spacing:2px;")
            vl = QLabel("—")
            vl.setStyleSheet(f"color:{FG}; font-family:Consolas; font-size:9pt;")
            dg.addWidget(kl, i//2, (i%2)*2)
            dg.addWidget(vl, i//2, (i%2)*2+1)
            self._det[key] = vl
        top.addLayout(dg)
        cl.addLayout(top)
        root.addWidget(cc)

        # Forecast
        fc, fl = make_card("3-DAY FORECAST")
        self._fc_row = QHBoxLayout(); self._fc_row.setSpacing(12)
        fl.addLayout(self._fc_row)
        root.addWidget(fc)

        self._status = QLabel("")
        self._status.setStyleSheet(f"color:{FG2}; font-family:Consolas; font-size:8pt;")
        root.addWidget(self._status)
        root.addStretch()

    def _fetch(self):
        city = self.city_in.text().strip() or "Colombo"
        self._status.setText(f"Fetching data for {city}…")
        self._w = ApiWorker(API_WEATHER.format(city=urllib.parse.quote(city)))
        self._w.done.connect(self._on_data)
        self._w.start()

    def _on_data(self, data):
        if "_error" in data:
            self._status.setText(f"Error: {data['_error']}"); return
        try:
            cur  = data["current_condition"][0]
            area = data["nearest_area"][0]
            city = area["areaName"][0]["value"]
            country = area["country"][0]["value"]
            tc   = cur["temp_C"]
            desc = cur["weatherDesc"][0]["value"]
            self.temp_lbl.setText(f"{tc}°C")
            self.desc_lbl.setText(desc)
            self.loc_lbl.setText(f"▸  {city}, {country}")

            self._det["fl"].setText(f"{cur['FeelsLikeC']}°C")
            self._det["hum"].setText(f"{cur['humidity']}%")
            self._det["wind"].setText(f"{cur['windspeedKmph']} km/h  {cur.get('winddir16Point','')}")
            self._det["vis"].setText(f"{cur['visibility']} km")
            self._det["cloud"].setText(f"{cur['cloudcover']}%")
            w0   = data["weather"][0]
            astro= w0["astronomy"][0]
            self._det["rise"].setText(astro.get("sunrise","—"))
            self._det["set"].setText(astro.get("sunset","—"))
            self._det["hl"].setText(f"{w0['maxtempC']}° / {w0['mintempC']}°")

            while self._fc_row.count():
                it = self._fc_row.takeAt(0)
                if it.widget(): it.widget().deleteLater()

            emoji_pool = ["☀","⛅","🌤","🌧","⛈","🌨","🌫","🌬"]
            for day in data["weather"][:3]:
                f = QFrame()
                f.setStyleSheet(
                    f"background:{B3}; border:1px solid {BB}; border-radius:6px;"
                    f"border-top:2px solid {T1};"
                )
                vl = QVBoxLayout(f); vl.setContentsMargins(14,10,14,10); vl.setSpacing(4)
                dl = QLabel(day["date"])
                dl.setStyleSheet(f"color:{FG2}; font-family:Consolas; font-size:8pt;")
                ic = QLabel(random.choice(emoji_pool))
                ic.setFont(QFont("Segoe UI Emoji", 20)); ic.setAlignment(Qt.AlignCenter)
                tl = QLabel(f"{day['maxtempC']}° / {day['mintempC']}°")
                tl.setFont(QFont("Consolas", 12, QFont.Bold))
                tl.setStyleSheet(f"color:{T0};")
                dd = QLabel(day["hourly"][4]["weatherDesc"][0]["value"])
                dd.setStyleSheet(f"color:{FG}; font-family:Consolas; font-size:8pt;")
                dd.setWordWrap(True)
                for w in [dl, ic, tl, dd]: vl.addWidget(w)
                self._fc_row.addWidget(f)

            ts = datetime.datetime.now().strftime("%H:%M:%S")
            self._status.setText(f"Updated at {ts}")
            self._log(f"Weather loaded: {city}, {tc}°C")
        except Exception as e:
            self._status.setText(f"Parse error: {e}")


# ═══════════════════════════════════════════════════════
#  TAB: TOOLS  (Dictionary · Country · Converter · Fun · IP)
# ═══════════════════════════════════════════════════════
class ToolsTab(QWidget):
    def __init__(self, log):
        super().__init__()
        self._log = log
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(0)

        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane   {{ border:1px solid {BB}; background:{B1}; border-radius:6px; }}
            QTabBar::tab       {{
                background:{B1}; color:{FG2};
                padding:8px 20px; border:none;
                font-family:Consolas; font-size:8pt; letter-spacing:1px;
                border-bottom:2px solid transparent;
            }}
            QTabBar::tab:selected  {{ background:{B2}; color:{T0}; border-bottom:2px solid {T0}; }}
            QTabBar::tab:hover     {{ background:{B3}; color:{FG}; }}
        """)
        tabs.addTab(self._dict_tab(),      "DICTIONARY")
        tabs.addTab(self._country_tab(),   "COUNTRY INFO")
        tabs.addTab(self._converter_tab(), "CONVERTER")
        tabs.addTab(self._fun_tab(),       "FUN APIS")
        tabs.addTab(self._ip_tab(),        "IP LOOKUP")
        root.addWidget(tabs)

    # ── Dictionary ──────────────────────────────────
    def _dict_tab(self):
        w = QWidget(); l = QVBoxLayout(w)
        l.setContentsMargins(18,18,18,18); l.setSpacing(12)
        row = QHBoxLayout()
        self.dict_in = field_input("Enter a word…")
        self.dict_in.returnPressed.connect(self._lookup)
        btn = teal_btn("▸  DEFINE")
        btn.clicked.connect(self._lookup)
        row.addWidget(self.dict_in); row.addWidget(btn); row.addStretch()
        l.addLayout(row)
        self.dict_out = mono_display()
        l.addWidget(self.dict_out)
        return w

    def _lookup(self):
        word = self.dict_in.text().strip()
        if not word: return
        self.dict_out.setPlainText( f'Looking up "{word}"…')
        url = API_DICTIONARY.format(word=urllib.parse.quote(word))
        self._dw = ApiWorker(url)
        self._dw.done.connect(self._on_dict)
        self._dw.start()

    def _on_dict(self, data):
        if isinstance(data, dict) and "_error" in data:
            self.dict_out.setPlainText(f"Error: {data['_error']}"); return
        try:
            entry = data[0]
            word  = entry["word"]
            phon  = entry.get("phonetic","")
            lines = [f"{'─'*44}", f"  {word.upper()}  {phon}", f"{'─'*44}", ""]
            for m in entry.get("meanings",[])[:3]:
                pos = m["partOfSpeech"].upper()
                lines.append(f"  [{pos}]")
                for d in m.get("definitions",[])[:2]:
                    lines.append(f"    •  {d['definition']}")
                    if d.get("example"):
                        lines.append(f'       "{d["example"]}"')
                lines.append("")
            self.dict_out.setPlainText("\n".join(lines))
            self._log(f"Defined: {word}")
        except Exception as e:
            self.dict_out.setPlainText(f"Parse error: {e}")

    # ── Country Info ────────────────────────────────
    def _country_tab(self):
        w = QWidget(); l = QVBoxLayout(w)
        l.setContentsMargins(18,18,18,18); l.setSpacing(12)
        row = QHBoxLayout()
        self.country_in = field_input("Country name…  e.g. Japan, Brazil, France")
        self.country_in.returnPressed.connect(self._country_lookup)
        btn = teal_btn("▸  LOOKUP", BLU)
        btn.clicked.connect(self._country_lookup)
        row.addWidget(self.country_in); row.addWidget(btn); row.addStretch()
        l.addLayout(row)
        self.country_out = mono_display()
        self.country_out.setPlainText("Enter a country name above and press LOOKUP.")
        l.addWidget(self.country_out)
        return w

    def _country_lookup(self):
        name = self.country_in.text().strip()
        if not name: return
        self.country_out.setPlainText(f'Fetching data for "{name}"…')
        url = API_COUNTRY.format(name=urllib.parse.quote(name))
        self._cw = ApiWorker(url)
        self._cw.done.connect(self._on_country)
        self._cw.start()

    def _on_country(self, data):
        if isinstance(data, dict) and "_error" in data:
            self.country_out.setPlainText(f"Error: {data['_error']}"); return
        try:
            c = data[0]
            name    = c["name"]["common"]
            official= c["name"]["official"]
            cap     = ", ".join(c.get("capital", ["—"]))
            region  = c.get("region","—")
            sub     = c.get("subregion","—")
            pop     = f"{c.get('population',0):,}"
            area    = f"{c.get('area',0):,.0f} km²"
            tld     = ", ".join(c.get("tld", ["—"]))
            langs   = ", ".join(c.get("languages",{}).values())
            currencies = ", ".join(
                f"{v.get('name',k)} ({v.get('symbol','')})"
                for k,v in c.get("currencies",{}).items()
            )
            borders = ", ".join(c.get("borders",[]) or ["None"])
            driveon = c.get("car",{}).get("side","—")
            timezones = ", ".join(c.get("timezones",[])[:4])
            calling = ", ".join(
                f"+{x}" for x in c.get("idd",{}).get("suffixes",
                [c.get("idd",{}).get("root","—").replace("+","")])[:3]
            )
            un      = "Yes" if c.get("unMember") else "No"

            lines = [
                f"{'─'*50}",
                f"  {name.upper()}",
                f"  {official}",
                f"{'─'*50}",
                f"  CAPITAL       :  {cap}",
                f"  REGION        :  {region}  /  {sub}",
                f"  POPULATION    :  {pop}",
                f"  AREA          :  {area}",
                f"  LANGUAGES     :  {langs}",
                f"  CURRENCIES    :  {currencies}",
                f"  TOP-LEVEL DOM :  {tld}",
                f"  CALLING CODE  :  {calling}",
                f"  BORDERS       :  {borders}",
                f"  DRIVES ON     :  {driveon}",
                f"  TIMEZONES     :  {timezones}",
                f"  UN MEMBER     :  {un}",
                f"{'─'*50}",
            ]
            self.country_out.setPlainText("\n".join(lines))
            self._log(f"Country: {name}")
        except Exception as e:
            self.country_out.setPlainText(f"Parse error: {e}\n\nRaw:\n{json.dumps(data,indent=2)[:600]}")

    # ── Converter ───────────────────────────────────
    _UNITS = {
        "LENGTH":      ["m","km","cm","mm","inch","foot","yard","mile","nautical mile"],
        "WEIGHT":      ["kg","g","mg","lb","oz","tonne","stone"],
        "TEMPERATURE": ["Celsius","Fahrenheit","Kelvin"],
        "SPEED":       ["m/s","km/h","mph","knot","ft/s"],
        "AREA":        ["m²","km²","cm²","mm²","acre","hectare","ft²","inch²"],
        "DATA":        ["bit","byte","KB","MB","GB","TB","PB"],
        "TIME":        ["second","minute","hour","day","week","month","year"],
    }

    def _converter_tab(self):
        w = QWidget(); l = QVBoxLayout(w)
        l.setContentsMargins(18,18,18,18); l.setSpacing(14)

        self.conv_cat = styled_combo(list(self._UNITS.keys()))
        self.conv_cat.currentIndexChanged.connect(self._refresh_units)
        l.addWidget(self.conv_cat)

        row = QHBoxLayout(); row.setSpacing(10)
        self.conv_val  = field_input("Value…", 130)
        self.conv_from = styled_combo([])
        arr = QLabel("▸"); arr.setStyleSheet(f"color:{T0}; font-size:14pt; font-weight:bold;")
        self.conv_to   = styled_combo([])
        go = teal_btn("CONVERT")
        go.clicked.connect(self._convert)
        for widget in [self.conv_val, self.conv_from, arr, self.conv_to, go]:
            row.addWidget(widget)
        row.addStretch()
        l.addLayout(row)

        self.conv_result = QLabel("—")
        self.conv_result.setFont(QFont("Consolas", 20, QFont.Bold))
        self.conv_result.setStyleSheet(
            f"color:{T0}; padding:14px 18px; background:{B2};"
            f"border:1px solid {BB}; border-left:4px solid {T0}; border-radius:5px;"
        )
        l.addWidget(self.conv_result)
        l.addStretch()
        self._refresh_units()
        return w

    def _refresh_units(self):
        units = self._UNITS.get(self.conv_cat.currentText(), [])
        self.conv_from.clear(); self.conv_to.clear()
        self.conv_from.addItems(units); self.conv_to.addItems(units)
        if len(units) > 1: self.conv_to.setCurrentIndex(1)

    def _convert(self):
        try: v = float(self.conv_val.text())
        except: self.conv_result.setText("Invalid input"); return
        fr, to = self.conv_from.currentText(), self.conv_to.currentText()
        result = self._calc(v, fr, to)
        self.conv_result.setText(f"{v} {fr}  =  {result:.10g} {to}")
        self._log(f"Convert: {v} {fr} → {result:.6g} {to}")

    _SI = {
        "m":1,"km":1e3,"cm":1e-2,"mm":1e-3,"inch":0.0254,"foot":0.3048,
        "yard":0.9144,"mile":1609.344,"nautical mile":1852,
        "kg":1,"g":1e-3,"mg":1e-6,"lb":0.453592,"oz":0.028349,"tonne":1e3,"stone":6.35029,
        "m/s":1,"km/h":0.277778,"mph":0.44704,"knot":0.514444,"ft/s":0.3048,
        "m²":1,"km²":1e6,"cm²":1e-4,"mm²":1e-6,"acre":4046.86,"hectare":1e4,"ft²":0.0929,"inch²":6.452e-4,
        "bit":1,"byte":8,"KB":8192,"MB":8388608,"GB":8589934592,"TB":8589934592000,"PB":8589934592000000,
        "second":1,"minute":60,"hour":3600,"day":86400,"week":604800,"month":2629800,"year":31557600,
    }

    def _calc(self, v, fr, to):
        if fr == to: return v
        if fr in ("Celsius","Fahrenheit","Kelvin"):
            k = (v+273.15 if fr=="Celsius" else
                 (v+459.67)*5/9 if fr=="Fahrenheit" else v)
            return (k-273.15 if to=="Celsius" else k*9/5-459.67 if to=="Fahrenheit" else k)
        return v * self._SI.get(fr,1) / self._SI.get(to,1)

    # ── Fun APIs ────────────────────────────────────
    def _fun_tab(self):
        w = QWidget(); l = QVBoxLayout(w)
        l.setContentsMargins(18,18,18,18); l.setSpacing(14)

        jc, jl = make_card("RANDOM JOKE")
        self.joke_lbl = QLabel("Press the button for a joke…")
        self.joke_lbl.setWordWrap(True)
        self.joke_lbl.setFont(QFont("Consolas", 10))
        self.joke_lbl.setStyleSheet(f"color:{FG}; min-height:55px; padding:4px;")
        jbtn = teal_btn("▸  GET JOKE")
        jbtn.clicked.connect(self._joke)
        jl.addWidget(self.joke_lbl); jl.addWidget(jbtn)
        l.addWidget(jc)

        qc, ql = make_card("INSPIRATIONAL QUOTE")
        self.quote_lbl = QLabel("Press the button for a quote…")
        self.quote_lbl.setWordWrap(True)
        self.quote_lbl.setFont(QFont("Consolas", 10))
        self.quote_lbl.setStyleSheet(f"color:{FG}; min-height:55px; font-style:italic;")
        qbtn = teal_btn("▸  GET QUOTE", YEL)
        qbtn.clicked.connect(self._quote)
        ql.addWidget(self.quote_lbl); ql.addWidget(qbtn)
        l.addWidget(qc)

        nc, nl = make_card("NUMBER TRIVIA")
        nrow = QHBoxLayout()
        self.num_in  = field_input("Enter a number…", 160)
        nbtn = teal_btn("▸  TRIVIA", PUR)
        nbtn.clicked.connect(self._trivia)
        self.num_lbl = QLabel("—")
        self.num_lbl.setWordWrap(True)
        self.num_lbl.setStyleSheet(f"color:{FG}; font-family:Consolas; font-size:9pt;")
        nrow.addWidget(self.num_in); nrow.addWidget(nbtn); nrow.addStretch()
        nl.addLayout(nrow); nl.addWidget(self.num_lbl)
        l.addWidget(nc)
        l.addStretch()
        return w

    def _joke(self):
        self.joke_lbl.setText("Fetching…")
        self._jw = ApiWorker(API_JOKE)
        self._jw.done.connect(lambda d: self.joke_lbl.setText(
            f"Q:  {d.get('setup','?')}\n\nA:  {d.get('punchline','?')}"
            if "_error" not in d else f"Error: {d['_error']}"
        ))
        self._jw.start()

    def _quote(self):
        self.quote_lbl.setText("Fetching…")
        self._qw = ApiWorker(API_QUOTE)
        self._qw.done.connect(lambda d: self.quote_lbl.setText(
            f'"{d.get("content","—")}"\n\n— {d.get("author","—")}'
            if "_error" not in d else f"Error: {d['_error']}"
        ))
        self._qw.start()

    def _trivia(self):
        n = self.num_in.text().strip() or str(random.randint(1, 9999))
        self.num_lbl.setText("Fetching…")
        self._nw = ApiWorker(API_NUMBERS.format(n=n))
        self._nw.done.connect(lambda d: self.num_lbl.setText(
            str(d) if isinstance(d, str) else d.get("text", str(d))
        ))
        self._nw.start()

    # ── IP Lookup ───────────────────────────────────
    def _ip_tab(self):
        w = QWidget(); l = QVBoxLayout(w)
        l.setContentsMargins(18,18,18,18); l.setSpacing(12)
        btn = teal_btn("▸  FETCH MY IP DETAILS", BLU2)
        btn.clicked.connect(self._ip)
        l.addWidget(btn)
        self.ip_out = mono_display()
        self.ip_out.setPlainText("Press the button to look up your public IP information.")
        l.addWidget(self.ip_out)
        return w

    def _ip(self):
        self.ip_out.setPlainText("Fetching…")
        self._ipw = ApiWorker(API_IP)
        self._ipw.done.connect(self._on_ip)
        self._ipw.start()

    def _on_ip(self, d):
        if "_error" in d:
            self.ip_out.setPlainText(f"Error: {d['_error']}"); return
        lines = [
            f"{'─'*44}",
            f"  IP ADDRESS  :  {d.get('ip','—')}",
            f"  CITY        :  {d.get('city','—')}",
            f"  REGION      :  {d.get('region','—')}",
            f"  COUNTRY     :  {d.get('country_name','—')}  ({d.get('country_code','—')})",
            f"  ISP / ORG   :  {d.get('org','—')}",
            f"  TIMEZONE    :  {d.get('timezone','—')}",
            f"  LATITUDE    :  {d.get('latitude','—')}",
            f"  LONGITUDE   :  {d.get('longitude','—')}",
            f"  POSTAL      :  {d.get('postal','—')}",
            f"{'─'*44}",
        ]
        self.ip_out.setPlainText("\n".join(lines))
        self._log(f"IP lookup: {d.get('ip','—')}")


# ═══════════════════════════════════════════════════════
#  TAB: WORLD CLOCK
# ═══════════════════════════════════════════════════════
class WorldClockTab(QWidget):
    ZONES = [
        ("LONDON",       0),   ("PARIS",        1),   ("CAIRO",        2),
        ("DUBAI",        4),   ("COLOMBO",      5.5), ("DELHI",        5.5),
        ("SINGAPORE",    8),   ("HONG KONG",    8),   ("TOKYO",        9),
        ("SYDNEY",      10),   ("NEW YORK",    -5),   ("CHICAGO",     -6),
        ("DENVER",      -7),   ("LOS ANGELES", -8),   ("SÃO PAULO",   -3),
    ]

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(14)

        hdr = QLabel("▸  WORLD CLOCK  —  15 TIME ZONES  —  LIVE")
        hdr.setStyleSheet(
            f"color:{T0}; font-family:Consolas; font-size:9pt;"
            f"letter-spacing:3px; font-weight:bold;"
        )
        root.addWidget(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border:none; background:{B1}; }}")
        container = QWidget()
        grid = QGridLayout(container); grid.setSpacing(10)

        self._clocks = []
        for i, (name, offset) in enumerate(self.ZONES):
            f = QFrame()
            f.setStyleSheet(
                f"background:{B2}; border:1px solid {BB}; border-radius:6px;"
                f"border-top:2px solid {T2};"
            )
            vl = QVBoxLayout(f); vl.setContentsMargins(14, 10, 14, 10); vl.setSpacing(2)
            nl = QLabel(name)
            nl.setStyleSheet(f"color:{FG2}; font-family:Consolas; font-size:8pt; letter-spacing:2px;")
            tl = QLabel("--:--:--")
            tl.setFont(QFont("Consolas", 18, QFont.Bold))
            tl.setStyleSheet(f"color:{T0};")
            dl = QLabel("")
            dl.setStyleSheet(f"color:{FG3}; font-family:Consolas; font-size:7pt;")
            tzl = QLabel(f"UTC{'+' if offset >= 0 else ''}{offset:g}")
            tzl.setStyleSheet(f"color:{FG3}; font-family:Consolas; font-size:7pt;")
            for lbl in [nl, tl, dl, tzl]: vl.addWidget(lbl)
            grid.addWidget(f, i // 3, i % 3)
            self._clocks.append((tl, dl, offset))

        scroll.setWidget(container)
        root.addWidget(scroll)

        t = QTimer(self); t.timeout.connect(self._tick); t.start(1000)
        self._tick()

    def _tick(self):
        utc = datetime.datetime.utcnow()
        for tl, dl, offset in self._clocks:
            local = utc + datetime.timedelta(hours=offset)
            tl.setText(local.strftime("%H:%M:%S"))
            dl.setText(local.strftime("%a  %d %b %Y"))


# ═══════════════════════════════════════════════════════
#  TAB: AI CHAT
# ═══════════════════════════════════════════════════════
class AiChatTab(QWidget):
    def __init__(self, log):
        super().__init__()
        self._log     = log
        self._history = []
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(12)

        # Header row
        hdr = QHBoxLayout()
        title = QLabel("▸  AI ASSISTANT  ")
        title.setStyleSheet(
            f"color:{T0}; font-family:Consolas; font-size:9pt;"
            f"letter-spacing:3px; font-weight:bold;"
        )
        key_lbl = QLabel("API KEY :")
        key_lbl.setStyleSheet(f"color:{FG2}; font-family:Consolas; font-size:8pt;")
        self.key_in = QLineEdit()
        self.key_in.setEchoMode(QLineEdit.Password)
        self.key_in.setPlaceholderText("sk-ant-…  (Anthropic API key)")
        self.key_in.setFixedWidth(270)
        self.key_in.setStyleSheet(f"""
            QLineEdit {{
                background:{B3}; color:{FG}; border:1px solid {BB};
                border-radius:5px; padding:5px 10px;
                font-family:Consolas; font-size:8pt;
            }}
            QLineEdit:focus {{ border:1px solid {T0}; }}
        """)
        hdr.addWidget(title); hdr.addStretch()
        hdr.addWidget(key_lbl); hdr.addWidget(self.key_in)
        root.addLayout(hdr)

        # Chat area
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet(f"""
            QTextEdit {{
                background:{B1}; color:{FG}; border:1px solid {BB};
                border-radius:6px; font-family:Consolas;
                font-size:9pt; padding:12px;
            }}
        """)
        root.addWidget(self.chat)

        # Input row
        row = QHBoxLayout()
        self.msg_in = QLineEdit()
        self.msg_in.setPlaceholderText("Type a message and press Enter…")
        self.msg_in.returnPressed.connect(self._send)
        self.msg_in.setStyleSheet(f"""
            QLineEdit {{
                background:{B3}; color:{FG}; border:1px solid {BB};
                border-radius:6px; padding:8px 14px;
                font-family:Consolas; font-size:10pt;
            }}
            QLineEdit:focus {{ border:1px solid {T0}; }}
        """)
        send_btn = teal_btn("▸  SEND")
        clr_btn  = teal_btn("CLR", RED)
        clr_btn.setFixedWidth(54)
        clr_btn.clicked.connect(self._clear)
        send_btn.clicked.connect(self._send)
        row.addWidget(self.msg_in); row.addWidget(send_btn); row.addWidget(clr_btn)
        root.addLayout(row)

        self.chat.append(
            f'<span style="color:{FG2}; font-family:Consolas; font-size:9pt;">'
            f'  ▸  NOVA TERMINAL  //  AI MODULE<br>'
            f'  {"─"*46}<br>'
            f'  Paste your Anthropic API key (sk-ant-...) above<br>'
            f'  to enable AI chat with Claude.<br>'
            f'  No key?  Use the Tools tab — all other features<br>'
            f'  are completely free with no sign-up required.<br>'
            f'  {"─"*46}</span>'
        )

    def _send(self):
        msg = self.msg_in.text().strip()
        if not msg: return
        key = self.key_in.text().strip()
        self.chat.append(
            f'<span style="color:{YEL}; font-family:Consolas;">'
            f'  YOU  ▸  {msg}</span>'
        )
        self.msg_in.clear()
        if not key:
            self.chat.append(
                f'<span style="color:{RED}; font-family:Consolas;">'
                f'  ✕  No API key — add your sk-ant-... key above.</span>'
            )
            return
        self.chat.append(
            f'<span style="color:{FG2}; font-family:Consolas;">'
            f'  AI   ▸  thinking…</span>'
        )
        self._history.append({"role": "user", "content": msg})
        self._worker = _ChatWorker(key, list(self._history))
        self._worker.done.connect(self._on_reply)
        self._worker.start()
        self._log(f"AI message sent: {msg[:40]}")

    def _on_reply(self, reply: str):
        cursor = self.chat.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()
        if reply.startswith("ERROR:"):
            self.chat.append(
                f'<span style="color:{RED}; font-family:Consolas;">'
                f'  ✕  {reply}</span>'
            )
        else:
            self.chat.append(
                f'<span style="color:{GRN}; font-family:Consolas;">'
                f'  AI   ▸  {reply}</span>'
            )
            self._history.append({"role": "assistant", "content": reply})
            self._log("AI reply received")
        self.chat.verticalScrollBar().setValue(
            self.chat.verticalScrollBar().maximum()
        )

    def _clear(self):
        self.chat.clear(); self._history.clear()
        self._log("AI chat cleared")


class _ChatWorker(QThread):
    done = pyqtSignal(str)
    def __init__(self, key, history):
        super().__init__()
        self._key     = key
        self._history = history

    def run(self):
        try:
            import json as _j, urllib.request as _r
            payload = _j.dumps({
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 512,
                "messages": self._history,
            }).encode()
            req = _r.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "Content-Type":       "application/json",
                    "x-api-key":          self._key,
                    "anthropic-version":  "2023-06-01",
                },
            )
            with _r.urlopen(req, timeout=20) as resp:
                data = _j.loads(resp.read())
                self.done.emit(data["content"][0]["text"])
        except Exception as e:
            self.done.emit(f"ERROR: {e}")


# ═══════════════════════════════════════════════════════
#  SIDEBAR BUTTON
# ═══════════════════════════════════════════════════════
class NavBtn(QPushButton):
    def __init__(self, icon: str, label: str):
        super().__init__()
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)
        ll = QHBoxLayout(self)
        ll.setContentsMargins(16, 0, 16, 0); ll.setSpacing(12)
        il = QLabel(icon); il.setAttribute(Qt.WA_TransparentForMouseEvents)
        il.setFont(QFont("Segoe UI Emoji", 13))
        tl = QLabel(label); tl.setAttribute(Qt.WA_TransparentForMouseEvents)
        tl.setFont(QFont("Consolas", 8))
        tl.setStyleSheet(f"color:{FG2}; letter-spacing:2px;")
        ll.addWidget(il); ll.addWidget(tl); ll.addStretch()
        self.setStyleSheet(f"""
            QPushButton {{
                background:transparent; border:none;
                border-left:3px solid transparent;
            }}
            QPushButton:hover   {{ background:{B3}; border-left:3px solid {T2}; }}
            QPushButton:checked {{ background:{B2}; border-left:3px solid {T0}; }}
        """)


# ═══════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NOVA TERMINAL  ·  v4")
        self.setGeometry(100, 60, 1220, 800)
        self.setMinimumSize(900, 600)
        self._build()

    def _build(self):
        root = QWidget(); self.setCentralWidget(root)
        ml = QVBoxLayout(root)
        ml.setContentsMargins(0,0,0,0); ml.setSpacing(0)

        # ── Top bar ──────────────────────────────────
        topbar = QFrame(); topbar.setFixedHeight(46)
        topbar.setStyleSheet(f"background:{B0}; border-bottom:1px solid {BB};")
        tbl = QHBoxLayout(topbar); tbl.setContentsMargins(20,0,20,0)

        logo = QLabel("◈  NOVA TERMINAL")
        logo.setFont(QFont("Consolas", 11, QFont.Bold))
        logo.setStyleSheet(f"color:{T0}; letter-spacing:5px;")

        self._tb_stats = QLabel()
        self._tb_stats.setStyleSheet(f"color:{FG2}; font-family:Consolas; font-size:8pt;")
        self._tb_time  = QLabel()
        self._tb_time.setFont(QFont("Consolas", 10))
        self._tb_time.setStyleSheet(f"color:{BLU2};")

        tbl.addWidget(logo); tbl.addStretch()
        tbl.addWidget(self._tb_stats); tbl.addSpacing(20)
        tbl.addWidget(self._tb_time)
        ml.addWidget(topbar)

        # ── Ticker ───────────────────────────────────
        self._ticker = ScrollingTicker()
        ml.addWidget(self._ticker)
        self._ticker.set_text(
            "NOVA TERMINAL  ·  WEATHER API  ·  DICTIONARY API  ·  "
            "COUNTRY INFO API  ·  IP LOOKUP  ·  UNIT CONVERTER  ·  "
            "JOKES  ·  QUOTES  ·  NUMBER TRIVIA  ·  WORLD CLOCK  ·  "
            "AI CHAT (Anthropic key required)  ·  SYSTEM MONITOR"
        )

        # ── Body ─────────────────────────────────────
        body_w = QWidget()
        body   = QHBoxLayout(body_w); body.setContentsMargins(0,0,0,0); body.setSpacing(0)

        # Sidebar
        sidebar = QFrame(); sidebar.setFixedWidth(178)
        sidebar.setStyleSheet(f"background:{B0}; border-right:1px solid {BB};")
        sbl = QVBoxLayout(sidebar); sbl.setContentsMargins(0,20,0,16); sbl.setSpacing(2)

        cat = QLabel("  MODULES")
        cat.setStyleSheet(
            f"color:{FG3}; font-family:Consolas; font-size:7pt;"
            f"letter-spacing:4px; margin-bottom:6px;"
        )
        sbl.addWidget(cat)

        nav_items = [
            ("◈", "DASHBOARD"),
            ("◌", "WEATHER"),
            ("◇", "TOOLS"),
            ("◉", "WORLD CLOCK"),
            ("◎", "AI CHAT"),
        ]
        self._nav_btns = []
        for icon, label in nav_items:
            btn = NavBtn(icon, label)
            btn.clicked.connect(lambda _, b=btn: self._nav(b))
            self._nav_btns.append(btn)
            sbl.addWidget(btn)
        self._nav_btns[0].setChecked(True)
        sbl.addStretch()

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{BB}; max-height:1px; margin:0 8px;")
        sbl.addWidget(sep)

        self._sb_cpu = QLabel("CPU  —%")
        self._sb_ram = QLabel("RAM  —%")
        for lbl in [self._sb_cpu, self._sb_ram]:
            lbl.setStyleSheet(
                f"color:{FG3}; font-family:Consolas; font-size:7pt;"
                f"padding-left:16px; padding-top:3px;"
            )
            sbl.addWidget(lbl)

        ver = QLabel("  v4.0  ·  NOVA SUITE")
        ver.setStyleSheet(f"color:{FG3}; font-family:Consolas; font-size:7pt; margin-top:8px;")
        sbl.addWidget(ver)
        body.addWidget(sidebar)

        # Content stack
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background:{B1};")

        self._dashboard  = DashboardTab()
        self._weather    = WeatherTab(self._dashboard.log)
        self._tools      = ToolsTab(self._dashboard.log)
        self._worldclock = WorldClockTab()
        self._aichat     = AiChatTab(self._dashboard.log)

        for tab in [self._dashboard, self._weather, self._tools,
                    self._worldclock, self._aichat]:
            self._stack.addWidget(tab)

        body.addWidget(self._stack)
        ml.addWidget(body_w)

        # Status bar
        sb = QStatusBar()
        sb.setStyleSheet(
            f"QStatusBar {{ background:{B0}; color:{FG3}; font-family:Consolas;"
            f"font-size:7pt; border-top:1px solid {BB}; letter-spacing:1px; }}"
        )
        self.setStatusBar(sb)
        sb.showMessage(
            "  SYSTEM ONLINE  ·  "
            "FREE APIs: weather · dictionary · country info · ip · jokes · quotes · trivia  ·  "
            "AI chat requires Anthropic API key"
        )

        # Clock / stats timer
        ct = QTimer(self); ct.timeout.connect(self._tick); ct.start(1000)
        self._tick()

    def _nav(self, clicked):
        for i, btn in enumerate(self._nav_btns):
            btn.setChecked(btn is clicked)
            if btn is clicked:
                self._stack.setCurrentIndex(i)

    def _tick(self):
        now = datetime.datetime.now()
        self._tb_time.setText(now.strftime("%H:%M:%S  ·  %a %d %b %Y"))
        if HAS_PSUTIL:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self._tb_stats.setText(f"CPU {cpu:.0f}%  ·  RAM {ram:.0f}%")
            self._sb_cpu.setText(f"CPU  {cpu:.0f}%")
            self._sb_ram.setText(f"RAM  {ram:.0f}%")
        elif not HAS_PSUTIL:
            self._tb_stats.setText("install psutil for live metrics")

    def closeEvent(self, ev):
        r = QMessageBox.question(
            self, "NOVA TERMINAL",
            "Shut down command suite?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        ev.accept() if r == QMessageBox.Yes else ev.ignore()


# ═══════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor(B1))
    pal.setColor(QPalette.WindowText,      QColor(FG))
    pal.setColor(QPalette.Base,            QColor(B1))
    pal.setColor(QPalette.AlternateBase,   QColor(B2))
    pal.setColor(QPalette.Text,            QColor(FG))
    pal.setColor(QPalette.Button,          QColor(B2))
    pal.setColor(QPalette.ButtonText,      QColor(FG))
    pal.setColor(QPalette.Highlight,       QColor(T0))
    pal.setColor(QPalette.HighlightedText, QColor(B0))
    pal.setColor(QPalette.ToolTipBase,     QColor(B2))
    pal.setColor(QPalette.ToolTipText,     QColor(FG))
    app.setPalette(pal)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()






