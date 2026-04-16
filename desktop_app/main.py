import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QGroupBox,
)


APP_TITLE = "Solena Desktop MVP"
DEFAULT_CORE_DIR = Path(__file__).resolve().parents[1] / "private-core"


@dataclass
class LoadedGuide:
    gps_path: str = ""
    pipeline_path: str = ""
    gps_loaded: bool = False
    pipeline_loaded: bool = False
    gps_project: str = "unknown"
    pipeline_mode: str = "unknown"


def read_json_file(path: Path) -> tuple[dict | None, str]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle), ""
    except FileNotFoundError:
        return None, f"Missing file: {path}"
    except json.JSONDecodeError as exc:
        return None, f"Invalid JSON in {path}: {exc}"
    except OSError as exc:
        return None, f"Cannot read {path}: {exc}"


def count_files(folder: Path) -> int:
    total = 0
    for _, _, files in os.walk(folder):
        total += len(files)
    return total


def collect_dialogue_files(folder: Path) -> list[str]:
    files: list[str] = []
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            rel_path = Path(root, filename).relative_to(folder).as_posix()
            files.append(rel_path)
    return sorted(files)


class SolenaDesktop(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1180, 820)

        self.core_path_input = QLineEdit(str(DEFAULT_CORE_DIR))
        self.dialogue_path_input = QLineEdit("")
        self.status_label = QLabel("Ready. Load the private core and import a dialogue folder.")
        self.summary_box = QPlainTextEdit()
        self.summary_box.setReadOnly(True)
        self.output_box = QPlainTextEdit()
        self.output_box.setReadOnly(True)
        self.file_count_label = QLabel("0 files")
        self.gps_status_label = QLabel("GPS not loaded")
        self.pipeline_status_label = QLabel("Pipeline guide not loaded")
        self.selected_files_label = QLabel("No folder selected")

        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setSpacing(16)

        title = QLabel("Solena Desktop MVP")
        title.setStyleSheet("font-size: 28px; font-weight: 800;")
        subtitle = QLabel(
            "Import a dialogue folder, load the GPS and pipeline guide, then preview a structured analysis."
        )
        subtitle.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        core_group = QGroupBox("Private Core")
        core_layout = QFormLayout(core_group)
        core_row = QHBoxLayout()
        core_row.addWidget(self.core_path_input)
        core_browse = QPushButton("Browse")
        core_browse.clicked.connect(self.browse_core)
        core_row.addWidget(core_browse)
        core_layout.addRow("Core folder", self._wrap(core_row))

        load_core_button = QPushButton("Load GPS + Pipeline")
        load_core_button.clicked.connect(self.load_core_guide)
        core_layout.addRow(load_core_button)
        core_layout.addRow("GPS", self.gps_status_label)
        core_layout.addRow("Pipeline", self.pipeline_status_label)

        layout.addWidget(core_group)

        dialogue_group = QGroupBox("Dialogue Import")
        dialogue_layout = QFormLayout(dialogue_group)
        dialogue_row = QHBoxLayout()
        dialogue_row.addWidget(self.dialogue_path_input)
        dialogue_browse = QPushButton("Browse")
        dialogue_browse.clicked.connect(self.browse_dialogue_folder)
        dialogue_row.addWidget(dialogue_browse)
        dialogue_layout.addRow("Dialogue folder", self._wrap(dialogue_row))

        analyze_button = QPushButton("Analyze with Solena")
        analyze_button.clicked.connect(self.analyze_dialogues)
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset_form)
        button_row = QHBoxLayout()
        button_row.addWidget(analyze_button)
        button_row.addWidget(reset_button)
        dialogue_layout.addRow(button_row)
        dialogue_layout.addRow("Selected", self.selected_files_label)
        dialogue_layout.addRow("File count", self.file_count_label)

        layout.addWidget(dialogue_group)

        output_group = QGroupBox("Analysis Output")
        output_layout = QVBoxLayout(output_group)
        output_layout.addWidget(self.status_label)
        output_layout.addWidget(QLabel("Summary"))
        output_layout.addWidget(self.summary_box)
        output_layout.addWidget(QLabel("JSON Preview"))
        output_layout.addWidget(self.output_box)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(output_group)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        self.summary_box.setMinimumHeight(140)
        self.output_box.setMinimumHeight(240)

    def _wrap(self, row: QHBoxLayout) -> QWidget:
        widget = QWidget()
        widget.setLayout(row)
        return widget

    def browse_core(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Solena Core Folder", self.core_path_input.text())
        if folder:
            self.core_path_input.setText(folder)

    def browse_dialogue_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Dialogue Folder")
        if folder:
            self.dialogue_path_input.setText(folder)
            self._refresh_folder_preview(Path(folder))

    def load_core_guide(self) -> None:
        core_dir = Path(self.core_path_input.text()).expanduser()
        gps_data, gps_error = read_json_file(core_dir / "project_gps.json")
        pipeline_data, pipeline_error = read_json_file(core_dir / "pipeline_guide.json")

        gps_loaded = gps_data is not None
        pipeline_loaded = pipeline_data is not None

        self.gps_status_label.setText(
            f"Loaded: {gps_data.get('project', 'unknown')}" if gps_loaded else f"Not loaded: {gps_error}"
        )
        self.pipeline_status_label.setText(
            f"Loaded: {pipeline_data.get('mode', 'unknown')}" if pipeline_loaded else f"Not loaded: {pipeline_error}"
        )

        self.status_label.setText("Core guide loaded." if gps_loaded and pipeline_loaded else "Core guide partially loaded.")
        guide = LoadedGuide(
            gps_path=str(core_dir / "project_gps.json"),
            pipeline_path=str(core_dir / "pipeline_guide.json"),
            gps_loaded=gps_loaded,
            pipeline_loaded=pipeline_loaded,
            gps_project=(gps_data or {}).get("project", "unknown"),
            pipeline_mode=(pipeline_data or {}).get("mode", "unknown"),
        )

        self.summary_box.setPlainText(
            "\n".join(
                [
                    f"Project: {guide.gps_project}",
                    f"Pipeline mode: {guide.pipeline_mode}",
                    f"GPS loaded: {guide.gps_loaded}",
                    f"Pipeline loaded: {guide.pipeline_loaded}",
                ]
            )
        )
        self.output_box.setPlainText(json.dumps(asdict(guide), ensure_ascii=False, indent=2))

    def _refresh_folder_preview(self, folder: Path) -> None:
        if not folder.exists():
            self.selected_files_label.setText("Folder not found")
            self.file_count_label.setText("0 files")
            return

        files = collect_dialogue_files(folder)
        self.selected_files_label.setText(folder.as_posix())
        self.file_count_label.setText(f"{len(files)} files")
        preview = "\n".join(files[:20]) if files else "Folder is empty."
        self.summary_box.setPlainText(preview)

    def analyze_dialogues(self) -> None:
        core_dir = Path(self.core_path_input.text()).expanduser()
        dialogue_dir = Path(self.dialogue_path_input.text()).expanduser()

        gps_data, gps_error = read_json_file(core_dir / "project_gps.json")
        pipeline_data, pipeline_error = read_json_file(core_dir / "pipeline_guide.json")

        if gps_data is None or pipeline_data is None:
            QMessageBox.warning(
                self,
                "Solena",
                "Load the private core GPS and pipeline guide before running the analysis.",
            )
            self.status_label.setText("Analysis blocked: core guide missing.")
            self.output_box.setPlainText(
                json.dumps(
                    {
                        "status": "blocked",
                        "reason": "missing_core_guide",
                        "gps_error": gps_error,
                        "pipeline_error": pipeline_error,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return

        if not dialogue_dir.exists():
            QMessageBox.warning(self, "Solena", "Select a valid dialogue folder first.")
            self.status_label.setText("Analysis blocked: dialogue folder missing.")
            return

        files = collect_dialogue_files(dialogue_dir)
        file_count = len(files)
        risk_first = pipeline_data.get("mode") == "risk_first_pipeline"
        has_dialogues = file_count > 0

        result = {
            "project": gps_data.get("project", "unknown"),
            "core_mode": pipeline_data.get("mode", "unknown"),
            "dialogue_folder": dialogue_dir.as_posix(),
            "file_count": file_count,
            "risk_first": risk_first,
            "loaded_guide": {
                "gps": True,
                "pipeline": True,
            },
            "summary": (
                "Dialogues detected and ready for refinement."
                if has_dialogues
                else "No dialogues found in the selected folder."
            ),
            "next_step": (
                "Refine dialogues using prompt_1_refinement.json"
                if has_dialogues
                else "Import a folder of raw dialogue files."
            ),
            "phase": (
                "refinement"
                if has_dialogues
                else "import"
            ),
            "files_preview": files[:25],
            "go_no_go": "go" if has_dialogues else "no_go",
        }

        self.status_label.setText(
            "Analysis complete: ready for refinement." if has_dialogues else "Analysis complete: import required."
        )
        self.summary_box.setPlainText(
            "\n".join(
                [
                    f"Project: {result['project']}",
                    f"Files detected: {file_count}",
                    f"Phase: {result['phase']}",
                    f"Next step: {result['next_step']}",
                    f"Decision: {result['go_no_go']}",
                ]
            )
        )
        self.output_box.setPlainText(json.dumps(result, ensure_ascii=False, indent=2))

    def reset_form(self) -> None:
        self.dialogue_path_input.clear()
        self.status_label.setText("Ready. Load the private core and import a dialogue folder.")
        self.file_count_label.setText("0 files")
        self.selected_files_label.setText("No folder selected")
        self.gps_status_label.setText("GPS not loaded")
        self.pipeline_status_label.setText("Pipeline guide not loaded")
        self.summary_box.clear()
        self.output_box.clear()


def main() -> None:
    app = QApplication([])
    window = SolenaDesktop()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
