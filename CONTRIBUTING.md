Contributing to Code Repository Ingestor
Thank you for considering contributing to the Code Repository Ingestor! This user-friendly desktop application, built with PyQt6, helps developers manage and analyze code repositories by ingesting selected files or folders with a modern GUI featuring animations and transitions. We welcome contributions to enhance its functionality and usability. Please follow the guidelines below to ensure a smooth collaboration process.
Getting Started
Prerequisites

Python 3.8+: Ensure Python is installed on your system.
PyQt6: Required for the GUI.
gitingest: A custom module for the actual ingestion process (ensure it's available in your setup).
Git: For version control.

Setting Up the Development Environment

Fork the Repository:

Fork the repository on GitHub and clone your fork:git clone https://github.com/madnansultandotme/CodeIngestor.git
cd CodeIngestor




Install Dependencies:
pip install PyQt6 gitingest


Note: If gitingest is a local module, place it in the project directory or install it as a package.


Prepare the Icon:

Place an icon.ico file in the project directory for the taskbar/window icon. Update the path in Local_Ingestion.py if necessary.


Run the Application:
python Local_Ingestion.py



Contribution Guidelines
Code Style

Follow PEP 8 for Python code style.
Use meaningful variable and function names.
Add comments for complex logic to improve readability.
Maintain the existing color scheme (#ffffff, #cf90ff, #0062ad, #00508e, #f4f4f4) unless proposing a redesign.
Ensure compatibility with PyQt6 and the ingestion process handled by gitingest.

Making Changes

Create a Branch:

Create a new branch for your feature or bug fix:git checkout -b feature/<feature-name>

orgit checkout -b bugfix/<bug-name>




Implement Your Changes:

Make changes in the Local_Ingestion.py codebase or related files.
Test thoroughly to ensure the GUI (two-screen interface, animations, transitions), selective ingestion, and output management work as expected.


Test Your Changes:

Run the application to verify your changes:python Local_Ingestion.py


Ensure no regressions in folder/file selection, ingestion prompt, progress bar, success toast, or output dialog.
Verify animations (button fade-in, screen transitions) and the color scheme.


Commit Your Changes:

Write clear, concise commit messages:git commit -m "Add feature: <description>"




Push to Your Fork:
git push origin feature/<feature-name>



Submitting a Pull Request

Create a Pull Request:

Go to the original repository (https://github.com/madnansultandotme/CodeIngestor) and create a pull request from your branch.
Provide a detailed description of your changes, including:
What you changed and why.
Any issues your changes address (link to GitHub issues if applicable).
Screenshots or videos of UI changes (e.g., new animations or layout adjustments).




Code Review:

Maintainers will review your pull request.
Be open to feedback and make requested changes if necessary.


Merge:

Once approved, your pull request will be merged into the main branch.



Reporting Bugs

Open a GitHub issue with the label bug.
Include:
A clear description of the bug.
Steps to reproduce.
Expected behavior vs. actual behavior.
Screenshots or logs if applicable (e.g., errors during ingestion or UI glitches).



Suggesting Features

Open a GitHub issue with the label enhancement.
Describe the feature, its use case, and potential implementation ideas (e.g., adding export options or supporting additional file types).

Code of Conduct

Be respectful and inclusive in all interactions.
Follow GitHub's Community Guidelines.

Thank you for contributing to the Code Repository Ingestor!
