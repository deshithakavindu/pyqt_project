from PyQt5.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
                              QWidget, QTableWidget, QTableWidgetItem,
                              QLabel, QLineEdit, QFrame, QSizePolicy,
                              QHeaderView, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QColor, QRadialGradient, QPainter, QBrush
from PyQt5.QtCore import (Qt, QPropertyAnimation, QEasingCurve,
                           QTimer, QThread, pyqtSignal, pyqtProperty)
import pandas as pd
import math

from database import init_db, save_books, load_old_prices
from chart import show_chart
from scraping import scrape_books


# ─────────────────────────────────────────────
#  ANIMATED COSMIC BACKGROUND
# ─────────────────────────────────────────────
class CosmicBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tick = 0
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        t = QTimer(self)
        t.timeout.connect(self._step)
        t.start(40)

    def _step(self):
        self._tick += 1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor("#0a0814"))
        t  = self._tick * 0.018
        w, h = self.width(), self.height()

        orbs = [
            (0.18, 0.22, 230, QColor(88,  28, 220, 30), QColor(120, 60, 255, 0)),
            (0.76, 0.14, 190, QColor(180, 70,  30, 24), QColor(220,100,  40, 0)),
            (0.54, 0.72, 270, QColor(20, 140, 200, 22), QColor( 40,180, 240, 0)),
            (0.10, 0.76, 160, QColor(200,  40, 120, 20), QColor(240, 60, 140, 0)),
        ]
        for i, (bx, by, br, c1, c2) in enumerate(orbs):
            cx = bx * w + math.sin(t + i * 1.3) * w * 0.055
            cy = by * h + math.cos(t * 0.7 + i * 0.9) * h * 0.055
            r  = br + math.sin(t * 0.5 + i) * 18
            g  = QRadialGradient(cx, cy, r)
            g.setColorAt(0.0, c1)
            g.setColorAt(1.0, c2)
            p.setBrush(QBrush(g))
            p.setPen(Qt.NoPen)
            p.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))

        p.setPen(QColor(255, 255, 255, 12))
        for gx in range(0, w, 44):
            for gy in range(0, h, 44):
                p.drawPoint(gx, gy)
        p.end()


# ─────────────────────────────────────────────
#  GLOW BUTTON  (hover glow via QPropertyAnimation)
# ─────────────────────────────────────────────
class GlowButton(QPushButton):
    def __init__(self, text, color="#c084fc", parent=None):
        super().__init__(text, parent)
        self._color  = color
        self._glow   = 0
        self.setCursor(Qt.PointingHandCursor)
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(0)
        self._shadow.setColor(QColor(color))
        self._shadow.setOffset(0, 0)
        self.setGraphicsEffect(self._shadow)
        self._anim = QPropertyAnimation(self, b"glowRadius")
        self._anim.setDuration(240)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    @pyqtProperty(int)
    def glowRadius(self):
        return self._glow

    @glowRadius.setter
    def glowRadius(self, v):
        self._glow = v
        self._shadow.setBlurRadius(v)

    def enterEvent(self, e):
        self._anim.stop()
        self._anim.setStartValue(self._glow)
        self._anim.setEndValue(30)
        self._anim.start()

    def leaveEvent(self, e):
        self._anim.stop()
        self._anim.setStartValue(self._glow)
        self._anim.setEndValue(0)
        self._anim.start()


# ─────────────────────────────────────────────
#  BACKGROUND SCRAPE WORKER
# ─────────────────────────────────────────────
class ScrapeWorker(QThread):
    finished = pyqtSignal(list)
    error    = pyqtSignal(str)

    def __init__(self, pages):
        super().__init__()
        self.pages = pages

    def run(self):
        try:
            self.finished.emit(scrape_books(self.pages))
        except Exception as e:
            self.error.emit(str(e))


# ─────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────
class ScraperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✦  BIBLIOSPHERE  —  Price Intelligence")
        self.setMinimumSize(820, 740)
        self.resize(860, 800)

        self.all_books  = []
        self._dot_count = 0

        init_db()
        self.old_prices = load_old_prices()

        # cosmic bg
        self._bg = CosmicBackground(self)
        self._bg.setGeometry(0, 0, self.width(), self.height())
        self._bg.lower()

        # root
        root = QWidget(self)
        root.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(32, 28, 32, 24)
        outer.setSpacing(0)

        # ── HEADER ──────────────────────────────────
        hdr = QHBoxLayout()
        badge = QLabel("✦")
        badge.setStyleSheet("color:#c084fc;font-size:28px;padding-right:10px;")

        tb = QVBoxLayout()
        tb.setSpacing(0)
        t1 = QLabel("BIBLIOSPHERE")
        t1.setStyleSheet(
            "color:#f0e6ff;font-family:'Georgia',serif;font-size:26px;"
            "font-weight:bold;letter-spacing:6px;"
        )
        t2 = QLabel("real-time book price intelligence & analytics")
        t2.setStyleSheet("color:#4a3f6b;font-size:11px;letter-spacing:1px;")
        tb.addWidget(t1); tb.addWidget(t2)

        hdr.addWidget(badge)
        hdr.addLayout(tb)
        hdr.addStretch()

        self._orb  = QLabel("●")
        self._orb.setStyleSheet("color:#4a3f6b;font-size:10px;")
        self._stxt = QLabel("IDLE")
        self._stxt.setStyleSheet(
            "color:#4a3f6b;font-size:10px;letter-spacing:2px;padding-left:5px;"
        )
        hdr.addWidget(self._orb); hdr.addWidget(self._stxt)
        outer.addLayout(hdr)
        outer.addSpacing(6)
        outer.addWidget(self._rule())
        outer.addSpacing(18)

        # ── SCRAPE ──────────────────────────────────
        outer.addWidget(self._sec("SCRAPE DATA"))
        outer.addSpacing(8)
        sr = QHBoxLayout(); sr.setSpacing(10)
        self.page_input = self._inp("Number of pages  (e.g. 3)")
        self.scrape_btn = GlowButton("▶   SCRAPE NOW", "#c084fc")
        self.scrape_btn.setFixedHeight(42)
        self._pbtn(self.scrape_btn)
        self.scrape_btn.clicked.connect(self._on_scrape)
        sr.addWidget(self.page_input, 3)
        sr.addWidget(self.scrape_btn, 2)
        outer.addLayout(sr)
        outer.addSpacing(18)

        # ── FILTER ──────────────────────────────────
        outer.addWidget(self._rule("#1e1630"))
        outer.addSpacing(14)
        outer.addWidget(self._sec("SEARCH  &  FILTER"))
        outer.addSpacing(8)
        fr = QHBoxLayout(); fr.setSpacing(10)
        self.search_input = self._inp("search title…")
        self.search_input.textChanged.connect(self._search)
        self.min_price = self._inp("min £", w=88)
        self.max_price = self._inp("max £", w=88)
        self.filter_btn = GlowButton("APPLY", "#f59e0b")
        self.filter_btn.setFixedHeight(38)
        self._sbtn(self.filter_btn, "#f59e0b")
        self.filter_btn.clicked.connect(self._filter)
        fr.addWidget(self.search_input, 4)
        fr.addWidget(self.min_price)
        fr.addWidget(self.max_price)
        fr.addWidget(self.filter_btn)
        outer.addLayout(fr)
        outer.addSpacing(18)

        # ── TABLE ──────────────────────────────────
        outer.addWidget(self._rule("#1e1630"))
        outer.addSpacing(14)
        cr = QHBoxLayout()
        cr.addWidget(self._sec("RESULTS"))
        cr.addStretch()
        self._count = QLabel("0 books")
        self._count.setStyleSheet("color:#4a3f6b;font-size:11px;letter-spacing:1px;")
        cr.addWidget(self._count)
        outer.addLayout(cr)
        outer.addSpacing(8)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["TITLE", "PRICE"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().resizeSection(1, 110)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setStyleSheet("""
            QTableWidget {
                background: rgba(12,8,26,0.88);
                border: 1px solid #2a1f3d;
                border-radius: 10px;
                font-family: 'Georgia', serif;
                font-size: 12px;
                color: #d4bfff;
                gridline-color: transparent;
                selection-background-color: #2d1f4e;
                outline: none;
            }
            QTableWidget::item {
                padding: 10px 14px;
                border-bottom: 1px solid #160f2e;
            }
            QTableWidget::item:selected {
                background: #2d1f4e;
                color: #e9d5ff;
            }
            QHeaderView::section {
                background: #130d24;
                color: #7c3aed;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 3px;
                padding: 12px 14px;
                border: none;
                border-bottom: 1px solid #2a1f3d;
            }
            QScrollBar:vertical {
                background: #0a0814;
                width: 5px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #3b2f5e;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #7c3aed;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height:0; }
        """)
        outer.addWidget(self.table, stretch=1)
        outer.addSpacing(16)

        # ── ACTIONS ─────────────────────────────────
        outer.addWidget(self._rule("#1e1630"))
        outer.addSpacing(14)
        ar = QHBoxLayout(); ar.setSpacing(10)

        self.sort_btn   = GlowButton("↑  SORT PRICE", "#818cf8")
        self.export_btn = GlowButton("⬇  EXCEL",      "#34d399")
        self.chart_btn  = GlowButton("◉  CHART",      "#f472b6")

        for b in (self.sort_btn, self.export_btn, self.chart_btn):
            b.setFixedHeight(38)

        self._sbtn(self.sort_btn,   "#818cf8")
        self._sbtn(self.export_btn, "#34d399")
        self._sbtn(self.chart_btn,  "#f472b6")

        self.sort_btn.clicked.connect(self._sort)
        self.export_btn.clicked.connect(self._export)
        self.chart_btn.clicked.connect(self._chart)

        ar.addWidget(self.sort_btn)
        ar.addWidget(self.export_btn)
        ar.addStretch()
        ar.addWidget(self.chart_btn)
        outer.addLayout(ar)

        # dot animation timer
        self._dot_timer = QTimer(self)
        self._dot_timer.timeout.connect(self._tick_dots)
        self._set_status("IDLE", "#4a3f6b")

    # ── widget helpers ───────────────────────────

    def resizeEvent(self, e):
        self._bg.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(e)

    def _rule(self, color="#2a1f3d"):
        f = QFrame()
        f.setFrameShape(QFrame.HLine)
        f.setStyleSheet(f"background:{color};border:none;max-height:1px;")
        return f

    def _sec(self, text):
        l = QLabel(text)
        l.setStyleSheet(
            "color:#7c3aed;font-size:10px;font-weight:bold;"
            "letter-spacing:4px;font-family:'Courier New',monospace;"
        )
        return l

    def _inp(self, ph, w=None):
        e = QLineEdit()
        e.setPlaceholderText(ph)
        e.setFixedHeight(38)
        if w: e.setFixedWidth(w)
        e.setStyleSheet("""
            QLineEdit {
                background: rgba(20,14,38,0.85);
                color: #e9d5ff;
                border: 1px solid #3b2f5e;
                border-radius: 8px;
                padding: 0 14px;
                font-family: 'Georgia', serif;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #a78bfa;
                background: rgba(30,18,56,0.95);
            }
        """)
        return e

    def _pbtn(self, btn):
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #7c3aed, stop:1 #a855f7);
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 2px;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #5b21b6, stop:1 #7c3aed);
            }
            QPushButton:disabled {
                background: #2a1f3d;
                color: #4a3f6b;
            }
        """)

    def _sbtn(self, btn, accent):
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(20,14,38,0.6);
                color: {accent};
                border: 1px solid {accent}55;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                letter-spacing: 1px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                background: rgba(20,14,38,0.9);
                border: 1px solid {accent}aa;
            }}
            QPushButton:pressed {{ background: {accent}22; }}
        """)

    def _set_status(self, text, color="#4a3f6b"):
        self._stxt.setText(text)
        self._stxt.setStyleSheet(
            f"color:{color};font-size:10px;letter-spacing:2px;padding-left:5px;"
        )
        self._orb.setStyleSheet(f"color:{color};font-size:10px;")

    def _tick_dots(self):
        self._dot_count = (self._dot_count + 1) % 4
        d = "●" * self._dot_count + "○" * (3 - self._dot_count)
        self._stxt.setText(f"SCRAPING  {d}")

    # ── slots ────────────────────────────────────

    def _on_scrape(self):
        t = self.page_input.text().strip()
        if not t.isdigit():
            self._set_status("INVALID INPUT", "#f87171")
            orig = self.page_input.styleSheet()
            self.page_input.setStyleSheet(orig + "border:1px solid #f87171;")
            QTimer.singleShot(700, lambda: self.page_input.setStyleSheet(orig))
            return
        self.scrape_btn.setEnabled(False)
        self.scrape_btn.setText("  RUNNING…")
        self._dot_count = 0
        self._dot_timer.start(420)
        self._set_status("SCRAPING  ●○○", "#a78bfa")
        self._worker = ScrapeWorker(int(t))
        self._worker.finished.connect(self._done)
        self._worker.error.connect(self._err)
        self._worker.start()

    def _done(self, books):
        self._dot_timer.stop()
        self.all_books = books
        save_books(books)
        self._fill_table(books)
        self.scrape_btn.setEnabled(True)
        self.scrape_btn.setText("▶   SCRAPE NOW")
        self._set_status(f"COMPLETE  ✦  {len(books)} BOOKS", "#34d399")

    def _err(self, msg):
        self._dot_timer.stop()
        self.scrape_btn.setEnabled(True)
        self.scrape_btn.setText("▶   SCRAPE NOW")
        self._set_status("SCRAPE ERROR", "#f87171")

    def _chart(self):
        if not show_chart(self.all_books, self.old_prices):
            self._set_status("NO DATA TO CHART", "#f87171")

    def _export(self):
        if not self.all_books:
            self._set_status("NO DATA", "#f87171"); return
        pd.DataFrame(self.all_books, columns=["Title","Price"]).to_excel("books.xlsx", index=False)
        self._set_status("EXPORTED  →  books.xlsx", "#34d399")

    def _search(self):
        q = self.search_input.text().lower()
        self._fill_table([b for b in self.all_books if q in b[0].lower()])

    def _filter(self):
        try:
            lo = float(self.min_price.text() or 0)
            hi = float(self.max_price.text() or 9999)
        except ValueError:
            self._set_status("BAD PRICE RANGE", "#f87171"); return
        f = [[t,p] for t,p in self.all_books if lo <= float(p[1:]) <= hi]
        self._fill_table(f)
        self._set_status(f"FILTER  ✦  {len(f)} RESULTS", "#f59e0b")

    def _sort(self):
        self.all_books.sort(key=lambda x: float(x[1][1:]))
        self._fill_table(self.all_books)
        self._set_status("SORTED BY PRICE  ↑", "#818cf8")

    # ── table ────────────────────────────────────

    def _fill_table(self, data):
        self.table.setRowCount(0)
        self._count.setText(f"{len(data)} books")

        def batch(start, size=10):
            end = min(start + size, len(data))
            for i in range(start, end):
                title, price = data[i]
                row = self.table.rowCount()
                self.table.insertRow(row)

                ti = QTableWidgetItem(title)
                ti.setForeground(QColor("#c4b5fd"))
                self.table.setItem(row, 0, ti)

                pi = QTableWidgetItem(price)
                pi.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                if title in self.old_prices:
                    old = float(self.old_prices[title][1:])
                    new = float(price[1:])
                    if new < old:
                        pi.setForeground(QColor("#34d399"))
                        pi.setBackground(QColor("#052e16"))
                    elif new > old:
                        pi.setForeground(QColor("#f87171"))
                        pi.setBackground(QColor("#2d0a0a"))
                    else:
                        pi.setForeground(QColor("#fbbf24"))
                        pi.setBackground(QColor("#1c1400"))
                else:
                    pi.setForeground(QColor("#a78bfa"))

                self.table.setItem(row, 1, pi)
                self.table.setRowHeight(row, 38)

            if end < len(data):
                QTimer.singleShot(25, lambda: batch(end))

        if data:
            batch(0)