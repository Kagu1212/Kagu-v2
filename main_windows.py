import sys
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QTextEdit,
    QFrame, QListWidget, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QColor, QPixmap, QIcon, QFont
from PyQt6.QtCore import Qt

from core.orchestrator import Orchestrator
from interface.widgets.chat_widget import ChatWidget
from interface.widgets.command_panel import CommandPanel
from interface.widgets.system_monitor import SystemMonitor
from interface.widgets.settings_panel import SettingsPanel
from interface.widgets.floating_avatar import FloatingAvatar
from interface.themes.theme_manager import ThemeManager

logger = logging.getLogger(__name__)

class KaguMainWindow(QMainWindow):
    """Ventana principal de KAGU"""
    
    # Señales
    send_message = pyqtSignal(str)
    process_voice_command = pyqtSignal(str)
    
    def __init__(self, orchestrator: Orchestrator):
        super().__init__()
        
        self.orchestrator = orchestrator
        self.theme_manager = ThemeManager()
        
        # Configuración de la ventana
        self.setWindowTitle("KAGU - Asistente de IA")
        self.setWindowIcon(QIcon("interface/assets/icons/kagu_icon.png"))
        
        # Tamaño inicial
        self.resize(1400, 900)
        self.setMinimumSize(1200, 700)
        
        # Configurar tema
        self.theme_manager.apply_theme("dark")
        
        # Inicializar interfaz
        self._init_ui()
        
        # Avatar flotante (segundo plano)
        self.floating_avatar = FloatingAvatar(orchestrator)
        
        # Timers
        self._setup_timers()
        
        logger.info("Ventana principal inicializada")
    
    def _init_ui(self):
        """Inicializa la interfaz gráfica"""
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # ===== PANEL IZQUIERDO: Logo + Opciones =====
        left_panel = self._create_left_panel()
        
        # ===== PANEL CENTRAL: Chat principal =====
        center_panel = self._create_center_panel()
        
        # ===== PANEL DERECHO: Sistema + Configuración =====
        right_panel = self._create_right_panel()
        
        # Agregar con splitters para redimensionar
        splitter_main = QSplitter(Qt.Orientation.Horizontal)
        splitter_main.addWidget(left_panel)
        splitter_main.addWidget(center_panel)
        splitter_main.addWidget(right_panel)
        
        splitter_main.setSizes([250, 850, 300])
        splitter_main.setCollapsible(0, False)
        splitter_main.setCollapsible(1, False)
        splitter_main.setCollapsible(2, True)
        
        main_layout.addWidget(splitter_main)
    
    def _create_left_panel(self) -> QFrame:
        """Panel izquierdo: Logo + Navegación"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Logo KAGU
        logo_label = QLabel()
        pixmap = QPixmap("interface/assets/icons/kagu_logo.png")
        pixmap = pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        layout.addSpacing(20)
        
        # Botones de navegación
        self.btn_chat = self._create_nav_button("💬 Chat", "chat")
        self.btn_commands = self._create_nav_button("⌨️ Comandos", "commands")
        self.btn_system = self._create_nav_button("🖥️ Sistema", "system")
        self.btn_settings = self._create_nav_button("⚙️ Configuración", "settings")
        
        layout.addWidget(self.btn_chat)
        layout.addWidget(self.btn_commands)
        layout.addWidget(self.btn_system)
        layout.addWidget(self.btn_settings)
        
        layout.addStretch()
        
        # Estado de conexión
        self.connection_status = QLabel("🟢 En línea")
        self.connection_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        layout.addWidget(self.connection_status)
        
        frame.setMaximumWidth(250)
        frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-right: 2px solid #333;
            }
        """)
        
        return frame
    
    def _create_center_panel(self) -> QWidget:
        """Panel central: Chat principal"""
        self.chat_widget = ChatWidget(self.orchestrator)
        self.command_panel = CommandPanel(self.orchestrator)
        
        # Panel apilado para cambiar entre vistas
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.chat_widget)
        self.stacked_widget.addWidget(self.command_panel)
        
        return self.stacked_widget
    
    def _create_right_panel(self) -> QFrame:
        """Panel derecho: Sistema + Configuración"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Monitor del sistema
        self.system_monitor = SystemMonitor(self.orchestrator)
        layout.addWidget(self.system_monitor)
        
        layout.addSpacing(20)
        
        # Panel de configuración
        self.settings_panel = SettingsPanel(self.orchestrator)
        layout.addWidget(self.settings_panel)
        
        layout.addStretch()
        
        frame.setMaximumWidth(300)
        frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-left: 2px solid #333;
            }
        """)
        
        return frame
    
    def _create_nav_button(self, text: str, view_name: str) -> QPushButton:
        """Crea un botón de navegación"""
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #ffffff;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #007bff;
            }
        """)
        
        # Conectar a cambio de vista
        if view_name == "chat":
            button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.chat_widget))
        elif view_name == "commands":
            button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.command_panel))
        
        return button
    
    def _setup_timers(self):
        """Configura timers para actualizaciones periódicas"""
        
        # Timer para actualizar estado de conexión
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self._update_connection_status)
        self.connection_timer.start(5000)  # Cada 5 segundos
        
        # Timer para actualizar monitor del sistema
        self.system_timer = QTimer()
        self.system_timer.timeout.connect(self._update_system_monitor)
        self.system_timer.start(2000)  # Cada 2 segundos
    
    def _update_connection_status(self):
        """Actualiza el estado de conexión a internet"""
        import socket
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            self.connection_status.setText("🟢 En línea")
            self.connection_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        except:
            self.connection_status.setText("🔴 Sin conexión")
            self.connection_status.setStyleSheet("color: #ff0000; font-weight: bold;")
    
    def _update_system_monitor(self):
        """Actualiza el monitor del sistema"""
        if hasattr(self, 'system_monitor'):
            self.system_monitor.update_stats()
    
    def show_notification(self, title: str, message: str, duration: int = 3000):
        """Muestra una notificación"""
        # Implementar notificación toast
        pass
    
    def closeEvent(self, event):
        """Evento al cerrar la ventana"""
        logger.info("Cerrando ventana principal")
        if hasattr(self, 'floating_avatar'):
            self.floating_avatar.show()  # Mostrar avatar flotante
        event.accept()