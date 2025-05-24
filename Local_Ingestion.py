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
    QLabel
)
from PyQt6.QtCore import Qt
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
                background-color: #2E2E2E;
                color: #E0E0E0;
                border: 1px solid #4A4A4A;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.text_edit)

        # Button layout
        button_layout = QHBoxLayout()
        view_location_btn = QPushButton("View Location")
        view_location_btn.clicked.connect(self.view_location)
        view_location_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: #E0E0E0;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-family: 'Arial', sans-serif;
            }
            QPushButton:hover {
                background-color: #27632A;
            }
        """)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: #E0E0E0;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-family: 'Arial', sans-serif;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
        """)
        button_layout.addWidget(view_location_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #212121;")

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

        # Set window icon (replace 'icon.png' with your icon file path)
        self.setWindowIcon(QIcon('icon.png'))

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Apply stylesheet for cohesive UI
        self.setStyleSheet("""
            QMainWindow {
                background-color: #212121;
            }
            QPushButton {
                background-color: #0288D1;
                color: #E0E0E0;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-family: 'Arial', sans-serif;
            }
            QPushButton:hover {
                background-color: #0277BD;
            }
            QCheckBox {
                color: #E0E0E0;
                font-size: 14px;
                font-family: 'Arial', sans-serif;
            }
            QTreeWidget {
                background-color: #2E2E2E;
                color: #E0E0E0;
                border: 1px solid #4A4A4A;
                border-radius: 5px;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #0288D1;
            }
            QProgressBar {
                background-color: #2E2E2E;
                color: #E0E0E0;
                border: 1px solid #4A4A4A;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2E7D32;
                border-radius: 5px;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 16px;
                font-family: 'Arial', sans-serif;
                font-weight: bold;
            }
        """)

        # Label to display selected folder name
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setFont(QFont("Arial", 16))
        self.layout.addWidget(self.folder_label)

        # Buttons
        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_folder_btn)

        # Checkbox for selecting all files
        self.select_all_chk = QCheckBox("Select All")
        self.select_all_chk.setFont(QFont("Arial", 12))
        self.select_all_chk.stateChanged.connect(self.toggle_select_all)
        self.layout.addWidget(self.select_all_chk)

        # Tree widget to display files
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File/Folder", "Size (KB)", "Selected"])
        self.tree.setColumnWidth(0, 400)
        self.tree.setFont(QFont("Arial", 11))
        self.tree.itemChanged.connect(self.item_changed)
        self.layout.addWidget(self.tree)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setFont(QFont("Arial", 11))
        self.layout.addWidget(self.progress_bar)

        # Process button
        self.process_btn = QPushButton("Process and Ingest")
        self.process_btn.clicked.connect(self.process_files)
        self.layout.addWidget(self.process_btn)

        self.selected_folder = ""
        self.selected_items = []
        self.all_items = []

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Repository Folder")
        if folder:
            self.selected_folder = folder
            folder_name = os.path.basename(folder)
            self.folder_label.setText(f"Selected Repository: {folder_name}")
            self.populate_tree()

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

        # Walk through directory
        for root, dirs, files in os.walk(self.selected_folder):
            # Filter out ignored directories (case-insensitive)
            dirs[:] = [d for d in dirs if d.lower() not in ignore_dirs]
            parent_item = self.get_parent_item(root)

            # Add directories
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                dir_size = self.get_folder_size(dir_path) / 1024  # Convert to KB
                if dir_size > 1024:  # Skip folders > 1MB
                    continue
                item = QTreeWidgetItem(parent_item, [dir_name, f"{dir_size:.2f}", ""])
                item.setCheckState(2, Qt.CheckState.Unchecked)
                item.setData(0, Qt.ItemDataRole.UserRole, dir_path)
                self.all_items.append(item)

            # Add files
            for file_name in files:
                if pathlib.Path(file_name).suffix in ignore_extensions:
                    continue
                file_path = os.path.join(root, file_name)
                file_size = os.path.getsize(file_path) / 1024  # Convert to KB
                if file_size > 1024:  # Skip files > 1MB
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
            # Check existing items at the current level
            for i in range(current.topLevelItemCount() if isinstance(current, QTreeWidget) else current.childCount()):
                item = current.topLevelItem(i) if isinstance(current, QTreeWidget) else current.child(i)
                if item.data(0, Qt.ItemDataRole.UserRole) == current_path:
                    current = item
                    found = True
                    break
            if not found:
                # Create a new item if the directory doesn't exist in the tree
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

    def process_files(self):
        if not self.selected_items:
            QMessageBox.warning(self, "Warning", "No files or folders selected!")
            return

        # Create output directory named after the selected folder
        folder_name = os.path.basename(self.selected_folder)
        username = getpass.getuser()
        copy_dir = os.path.join("C:/LocalIngest", folder_name)
        ingestion_dir = os.path.join("C:/LocalIngest", "Ingestion", f"{folder_name}_ingest_{username}")
        os.makedirs(copy_dir, exist_ok=True)
        os.makedirs(ingestion_dir, exist_ok=True)

        # Copy selected files/folders
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

        # Process files using gitingest
        try:
            summary, tree, content = ingest(copy_dir)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to ingest directory: {str(e)}")
            self.progress_bar.setValue(0)
            return

        # Save to output file in Ingestion directory
        output_file = os.path.join(ingestion_dir, "output_digest.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(summary + "\n\n" + tree + "\n\n" + content)

        # Show output in modal dialog
        with open(output_file, "r", encoding="utf-8") as f:
            output_text = f.read()
        dialog = OutputDialog(output_text, ingestion_dir, self)
        dialog.exec()

        # Clean up the copied folder
        try:
            shutil.rmtree(copy_dir)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to delete copied folder {copy_dir}: {str(e)}")

        # Reset GUI for next ingestion
        self.tree.clear()
        self.all_items = []
        self.selected_items = []
        self.selected_folder = ""
        self.folder_label.setText("No folder selected")
        self.select_all_chk.setChecked(False)
        self.select_all_chk.setEnabled(False)
        self.process_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        QMessageBox.information(self, "Success", f"Files processed and saved to {output_file}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IngestGUI()
    window.show()
    sys.exit(app.exec())