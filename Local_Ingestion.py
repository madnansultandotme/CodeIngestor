import os
import shutil
import sys
import subprocess
import getpass
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QMessageBox,
    QProgressBar,
    QCheckBox,
    QDialog,
    QTextEdit,
    QHBoxLayout,
    QLabel,
    QStackedWidget
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont, QIcon
import pathlib
from gitingest import ingest

class OutputDialog(QDialog):
    def __init__(self, output_text, output_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ingest Output")
        self.setGeometry(200, 200, 600, 400)
        self.output_dir = output_dir

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(output_text)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #f4f4f4;
                color: #00508e;
                border: 1px solid #cf90ff;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.text_edit)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        view_location_btn = QPushButton("View Location")
        view_location_btn.clicked.connect(self.view_location)
        view_location_btn.setStyleSheet("""
            QPushButton {
                background-color: #cf90ff;
                color: #00508e;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-family: 'Arial', sans-serif;
            }
            QPushButton:hover {
                background-color: #0062ad;
            }
        """)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #cf90ff;
                color: #00508e;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-family: 'Arial', sans-serif;
            }
            QPushButton:hover {
                background-color: #0062ad;
            }
        """)
        button_layout.addWidget(view_location_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #ffffff;")

    def view_location(self):
        if os.name == 'nt':
            subprocess.run(['explorer', os.path.normpath(self.output_dir)])
        else:
            subprocess.run(['xdg-open', self.output_dir])

class IngestGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Repository Ingestor")
        self.setGeometry(100, 100, 800, 600)

        # Set window icon for window and taskbar
        self.setWindowIcon(QIcon('icon.ico'))

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Stacked widget for screens
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Apply stylesheet for cohesive UI
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QWidget {
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #cf90ff;
                color: #00508e;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-family: 'Arial', sans-serif;
            }
            QPushButton:hover {
                background-color: #0062ad;
            }
            QCheckBox {
                color: #00508e;
                font-size: 14px;
                font-family: 'Arial', sans-serif;
            }
            QTreeWidget {
                background-color: #f4f4f4;
                color: #00508e;
                border: 1px solid #cf90ff;
                border-radius: 5px;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #0062ad;
                color: #ffffff;
            }
            QProgressBar {
                background-color: #f4f4f4;
                color: #00508e;
                border: 1px solid #cf90ff;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #cf90ff;
                border-radius: 5px;
            }
            QLabel {
                color: #00508e;
                font-size: 16px;
                font-family: 'Arial', sans-serif;
                font-weight: bold;
            }
        """)

        # Folder selection screen
        self.folder_screen = QWidget()
        self.folder_layout = QVBoxLayout(self.folder_screen)
        self.folder_layout.setSpacing(20)
        self.folder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.folder_label = QLabel("No repository selected")
        self.folder_label.setFont(QFont("Arial", 16))
        self.folder_layout.addWidget(self.folder_label)

        self.select_folder_btn = QPushButton("Select Repository")
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.select_folder_btn.setFixedWidth(200)
        self.select_folder_btn.setProperty("opacity", 0)
        self.folder_layout.addWidget(self.select_folder_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # File selection screen
        self.file_screen = QWidget()
        self.file_layout = QVBoxLayout(self.file_screen)
        self.file_layout.setSpacing(10)
        self.file_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.file_label = QLabel("Selected Repository: None")
        self.file_label.setFont(QFont("Arial", 16))
        self.file_layout.addWidget(self.file_label)

        self.select_all_chk = QCheckBox("Select All Assets")
        self.select_all_chk.setFont(QFont("Arial", 12))
        self.select_all_chk.stateChanged.connect(self.toggle_select_all)
        self.file_layout.addWidget(self.select_all_chk)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Asset", "Size (KB)", "Selected"])
        self.tree.setColumnWidth(0, 400)
        self.tree.setFont(QFont("Arial", 11))
        self.tree.itemChanged.connect(self.item_changed)
        self.file_layout.addWidget(self.tree)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setFont(QFont("Arial", 11))
        self.file_layout.addWidget(self.progress_bar)

        # Button layout for centered buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.setSpacing(10)

        self.process_btn = QPushButton("Process Assets")
        self.process_btn.clicked.connect(self.prompt_ingestion)
        self.process_btn.setFixedWidth(200)
        self.process_btn.setProperty("opacity", 0)
        button_layout.addWidget(self.process_btn)

        self.back_btn = QPushButton("Back to Repository Selection")
        self.back_btn.clicked.connect(self.show_folder_screen)
        self.back_btn.setFixedWidth(200)
        self.back_btn.setProperty("opacity", 0)
        button_layout.addWidget(self.back_btn)

        self.file_layout.addLayout(button_layout)

        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.folder_screen)
        self.stacked_widget.addWidget(self.file_screen)

        self.selected_folder = ""
        self.selected_items = []
        self.all_items = []

        # Initialize animations
        self.current_pos = 0

    def animate_buttons(self, buttons):
        for btn in buttons:
            btn.setProperty("opacity", 0)
            animation = QPropertyAnimation(btn, b"windowOpacity", self)
            animation.setDuration(500)
            animation.setStartValue(0)
            animation.setEndValue(1)
            animation.start()

    def show_folder_screen(self):
        # Slide transition: slide to the left
        self.current_pos = 0
        animation = QPropertyAnimation(self.stacked_widget, b"geometry", self)
        animation.setDuration(500)
        start_rect = self.stacked_widget.geometry()
        end_rect = QRect(self.current_pos, start_rect.y(), start_rect.width(), start_rect.height())
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        animation.finished.connect(lambda: self.stacked_widget.setCurrentWidget(self.folder_screen))
        animation.start()

        # Animate buttons
        self.animate_buttons([self.select_folder_btn])

        # Reset GUI
        self.tree.clear()
        self.all_items = []
        self.selected_items = []
        self.selected_folder = ""
        self.folder_label.setText("No repository selected")
        self.file_label.setText("Selected Repository: None")
        self.select_all_chk.setChecked(False)
        self.select_all_chk.setEnabled(False)
        self.process_btn.setEnabled(False)
        self.progress_bar.setValue(0)

    def show_file_screen(self):
        # Slide transition: slide to the right
        self.current_pos = -self.stacked_widget.width()
        animation = QPropertyAnimation(self.stacked_widget, b"geometry", self)
        animation.setDuration(500)
        start_rect = self.stacked_widget.geometry()
        end_rect = QRect(self.current_pos, start_rect.y(), start_rect.width(), start_rect.height())
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        animation.finished.connect(lambda: self.stacked_widget.setCurrentWidget(self.file_screen))
        animation.start()

        # Animate buttons
        self.animate_buttons([self.process_btn, self.back_btn])

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Repository Folder")
        if folder:
            self.selected_folder = folder
            folder_name = os.path.basename(folder)
            self.folder_label.setText(f"Selected Repository: {folder_name}")
            self.file_label.setText(f"Selected Repository: {folder_name}")
            self.populate_tree()
            self.show_file_screen()

    def populate_tree(self):
        self.tree.clear()
        self.all_items = []
        self.selected_items = []
        self.select_all_chk.setChecked(False)

        # Common directories/files to ignore
        ignore_dirs = {
            'venv', '.venv', 'env', '.env', 'node_modules',
            '__pycache__', '.git', 'build', 'dist', 'images', 'icons'
        }
        ignore_extensions = {'.pyc', '.log', '.lock', '.DS_Store'}

        for root, dirs, files in os.walk(self.selected_folder):
            dirs[:] = [d for d in dirs if d.lower() not in ignore_dirs]
            parent_item = self.get_parent_item(root)

            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                dir_size = self.get_folder_size(dir_path) / 1024
                if dir_size > 1024:
                    continue
                item = QTreeWidgetItem(parent_item, [dir_name, f"{dir_size:.2f}", ""])
                item.setCheckState(2, Qt.CheckState.Unchecked)
                item.setData(0, Qt.ItemDataRole.UserRole, dir_path)
                self.all_items.append(item)

            for file_name in files:
                if pathlib.Path(file_name).suffix in ignore_extensions:
                    continue
                file_path = os.path.join(root, file_name)
                file_size = os.path.getsize(file_path) / 1024
                if file_size > 1024:
                    continue
                item = QTreeWidgetItem(parent_item, [file_name, f"{file_size:.2f}", ""])
                item.setCheckState(2, Qt.CheckState.Unchecked)
                item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                self.all_items.append(item)

        self.select_all_chk.setEnabled(True)
        self.process_btn.setEnabled(True)

    def get_parent_item(self, root):
        if root == self.selected_folder:
            return self.tree
        relative_path = os.path.relpath(root, self.selected_folder)
        parts = relative_path.split(os.sep)
        current = self.tree
        current_path = self.selected_folder

        for part in parts:
            current_path = os.path.join(current_path, part)
            found = False
            for i in range(current.topLevelItemCount() if isinstance(current, QTreeWidget) else current.childCount()):
                item = current.topLevelItem(i) if isinstance(current, QTreeWidget) else current.child(i)
                if item.data(0, Qt.ItemDataRole.UserRole) == current_path:
                    current = item
                    found = True
                    break
            if not found:
                item = QTreeWidgetItem(current, [part, "0.00", ""])
                item.setData(0, Qt.ItemDataRole.UserRole, current_path)
                current = item
        return current

    def get_folder_size(self, folder_path):
        total_size = 0
        for dirpath, _, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def toggle_select_all(self, state):
        check_state = Qt.CheckState.Checked if state == Qt.CheckState.Checked.value else Qt.CheckState.Unchecked
        for item in self.all_items:
            item.setCheckState(2, check_state)
        self.selected_items = [item.data(0, Qt.ItemDataRole.UserRole) for item in self.all_items] if state == Qt.CheckState.Checked.value else []

    def item_changed(self, item, column):
        if column == 2:
            path = item.data(0, Qt.ItemDataRole.UserRole)
            if item.checkState(2) == Qt.CheckState.Checked:
                if path not in self.selected_items:
                    self.selected_items.append(path)
            else:
                if path in self.selected_items:
                    self.selected_items.remove(path)

    def prompt_ingestion(self):
        if not self.selected_items:
            QMessageBox.warning(self, "Warning", "No assets selected!")
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Confirm Ingestion")
        msg.setText("Do you want to ingest all selected assets or refine your selection?")
        ingest_btn = msg.addButton("Ingest Completely", QMessageBox.ButtonRole.AcceptRole)
        select_btn = msg.addButton("Select Some", QMessageBox.ButtonRole.RejectRole)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                color: #00508e;
            }
            QLabel {
                color: #00508e;
                font-family: 'Arial', sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #cf90ff;
                color: #00508e;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-family: 'Arial', sans-serif;
            }
            QPushButton:hover {
                background-color: #0062ad;
            }
        """)
        msg.exec()

        if msg.clickedButton() == ingest_btn:
            self.process_files()

    def process_files(self):
        folder_name = os.path.basename(self.selected_folder)
        username = getpass.getuser()
        copy_dir = os.path.join("C:/LocalIngest", folder_name)
        ingestion_dir = os.path.join("C:/LocalIngest", "Ingestion", f"{folder_name}_ingest_{username}")
        os.makedirs(copy_dir, exist_ok=True)
        os.makedirs(ingestion_dir, exist_ok=True)

        self.progress_bar.setMaximum(len(self.selected_items))
        for i, item_path in enumerate(self.selected_items):
            relative_path = os.path.relpath(item_path, self.selected_folder)
            dest_path = os.path.join(copy_dir, relative_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            if os.path.isfile(item_path):
                shutil.copy2(item_path, dest_path)
            else:
                shutil.copytree(item_path, dest_path, dirs_exist_ok=True)
            self.progress_bar.setValue(i + 1)

        try:
            summary, tree, content = ingest(copy_dir)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to ingest repository: {str(e)}")
            self.progress_bar.setValue(0)
            return

        output_file = os.path.join(ingestion_dir, "output_digest.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(summary + "\n\n" + tree + "\n\n" + content)

        with open(output_file, "r", encoding="utf-8") as f:
            output_text = f.read()
        dialog = OutputDialog(output_text, ingestion_dir, self)
        dialog.exec()

        try:
            shutil.rmtree(copy_dir)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to delete copied folder {copy_dir}: {str(e)}")

        success_msg = QMessageBox(self)
        success_msg.setWindowTitle("Success")
        success_msg.setText(f"Repository processed and saved to {output_file}")
        success_msg.setStyleSheet("""
            QMessageBox {
                background-color: #f4f4f4;
                color: #00508e;
            }
            QLabel {
                color: #00508e;
                font-family: 'Arial', sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #cf90ff;
                color: #00508e;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-family: 'Arial', sans-serif;
            }
            QPushButton:hover {
                background-color: #0062ad;
            }
        """)
        success_msg.exec()

        self.show_folder_screen()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IngestGUI()
    window.show()
    sys.exit(app.exec())