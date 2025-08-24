# -*- coding: utf-8 -*-
import os, sys, json, subprocess, tempfile, threading
from pathlib import Path
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (QApplication, QWidget, QFileDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QTextEdit, QMessageBox)

APP_NAME = "ReverseX"
CFG_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "ReverseX"
CFG_PATH = CFG_DIR / "config.json"
DEFAULT_CFG = {"target_faces": 80000, "last_input": ""}

def load_cfg():
    try:
        CFG_DIR.mkdir(parents=True, exist_ok=True)
        if CFG_PATH.exists():
            return json.load(open(CFG_PATH, "r", encoding="utf-8"))
    except: pass
    return DEFAULT_CFG.copy()

def save_cfg(cfg):
    CFG_DIR.mkdir(parents=True, exist_ok=True)
    json.dump(cfg, open(CFG_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

class Worker(QThread):
    log = Signal(str)
    done = Signal(str, str)  # out_dir, step_path
    def __init__(self, input_path, target_faces):
        super().__init__()
        self.input_path = input_path
        self.target_faces = target_faces
    def run(self):
        try:
            out_dir = Path(tempfile.gettempdir()) / f"reversex_{os.getpid()}_{threading.get_ident()}"
            out_dir.mkdir(parents=True, exist_ok=True)
            tool = Path(__file__).parent / "engine" / "auto_reverse_basic.py"
            args = [sys.executable, str(tool), "--input", self.input_path, "--out", str(out_dir), "--target-faces", str(self.target_faces), "--export-step"]
            self.log.emit("[i] " + " ".join(args))
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout: self.log.emit(line.rstrip())
            ret = proc.wait()
            step = out_dir / "reconstructed.step"
            self.done.emit(str(out_dir), str(step) if step.exists() and ret==0 else "")
        except Exception as e:
            self.log.emit("[EXC] " + str(e))
            self.done.emit("", "")

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ReverseX — Scan→STEP")
        self.cfg = load_cfg()
        self._build()
    def _build(self):
        v = QVBoxLayout(self)
        row = QHBoxLayout()
        self.path = QLineEdit(self.cfg.get("last_input","")); self.path.setPlaceholderText("STL/PLY/OBJ...")
        b = QPushButton("Выбрать"); b.clicked.connect(self.on_browse); row.addWidget(self.path); row.addWidget(b)
        v.addLayout(row)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("target_faces")); 
        self.faces = QSpinBox(); self.faces.setRange(5000, 300000); self.faces.setSingleStep(5000); self.faces.setValue(int(self.cfg.get("target_faces",80000)))
        row2.addWidget(self.faces); v.addLayout(row2)
        row3 = QHBoxLayout()
        self.run = QPushButton("Запустить → STEP"); self.run.clicked.connect(self.on_run)
        self.open_step = QPushButton("Открыть STEP"); self.open_step.setEnabled(False); self.open_step.clicked.connect(self.on_open_step)
        self.open_dir = QPushButton("Открыть папку"); self.open_dir.setEnabled(False); self.open_dir.clicked.connect(self.on_open_dir)
        row3.addWidget(self.run); row3.addWidget(self.open_step); row3.addWidget(self.open_dir); v.addLayout(row3)
        self.log = QTextEdit(); self.log.setReadOnly(True); self.log.setMinimumHeight(220); v.addWidget(self.log)
        self.out_dir = ""; self.step_path = ""
    def on_browse(self):
        p,_ = QFileDialog.getOpenFileName(self, "Выберите STL/PLY/OBJ", "", "Scans (*.stl *.ply *.obj);;All files (*.*)")
        if p: self.path.setText(p)
    def on_run(self):
        p = self.path.text().strip()
        if not p or not os.path.exists(p): QMessageBox.warning(self, APP_NAME, "Укажи файл скана"); return
        self.cfg.update({"last_input": p, "target_faces": self.faces.value()}); save_cfg(self.cfg)
        self.log.clear(); self.run.setEnabled(False); self.open_step.setEnabled(False); self.open_dir.setEnabled(False)
        self.worker = Worker(p, self.faces.value())
        self.worker.log.connect(lambda s: self.log.append(s))
        self.worker.done.connect(self.on_done)
        self.worker.start()
    def on_done(self, out_dir, step_path):
        self.out_dir, self.step_path = out_dir, step_path
        self.run.setEnabled(True); self.open_dir.setEnabled(bool(out_dir)); self.open_step.setEnabled(bool(step_path))
        if step_path: self.log.append(f"[OK] STEP: {step_path}")
        else: self.log.append("[!] Не удалось создать STEP (см. report.json)")
    def on_open_step(self):
        if self.step_path and os.path.exists(self.step_path): os.startfile(self.step_path)
    def on_open_dir(self):
        if self.out_dir and os.path.exists(self.out_dir): os.startfile(self.out_dir)

if __name__ == "__main__":
    app = QApplication(sys.argv); w = App(); w.resize(860, 520); w.show(); sys.exit(app.exec())
