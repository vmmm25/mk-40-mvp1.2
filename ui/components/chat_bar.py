import os
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QEvent
from PyQt6.QtGui import QFont, QAction, QIcon, QTextCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QComboBox, QMenu, QFrame, QLabel, QSizePolicy, QFileDialog
)
from ui.theme import Theme as C
from ui.config_toolbar import _COMBO_STYLE

class AutoExpandingTextEdit(QTextEdit):
    returnPressed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Segoe UI", 11))
        self.setPlaceholderText("Type a command or question... (Shift+Enter for new line)")
        self.setStyleSheet(f"""
            QTextEdit {{
                background: #000d14; color: {C.WHITE};
                border: 1px solid {C.BORDER}; border-radius: 10px; padding: 6px;
            }}
            QTextEdit:focus {{ border: 1px solid {C.PRI}; }}
            QScrollBar:vertical {{ width: 0px; }}
        """)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textChanged.connect(self._adjust_height)
        self._min_height = 36
        self._max_height = 150
        self.setFixedHeight(self._min_height)

    def _adjust_height(self):
        doc_height = int(self.document().size().height())
        margins = self.contentsMargins()
        new_height = doc_height + margins.top() + margins.bottom() + 10
        if new_height < self._min_height:
            new_height = self._min_height
        if new_height > self._max_height:
            new_height = self._max_height
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
        self.setFixedHeight(new_height)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.returnPressed.emit()
        else:
            super().keyPressEvent(event)

class ChatBarWidget(QWidget):
    send_requested = pyqtSignal(str)
    file_selected = pyqtSignal(str)
    folder_selected = pyqtSignal(str)
    tool_command_requested = pyqtSignal(str)
    provider_changed = pyqtSignal(str)
    permissions_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(6)
        
        # --- Toolbar (Top row) ---
        toolbar_lay = QHBoxLayout()
        toolbar_lay.setSpacing(8)
        
        # Provider Combo
        self.provider_combo = QComboBox()
        self.provider_combo.setFont(QFont("Segoe UI", 9))
        self.provider_combo.setFixedHeight(28)
        self.provider_combo.setStyleSheet(_COMBO_STYLE)
        self.provider_combo.addItems(["gemini", "ollama", "openrouter", "lmstudio"])
        self.provider_combo.currentTextChanged.connect(self._on_provider_change)
        toolbar_lay.addWidget(self.provider_combo)
        
        # Model Combo (To be populated by main window)
        self.model_combo = QComboBox()
        self.model_combo.setFont(QFont("Segoe UI", 9))
        self.model_combo.setFixedHeight(28)
        self.model_combo.setStyleSheet(_COMBO_STYLE)
        self.model_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        toolbar_lay.addWidget(self.model_combo, stretch=1)
        
        # Thinking Level Combo
        self.thinking_combo = QComboBox()
        self.thinking_combo.setFont(QFont("Segoe UI", 9))
        self.thinking_combo.setFixedHeight(28)
        self.thinking_combo.setStyleSheet(_COMBO_STYLE)
        self.thinking_combo.addItems(["Low Thinking", "Standard", "Deep Think", "Architect"])
        toolbar_lay.addWidget(self.thinking_combo)
        
        # LLM Toggle Button
        self.llm_toggle_btn = QPushButton("● LLM ONLINE")
        self.llm_toggle_btn.setFixedHeight(28)
        self.llm_toggle_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.llm_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        toolbar_lay.addWidget(self.llm_toggle_btn)
        
        # Permissions Panel Button
        self.perms_btn = QPushButton("🛡 Permisos")
        self.perms_btn.setFixedHeight(28)
        self.perms_btn.setFont(QFont("Segoe UI", 9))
        self.perms_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.perms_btn.setStyleSheet(f"""
            QPushButton {{ background: #000d12; color: {C.TEXT_DIM}; border: 1px solid {C.BORDER}; border-radius: 8px; padding: 0 8px; }}
            QPushButton:hover {{ color: {C.TEXT}; border-color: {C.BORDER_B}; }}
        """)
        self.perms_btn.clicked.connect(lambda: self.permissions_requested.emit())
        toolbar_lay.addWidget(self.perms_btn)
        
        main_layout.addLayout(toolbar_lay)
        
        # --- Input area (Bottom row) ---
        input_row = QHBoxLayout()
        input_row.setSpacing(5)
        
        # Attachment Button (Paperclip)
        self.attach_btn = QPushButton("📎")
        self.attach_btn.setFixedSize(34, 34)
        self.attach_btn.setFont(QFont("Segoe UI", 14))
        self.attach_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.attach_btn.setStyleSheet(f"""
            QPushButton {{ background: {C.PANEL}; color: {C.ACC2}; border: 1px solid {C.BORDER_A}; border-radius: 10px; }}
            QPushButton:hover {{ background: {C.PANEL2}; border: 1px solid {C.ACC2}; }}
            QPushButton::menu-indicator {{ image: none; }}
        """)
        self._attach_menu = QMenu(self)
        self._attach_menu.setStyleSheet(f"QMenu {{ background-color: {C.DARK}; color: {C.TEXT}; border: 1px solid {C.BORDER_B}; padding: 4px; }} QMenu::item {{ padding: 6px 24px 6px 12px; }} QMenu::item:selected {{ background-color: {C.PRI_GHO}; color: {C.PRI}; }}")
        
        act_file = QAction("📄 Subir Archivo...", self)
        act_file.triggered.connect(self._select_file)
        self._attach_menu.addAction(act_file)
        act_folder = QAction("📁 Subir Carpeta...", self)
        act_folder.triggered.connect(self._select_folder)
        self._attach_menu.addAction(act_folder)
        self._attach_menu.addSeparator()
        act_all = QAction("📎 Todos los archivos...", self)
        act_all.triggered.connect(self._select_all_files)
        self._attach_menu.addAction(act_all)
        
        self.attach_btn.setMenu(self._attach_menu)
        input_row.addWidget(self.attach_btn)
        
        # Tools Button (+)
        self.tools_btn = QPushButton("+")
        self.tools_btn.setFixedSize(34, 34)
        self.tools_btn.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.tools_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tools_btn.setStyleSheet(f"""
            QPushButton {{ background: {C.PANEL}; color: {C.GREEN}; border: 1px solid {C.GREEN}; border-radius: 10px; }}
            QPushButton:hover {{ background: {C.GREEN}22; border: 1px solid #00ffaa; }}
            QPushButton::menu-indicator {{ image: none; }}
        """)
        self._tools_menu = QMenu(self)
        self._tools_menu.setStyleSheet(self._attach_menu.styleSheet())
        for action_name, cmd in [
            ("🖼 Crear imagen", "/imagen "),
            ("🎵 Crear audio", "/audio "),
            ("🎬 Crear video", "/video "),
            ("🤖 Agentes", "/agentes "),
            ("📁 Sesiones", "/sesiones ")
        ]:
            act = QAction(action_name, self)
            act.triggered.connect(lambda checked, c=cmd: self.tool_command_requested.emit(c))
            self._tools_menu.addAction(act)
            
        self.tools_btn.setMenu(self._tools_menu)
        input_row.addWidget(self.tools_btn)
        
        # Text Input
        self.text_input = AutoExpandingTextEdit()
        self.text_input.returnPressed.connect(self._on_send)
        input_row.addWidget(self.text_input, stretch=1)
        
        # Send Button
        self.send_btn = QPushButton("▸")
        self.send_btn.setFixedSize(34, 34)
        self.send_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setStyleSheet(f"""
            QPushButton {{ background: {C.PANEL}; color: {C.PRI}; border: 1px solid {C.PRI_DIM}; border-radius: 10px; font-weight: bold; }}
            QPushButton:hover {{ background: {C.PRI_GHO}; border: 1px solid {C.PRI}; }}
        """)
        self.send_btn.clicked.connect(self._on_send)
        input_row.addWidget(self.send_btn)
        
        main_layout.addLayout(input_row)
        
    def _on_provider_change(self, text):
        self.provider_changed.emit(text)
        
    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo a enviar")
        if path:
            self.file_selected.emit(path)
            
    def _select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta a enviar")
        if path:
            self.folder_selected.emit(path)
            
    def _select_all_files(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo a enviar", "",
            "Todos los archivos (*.*);;Imágenes (*.jpg *.jpeg *.png *.gif *.webp *.bmp *.svg);;Documentos (*.pdf *.docx *.txt *.md *.pptx);;Código (*.py *.js *.ts *.html *.css *.java *.cpp *.go);;Audio (*.mp3 *.wav *.ogg *.m4a *.flac);;Video (*.mp4 *.avi *.mov *.mkv *.webm);;Archivos (*.zip *.rar *.tar *.gz *.7z)"
        )
        if path:
            self.file_selected.emit(path)

    def _on_send(self):
        text = self.text_input.toPlainText().strip()
        if text:
            self.send_requested.emit(text)
            self.text_input.clear()
            self.text_input._adjust_height()
