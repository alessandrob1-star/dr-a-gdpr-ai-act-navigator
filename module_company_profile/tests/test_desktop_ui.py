from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_desktop_ui_reuses_shared_agents_and_schema():
    desktop = (ROOT / "module_company_profile" / "desktop_app.py").read_text(encoding="utf-8")
    schema = (ROOT / "module_company_profile" / "dashboard" / "questionnaire_schema.py").read_text(
        encoding="utf-8"
    )

    assert "from PySide6.QtWidgets import" in desktop
    assert "evaluate_payload" in desktop
    assert "generate_grounded_reply" in desktop
    assert "save_profile_snapshot" in desktop
    assert "build_pdf_report" in desktop
    assert "load_report_locale" in desktop
    assert "localize_result" in desktop
    assert "self.language_select = QComboBox()" in desktop
    assert "self.language_flag = QLabel()" in desktop
    assert "LANGUAGE_FLAG_CODES" in desktop
    assert "QUESTIONNAIRE_SCHEMA" in desktop
    assert "company_gdpr_ai_act_initial_assessment" in schema
    assert "EXCLUSIVE_CHECKBOX_VALUES" in schema


def test_desktop_ui_loads_all_local_dashboard_dictionaries():
    locales_dir = ROOT / "module_company_profile" / "dashboard" / "locales"
    desktop = (ROOT / "module_company_profile" / "desktop_app.py").read_text(encoding="utf-8")

    assert len(list(locales_dir.glob("*.json"))) == 25
    assert 'LOCALES_DIR.glob("*.json")' in desktop
    assert "self.tq(questionnaire_text)" in desktop
    assert "build_pdf_report(evaluation, language=self.language)" in desktop
    assert "color: #172033" in desktop
    assert "background: #ffffff" in desktop


def test_desktop_specific_text_has_all_25_languages():
    desktop = (ROOT / "module_company_profile" / "desktop_app.py").read_text(encoding="utf-8")

    assert "DESKTOP_LOCALE_TEXT" in desktop
    for code in (
        "sq",
        "bg",
        "cs",
        "da",
        "de",
        "et",
        "el",
        "en",
        "es",
        "fr",
        "ga",
        "hr",
        "it",
        "lv",
        "lt",
        "hu",
        "mt",
        "nl",
        "pl",
        "pt",
        "ro",
        "sk",
        "sl",
        "fi",
        "sv",
    ):
        assert f'"{code}": {{' in desktop
    for key in (
        "intro",
        "import_json",
        "export_json",
        "model_ready",
        "assessment_clean",
        "assessment_dirty",
        "assessment_running",
    ):
        assert key in desktop
    assert "Impordi JSON" in desktop
    assert "Ekspordi JSON" in desktop
    assert "Kohalik mudel on valmis" in desktop


def test_desktop_ui_keeps_interaction_feedback_visible():
    desktop = (ROOT / "module_company_profile" / "desktop_app.py").read_text(encoding="utf-8")

    assert "button.setCheckable(True)" in desktop
    assert "self.set_active_demo(profile_id)" in desktop
    assert "QPushButton:checked" in desktop
    assert "QCheckBox::indicator" in desktop
    assert "QRadioButton::indicator" in desktop
    assert "matched_early_warnings" in desktop
    assert "event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}" in desktop


def test_desktop_ui_uses_visual_assessment_state_and_responsive_layout():
    desktop = (ROOT / "module_company_profile" / "desktop_app.py").read_text(encoding="utf-8")

    assert "self.assessment_light = QLabel()" in desktop
    assert 'set_assessment_state("clean")' in desktop
    assert 'set_assessment_state("dirty")' in desktop
    assert "self.statusBar().hide()" in desktop
    assert "statusBar().showMessage" not in desktop
    assert "Qt.Orientation.Vertical if self.width() < 1050" in desktop
    assert "self.setMinimumSize(820, 620)" in desktop
    assert "file_buttons.addWidget(evaluate_button)" in desktop
    assert "file_buttons.addWidget(self.assessment_light)" in desktop


def test_desktop_chat_highlights_user_messages():
    desktop = (ROOT / "module_company_profile" / "desktop_app.py").read_text(encoding="utf-8")

    assert "def chat_message_html" in desktop
    assert 'background = "#edf7f3" if user else "#ffffff"' in desktop
    assert 'self.chat_message_html(self.t("you"), message, user=True)' in desktop


def test_desktop_help_uses_localized_dashboard_dictionaries():
    desktop = (ROOT / "module_company_profile" / "desktop_app.py").read_text(encoding="utf-8")

    assert "HELP_SECTIONS" in desktop
    assert "self.help_button = QPushButton()" in desktop
    assert 'self.help_button.setProperty("ui_key", "help_tab")' in desktop
    assert "def help_html" in desktop
    assert "self.t(title_key)" in desktop
    assert "self.t(text_key)" in desktop
    assert "self.t(key)" in desktop


def test_desktop_window_uses_custom_glass_title_bar():
    desktop = (ROOT / "module_company_profile" / "desktop_app.py").read_text(encoding="utf-8")

    assert "class DesktopTitleBar(QWidget)" in desktop
    assert "Qt.WindowType.FramelessWindowHint" in desktop
    assert "Qt.WidgetAttribute.WA_TranslucentBackground" in desktop
    assert "QSizeGrip" in desktop
    assert "self.resize_grip = QSizeGrip(root)" in desktop
    assert "def _resize_edges_at" in desktop
    assert "def _resize_from_global_position" in desktop
    assert "Qt.CursorShape.SizeFDiagCursor" in desktop
    assert "GlassTitleBar" in desktop
    assert "WindowControlButton" in desktop
    assert "CloseWindowButton" in desktop
    assert "rgba(222, 243, 255, 198)" in desktop
    assert "QGraphicsDropShadowEffect" in desktop
    assert 'QColor("#7dd3fc")' in desktop
    assert "glow.setBlurRadius(10)" in desktop
    assert "color: #0284c7" in desktop
    assert "font-size: 28px" in desktop
    assert "left_spacer.setFixedWidth(112)" in desktop
    assert "dr-a-avatar.webp" not in desktop


def test_desktop_glass_text_remains_readable():
    desktop = (ROOT / "module_company_profile" / "desktop_app.py").read_text(encoding="utf-8")

    assert "QLabel {" in desktop
    assert "color: #0f3f78" in desktop
    assert "QGroupBox::title" in desktop
    assert "color: #0b3a6f" in desktop
    assert "QScrollArea {" in desktop
    assert "rgba(236, 248, 255, 185)" in desktop


def test_desktop_links_and_dialogs_are_readable():
    desktop = (ROOT / "module_company_profile" / "desktop_app.py").read_text(encoding="utf-8")

    assert "def configure_external_links" in desktop
    assert "QDesktopServices.openUrl(url)" in desktop
    assert "browser.setOpenLinks(False)" in desktop
    assert "QMessageBox QLabel" in desktop
    assert "color: #f8fafc" in desktop


def test_desktop_launchers_install_the_declared_dependencies():
    windows = (ROOT / "Start desktop dashboard.bat").read_text(encoding="utf-8")
    shell = (ROOT / "Start-Desktop-Dashboard.sh").read_text(encoding="utf-8")
    requirements = (ROOT / "module_company_profile" / "requirements.txt").read_text(
        encoding="utf-8"
    )

    assert "module_company_profile\\desktop_app.py" in windows
    assert "module_company_profile/desktop_app.py" in shell
    assert "pip install -r" in windows
    assert "pip install -r" in shell
    assert "PySide6" in requirements
