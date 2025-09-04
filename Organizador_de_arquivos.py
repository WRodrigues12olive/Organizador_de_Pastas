import sys
import os
import shutil
import time
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QPlainTextEdit
)
from PySide6.QtCore import QThread, QObject, Signal, Slot
from PySide6.QtGui import QFont, QIcon, QColor
import qtawesome as qta

APP_STYLESHEET = """
    QWidget {
        background-color: #2E3440;
        color: #D8DEE9;
        font-family: 'Segoe UI', 'Arial';
        font-size: 11pt;
    }
    QMainWindow {
        border-image: None;
    }
    QPushButton {
        background-color: #4C566A;
        border: 1px solid #4C566A;
        padding: 8px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #5E81AC;
    }
    QPushButton:pressed {
        background-color: #81A1C1;
    }
    QPushButton:disabled {
        background-color: #3B4252;
        color: #4C566A;
    }
    QLineEdit, QPlainTextEdit, QTableWidget {
        background-color: #3B4252;
        border: 1px solid #4C566A;
        border-radius: 4px;
        padding: 5px;
    }
    QHeaderView::section {
        background-color: #434C5E;
        padding: 4px;
        border: 1px solid #4C566A;
    }
    QLabel {
        font-weight: bold;
    }
"""

CONFIG_FILE = "organizador_config.json"


class Worker(QObject):
    log_message = Signal(str)
    finished = Signal()

    def __init__(self, source_path, rules):
        super().__init__()
        self.source_path = source_path
        self.rules = rules
        self.is_running = True

    @Slot()
    def run(self):
        self.log_message.emit(f"Iniciando monitoramento em: {self.source_path}")
        path_origem = Path(self.source_path)

        for category in self.rules.keys():
            (path_origem / category).mkdir(exist_ok=True)
        (path_origem / "Outros").mkdir(exist_ok=True)
        self.log_message.emit("Pastas de destino verificadas/criadas.")

        while self.is_running:
            try:
                files_in_folder = [f for f in path_origem.iterdir() if f.is_file()]
                for file_path in files_in_folder:
                    extension = file_path.suffix.lower()
                    destination_category = "Outros"

                    for category, extensions in self.rules.items():
                        if extension in extensions:
                            destination_category = category
                            break

                    destination_folder = path_origem / destination_category
                    destination_path = destination_folder / file_path.name

                    self.log_message.emit(f"Movendo '{file_path.name}' para '{destination_category}'...")
                    shutil.move(str(file_path), str(destination_path))

                time.sleep(5)
            except Exception as e:
                self.log_message.emit(f"ERRO: {e}")
                time.sleep(10)

        self.log_message.emit("Monitoramento parado.")
        self.finished.emit()


class FileOrganizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organizador de Arquivos Automático")
        self.setWindowIcon(qta.icon("fa5s.folder-open"))
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(APP_STYLESHEET)

        self.thread = None
        self.worker = None

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        folder_layout = QHBoxLayout()
        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setPlaceholderText("Selecione a pasta a ser organizada...")
        self.folder_path_edit.setReadOnly(True)
        folder_layout.addWidget(QLabel("Pasta a Organizar:"))
        folder_layout.addWidget(self.folder_path_edit)
        self.select_folder_btn = QPushButton(qta.icon("fa5s.folder"), " Selecionar...")
        self.select_folder_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.select_folder_btn)
        main_layout.addLayout(folder_layout)

        main_layout.addWidget(QLabel("Regras de Organização:"))
        self.rules_table = QTableWidget(0, 2)
        self.rules_table.setHorizontalHeaderLabels(
            ["Categoria (Nome da Pasta)", "Extensões (separadas por vírgula, ex: .jpg, .png)"])
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rules_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        main_layout.addWidget(self.rules_table)

        rules_btn_layout = QHBoxLayout()
        self.add_rule_btn = QPushButton(qta.icon("fa5s.plus"), " Adicionar Regra")
        self.add_rule_btn.clicked.connect(self.add_rule)
        self.remove_rule_btn = QPushButton(qta.icon("fa5s.trash-alt"), " Remover Regra Selecionada")
        self.remove_rule_btn.clicked.connect(self.remove_rule)
        rules_btn_layout.addWidget(self.add_rule_btn)
        rules_btn_layout.addWidget(self.remove_rule_btn)
        rules_btn_layout.addStretch()
        main_layout.addLayout(rules_btn_layout)

        control_layout = QHBoxLayout()
        self.start_btn = QPushButton(qta.icon("fa5s.play-circle"), " Iniciar Organização")
        self.start_btn.clicked.connect(self.start_organizing)
        self.stop_btn = QPushButton(qta.icon("fa5s.stop-circle"), " Parar Organização")
        self.stop_btn.clicked.connect(self.stop_organizing)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        main_layout.addLayout(control_layout)

        main_layout.addWidget(QLabel("Log de Atividades:"))
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        main_layout.addWidget(self.log_area)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    @Slot()
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione uma Pasta")
        if folder:
            self.folder_path_edit.setText(folder)
            self.save_settings()

    @Slot()
    def add_rule(self):
        row_count = self.rules_table.rowCount()
        self.rules_table.insertRow(row_count)

    @Slot()
    def remove_rule(self):
        current_row = self.rules_table.currentRow()
        if current_row >= 0:
            self.rules_table.removeRow(current_row)

    @Slot()
    def start_organizing(self):
        source_path = self.folder_path_edit.text()
        if not source_path or not os.path.isdir(source_path):
            self.log_message("ERRO: Por favor, selecione uma pasta válida antes de iniciar.")
            return

        rules = self.get_rules_from_table()
        if not rules:
            self.log_message("ERRO: Por favor, adicione pelo menos uma regra de organização.")
            return

        self.save_settings()

        self.set_controls_enabled(False)

        self.thread = QThread()
        self.worker = Worker(source_path, rules)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.log_message.connect(self.log_message)
        self.thread.finished.connect(lambda: self.set_controls_enabled(True))

        self.thread.start()

    @Slot()
    def stop_organizing(self):
        if self.worker:
            self.worker.is_running = False
            self.stop_btn.setEnabled(False)
            self.log_message("Sinal para parar enviado. Aguardando a finalização...")

    @Slot(str)
    def log_message(self, message):
        self.log_area.appendPlainText(message)

    def set_controls_enabled(self, enabled):
        self.start_btn.setEnabled(enabled)
        self.stop_btn.setEnabled(not enabled)
        self.select_folder_btn.setEnabled(enabled)
        self.rules_table.setEnabled(enabled)
        self.add_rule_btn.setEnabled(enabled)
        self.remove_rule_btn.setEnabled(enabled)

    def get_rules_from_table(self):
        rules = {}
        for row in range(self.rules_table.rowCount()):
            category_item = self.rules_table.item(row, 0)
            extensions_item = self.rules_table.item(row, 1)

            if category_item and extensions_item:
                category = category_item.text().strip()
                extensions_str = extensions_item.text().strip()
                if category and extensions_str:
                    extensions = [f".{ext.strip().lstrip('.')}".lower() for ext in extensions_str.split(",")]
                    rules[category] = extensions
        return rules

    def load_settings(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)

            self.folder_path_edit.setText(config.get("source_path", ""))

            rules = config.get("rules", {})
            self.rules_table.setRowCount(0)
            for category, extensions in rules.items():
                row_count = self.rules_table.rowCount()
                self.rules_table.insertRow(row_count)
                self.rules_table.setItem(row_count, 0, QTableWidgetItem(category))
                extensions_display = ", ".join([ext.lstrip('.') for ext in extensions])
                self.rules_table.setItem(row_count, 1, QTableWidgetItem(extensions_display))
            self.log_message("Configurações carregadas.")
        except FileNotFoundError:
            self.log_message("Arquivo de configuração não encontrado. Usando padrões.")
            self.populate_default_rules()
        except Exception as e:
            self.log_message(f"Erro ao carregar configurações: {e}")

    def save_settings(self):
        config = {
            "source_path": self.folder_path_edit.text(),
            "rules": self.get_rules_from_table()
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            self.log_message(f"Erro ao salvar configurações: {e}")

    def populate_default_rules(self):
        default_rules = {
            "Imagens": ".jpg, .jpeg, .png, .gif, .bmp, .svg",
            "Documentos": ".pdf, .docx, .doc, .xlsx, .xls, .pptx, .ppt, .txt",
            "Vídeos": ".mp4, .mov, .avi, .mkv",
            "Compactados": ".zip, .rar, .7z"
        }
        for category, extensions in default_rules.items():
            row_count = self.rules_table.rowCount()
            self.rules_table.insertRow(row_count)
            self.rules_table.setItem(row_count, 0, QTableWidgetItem(category))
            self.rules_table.setItem(row_count, 1, QTableWidgetItem(extensions))

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileOrganizerApp()
    window.show()
    sys.exit(app.exec())