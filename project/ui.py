from PyQt5.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
                              QWidget, QTableWidget, QTableWidgetItem, QLabel,
                              QLineEdit, QFrame, QSizePolicy, QHeaderView,
                              QGraphicsDropShadowEffect, QDialog, QComboBox,
                              QCheckBox, QScrollArea, QMessageBox, QFormLayout,
                              QTextEdit)
from PyQt5.QtGui import QColor, QRadialGradient, QPainter, QBrush
from PyQt5.QtCore import (Qt, QPropertyAnimation, QEasingCurve,
                           QTimer, QThread, pyqtSignal, pyqtProperty)
import pandas as pd
import math
import re

from database import init_db, save_books, load_old_prices
from chart import show_chart
from scraping import scrape_books, scrape_custom, preview_custom


# ─────────────────────────────────────────────
#  ANIMATED BACKGROUND
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
            g.setColorAt(0.0, c1); g.setColorAt(1.0, c2)
            p.setBrush(QBrush(g)); p.setPen(Qt.NoPen)
            p.drawEllipse(int(cx-r), int(cy-r), int(r*2), int(r*2))
        p.setPen(QColor(255, 255, 255, 12))
        for gx in range(0, w, 44):
            for gy in range(0, h, 44):
                p.drawPoint(gx, gy)
        p.end()


# ─────────────────────────────────────────────
#  GLOW BUTTON
# ─────────────────────────────────────────────
class GlowButton(QPushButton):
    def __init__(self, text, color="#c084fc", parent=None):
        super().__init__(text, parent)
        self._color = color
        self._glow  = 0
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
#  WORKER THREAD
# ─────────────────────────────────────────────
class ScrapeWorker(QThread):
    finished = pyqtSignal(list)
    error    = pyqtSignal(str)

    def __init__(self, mode, pages=1, config=None):
        super().__init__()
        self.mode   = mode
        self.pages  = pages
        self.config = config

    def run(self):
        try:
            if self.mode == "preset":
                self.finished.emit(scrape_books(self.pages))
            elif self.mode == "custom":
                self.finished.emit(scrape_custom(self.config))
            elif self.mode == "preview":
                self.finished.emit(preview_custom(self.config))
        except Exception as e:
            self.error.emit(str(e))


# ─────────────────────────────────────────────
#  CUSTOM SITE CONFIG DIALOG
# ─────────────────────────────────────────────
DIALOG_STYLE = """
QDialog { background: #0e0920; }
QWidget { background: transparent; color: #e9d5ff; font-family: 'Georgia', serif; }
QLabel { color: #a78bfa; font-size: 11px; letter-spacing: 1px; }
QLabel#title {
    color: #f0e6ff; font-size: 16px; font-weight: bold;
    letter-spacing: 3px; font-family: 'Georgia', serif;
}
QLabel#hint { color: #4a3f6b; font-size: 10px; font-style: italic; }
QLineEdit, QTextEdit {
    background: rgba(20,14,38,0.9); color: #e9d5ff;
    border: 1px solid #3b2f5e; border-radius: 7px;
    padding: 8px 12px; font-family: 'Courier New', monospace; font-size: 11px;
}
QLineEdit:focus, QTextEdit:focus { border: 1px solid #a78bfa; }
QComboBox {
    background: rgba(20,14,38,0.9); color: #e9d5ff;
    border: 1px solid #3b2f5e; border-radius: 7px;
    padding: 6px 12px; font-family: 'Courier New', monospace; font-size: 11px;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background: #130d24; color: #e9d5ff;
    border: 1px solid #3b2f5e; selection-background-color: #2d1f4e;
}
QCheckBox { color: #a78bfa; font-size: 11px; spacing: 8px; }
QCheckBox::indicator {
    width: 14px; height: 14px; border: 1px solid #3b2f5e;
    border-radius: 3px; background: rgba(20,14,38,0.9);
}
QCheckBox::indicator:checked { background: #7c3aed; border-color: #a78bfa; }
QFrame#rule { background: #2a1f3d; border: none; max-height: 1px; }
QTextEdit#preview_box {
    background: rgba(10,8,20,0.95); color: #34d399;
    border: 1px solid #1a3a2a; font-family: 'Courier New', monospace;
    font-size: 11px; border-radius: 7px;
}
"""

class SiteConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Custom Website")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setStyleSheet(DIALOG_STYLE)
        self.result_config = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        t = QLabel("CUSTOM WEBSITE SCRAPER")
        t.setObjectName("title")
        layout.addWidget(t)

        hint = QLabel(
            "Enter the URL and CSS selectors for the site you want to scrape.\n"
            "Use  {page}  in the URL where the page number should go.  "
            "e.g.  https://example.com/page/{page}"
        )
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addWidget(self._rule())

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.f_url      = self._field("https://example.com/shop/page/{page}")
        self.f_pages    = self._field("1")
        self.f_wait     = self._field(".product-item   (optional)")
        self.f_title    = self._field(".product-title  or  h2 a")
        self.f_t_attr   = self._field("title  or  data-name  (blank = use text)")
        self.f_price    = self._field(".price  or  span.amount")
        self.f_p_attr   = self._field("blank = use element text")
        self.f_headless = QCheckBox("Run browser in headless (invisible) mode")
        self.f_headless.setChecked(True)

        form.addRow("URL",             self.f_url)
        form.addRow("Pages",           self.f_pages)
        form.addRow("Wait selector",   self.f_wait)
        form.addRow("Title selector",  self.f_title)
        form.addRow("Title attribute", self.f_t_attr)
        form.addRow("Price selector",  self.f_price)
        form.addRow("Price attribute", self.f_p_attr)
        form.addRow("",                self.f_headless)
        layout.addLayout(form)
        layout.addWidget(self._rule())

        prev_lbl = QLabel("PREVIEW  ( first 5 results from page 1 )")
        prev_lbl.setStyleSheet(
            "color:#7c3aed;font-size:10px;font-weight:bold;"
            "letter-spacing:3px;font-family:'Courier New',monospace;"
        )
        layout.addWidget(prev_lbl)

        self.preview_box = QTextEdit()
        self.preview_box.setObjectName("preview_box")
        self.preview_box.setReadOnly(True)
        self.preview_box.setFixedHeight(110)
        self.preview_box.setPlaceholderText("click  ▶ PREVIEW  to test your selectors...")
        layout.addWidget(self.preview_box)

        btn_row = QHBoxLayout(); btn_row.setSpacing(10)
        self.prev_btn   = GlowButton("▶  PREVIEW", "#f59e0b")
        self.scrape_btn = GlowButton("✦  SCRAPE",  "#c084fc")
        cancel_btn      = GlowButton("✕  CANCEL",  "#f87171")
        self.prev_btn.setFixedHeight(38)
        self.scrape_btn.setFixedHeight(38)
        cancel_btn.setFixedHeight(38)

        for btn, acc in [(self.prev_btn,"#f59e0b"),
                         (self.scrape_btn,"#c084fc"),
                         (cancel_btn,"#f87171")]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:rgba(20,14,38,0.7); color:{acc};
                    border:1px solid {acc}66; border-radius:8px;
                    font-family:'Courier New',monospace;
                    font-size:11px; letter-spacing:1px; padding:0 18px;
                }}
                QPushButton:hover {{
                    background:rgba(20,14,38,0.95); border:1px solid {acc}bb;
                }}
                QPushButton:pressed {{ background:{acc}22; }}
                QPushButton:disabled {{ color:#4a3f6b; border-color:#2a1f3d; }}
            """)

        self.prev_btn.clicked.connect(self._run_preview)
        self.scrape_btn.clicked.connect(self._confirm)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.prev_btn)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self.scrape_btn)
        layout.addLayout(btn_row)
        self._worker = None

    def _field(self, placeholder):
        e = QLineEdit()
        e.setPlaceholderText(placeholder)
        e.setFixedHeight(34)
        return e

    def _rule(self):
        f = QFrame(); f.setObjectName("rule")
        f.setFrameShape(QFrame.HLine)
        return f

    def _build_config(self):
        return {
            "url":        self.f_url.text().strip(),
            "pages":      self.f_pages.text().strip() or "1",
            "wait_sel":   self.f_wait.text().strip(),
            "title_sel":  self.f_title.text().strip(),
            "title_attr": self.f_t_attr.text().strip(),
            "price_sel":  self.f_price.text().strip(),
            "price_attr": self.f_p_attr.text().strip(),
            "headless":   self.f_headless.isChecked(),
        }

    def _run_preview(self):
        cfg = self._build_config()
        if not cfg["url"] or not cfg["title_sel"] or not cfg["price_sel"]:
            self.preview_box.setPlainText("⚠  Please fill in URL, title selector, and price selector.")
            return
        self.prev_btn.setEnabled(False)
        self.scrape_btn.setEnabled(False)
        self.preview_box.setPlainText("⟳  Running preview on page 1…")
        self._worker = ScrapeWorker("preview", config=cfg)
        self._worker.finished.connect(self._show_preview)
        self._worker.error.connect(self._preview_error)
        self._worker.start()

    def _show_preview(self, rows):
        self.prev_btn.setEnabled(True)
        self.scrape_btn.setEnabled(True)
        if not rows:
            self.preview_box.setPlainText(
                "⚠  No results found.\n"
                "Check your CSS selectors — open DevTools (F12) and inspect the element."
            )
            return
        lines = [f"✦  Found {len(rows)} preview rows:\n"]
        for title, price in rows:
            lines.append(f"  {title[:55]:<56}  {price}")
        self.preview_box.setPlainText("\n".join(lines))

    def _preview_error(self, msg):
        self.prev_btn.setEnabled(True)
        self.scrape_btn.setEnabled(True)
        self.preview_box.setPlainText(f"✕  Error:\n{msg}")

    def _confirm(self):
        cfg = self._build_config()
        if not cfg["url"] or not cfg["title_sel"] or not cfg["price_sel"]:
            self.preview_box.setPlainText("⚠  URL, title selector, and price selector are required.")
            return
        self.result_config = cfg
        self.accept()


# ─────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────
class ScraperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✦  BIBLIOSPHERE  —  Price Intelligence")
        self.setMinimumSize(820, 780)
        self.resize(880, 820)

        self.all_books  = []
        self._dot_count = 0

        init_db()
        self.old_prices = load_old_prices()

        self._bg = CosmicBackground(self)
        self._bg.setGeometry(0, 0, self.width(), self.height())
        self._bg.lower()

        root = QWidget(self)
        root.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(32, 28, 32, 24)
        outer.setSpacing(0)

        # ── HEADER ──
        hdr = QHBoxLayout()
        badge = QLabel("✦")
        badge.setStyleSheet("color:#c084fc;font-size:28px;padding-right:10px;")
        tb = QVBoxLayout(); tb.setSpacing(0)
        t1 = QLabel("BIBLIOSPHERE")
        t1.setStyleSheet(
            "color:#f0e6ff;font-family:'Georgia',serif;font-size:26px;"
            "font-weight:bold;letter-spacing:6px;"
        )
        t2 = QLabel("multi-site price intelligence & analytics")
        t2.setStyleSheet("color:#4a3f6b;font-size:11px;letter-spacing:1px;")
        tb.addWidget(t1); tb.addWidget(t2)
        hdr.addWidget(badge); hdr.addLayout(tb); hdr.addStretch()
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

        # ── SOURCE SELECTOR ──
        outer.addWidget(self._sec("DATA SOURCE"))
        outer.addSpacing(8)
        src_row = QHBoxLayout(); src_row.setSpacing(10)

        self.site_combo = QComboBox()
        self.site_combo.addItems([
            "Books to Scrape  (built-in)",
            "Custom Website  →  configure"
        ])
        self.site_combo.setFixedHeight(38)
        self.site_combo.setStyleSheet("""
            QComboBox {
                background:rgba(20,14,38,0.85); color:#e9d5ff;
                border:1px solid #3b2f5e; border-radius:8px;
                padding:0 14px; font-family:'Courier New',monospace; font-size:12px;
            }
            QComboBox:focus { border:1px solid #a78bfa; }
            QComboBox::drop-down { border:none; width:24px; }
            QComboBox QAbstractItemView {
                background:#130d24; color:#e9d5ff;
                border:1px solid #3b2f5e;
                selection-background-color:#2d1f4e; padding:4px;
            }
        """)
        self.site_combo.currentIndexChanged.connect(self._on_site_changed)

        self.config_btn = GlowButton("⚙  CONFIGURE", "#818cf8")
        self.config_btn.setFixedHeight(38)
        self.config_btn.setVisible(False)
        self._sbtn(self.config_btn, "#818cf8")
        self.config_btn.clicked.connect(self._open_config)

        src_row.addWidget(self.site_combo, 3)
        src_row.addWidget(self.config_btn, 1)
        outer.addLayout(src_row)
        outer.addSpacing(14)

        # ── SCRAPE ROW ──
        outer.addWidget(self._sec("SCRAPE"))
        outer.addSpacing(8)
        sr = QHBoxLayout(); sr.setSpacing(10)
        self.page_input = self._inp("Pages  (e.g. 3)  — for built-in site")
        self.scrape_btn = GlowButton("▶   SCRAPE NOW", "#c084fc")
        self.scrape_btn.setFixedHeight(42)
        self._pbtn(self.scrape_btn)
        self.scrape_btn.clicked.connect(self._on_scrape)
        sr.addWidget(self.page_input, 3)
        sr.addWidget(self.scrape_btn, 2)
        outer.addLayout(sr)
        outer.addSpacing(18)

        # ── FILTER ROW ──
        outer.addWidget(self._rule("#1e1630"))
        outer.addSpacing(14)
        outer.addWidget(self._sec("SEARCH  &  FILTER"))
        outer.addSpacing(8)
        fr = QHBoxLayout(); fr.setSpacing(10)
        self.search_input = self._inp("search title…")
        self.search_input.textChanged.connect(self._search)
        self.min_price = self._inp("min", w=80)
        self.max_price = self._inp("max", w=80)
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

        # ── TABLE ──
        outer.addWidget(self._rule("#1e1630"))
        outer.addSpacing(14)
        cr = QHBoxLayout()
        cr.addWidget(self._sec("RESULTS"))
        cr.addStretch()
        self._count = QLabel("0 items")
        self._count.setStyleSheet("color:#4a3f6b;font-size:11px;letter-spacing:1px;")
        cr.addWidget(self._count)
        outer.addLayout(cr)
        outer.addSpacing(8)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["TITLE", "PRICE"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().resizeSection(1, 120)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setStyleSheet("""
            QTableWidget {
                background:rgba(12,8,26,0.88); border:1px solid #2a1f3d;
                border-radius:10px; font-family:'Georgia',serif; font-size:12px;
                color:#d4bfff; gridline-color:transparent;
                selection-background-color:#2d1f4e; outline:none;
            }
            QTableWidget::item { padding:10px 14px; border-bottom:1px solid #160f2e; }
            QTableWidget::item:selected { background:#2d1f4e; color:#e9d5ff; }
            QHeaderView::section {
                background:#130d24; color:#7c3aed;
                font-family:'Courier New',monospace; font-size:10px;
                font-weight:bold; letter-spacing:3px;
                padding:12px 14px; border:none; border-bottom:1px solid #2a1f3d;
            }
            QScrollBar:vertical { background:#0a0814; width:5px; border-radius:3px; }
            QScrollBar::handle:vertical { background:#3b2f5e; border-radius:3px; }
            QScrollBar::handle:vertical:hover { background:#7c3aed; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
        """)
        outer.addWidget(self.table, stretch=1)
        outer.addSpacing(16)

        # ── ACTION BUTTONS ──
        outer.addWidget(self._rule("#1e1630"))
        outer.addSpacing(14)
        ar = QHBoxLayout(); ar.setSpacing(10)
        self.sort_btn   = GlowButton("↑  SORT",  "#818cf8")
        self.export_btn = GlowButton("⬇  EXCEL", "#34d399")
        self.chart_btn  = GlowButton("◉  CHART", "#f472b6")
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

        self._dot_timer = QTimer(self)
        self._dot_timer.timeout.connect(self._tick_dots)
        self._custom_config = None
        self._set_status("IDLE", "#4a3f6b")

    # ── widget helpers ────────────────────────

    def resizeEvent(self, e):
        self._bg.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(e)

    def _rule(self, color="#2a1f3d"):
        f = QFrame(); f.setFrameShape(QFrame.HLine)
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
        e = QLineEdit(); e.setPlaceholderText(ph); e.setFixedHeight(38)
        if w: e.setFixedWidth(w)
        e.setStyleSheet("""
            QLineEdit {
                background:rgba(20,14,38,0.85); color:#e9d5ff;
                border:1px solid #3b2f5e; border-radius:8px;
                padding:0 14px; font-family:'Georgia',serif; font-size:12px;
            }
            QLineEdit:focus {
                border:1px solid #a78bfa; background:rgba(30,18,56,0.95);
            }
        """)
        return e

    def _pbtn(self, btn):
        btn.setStyleSheet("""
            QPushButton {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #7c3aed,stop:1 #a855f7);
                color:#ffffff; border:none; border-radius:8px;
                font-family:'Courier New',monospace; font-size:12px;
                font-weight:bold; letter-spacing:2px;
            }
            QPushButton:pressed {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #5b21b6,stop:1 #7c3aed);
            }
            QPushButton:disabled { background:#2a1f3d; color:#4a3f6b; }
        """)

    def _sbtn(self, btn, accent):
        btn.setStyleSheet(f"""
            QPushButton {{
                background:rgba(20,14,38,0.6); color:{accent};
                border:1px solid {accent}55; border-radius:8px;
                font-family:'Courier New',monospace; font-size:11px;
                letter-spacing:1px; padding:0 14px;
            }}
            QPushButton:hover {{
                background:rgba(20,14,38,0.9); border:1px solid {accent}aa;
            }}
            QPushButton:pressed {{ background:{accent}22; }}
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

    # ── price cleaner ─────────────────────────

    def _clean_price(self, price_str):
        """
        Universal price → float converter.
        Handles: £1.99  $2.50  1,99 Ç  1.234,56  $1,234.56  Rs.1,500  etc.
        """
        # Strip everything except digits, dot, comma
        cleaned = re.sub(r'[^\d.,]', '', str(price_str)).strip()
        if not cleaned:
            return 0.0

        if ',' in cleaned and '.' in cleaned:
            # 1.234,56 → European  |  1,234.56 → US
            if cleaned.rfind(',') > cleaned.rfind('.'):
                cleaned = cleaned.replace('.', '').replace(',', '.')   # European
            else:
                cleaned = cleaned.replace(',', '')                     # US
        elif ',' in cleaned:
            cleaned = cleaned.replace(',', '.')                        # 1,99 → 1.99

        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    # ── site switching ────────────────────────

    def _on_site_changed(self, idx):
        is_custom = idx == 1
        self.config_btn.setVisible(is_custom)
        self.page_input.setEnabled(not is_custom)
        if is_custom:
            self.page_input.setPlaceholderText("pages set inside  ⚙ Configure")
        else:
            self.page_input.setPlaceholderText("Pages  (e.g. 3)  — for built-in site")

    def _open_config(self):
        dlg = SiteConfigDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self._custom_config = dlg.result_config
            pages = self._custom_config.get("pages", "1")
            self._set_status(f"CONFIG SAVED  ✦  {pages} page(s)", "#a78bfa")

    # ── scrape ────────────────────────────────

    def _on_scrape(self):
        is_custom = self.site_combo.currentIndex() == 1

        if is_custom:
            if not self._custom_config:
                self._set_status("CONFIGURE SITE FIRST  ⚙", "#f87171")
                return
            mode, config = "custom", self._custom_config
            pages = 1
        else:
            t = self.page_input.text().strip()
            if not t.isdigit():
                self._set_status("INVALID PAGE NUMBER", "#f87171")
                orig = self.page_input.styleSheet()
                self.page_input.setStyleSheet(orig + "border:1px solid #f87171;")
                QTimer.singleShot(700, lambda: self.page_input.setStyleSheet(orig))
                return
            mode, config = "preset", None
            pages = int(t)

        self.scrape_btn.setEnabled(False)
        self.scrape_btn.setText("  RUNNING…")
        self._dot_count = 0
        self._dot_timer.start(420)
        self._set_status("SCRAPING  ●○○", "#a78bfa")

        self._worker = ScrapeWorker(mode, pages=pages, config=config)
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
        self._set_status(f"COMPLETE  ✦  {len(books)} ITEMS", "#34d399")

    def _err(self, msg):
        self._dot_timer.stop()
        self.scrape_btn.setEnabled(True)
        self.scrape_btn.setText("▶   SCRAPE NOW")
        self._set_status("SCRAPE ERROR", "#f87171")
        QMessageBox.critical(self, "Scrape Error", msg)

    # ── actions ───────────────────────────────

    def _chart(self):
        if not show_chart(self.all_books, self.old_prices):
            self._set_status("NO DATA TO CHART", "#f87171")

    def _export(self):
        if not self.all_books:
            self._set_status("NO DATA", "#f87171"); return
        pd.DataFrame(self.all_books, columns=["Title", "Price"]).to_excel(
            "books.xlsx", index=False
        )
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

        # ✅ _clean_price handles £ $ , Ç and any currency format
        f = [[t, p] for t, p in self.all_books
             if lo <= self._clean_price(p) <= hi]
        self._fill_table(f)
        self._set_status(f"FILTER  ✦  {len(f)} RESULTS", "#f59e0b")

    def _sort(self):
        # ✅ _clean_price handles all formats safely
        self.all_books.sort(key=lambda x: self._clean_price(x[1]))
        self._fill_table(self.all_books)
        self._set_status("SORTED BY PRICE  ↑", "#818cf8")

    # ── table ─────────────────────────────────

    def _fill_table(self, data):
        self.table.setRowCount(0)
        self._count.setText(f"{len(data)} items")

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
                    try:
                        # ✅ _clean_price used here too — no more [1:] hacks
                        old = self._clean_price(self.old_prices[title])
                        new = self._clean_price(price)
                        if new < old:
                            pi.setForeground(QColor("#34d399"))
                            pi.setBackground(QColor("#052e16"))
                        elif new > old:
                            pi.setForeground(QColor("#f87171"))
                            pi.setBackground(QColor("#2d0a0a"))
                        else:
                            pi.setForeground(QColor("#fbbf24"))
                            pi.setBackground(QColor("#1c1400"))
                    except Exception:
                        pi.setForeground(QColor("#a78bfa"))
                else:
                    pi.setForeground(QColor("#a78bfa"))

                self.table.setItem(row, 1, pi)
                self.table.setRowHeight(row, 38)

            if end < len(data):
                QTimer.singleShot(25, lambda: batch(end))

        if data:
            batch(0)