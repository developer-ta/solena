import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
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
    QFrame,
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
        self.core_state_label = QLabel("Core: not loaded")
        self.pipeline_state_label = QLabel("Pipeline: not loaded")
        self.dialogue_state_label = QLabel("Dialogues: not imported")
        self.stage_labels: dict[str, QLabel] = {}

        self._build_ui()
        self._apply_styles()
        self._set_stage_states("import")

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setSpacing(18)
        layout.setContentsMargins(24, 24, 24, 24)

        hero = QFrame()
        hero.setObjectName("heroCard")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(24, 24, 24, 24)
        hero_layout.setSpacing(12)

        badge = QLabel("Solena · dashboard MVP")
        badge.setObjectName("badge")
        title = QLabel("A structured AI dashboard for dialogue projects")
        title.setObjectName("heroTitle")
        subtitle = QLabel(
            "Load the private core, import a dialogue folder, and preview a clean pipeline result before moving to refinement."
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName("heroSubtitle")

        hero_actions = QHBoxLayout()
        load_core_button = QPushButton("Load GPS + Pipeline")
        load_core_button.clicked.connect(self.load_core_guide)
        analyze_button = QPushButton("Analyze with Solena")
        analyze_button.setObjectName("primaryButton")
        analyze_button.clicked.connect(self.analyze_dialogues)
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset_form)
        hero_actions.addWidget(load_core_button)
        hero_actions.addWidget(analyze_button)
        hero_actions.addWidget(reset_button)
        hero_actions.addStretch()

        hero_layout.addWidget(badge)
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        hero_layout.addLayout(hero_actions)

        metrics = QHBoxLayout()
        metrics.setSpacing(14)
        metrics.addWidget(self._metric_card("Core", self.core_state_label))
        metrics.addWidget(self._metric_card("Pipeline", self.pipeline_state_label))
        metrics.addWidget(self._metric_card("Dialogues", self.dialogue_state_label))

        stages = QFrame()
        stages.setObjectName("stageStrip")
        stages_layout = QHBoxLayout(stages)
        stages_layout.setContentsMargins(18, 16, 18, 16)
        stages_layout.setSpacing(12)
        stages_layout.addWidget(self._stage_chip("import", "01 Import"))
        stages_layout.addWidget(self._stage_chip("refine", "02 Refine"))
        stages_layout.addWidget(self._stage_chip("lab", "03 Lab"))
        stages_layout.addWidget(self._stage_chip("init", "04 Go / No-Go"))
        stages_layout.addStretch()

        layout.addWidget(hero)
        layout.addLayout(metrics)
        layout.addWidget(stages)

        content = QGridLayout()
        content.setSpacing(18)

        left_column = self._build_source_column()
        right_column = self._build_output_column()

        content.addWidget(left_column, 0, 0)
        content.addWidget(right_column, 0, 1)
        content.setColumnStretch(0, 1)
        content.setColumnStretch(1, 1)

        layout.addLayout(content)

        footer = QLabel("Solena desktop MVP · simple first version, richer features later.")
        footer.setObjectName("footerNote")
        layout.addWidget(footer)

        self.summary_box.setMinimumHeight(170)
        self.output_box.setMinimumHeight(260)
        self.summary_box.setReadOnly(True)
        self.output_box.setReadOnly(True)
        self.status_label.setWordWrap(True)

    def _build_source_column(self) -> QFrame:
        column = QFrame()
        column.setObjectName("panelCard")
        layout = QVBoxLayout(column)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(16)

        heading = QLabel("Source preparation")
        heading.setObjectName("sectionLabel")
        title = QLabel("Load the private core and the dialogue folder.")
        title.setObjectName("sectionTitle")
        title.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(title)

        core_group = QGroupBox("Private core")
        core_layout = QFormLayout(core_group)
        core_row = QHBoxLayout()
        core_row.addWidget(self.core_path_input)
        core_browse = QPushButton("Browse")
        core_browse.clicked.connect(self.browse_core)
        core_row.addWidget(core_browse)
        core_layout.addRow("Core folder", self._wrap(core_row))
        core_layout.addRow("GPS", self.gps_status_label)
        core_layout.addRow("Pipeline", self.pipeline_status_label)
        layout.addWidget(core_group)

        dialogue_group = QGroupBox("Dialogue import")
        dialogue_layout = QFormLayout(dialogue_group)
        dialogue_row = QHBoxLayout()
        dialogue_row.addWidget(self.dialogue_path_input)
        dialogue_browse = QPushButton("Browse")
        dialogue_browse.clicked.connect(self.browse_dialogue_folder)
        dialogue_row.addWidget(dialogue_browse)
        dialogue_layout.addRow("Dialogue folder", self._wrap(dialogue_row))
        dialogue_layout.addRow("Selected", self.selected_files_label)
        dialogue_layout.addRow("File count", self.file_count_label)
        layout.addWidget(dialogue_group)

        action_row = QHBoxLayout()
        analyze_button = QPushButton("Analyze with Solena")
        analyze_button.setObjectName("primaryButton")
        analyze_button.clicked.connect(self.analyze_dialogues)
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset_form)
        action_row.addWidget(analyze_button)
        action_row.addWidget(reset_button)
        action_row.addStretch()
        layout.addLayout(action_row)

        return column

    def _build_output_column(self) -> QFrame:
        column = QFrame()
        column.setObjectName("panelCard")
        layout = QVBoxLayout(column)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(16)

        heading = QLabel("Pipeline preview")
        heading.setObjectName("sectionLabel")
        title = QLabel("Read the current status and the structured JSON result.")
        title.setObjectName("sectionTitle")
        title.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(title)

        self.status_label.setObjectName("statusText")
        layout.addWidget(self.status_label)

        summary_label = QLabel("Summary")
        summary_label.setObjectName("miniLabel")
        layout.addWidget(summary_label)
        layout.addWidget(self.summary_box)

        output_label = QLabel("JSON preview")
        output_label.setObjectName("miniLabel")
        layout.addWidget(output_label)
        layout.addWidget(self.output_box)

        return column

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                color: #edf4ff;
                font-family: "Segoe UI", "Inter", sans-serif;
                font-size: 13px;
            }
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #07111f, stop:1 #050b15);
            }
            QFrame#heroCard, QFrame#panelCard, QFrame#stageStrip {
                background: rgba(11, 20, 36, 0.82);
                border: 1px solid rgba(125, 211, 252, 0.14);
                border-radius: 22px;
            }
            QLabel#badge {
                color: #7dd3fc;
                font-weight: 700;
                letter-spacing: 0.10em;
                text-transform: uppercase;
            }
            QLabel#heroTitle {
                font-size: 30px;
                font-weight: 800;
                letter-spacing: -0.04em;
            }
            QLabel#heroSubtitle {
                color: #a9b8d0;
                font-size: 14px;
                line-height: 1.6;
            }
            QLabel#footerNote {
                color: #8ea1bf;
                padding-left: 4px;
            }
            QLabel#sectionLabel {
                color: #7dd3fc;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.18em;
            }
            QLabel#sectionTitle {
                font-size: 20px;
                font-weight: 700;
            }
            QLabel#miniLabel {
                color: #9fb0c9;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.14em;
                margin-top: 4px;
            }
            QLabel#statusText {
                color: #d9e7ff;
                padding: 12px 14px;
                border-radius: 14px;
                background: rgba(4, 12, 24, 0.82);
                border: 1px solid rgba(125, 211, 252, 0.10);
            }
            QGroupBox {
                margin-top: 10px;
                border: 1px solid rgba(125, 211, 252, 0.10);
                border-radius: 18px;
                background: rgba(8, 15, 28, 0.62);
                padding-top: 16px;
                font-weight: 700;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 8px;
                color: #edf4ff;
            }
            QLineEdit, QPlainTextEdit {
                background: rgba(4, 12, 24, 0.88);
                border: 1px solid rgba(125, 211, 252, 0.12);
                border-radius: 14px;
                padding: 10px 12px;
                color: #edf4ff;
                selection-background-color: #38bdf8;
            }
            QPlainTextEdit {
                font-family: "Cascadia Mono", "Consolas", monospace;
                line-height: 1.5;
            }
            QPushButton {
                min-height: 42px;
                padding: 0 16px;
                border-radius: 14px;
                border: 1px solid rgba(125, 211, 252, 0.16);
                background: rgba(9, 16, 29, 0.92);
                color: #edf4ff;
                font-weight: 700;
            }
            QPushButton:hover {
                background: rgba(15, 29, 50, 0.96);
                border-color: rgba(125, 211, 252, 0.32);
            }
            QPushButton#primaryButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7dd3fc, stop:1 #38bdf8);
                color: #06111d;
                border: none;
            }
            QPushButton#primaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9ae1ff, stop:1 #60c8ff);
            }
            """
        )

    def _metric_card(self, title: str, value: QLabel) -> QFrame:
        card = QFrame()
        card.setObjectName("panelCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(8)

        label = QLabel(title)
        label.setObjectName("miniLabel")
        value.setObjectName("metricValue")
        value.setWordWrap(True)
        value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        card_layout.addWidget(label)
        card_layout.addWidget(value)
        return card

    def _stage_chip(self, key: str, text: str) -> QLabel:
        chip = QLabel(text)
        chip.setObjectName(f"stage_{key}")
        chip.setProperty("role", "stageChip")
        chip.setContentsMargins(12, 8, 12, 8)
        self.stage_labels[key] = chip
        return chip

    def _set_stage_states(self, active: str) -> None:
        for key, label in self.stage_labels.items():
            is_active = key == active
            label.setStyleSheet(
                """
                QLabel {
                    padding: 10px 14px;
                    border-radius: 999px;
                    border: 1px solid %s;
                    background: %s;
                    color: %s;
                    font-weight: 700;
                }
                """
                % (
                    "rgba(125, 211, 252, 0.36)" if is_active else "rgba(125, 211, 252, 0.12)",
                    "rgba(56, 189, 248, 0.20)" if is_active else "rgba(4, 12, 24, 0.75)",
                    "#f7fbff" if is_active else "#a9b8d0",
                )
            )

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
        self.core_state_label.setText("Core: loaded" if gps_loaded and pipeline_loaded else "Core: partial")
        self.pipeline_state_label.setText(
            f"Pipeline: {pipeline_data.get('mode', 'unknown')}" if pipeline_loaded else "Pipeline: not loaded"
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
        self._set_stage_states("refine" if gps_loaded and pipeline_loaded else "import")

    def _refresh_folder_preview(self, folder: Path) -> None:
        if not folder.exists():
            self.selected_files_label.setText("Folder not found")
            self.file_count_label.setText("0 files")
            self.dialogue_state_label.setText("Dialogues: missing")
            return

        files = collect_dialogue_files(folder)
        self.selected_files_label.setText(folder.as_posix())
        self.file_count_label.setText(f"{len(files)} files")
        self.dialogue_state_label.setText(f"Dialogues: {len(files)} files")
        preview = "\n".join(files[:20]) if files else "Folder is empty."
        self.summary_box.setPlainText(preview)
        self._set_stage_states("import")

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
        self.core_state_label.setText("Core: loaded")
        self.pipeline_state_label.setText(f"Pipeline: {pipeline_data.get('mode', 'unknown')}")
        self.dialogue_state_label.setText(f"Dialogues: {file_count} files")
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
        self._set_stage_states("lab" if has_dialogues else "import")

    def reset_form(self) -> None:
        self.dialogue_path_input.clear()
        self.status_label.setText("Ready. Load the private core and import a dialogue folder.")
        self.file_count_label.setText("0 files")
        self.selected_files_label.setText("No folder selected")
        self.gps_status_label.setText("GPS not loaded")
        self.pipeline_status_label.setText("Pipeline guide not loaded")
        self.core_state_label.setText("Core: not loaded")
        self.pipeline_state_label.setText("Pipeline: not loaded")
        self.dialogue_state_label.setText("Dialogues: not imported")
        self.summary_box.clear()
        self.output_box.clear()
        self._set_stage_states("import")


def main() -> None:
    app = QApplication([])
    window = SolenaDesktop()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
