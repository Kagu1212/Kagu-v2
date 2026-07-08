# interface/widgets/chat_widget.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QScrollArea, QListWidget,
    QListWidgetItem, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QIcon
import logging
from typing import Optional
import asyncio

from core.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

class ChatWidget(QWidget):
    """Widget principal de chat"""
    
    # Señales
    send_message = pyqtSignal(str)
    send_image = pyqtSignal(str)
    
    def __init__(self, orchestrator: Orchestrator):
        super().__init__()
        self.orchestrator = orchestrator
        
        self._init_ui()
    
    def _init_ui(self):
        """Inicializa la interfaz del chat"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ===== ÁREA DE MENSAJES =====
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #0f0f0f;
                border: none;
            }
        """)
        
        # Widget para contenedor de mensajes
        messages_container = QWidget()
        self.messages_layout = QVBoxLayout(messages_container)
        self.messages_layout.addStretch()
        
        self.scroll_area.setWidget(messages_container)
        layout.addWidget(self.scroll_area)
        
        # ===== ÁREA DE ENTRADA =====
        input_layout = QHBoxLayout()
        
        # Input de texto
        self.input_text = QTextEdit()
        self.input_text.setMaximumHeight(100)
        self.input_text.setPlaceholderText("Escribe tu mensaje aquí...")
        self.input_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #333;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
            QTextEdit:focus {
                border: 2px solid #007bff;
            }
        """)
        input_layout.addWidget(self.input_text)
        
        # Botón para adjuntar imagen
        btn_attach = QPushButton("📎")
        btn_attach.setMaximumWidth(40)
        btn_attach.clicked.connect(self._attach_image)
        btn_attach.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 2px solid #333;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
        """)
        input_layout.addWidget(btn_attach)
        
        # Botón enviar
        btn_send = QPushButton("Enviar")
        btn_send.setMaximumWidth(100)
        btn_send.clicked.connect(self._send_message)
        btn_send.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        input_layout.addWidget(btn_send)
        
        layout.addLayout(input_layout)
    
    def add_user_message(self, text: str, image_path: Optional[str] = None):
        """Añade un mensaje del usuario al chat"""
        message_widget = self._create_message_bubble(
            text=text,
            is_user=True,
            image_path=image_path
        )
        
        # Insertar antes del stretch
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, message_widget)
        
        # Scroll al final
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )
    
    def add_assistant_message(self, text: str, audio_path: Optional[str] = None):
        """Añade un mensaje del asistente"""
        message_widget = self._create_message_bubble(
            text=text,
            is_user=False,
            audio_path=audio_path
        )
        
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, message_widget)
        
        # Scroll al final
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )
    
    def _create_message_bubble(self,
                              text: str,
                              is_user: bool = True,
                              image_path: Optional[str] = None,
                              audio_path: Optional[str] = None) -> QWidget:
        """Crea una burbuja de mensaje"""
        bubble = QWidget()
        layout = QHBoxLayout(bubble)
        
        # Crear label con el mensaje
        message_label = QLabel(text)
        message_label.setWordWrap(True)
        message_label.setMaximumWidth(600)
        
        if is_user:
            message_label.setStyleSheet("""
                QLabel {
                    background-color: #007bff;
                    color: #ffffff;
                    padding: 8px 12px;
                    border-radius: 8px;
                }
            """)
            layout.addStretch()
            layout.addWidget(message_label)
        else:
            message_label.setStyleSheet("""
                QLabel {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    padding: 8px 12px;
                    border-radius: 8px;
                }
            """)
            layout.addWidget(message_label)
            layout.addStretch()
        
        # Agregar imagen si existe
        if image_path:
            img_label = QLabel()
            pixmap = QPixmap(image_path).scaledToWidth(300)
            img_label.setPixmap(pixmap)
            layout.addWidget(img_label)
        
        return bubble
    
    def _send_message(self):
        """Envía un mensaje"""
        text = self.input_text.toPlainText().strip()
        
        if not text:
            return
        
        # Agregar mensaje del usuario
        self.add_user_message(text)
        self.input_text.clear()
        
        # Procesar en segundo plano
        self._process_message_async(text)
    
    async def _process_message_async(self, text: str):
        """Procesa el mensaje de forma asincrónica"""
        try:
            logger.info(f"Procesando mensaje: {text}")
            
            # Procesar con orquestador
            response = await self.orchestrator.process_input({
                "type": "text",
                "text": text
            })
            
            logger.debug(f"Respuesta: {response}")
            
            # Mostrar respuesta
            self.add_assistant_message(response.get("text", "Error procesando mensaje"))
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            self.add_assistant_message(f"Error: {str(e)}")
    
    def _attach_image(self):
        """Adjunta una imagen al chat"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar imagen",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp);;Todos los archivos (*)"
        )
        
        if file_path:
            # Agregar al chat
            text = self.input_text.toPlainText()
            self.add_user_message(text or "[Imagen adjunta]", image_path=file_path)
            
            # Procesar
            self._process_message_async_with_image(text, file_path)
    
    async def _process_message_async_with_image(self, text: str, image_path: str):
        """Procesa un mensaje con imagen"""
        try:
            response = await self.orchestrator.process_input({
                "type": "text_with_image",
                "text": text,
                "image_path": image_path
            })
            
            self.add_assistant_message(response.get("text", "Error procesando imagen"))
            
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            self.add_assistant_message(f"Error: {str(e)}")