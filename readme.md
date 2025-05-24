Code Repository Ingestor
A user-friendly desktop application built with PyQt6 to ingest code repositories, process files, and generate structured output. This tool helps developers manage and analyze repositories by selecting specific files or folders to ingest, with a modern GUI featuring animations and transitions.
Features

Two-Screen Interface: Separate screens for repository selection and asset (file/folder) selection.
Selective Ingestion: Choose to ingest all selected assets or refine your selection.
Visual Feedback: Progress bar, success toast, and output dialog for clear feedback.
Modern Design: Clean UI with a white theme (#ffffff), vibrant purple buttons (#cf90ff), and dark blue text (#00508e).
Animations: Button fade-in effects and sliding screen transitions for a smooth experience.
File Exclusions: Automatically skips venv, node_modules, images, icons, and files/folders > 1MB.
Output Management: Saves output to C:/LocalIngest/Ingestion/<folder_name>_ingest_<username> and deletes temporary folders.

Screenshots
(Add screenshots of the application here, e.g., folder selection screen, file selection screen, and output dialog.)
Installation
Prerequisites

Python 3.8+: Ensure Python is installed on your system.
PyQt6: Required for the GUI.
gitingest:For Actual Ingestion Process

Steps

Clone the Repository:
git clone https://github.com/madnansultandotme/CodeIngestor.git
cd CodeIngestor


Install Dependencies:
pip install PyQt6 gitingest

Note: If gitingest is a local module, place it in the project directory or install it as a package.

Prepare the Icon:

Place a icon.ico file in the project directory for the taskbar/window icon. Update the path in code_ingest_gui.py if necessary.


Run the Application:
python Local_Ingestion.py



Building an Executable
To distribute the application as a standalone executable:

Install PyInstaller:pip install pyinstaller


Build the Executable:pyinstaller --onefile --windowed --icon=icon.ico --name=CodeIngestor Local_Ingestion.py


If gitingest is a local module, include it:pyinstaller --onefile --windowed --icon=icon.ico --name=CodeIngestor Local_Ingestion.py


Use ; for Windows, : for Unix.




Locate the Executable:
Find CodeIngestor.exe in the dist folder.
Ensure C:/LocalIngest has write permissions on the target system.



Usage

Launch the Application:

Run python Local_Ingestion.py or the executable.
The window displays the folder selection screen with a white background and centered "Select Repository" button.


Select a Repository:

Click "Select Repository" to choose a folder (e.g., D:/A2FOD/a2fod-desktop).
The screen slides to the file selection screen.


Select Assets:

View files/folders in the tree widget (excludes venv, images, etc., and > 1MB).
Use "Select All Assets" to check/uncheck all, or select individually.
Click "Process Assets" to proceed or "Back to Repository Selection" to return.


Confirm Ingestion:

A prompt asks: "Do you want to ingest all selected assets or refine your selection?"
Choose "Ingest Completely" to process or "Select Some" to return to selection.


View Output:

Files are copied to C:/LocalIngest/<folder_name>, processed, and saved to C:/LocalIngest/Ingestion/<folder_name>_ingest_<username>/output_digest.txt.
An output dialog (white background) displays the result with "View Location" and "Close" options.
A success toast confirms completion, and the GUI resets to the folder selection screen.



Contributing
See CONTRIBUTING.md for guidelines on how to contribute to this project.
License
This project is licensed under the MIT License. See the LICENSE file for details.
