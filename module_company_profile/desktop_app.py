"""PySide6 desktop UI for Dr. G.D.P.R. & AI Act navigator."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from module_agents.dr_a_agent import (  # noqa: E402
    DEFAULT_ASSISTANT_NAME,
    LocalModelError,
    build_chat_messages,
    build_chat_sources,
    generate_grounded_reply,
    local_model_runtime_status,
    select_supported_sources,
)
from module_company_profile.dashboard.profile_store import (  # noqa: E402
    compare_evaluations,
    delete_profile_snapshot,
    list_profile_snapshots,
    load_profile_snapshot,
    save_profile_snapshot,
)
from module_company_profile.dashboard.questionnaire_schema import (  # noqa: E402
    EXCLUSIVE_CHECKBOX_VALUES,
    QUESTIONNAIRE_NAME,
    QUESTIONNAIRE_SCHEMA,
    QUESTIONNAIRE_VERSION,
)
from module_company_profile.dashboard.report_exporter import (  # noqa: E402
    build_docx_report,
    build_pdf_report,
)
from module_company_profile.dashboard.report_localizer import (  # noqa: E402
    LOCALES_DIR,
    load_report_locale,
    localize_result,
    localize_timeline_item,
)
from module_company_profile.desktop_runtime import (  # noqa: E402
    DR_A_AGENT,
    PROFILE_HISTORY_DIR,
    build_export_evaluation,
    evaluate_payload,
    load_demo_profile,
)

try:
    from PySide6.QtCore import QEvent, QObject, QRect, QRunnable, Qt, QThreadPool, QUrl, Signal
    from PySide6.QtGui import QAction, QColor, QDesktopServices, QPixmap
    from PySide6.QtWidgets import (
        QApplication,
        QButtonGroup,
        QCheckBox,
        QComboBox,
        QDialog,
        QFileDialog,
        QFrame,
        QGraphicsDropShadowEffect,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QRadioButton,
        QScrollArea,
        QSizeGrip,
        QSplitter,
        QTabWidget,
        QTextBrowser,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError as exc:  # pragma: no cover - exercised only without desktop deps.
    raise SystemExit(
        "PySide6 is required for the desktop UI. Install it with:\n"
        "  python -m pip install -r module_company_profile/requirements.txt"
    ) from exc


class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class FunctionWorker(QRunnable):
    def __init__(self, function: Any, *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            self.signals.finished.emit(self.function(*self.args, **self.kwargs))
        except Exception as exc:  # noqa: BLE001
            self.signals.failed.emit(str(exc))


class DesktopTitleBar(QWidget):
    """Custom frameless-window title bar with visible window controls."""

    def __init__(self, window: QMainWindow) -> None:
        super().__init__(window)
        self.window = window
        self.drag_position = None
        self.setObjectName("GlassTitleBar")
        self.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 8, 6)
        layout.setSpacing(8)

        title = QLabel("Dr. G.D.P.R. & AI Act navigator")
        title.setObjectName("WindowTitle")
        glow = QGraphicsDropShadowEffect(title)
        glow.setBlurRadius(10)
        glow.setColor(QColor("#7dd3fc"))
        glow.setOffset(0, 0)
        title.setGraphicsEffect(glow)

        left_spacer = QWidget()
        left_spacer.setFixedWidth(112)
        layout.addStretch()
        layout.addWidget(left_spacer)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self._window_button("_", self.window.showMinimized, "Minimize"))
        layout.addWidget(self._window_button("□", self.toggle_maximized, "Resize"))
        layout.addWidget(self._window_button("×", self.window.close, "Close", close=True))

    def _window_button(
        self, text: str, callback: Any, tooltip: str, *, close: bool = False
    ) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("CloseWindowButton" if close else "WindowControlButton")
        button.setFixedSize(32, 28)
        button.setToolTip(tooltip)
        button.clicked.connect(callback)
        return button

    def toggle_maximized(self) -> None:
        if self.window.isMaximized():
            self.window.showNormal()
        else:
            self.window.showMaximized()

    def mousePressEvent(self, event: Any) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.window.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event: Any) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_position is not None:
            if self.window.isMaximized():
                self.window.showNormal()
            self.window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseDoubleClickEvent(self, event: Any) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_maximized()
            event.accept()


def html_list(items: list[Any], empty: str = "Nessun elemento.") -> str:
    if not items:
        return f"<p>{empty}</p>"
    rendered = "".join(f"<li>{escape_html(str(item))}</li>" for item in items)
    return f"<ul>{rendered}</ul>"


def escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "company"


LANGUAGE_NAMES = {
    "sq": "Shqip",
    "bg": "Balgarski",
    "cs": "Cestina",
    "da": "Dansk",
    "de": "Deutsch",
    "et": "Eesti",
    "el": "Ellinika",
    "en": "English",
    "es": "Espanol",
    "fr": "Francais",
    "ga": "Gaeilge",
    "hr": "Hrvatski",
    "it": "Italiano",
    "lv": "Latviesu",
    "lt": "Lietuviu",
    "hu": "Magyar",
    "mt": "Malti",
    "nl": "Nederlands",
    "pl": "Polski",
    "pt": "Portugues",
    "ro": "Romana",
    "sk": "Slovencina",
    "sl": "Slovenscina",
    "fi": "Suomi",
    "sv": "Svenska",
}

LANGUAGE_FLAG_CODES = {
    "sq": "al",
    "bg": "bg",
    "cs": "cz",
    "da": "dk",
    "de": "de",
    "et": "ee",
    "el": "gr",
    "en": "gb",
    "es": "es",
    "fr": "fr",
    "ga": "ie",
    "hr": "hr",
    "it": "it",
    "lv": "lv",
    "lt": "lt",
    "hu": "hu",
    "mt": "mt",
    "nl": "nl",
    "pl": "pl",
    "pt": "pt",
    "ro": "ro",
    "sk": "sk",
    "sl": "si",
    "fi": "fi",
    "sv": "se",
}

HELP_SECTIONS = (
    (
        ("loading_title", "loading_text", ("loading_1", "loading_2", "loading_3")),
        (
            "questionnaire_overview_title",
            "questionnaire_overview_text",
            (
                "questionnaire_answer_1",
                "questionnaire_answer_2",
                "questionnaire_answer_3",
                "questionnaire_answer_4",
            ),
        ),
        ("evaluate_questionnaire", "assessment_1", ()),
        (
            "snapshots_title",
            "snapshots_text",
            ("snapshot_save", "snapshot_load", "snapshot_compare", "snapshot_delete"),
        ),
    ),
    (
        ("dashboard_score_title", "dashboard_score_text", ()),
        ("dashboard_warnings_title", "dashboard_warnings_text", ()),
        ("dashboard_timeline_title", "dashboard_timeline_text", ()),
        (
            "dashboard_news_title",
            "",
            ("dashboard_news_events", "dashboard_news_updates", "dashboard_news_refresh"),
        ),
        ("dashboard_assistant_title", "dashboard_assistant_text", ("chat_placeholder",)),
    ),
)

DESKTOP_LOCALE_TEXT = {
    "sq": {
        "intro": "Ploteso pyetesorin, ngarko nje profil demo ose importo JSON. Vleresimi llogaritet lokalisht nga agjentet Python.",
        "import_json": "Importo JSON",
        "export_json": "Eksporto JSON",
        "model_ready": "Modeli lokal eshte gati",
        "assessment_clean": "Vleresimi eshte i perditesuar: nuk ka ndryshime pas tij.",
        "assessment_dirty": "Pyetesori eshte ndryshuar ose ende nuk eshte vleresuar.",
        "assessment_running": "Vleresimi eshte ne vazhdim.",
    },
    "bg": {
        "intro": "Popalnete vaprosnika, zaredate demo profil ili importirayte JSON. Otsenkata se izchislyava lokalno ot Python agentite.",
        "import_json": "Importiray JSON",
        "export_json": "Eksportiray JSON",
        "model_ready": "Lokalniyat model e gotov",
        "assessment_clean": "Otsenkata e aktualna: nyama posledvashti promeni.",
        "assessment_dirty": "Vaprosnikat e promenen ili oshte ne e otsenen.",
        "assessment_running": "Otsenkata se izpalnyava.",
    },
    "cs": {
        "intro": "Vyplnte dotaznik, nactete demo profil nebo importujte JSON. Hodnoceni se pocita lokalne pomoci agentu Python.",
        "import_json": "Importovat JSON",
        "export_json": "Exportovat JSON",
        "model_ready": "Mistni model je pripraven",
        "assessment_clean": "Hodnoceni je aktualni: po nem nebyly provedeny zadne zmeny.",
        "assessment_dirty": "Dotaznik byl zmenen nebo jeste nebyl vyhodnocen.",
        "assessment_running": "Hodnoceni probiha.",
    },
    "da": {
        "intro": "Udfyld spoergeskemaet, indlaes en demoprofil eller importer JSON. Vurderingen beregnes lokalt af Python-agenterne.",
        "import_json": "Importer JSON",
        "export_json": "Eksporter JSON",
        "model_ready": "Lokal model klar",
        "assessment_clean": "Vurderingen er aktuel: ingen senere aendringer.",
        "assessment_dirty": "Spoergeskemaet er aendret eller endnu ikke vurderet.",
        "assessment_running": "Vurdering koerer.",
    },
    "de": {
        "intro": "Fuellen Sie den Fragebogen aus, laden Sie ein Demoprofil oder importieren Sie JSON. Die Bewertung wird lokal von den Python-Agenten berechnet.",
        "import_json": "JSON importieren",
        "export_json": "JSON exportieren",
        "model_ready": "Lokales Modell bereit",
        "assessment_clean": "Die Bewertung ist aktuell: keine spaeteren Aenderungen.",
        "assessment_dirty": "Der Fragebogen wurde geaendert oder noch nicht bewertet.",
        "assessment_running": "Bewertung laeuft.",
    },
    "el": {
        "intro": "Συμπληρώστε το ερωτηματολόγιο, φορτώστε ένα demo προφίλ ή εισαγάγετε JSON. Η αξιολόγηση υπολογίζεται τοπικά από τους Python agents.",
        "import_json": "Εισαγωγή JSON",
        "export_json": "Εξαγωγή JSON",
        "model_ready": "Το τοπικό μοντέλο είναι έτοιμο",
        "assessment_clean": "Η αξιολόγηση είναι ενημερωμένη: δεν έγιναν μεταγενέστερες αλλαγές.",
        "assessment_dirty": "Το ερωτηματολόγιο άλλαξε ή δεν έχει ακόμη αξιολογηθεί.",
        "assessment_running": "Η αξιολόγηση εκτελείται.",
    },
    "en": {
        "intro": "Complete the questionnaire, load a demo profile, or import JSON. The assessment is calculated locally by the Python agents.",
        "import_json": "Import JSON",
        "export_json": "Export JSON",
        "model_ready": "Local model ready",
        "assessment_clean": "Assessment is current: no later questionnaire changes.",
        "assessment_dirty": "Questionnaire changed or not assessed yet.",
        "assessment_running": "Assessment running.",
    },
    "es": {
        "intro": "Complete el cuestionario, cargue un perfil demo o importe JSON. La evaluacion se calcula localmente mediante los agentes Python.",
        "import_json": "Importar JSON",
        "export_json": "Exportar JSON",
        "model_ready": "Modelo local listo",
        "assessment_clean": "La evaluacion esta actualizada: no hay cambios posteriores.",
        "assessment_dirty": "El cuestionario cambio o aun no se ha evaluado.",
        "assessment_running": "Evaluacion en curso.",
    },
    "et": {
        "intro": "Täida küsimustik, laadi demoprofiil või impordi JSON. Hindamine arvutatakse lokaalselt Pythoni agentide poolt.",
        "import_json": "Impordi JSON",
        "export_json": "Ekspordi JSON",
        "model_ready": "Kohalik mudel on valmis",
        "assessment_clean": "Hindamine on ajakohane: hilisemaid muudatusi pole.",
        "assessment_dirty": "Küsimustikku on muudetud või seda pole veel hinnatud.",
        "assessment_running": "Hindamine on käimas.",
    },
    "fi": {
        "intro": "Täytä kysely, lataa demoprofiili tai tuo JSON. Arviointi lasketaan paikallisesti Python-agenttien avulla.",
        "import_json": "Tuo JSON",
        "export_json": "Vie JSON",
        "model_ready": "Paikallinen malli valmis",
        "assessment_clean": "Arviointi on ajan tasalla: myöhempiä muutoksia ei ole.",
        "assessment_dirty": "Kyselyä on muutettu tai sitä ei ole vielä arvioitu.",
        "assessment_running": "Arviointi käynnissä.",
    },
    "fr": {
        "intro": "Remplissez le questionnaire, chargez un profil de demo ou importez un JSON. L'evaluation est calculee localement par les agents Python.",
        "import_json": "Importer JSON",
        "export_json": "Exporter JSON",
        "model_ready": "Modele local pret",
        "assessment_clean": "L'evaluation est a jour : aucune modification ulterieure.",
        "assessment_dirty": "Le questionnaire a ete modifie ou n'a pas encore ete evalue.",
        "assessment_running": "Evaluation en cours.",
    },
    "ga": {
        "intro": "Comhlánaigh an ceistneoir, luchtaigh próifíl demo nó iompórtáil JSON. Ríomhtar an measúnú go háitiúil ag na gníomhairí Python.",
        "import_json": "Iompórtáil JSON",
        "export_json": "Easpórtáil JSON",
        "model_ready": "Samhail aitiuil reidh",
        "assessment_clean": "Tá an measúnú cothrom le dáta: níl aon athrú ina dhiaidh.",
        "assessment_dirty": "Athraíodh an ceistneoir nó níor measúnaíodh fós é.",
        "assessment_running": "Tá an measúnú ar siúl.",
    },
    "hr": {
        "intro": "Ispunite upitnik, ucitajte demo profil ili uvezite JSON. Procjena se izracunava lokalno pomocu Python agenata.",
        "import_json": "Uvezi JSON",
        "export_json": "Izvezi JSON",
        "model_ready": "Lokalni model spreman",
        "assessment_clean": "Procjena je azurna: nema naknadnih promjena.",
        "assessment_dirty": "Upitnik je promijenjen ili jos nije procijenjen.",
        "assessment_running": "Procjena je u tijeku.",
    },
    "hu": {
        "intro": "Töltse ki a kérdőívet, töltsön be demóprofilt vagy importáljon JSON-t. Az értékelést helyben a Python ügynökök számítják ki.",
        "import_json": "JSON importálása",
        "export_json": "JSON exportálása",
        "model_ready": "Helyi modell kesz",
        "assessment_clean": "Az értékelés naprakész: nincs későbbi módosítás.",
        "assessment_dirty": "A kérdőív módosult, vagy még nincs értékelve.",
        "assessment_running": "Az értékelés folyamatban van.",
    },
    "it": {
        "intro": "Compila il questionario, carica un profilo demo o importa JSON. La valutazione viene calcolata localmente dagli agenti Python.",
        "import_json": "Importa JSON",
        "export_json": "Esporta JSON",
        "model_ready": "Modello locale pronto",
        "assessment_clean": "Valutazione aggiornata: nessuna modifica successiva.",
        "assessment_dirty": "Questionario modificato o non ancora valutato.",
        "assessment_running": "Valutazione in corso.",
    },
    "lt": {
        "intro": "Užpildykite klausimyną, įkelkite demonstracinį profilį arba importuokite JSON. Vertinimą vietoje apskaičiuoja Python agentai.",
        "import_json": "Importuoti JSON",
        "export_json": "Eksportuoti JSON",
        "model_ready": "Vietinis modelis parengtas",
        "assessment_clean": "Vertinimas atnaujintas: vėlesnių pakeitimų nėra.",
        "assessment_dirty": "Klausimynas pakeistas arba dar neįvertintas.",
        "assessment_running": "Vertinimas vyksta.",
    },
    "lv": {
        "intro": "Aizpildiet anketu, ielādējiet demo profilu vai importējiet JSON. Novērtējumu lokāli aprēķina Python aģenti.",
        "import_json": "Importēt JSON",
        "export_json": "Eksportēt JSON",
        "model_ready": "Vietejais modelis gatavs",
        "assessment_clean": "Novērtējums ir aktuāls: vēlākas izmaiņas nav veiktas.",
        "assessment_dirty": "Anketa ir mainīta vai vēl nav novērtēta.",
        "assessment_running": "Notiek novērtēšana.",
    },
    "mt": {
        "intro": "Imla l-kwestjonarju, ittella' profil demo jew importa JSON. Il-valutazzjoni tigi kkalkulata lokalment mill-agenti Python.",
        "import_json": "Importa JSON",
        "export_json": "Esporta JSON",
        "model_ready": "Mudell lokali lest",
        "assessment_clean": "Il-valutazzjoni hija aggiornata: ma sarux bidliet wara.",
        "assessment_dirty": "Il-kwestjonarju nbidel jew ghadu ma giex evalwat.",
        "assessment_running": "Il-valutazzjoni ghaddejja.",
    },
    "nl": {
        "intro": "Vul de vragenlijst in, laad een demoprofiel of importeer JSON. De beoordeling wordt lokaal berekend door de Python-agenten.",
        "import_json": "JSON importeren",
        "export_json": "JSON exporteren",
        "model_ready": "Lokaal model gereed",
        "assessment_clean": "De beoordeling is actueel: geen latere wijzigingen.",
        "assessment_dirty": "De vragenlijst is gewijzigd of nog niet beoordeeld.",
        "assessment_running": "Beoordeling wordt uitgevoerd.",
    },
    "pl": {
        "intro": "Wypelnij kwestionariusz, zaladuj profil demo albo zaimportuj JSON. Ocena jest obliczana lokalnie przez agentow Python.",
        "import_json": "Importuj JSON",
        "export_json": "Eksportuj JSON",
        "model_ready": "Model lokalny gotowy",
        "assessment_clean": "Ocena jest aktualna: brak pozniejszych zmian.",
        "assessment_dirty": "Kwestionariusz zostal zmieniony albo nie zostal jeszcze oceniony.",
        "assessment_running": "Ocena w toku.",
    },
    "pt": {
        "intro": "Preencha o questionario, carregue um perfil demo ou importe JSON. A avaliacao e calculada localmente pelos agentes Python.",
        "import_json": "Importar JSON",
        "export_json": "Exportar JSON",
        "model_ready": "Modelo local pronto",
        "assessment_clean": "A avaliacao esta atualizada: nao ha alteracoes posteriores.",
        "assessment_dirty": "O questionario foi alterado ou ainda nao foi avaliado.",
        "assessment_running": "Avaliacao em curso.",
    },
    "ro": {
        "intro": "Completati chestionarul, incarcati un profil demo sau importati JSON. Evaluarea este calculata local de agentii Python.",
        "import_json": "Importa JSON",
        "export_json": "Exporta JSON",
        "model_ready": "Model local pregatit",
        "assessment_clean": "Evaluarea este actuala: nu exista modificari ulterioare.",
        "assessment_dirty": "Chestionarul a fost modificat sau nu a fost inca evaluat.",
        "assessment_running": "Evaluarea este in curs.",
    },
    "sk": {
        "intro": "Vyplnte dotaznik, nacitajte demo profil alebo importujte JSON. Hodnotenie sa pocita lokalne pomocou agentov Python.",
        "import_json": "Importovat JSON",
        "export_json": "Exportovat JSON",
        "model_ready": "Miestny model je pripraveny",
        "assessment_clean": "Hodnotenie je aktualne: neboli vykonane ziadne neskorsie zmeny.",
        "assessment_dirty": "Dotaznik bol zmeneny alebo este nebol vyhodnoteny.",
        "assessment_running": "Hodnotenie prebieha.",
    },
    "sl": {
        "intro": "Izpolnite vprasalnik, nalozite demo profil ali uvozite JSON. Ocena se lokalno izracuna z agenti Python.",
        "import_json": "Uvozi JSON",
        "export_json": "Izvozi JSON",
        "model_ready": "Lokalni model pripravljen",
        "assessment_clean": "Ocena je posodobljena: kasnejsih sprememb ni.",
        "assessment_dirty": "Vprasalnik je bil spremenjen ali se ni bil ocenjen.",
        "assessment_running": "Ocena poteka.",
    },
    "sv": {
        "intro": "Fyll i fragorna, las in en demoprofil eller importera JSON. Bedomningen beraknas lokalt av Python-agenterna.",
        "import_json": "Importera JSON",
        "export_json": "Exportera JSON",
        "model_ready": "Lokal modell redo",
        "assessment_clean": "Bedomningen ar aktuell: inga senare andringar.",
        "assessment_dirty": "Fragorna har andrats eller har inte bedomts annu.",
        "assessment_running": "Bedomning pagar.",
    },
}


class DesktopDashboard(QMainWindow):
    RESIZE_MARGIN = 8

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setWindowTitle("Dr. G.D.P.R. & AI Act navigator")
        screen = QApplication.primaryScreen()
        if screen:
            available = screen.availableGeometry()
            self.resize(min(1280, available.width() - 80), min(840, available.height() - 80))
        else:
            self.resize(1280, 840)
        self.setMinimumSize(820, 620)
        self.thread_pool = QThreadPool.globalInstance()
        self.field_widgets: dict[str, list[Any]] = {}
        self.radio_groups: dict[str, QButtonGroup] = {}
        self.current_questionnaire: dict[str, Any] | None = None
        self.current_evaluation: dict[str, Any] | None = None
        self.chat_history: list[dict[str, str]] = []
        self.language = "it"
        self.locale_codes = sorted(path.stem for path in LOCALES_DIR.glob("*.json"))
        self.is_populating = False
        self.demo_buttons: dict[str, QPushButton] = {}
        self.active_demo_profile: str | None = None
        self.assessment_state = "dirty"
        self.resize_edges: set[str] = set()
        self.resize_start_global = None
        self.resize_start_geometry: QRect | None = None
        self._build_ui()
        self.apply_language(self.language)
        self._refresh_profiles()
        self._update_model_status()

    def t(self, key: str) -> str:
        bundle = load_report_locale(self.language)
        ui = bundle.get("ui") or {}
        fallback = load_report_locale("it").get("ui") or {}
        return str(ui.get(key) or fallback.get(key) or key)

    def desktop_text(self, key: str) -> str:
        dictionary = DESKTOP_LOCALE_TEXT.get(self.language) or DESKTOP_LOCALE_TEXT["it"]
        fallback = DESKTOP_LOCALE_TEXT["it"]
        return dictionary.get(key) or fallback.get(key) or key

    def tq(self, text: str) -> str:
        if self.language == "it":
            return text
        dictionary = load_report_locale(self.language).get("questionnaire") or {}
        return str(dictionary.get(text) or text)

    def tr(self, value: Any) -> str:
        return localize_result(self.language, value)

    def set_browser_html(self, browser: QTextBrowser, body: str) -> None:
        browser.setHtml(
            """
            <html>
            <head>
              <style>
                body {
                  color: #172033;
                  background: #ffffff;
                  font-family: "Segoe UI", Arial, sans-serif;
                  font-size: 13px;
                  line-height: 1.45;
                }
                h2 { color: #0f172a; font-size: 20px; margin: 0 0 10px; }
                p { margin: 0 0 10px; }
                li { margin-bottom: 8px; }
                a { color: #0b63ce; text-decoration: underline; }
              </style>
            </head>
            <body>
            """
            + body
            + "</body></html>"
        )

    def help_html(self) -> str:
        sections = []
        for group in HELP_SECTIONS:
            for title_key, text_key, item_keys in group:
                items = "".join(f"<li>{escape_html(self.t(key))}</li>" for key in item_keys)
                list_html = f"<ul>{items}</ul>" if items else ""
                text_html = f"<p>{escape_html(self.t(text_key))}</p>" if text_key else ""
                sections.append(f"<h2>{escape_html(self.t(title_key))}</h2>{text_html}{list_html}")
        return "".join(sections)

    def open_help(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle(self.t("help_tab"))
        dialog.resize(
            min(760, max(520, self.width() - 160)), min(680, max(460, self.height() - 140))
        )
        layout = QVBoxLayout(dialog)
        browser = QTextBrowser()
        self.set_browser_html(browser, self.help_html())
        close_button = QPushButton(self.t("help_tab"))
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(browser, 1)
        layout.addWidget(close_button)
        dialog.exec()

    def configure_external_links(self, browser: QTextBrowser) -> None:
        browser.setOpenLinks(False)
        browser.setOpenExternalLinks(False)
        browser.anchorClicked.connect(self.open_external_link)

    def open_external_link(self, url: QUrl) -> None:
        if url.scheme() in {"http", "https"}:
            QDesktopServices.openUrl(url)

    def chat_message_html(self, speaker: str, text: str, *, user: bool = False) -> str:
        background = "#edf7f3" if user else "#ffffff"
        border = "#b8dccb" if user else "#d6deea"
        align = "right" if user else "left"
        return f"""
        <div align="{align}">
          <table width="92%" cellspacing="0" cellpadding="8"
                 style="background-color:{background}; border:1px solid {border}; border-radius:6px;">
            <tr><td>
              <b>{escape_html(speaker)}</b><br>
              {escape_html(text).replace(chr(10), "<br>")}
            </td></tr>
          </table>
        </div>
        <br>
        """

    def on_language_changed(self) -> None:
        code = self.language_select.currentData()
        if isinstance(code, str):
            self.apply_language(code)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if (
            watched is self.chat_input
            and event.type() == QEvent.Type.KeyPress
            and event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}
            and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        ):
            self.ask_dr_a()
            return True
        return super().eventFilter(watched, event)

    def update_language_flag(self) -> None:
        country_code = LANGUAGE_FLAG_CODES.get(self.language, "it")
        flag_path = LOCALES_DIR.parent / "assets" / "flags" / f"{country_code}.svg"
        pixmap = QPixmap(str(flag_path))
        if pixmap.isNull():
            self.language_flag.setText(country_code.upper())
            return
        self.language_flag.setPixmap(
            pixmap.scaled(
                self.language_flag.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def clear_demo_selection(self) -> None:
        if self.is_populating:
            return
        self.set_active_demo(None)
        self.set_assessment_state("dirty")

    def set_active_demo(self, profile_id: str | None) -> None:
        self.active_demo_profile = profile_id
        for key, button in self.demo_buttons.items():
            button.setChecked(key == profile_id)

    def set_assessment_state(self, state: str) -> None:
        self.assessment_state = state
        colors = {
            "clean": ("#16a34a", self.desktop_text("assessment_clean")),
            "dirty": ("#f59e0b", self.desktop_text("assessment_dirty")),
            "running": ("#f59e0b", self.desktop_text("assessment_running")),
        }
        color, tooltip = colors.get(state, colors["dirty"])
        self.assessment_light.setStyleSheet(
            f"background-color: {color}; border: 1px solid #334155; border-radius: 7px;"
        )
        self.assessment_light.setToolTip(tooltip)

    def apply_language(self, language: str) -> None:
        self.language = language if language in self.locale_codes else "it"
        for widget in self.findChildren(QWidget):
            ui_key = widget.property("ui_key")
            if isinstance(ui_key, str) and hasattr(widget, "setText"):
                widget.setText(self.t(ui_key))
            desktop_key = widget.property("desktop_text_key")
            if isinstance(desktop_key, str) and hasattr(widget, "setText"):
                widget.setText(self.desktop_text(desktop_key))
            questionnaire_text = widget.property("questionnaire_text")
            if isinstance(questionnaire_text, str):
                if isinstance(widget, QGroupBox):
                    widget.setTitle(self.tq(questionnaire_text))
                elif hasattr(widget, "setText"):
                    widget.setText(self.tq(questionnaire_text))
        self.tabs.setTabText(0, self.t("score_priority"))
        self.tabs.setTabText(1, self.t("warnings_controls"))
        self.tabs.setTabText(2, self.t("regulatory_events"))
        self.tabs.setTabText(3, self.t("compliance_timeline"))
        self.tabs.setTabText(4, self.t("chatbot"))
        self.chat_input.setPlaceholderText(self.t("chat_placeholder"))
        self.update_language_flag()
        if self.current_evaluation:
            self.render_evaluation(self.current_evaluation)
        else:
            self.render_empty()
        self._refresh_profiles()
        self._update_model_status()
        self.set_assessment_state(self.assessment_state)

    def resizeEvent(self, event: Any) -> None:
        super().resizeEvent(event)
        if hasattr(self, "splitter"):
            self.splitter.setOrientation(
                Qt.Orientation.Vertical if self.width() < 1050 else Qt.Orientation.Horizontal
            )
        if hasattr(self, "resize_grip"):
            self.resize_grip.move(self.width() - self.resize_grip.width() - 14, self.height() - 30)

    def leaveEvent(self, event: Any) -> None:
        if not self.resize_edges:
            self.unsetCursor()
        super().leaveEvent(event)

    def mousePressEvent(self, event: Any) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            edges = self._resize_edges_at(event.position().toPoint())
            if edges:
                self.resize_edges = edges
                self.resize_start_global = event.globalPosition().toPoint()
                self.resize_start_geometry = self.geometry()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: Any) -> None:
        if self.resize_edges and self.resize_start_global and self.resize_start_geometry:
            self._resize_from_global_position(event.globalPosition().toPoint())
            event.accept()
            return
        self._update_resize_cursor(event.position().toPoint())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: Any) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.resize_edges:
            self.resize_edges = set()
            self.resize_start_global = None
            self.resize_start_geometry = None
            self._update_resize_cursor(event.position().toPoint())
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _resize_edges_at(self, position: Any) -> set[str]:
        if self.isMaximized():
            return set()
        edges: set[str] = set()
        margin = self.RESIZE_MARGIN
        if position.x() <= margin:
            edges.add("left")
        elif position.x() >= self.width() - margin:
            edges.add("right")
        if position.y() <= margin:
            edges.add("top")
        elif position.y() >= self.height() - margin:
            edges.add("bottom")
        return edges

    def _update_resize_cursor(self, position: Any) -> None:
        edges = self._resize_edges_at(position)
        if {"left", "top"} <= edges or {"right", "bottom"} <= edges:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif {"right", "top"} <= edges or {"left", "bottom"} <= edges:
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edges & {"left", "right"}:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edges & {"top", "bottom"}:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.unsetCursor()

    def _resize_from_global_position(self, global_position: Any) -> None:
        if not self.resize_start_global or not self.resize_start_geometry:
            return
        delta = global_position - self.resize_start_global
        geometry = QRect(self.resize_start_geometry)
        minimum = self.minimumSize()
        if "left" in self.resize_edges:
            geometry.setLeft(min(geometry.left() + delta.x(), geometry.right() - minimum.width()))
        if "right" in self.resize_edges:
            geometry.setRight(max(geometry.right() + delta.x(), geometry.left() + minimum.width()))
        if "top" in self.resize_edges:
            geometry.setTop(min(geometry.top() + delta.y(), geometry.bottom() - minimum.height()))
        if "bottom" in self.resize_edges:
            geometry.setBottom(
                max(geometry.bottom() + delta.y(), geometry.top() + minimum.height())
            )
        self.setGeometry(geometry)

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("WindowShell")
        root.setMouseTracking(True)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(12)
        outer.addWidget(DesktopTitleBar(self))

        header = QHBoxLayout()
        header.addStretch()
        language_label = QLabel()
        language_label.setProperty("ui_key", "language_label")
        self.language_select = QComboBox()
        for code in self.locale_codes:
            self.language_select.addItem(LANGUAGE_NAMES.get(code, code), code)
        self.language_select.setCurrentIndex(max(0, self.language_select.findData(self.language)))
        self.language_select.currentIndexChanged.connect(lambda: self.on_language_changed())
        self.language_flag = QLabel()
        self.language_flag.setFixedSize(30, 22)
        self.help_button = QPushButton()
        self.help_button.setProperty("ui_key", "help_tab")
        self.help_button.clicked.connect(self.open_help)
        self.model_status = QLabel()
        header.addWidget(language_label)
        header.addWidget(self.language_select)
        header.addWidget(self.language_flag)
        header.addWidget(self.help_button)
        header.addWidget(self.model_status)
        outer.addLayout(header)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self._questionnaire_panel())
        self.splitter.addWidget(self._results_panel())
        self.splitter.setStretchFactor(0, 4)
        self.splitter.setStretchFactor(1, 5)
        self.splitter.setChildrenCollapsible(False)
        outer.addWidget(self.splitter, 1)
        self.resize_grip = QSizeGrip(root)
        self.resize_grip.setFixedSize(18, 18)
        self.resize_grip.setToolTip("Resize")
        self.resize_grip.raise_()
        self.setCentralWidget(root)

        self.statusBar().hide()
        self.setStyleSheet(
            """
            QMainWindow { background: transparent; }
            QWidget#WindowShell {
                color: #172033;
                background: rgba(222, 243, 255, 198);
                border: 1px solid rgba(210, 238, 255, 125);
                border-radius: 14px;
            }
            QWidget#GlassTitleBar {
                background: rgba(199, 232, 255, 135);
                border: 1px solid rgba(226, 247, 255, 110);
                border-radius: 10px;
            }
            QLabel {
                color: #0f3f78;
                background: transparent;
            }
            QLabel#WindowTitle {
                font-size: 28px;
                font-weight: 900;
                color: #0284c7;
                padding: 0 12px;
            }
            QPushButton#WindowControlButton, QPushButton#CloseWindowButton {
                color: #0f3f78;
                background: rgba(219, 234, 254, 135);
                border: 1px solid rgba(59, 130, 246, 120);
                border-radius: 6px;
                font-weight: 700;
                padding: 0;
            }
            QPushButton#WindowControlButton:hover {
                color: #082f49;
                background: rgba(186, 230, 253, 215);
            }
            QPushButton#CloseWindowButton:hover {
                color: #082f49;
                background: rgba(147, 197, 253, 230);
            }
            QGroupBox {
                color: #172033;
                background: rgba(255, 255, 255, 202);
                border: 1px solid rgba(207, 215, 230, 150);
                border-radius: 6px;
                font-weight: 600;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                color: #0b3a6f;
                background: rgba(222, 243, 255, 175);
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 6px;
            }
            QPushButton {
                color: #122033;
                background: #ffffff;
                border: 1px solid #aebbd0;
                border-radius: 5px;
                padding: 7px 10px;
            }
            QPushButton:hover { background: #eef4ff; border-color: #7aa6e8; }
            QPushButton:pressed { background: #dbeafe; border-color: #2563eb; }
            QPushButton:checked {
                color: #67e8f9;
                background: #1d4ed8;
                border-color: #1e40af;
                font-weight: 700;
            }
            QLineEdit, QTextEdit, QComboBox {
                color: #172033;
                background: rgba(255, 255, 255, 218);
                border: 1px solid #b9c4d6;
                border-radius: 4px;
                padding: 5px;
            }
            QTabWidget::pane {
                border: 1px solid rgba(207, 215, 230, 145);
                background: rgba(255, 255, 255, 198);
            }
            QTabBar::tab {
                color: #172033;
                background: #e9eef7;
                padding: 8px 12px;
                border: 1px solid #cfd7e6;
            }
            QTabBar::tab:selected {
                background: rgba(255, 255, 255, 210);
                border-bottom-color: rgba(255, 255, 255, 210);
            }
            QScrollArea {
                color: #172033;
                background: rgba(236, 248, 255, 185);
                border: 1px solid rgba(148, 191, 219, 105);
                border-radius: 8px;
            }
            QScrollArea > QWidget > QWidget {
                background: rgba(236, 248, 255, 185);
            }
            QTextBrowser {
                color: #172033;
                background: rgba(255, 255, 255, 205);
                border: 1px solid rgba(207, 215, 230, 145);
            }
            QTextBrowser a { color: #0b63ce; }
            QCheckBox, QRadioButton {
                color: #172033;
                spacing: 8px;
                padding: 3px 0;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #64748b;
                background: rgba(255, 255, 255, 220);
            }
            QCheckBox::indicator { border-radius: 4px; }
            QRadioButton::indicator { border-radius: 10px; }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                background: #1d4ed8;
                border-color: #1d4ed8;
            }
            QCheckBox::indicator:checked {
                image: none;
            }
            QMessageBox {
                background: #111827;
            }
            QMessageBox QLabel {
                color: #f8fafc;
                background: transparent;
            }
            QMessageBox QPushButton {
                color: #0f172a;
                background: #f8fafc;
                border: 1px solid #bfdbfe;
                border-radius: 5px;
                padding: 7px 14px;
            }
            """
        )

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        open_action = QAction("Carica questionario JSON", self)
        open_action.triggered.connect(self.load_questionnaire_file)
        file_menu.addAction(open_action)
        save_action = QAction("Salva questionario JSON", self)
        save_action.triggered.connect(self.save_questionnaire_file)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        exit_action = QAction("Esci", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _questionnaire_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(10)

        intro = QLabel()
        intro.setProperty("desktop_text_key", "intro")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        buttons = QHBoxLayout()
        for key, profile_id in (
            ("demo_saas", "low-risk-saas"),
            ("demo_hr", "hr-ai"),
            ("demo_gpai", "gpai-provider"),
        ):
            button = QPushButton()
            button.setProperty("ui_key", key)
            button.setCheckable(True)
            button.clicked.connect(lambda _checked=False, value=profile_id: self.load_demo(value))
            self.demo_buttons[profile_id] = button
            buttons.addWidget(button)
        layout.addLayout(buttons)

        file_buttons = QHBoxLayout()
        load_button = QPushButton()
        load_button.setProperty("desktop_text_key", "import_json")
        load_button.clicked.connect(self.load_questionnaire_file)
        save_button = QPushButton()
        save_button.setProperty("desktop_text_key", "export_json")
        save_button.clicked.connect(self.save_questionnaire_file)
        evaluate_button = QPushButton()
        evaluate_button.setProperty("ui_key", "evaluate_questionnaire")
        evaluate_button.clicked.connect(self.evaluate_current_form)
        self.assessment_light = QLabel()
        self.assessment_light.setFixedSize(14, 14)
        self.assessment_light.setProperty("semantic_role", "assessment_light")
        file_buttons.addWidget(load_button)
        file_buttons.addWidget(save_button)
        file_buttons.addWidget(evaluate_button)
        file_buttons.addWidget(self.assessment_light)
        file_buttons.addStretch()
        layout.addLayout(file_buttons)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(10)
        for section in QUESTIONNAIRE_SCHEMA:
            group = QGroupBox()
            group.setProperty("questionnaire_text", section.title)
            section_layout = QVBoxLayout(group)
            for question in section.questions:
                section_layout.addWidget(self._question_widget(question))
            form_layout.addWidget(group)
        form_layout.addStretch()
        scroll.setWidget(form_widget)
        layout.addWidget(scroll, 1)
        return container

    def _question_widget(self, question: Any) -> QWidget:
        box = QFrame()
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 4, 0, 4)
        label = QLabel()
        label.setProperty("questionnaire_text", question.label)
        label.setWordWrap(True)
        layout.addWidget(label)
        widgets: list[Any] = []

        if question.type == "text":
            field = QLineEdit()
            field.textEdited.connect(self.clear_demo_selection)
            layout.addWidget(field)
            widgets.append(field)
        elif question.type == "textarea":
            field = QTextEdit()
            field.setFixedHeight(80)
            field.textChanged.connect(self.clear_demo_selection)
            layout.addWidget(field)
            widgets.append(field)
        elif question.type == "radio":
            group = QButtonGroup(self)
            group.setExclusive(True)
            self.radio_groups[question.name] = group
            for value, option_label in question.options:
                radio = QRadioButton()
                radio.setProperty("answer_value", value)
                radio.setProperty("questionnaire_text", option_label)
                radio.toggled.connect(
                    lambda checked: self.clear_demo_selection() if checked else None
                )
                group.addButton(radio)
                layout.addWidget(radio)
                widgets.append(radio)
        elif question.type == "checkbox":
            for value, option_label in question.options:
                checkbox = QCheckBox()
                checkbox.setProperty("answer_value", value)
                checkbox.setProperty("questionnaire_text", option_label)
                checkbox.toggled.connect(
                    lambda checked, name=question.name, cb=checkbox: self._enforce_exclusive(
                        name, cb, checked
                    )
                )
                checkbox.toggled.connect(
                    lambda checked: self.clear_demo_selection() if checked else None
                )
                layout.addWidget(checkbox)
                widgets.append(checkbox)

        self.field_widgets[question.name] = widgets
        return box

    def _results_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)

        self.tabs = QTabWidget()
        self.summary_view = QTextBrowser()
        self.controls_view = QTextBrowser()
        self.events_view = QTextBrowser()
        self.timeline_view = QTextBrowser()
        self.chat_view = QTextBrowser()
        for browser in (
            self.summary_view,
            self.controls_view,
            self.events_view,
            self.timeline_view,
            self.chat_view,
        ):
            self.configure_external_links(browser)
        self.chat_input = QTextEdit()
        self.chat_input.setFixedHeight(90)
        self.chat_input.installEventFilter(self)

        self.tabs.addTab(self.summary_view, "")
        self.tabs.addTab(self.controls_view, "")
        self.tabs.addTab(self.events_view, "")
        self.tabs.addTab(self.timeline_view, "")
        self.tabs.addTab(self._chat_panel(), "Dr. A")
        layout.addWidget(self.tabs, 1)

        actions = QHBoxLayout()
        self.profile_combo = QComboBox()
        self.compare_combo = QComboBox()
        actions.addWidget(self.profile_combo, 2)
        actions.addWidget(self.compare_combo, 2)

        save_snapshot = QPushButton()
        save_snapshot.setProperty("ui_key", "save_profile")
        save_snapshot.clicked.connect(self.save_snapshot)
        load_snapshot = QPushButton()
        load_snapshot.setProperty("ui_key", "load_saved_profile")
        load_snapshot.clicked.connect(self.load_snapshot)
        compare_snapshot = QPushButton()
        compare_snapshot.setProperty("ui_key", "compare_profiles")
        compare_snapshot.clicked.connect(self.compare_snapshot)
        delete_snapshot = QPushButton()
        delete_snapshot.setProperty("ui_key", "delete_profile")
        delete_snapshot.clicked.connect(self.delete_snapshot)
        export_pdf = QPushButton("PDF")
        export_pdf.clicked.connect(lambda: self.export_report("pdf"))
        export_docx = QPushButton("DOCX")
        export_docx.clicked.connect(lambda: self.export_report("docx"))

        for button in (
            save_snapshot,
            load_snapshot,
            compare_snapshot,
            delete_snapshot,
            export_pdf,
            export_docx,
        ):
            actions.addWidget(button)
        layout.addLayout(actions)
        self.render_empty()
        return container

    def _chat_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        notice = QLabel()
        notice.setProperty("ui_key", "assistant_disclaimer")
        notice.setWordWrap(True)
        layout.addWidget(notice)
        layout.addWidget(self.chat_view, 1)
        layout.addWidget(self.chat_input)
        send = QPushButton()
        send.setProperty("ui_key", "send_question")
        send.clicked.connect(self.ask_dr_a)
        layout.addWidget(send)
        return panel

    def render_empty(self) -> None:
        empty = f"<p>{escape_html(self.t('empty_profile'))}</p>"
        self.set_browser_html(self.summary_view, empty)
        self.set_browser_html(self.controls_view, empty)
        self.set_browser_html(self.events_view, empty)
        self.set_browser_html(self.timeline_view, empty)
        self.set_browser_html(self.chat_view, "")

    def _enforce_exclusive(self, name: str, changed: QCheckBox, checked: bool) -> None:
        if not checked:
            return
        exclusive = EXCLUSIVE_CHECKBOX_VALUES.get(name)
        if not exclusive:
            return
        changed_value = str(changed.property("answer_value"))
        for widget in self.field_widgets.get(name, []):
            if not isinstance(widget, QCheckBox) or widget is changed:
                continue
            widget_value = str(widget.property("answer_value"))
            if changed_value in exclusive or widget_value in exclusive:
                widget.blockSignals(True)
                widget.setChecked(False)
                widget.blockSignals(False)

    def collect_payload(self) -> dict[str, Any]:
        answers: dict[str, Any] = {}
        for section in QUESTIONNAIRE_SCHEMA:
            for question in section.questions:
                widgets = self.field_widgets[question.name]
                if question.type == "checkbox":
                    answers[question.name] = [
                        str(widget.property("answer_value"))
                        for widget in widgets
                        if isinstance(widget, QCheckBox) and widget.isChecked()
                    ]
                elif question.type == "radio":
                    selected = self.radio_groups[question.name].checkedButton()
                    answers[question.name] = (
                        str(selected.property("answer_value")) if selected else ""
                    )
                elif question.type == "textarea":
                    answers[question.name] = widgets[0].toPlainText().strip()
                else:
                    answers[question.name] = widgets[0].text().strip()
        return {
            "questionnaire": QUESTIONNAIRE_NAME,
            "version": QUESTIONNAIRE_VERSION,
            "completed_at": datetime.now(UTC).isoformat(),
            "answers": answers,
        }

    def populate_questionnaire(self, payload: dict[str, Any]) -> None:
        self.is_populating = True
        answers = payload.get("answers") or {}
        try:
            for section in QUESTIONNAIRE_SCHEMA:
                for question in section.questions:
                    value = answers.get(question.name, [] if question.type == "checkbox" else "")
                    widgets = self.field_widgets[question.name]
                    if question.type == "checkbox":
                        selected = set(value if isinstance(value, list) else [])
                        for widget in widgets:
                            widget.setChecked(str(widget.property("answer_value")) in selected)
                    elif question.type == "radio":
                        for widget in widgets:
                            widget.setChecked(str(widget.property("answer_value")) == value)
                    elif question.type == "textarea":
                        widgets[0].setPlainText(str(value or ""))
                    else:
                        widgets[0].setText(str(value or ""))
        finally:
            self.is_populating = False
        self.current_questionnaire = payload

    def evaluate_current_form(self) -> None:
        self.run_evaluation(self.collect_payload())

    def run_evaluation(self, payload: dict[str, Any]) -> None:
        self.set_assessment_state("running")
        worker = FunctionWorker(evaluate_payload, payload)
        worker.signals.finished.connect(self.on_evaluation_ready)
        worker.signals.failed.connect(self.show_error)
        self.thread_pool.start(worker)

    def on_evaluation_ready(self, evaluation: dict[str, Any]) -> None:
        self.current_evaluation = evaluation
        self.current_questionnaire = evaluation.get("questionnaire_payload")
        self.chat_history.clear()
        self.render_evaluation(evaluation)
        self.set_assessment_state("clean")

    def render_evaluation(self, evaluation: dict[str, Any]) -> None:
        ctx = evaluation.get("dashboard_context") or {}
        memory = evaluation.get("company_memory") or {}
        score = ctx.get("compliance_score") or {}
        feed_meta = evaluation.get("feed_meta") or {}
        self.set_browser_html(
            self.summary_view,
            f"""
            <h2>{escape_html(str(ctx.get("company_name") or "Profilo"))}</h2>
            <p><b>{escape_html(self.t("compliance_score"))}:</b>
            {escape_html(str(score.get("score", "n/d")))}
            ({escape_html(self.tr(score.get("band", "n/d")))})</p>
            <p><b>{escape_html(self.t("personalized_feed"))}:</b>
            {escape_html(str(feed_meta.get("mode", "n/d")))}</p>
            <p><b>{escape_html(self.t("relevant_tags"))}:</b>
            {escape_html(", ".join(ctx.get("relevance_tags") or []))}</p>
            """,
        )

        warnings = ctx.get("risk_warnings") or []
        controls = memory.get("controls") or {}
        warning_html = "".join(
            "<li><b>{}</b> [{}]<br>{}</li>".format(
                escape_html(self.tr(item.get("title", "Warning"))),
                escape_html(self.tr(item.get("level", ""))),
                escape_html(self.tr(item.get("description", ""))),
            )
            for item in warnings
        )
        self.set_browser_html(
            self.controls_view,
            f"<h2>{escape_html(self.t('warnings'))}</h2>"
            + (
                f"<ul>{warning_html}</ul>"
                if warning_html
                else f"<p>{escape_html(self.t('empty_profile'))}</p>"
            )
            + f"<h2>{escape_html(self.t('existing_controls'))}</h2>"
            + html_list([self.tr(item) for item in list(controls.get("existing") or [])])
            + f"<h2>{escape_html(self.t('missing_controls'))}</h2>"
            + html_list(
                [self.tr(item) for item in list(controls.get("missing_or_to_verify") or [])]
            ),
        )

        events = ctx.get("matched_regulatory_events") or []
        news = ctx.get("matched_news_feed") or []
        early = ctx.get("matched_early_warnings") or []
        self.set_browser_html(
            self.events_view,
            f"<h2>{escape_html(self.t('regulatory_events'))}</h2>"
            + self._render_feed(events)
            + f"<h2>{escape_html(self.t('filtered_news'))}</h2>"
            + self._render_feed(news)
            + f"<h2>{escape_html(self.t('early_warning_title'))}</h2>"
            + self._render_feed(early),
        )

        timeline = ctx.get("compliance_timeline") or []
        timeline_html = ""
        for item in timeline:
            status, title = localize_timeline_item(self.language, item)
            timeline_html += "<li><b>{}</b> - {}<br>{}</li>".format(
                escape_html(str(item.get("date", ""))),
                escape_html(title),
                escape_html(status),
            )
        self.set_browser_html(
            self.timeline_view,
            f"<ul>{timeline_html}</ul>"
            if timeline_html
            else f"<p>{escape_html(self.t('empty_profile'))}</p>",
        )

    def _render_feed(self, items: list[dict[str, Any]]) -> str:
        if not items:
            return "<p>Nessun elemento.</p>"
        rendered = []
        for item in items:
            title = escape_html(str(item.get("title", "Fonte")))
            summary = escape_html(self.tr(item.get("summary") or item.get("description") or ""))
            url = str(item.get("url") or item.get("source_url") or "")
            link = f'<br><a href="{escape_html(url)}">{escape_html(url)}</a>' if url else ""
            rendered.append(f"<li><b>{title}</b><br>{summary}{link}</li>")
        return "<ul>" + "".join(rendered) + "</ul>"

    def load_demo(self, profile_id: str) -> None:
        try:
            payload = load_demo_profile(profile_id)
            self.populate_questionnaire(payload)
            self.set_active_demo(profile_id)
            self.run_evaluation(payload)
        except ValueError as exc:
            self.show_error(str(exc))

    def load_questionnaire_file(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self, "Carica questionario", str(ROOT), "JSON (*.json)"
        )
        if not filename:
            return
        try:
            payload = json.loads(Path(filename).read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Il file deve contenere un oggetto JSON.")
            self.set_active_demo(None)
            self.populate_questionnaire(payload)
            self.run_evaluation(payload)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            self.show_error(str(exc))

    def save_questionnaire_file(self) -> None:
        payload = self.collect_payload()
        company = slug(str((payload.get("answers") or {}).get("company_name") or "azienda"))
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salva questionario",
            str(ROOT / f"questionario-{company}.json"),
            "JSON (*.json)",
        )
        if not filename:
            return
        Path(filename).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def save_snapshot(self) -> None:
        if not self.current_evaluation:
            self.show_error("Calcola una valutazione prima di salvarla.")
            return
        snapshot = save_profile_snapshot(PROFILE_HISTORY_DIR, self.current_evaluation)
        self._refresh_profiles()
        self.setWindowTitle(f"Dr. G.D.P.R. & AI Act navigator - {snapshot['id']}")

    def _refresh_profiles(self) -> None:
        profiles = list_profile_snapshots(PROFILE_HISTORY_DIR)
        for combo in (self.profile_combo, self.compare_combo):
            combo.clear()
            combo.addItem(self.t("saved_profiles"), "")
            for profile in profiles:
                label = f"{profile.get('company_name')} - {profile.get('saved_at')}"
                combo.addItem(label, profile.get("id"))

    def load_snapshot(self) -> None:
        profile_id = self.profile_combo.currentData()
        if not profile_id:
            self.show_error("Seleziona uno snapshot da caricare.")
            return
        try:
            stored = load_profile_snapshot(PROFILE_HISTORY_DIR, str(profile_id))
            questionnaire = stored.get("questionnaire_payload")
            if not isinstance(questionnaire, dict):
                raise ValueError("Snapshot non valido.")
            self.populate_questionnaire(questionnaire)
            self.run_evaluation(questionnaire)
        except ValueError as exc:
            self.show_error(str(exc))

    def compare_snapshot(self) -> None:
        if not self.current_evaluation:
            self.show_error("Carica o calcola il profilo corrente prima del confronto.")
            return
        older_id = self.compare_combo.currentData()
        if not older_id:
            self.show_error("Seleziona lo snapshot di confronto.")
            return
        try:
            older = load_profile_snapshot(PROFILE_HISTORY_DIR, str(older_id))
            questionnaire = older.get("questionnaire_payload")
            if not isinstance(questionnaire, dict):
                raise ValueError("Snapshot non valido.")
            comparison = compare_evaluations(
                evaluate_payload(questionnaire),
                self.current_evaluation,
                str(older_id),
                "profilo corrente",
            )
            self.summary_view.append(
                "<h2>Confronto snapshot</h2>"
                f"<p><b>Delta score:</b> {comparison['score_delta']}</p>"
                f"<p><b>Nuovi tag:</b> {escape_html(', '.join(comparison['added_tags']) or 'nessuno')}</p>"
                f"<p><b>Controlli risolti:</b> {escape_html(', '.join(comparison['resolved_controls']) or 'nessuno')}</p>"
            )
        except ValueError as exc:
            self.show_error(str(exc))

    def delete_snapshot(self) -> None:
        profile_id = self.profile_combo.currentData()
        if not profile_id:
            self.show_error("Seleziona uno snapshot da eliminare.")
            return
        if (
            QMessageBox.question(self, "Elimina snapshot", "Eliminare lo snapshot selezionato?")
            != QMessageBox.StandardButton.Yes
        ):
            return
        try:
            delete_profile_snapshot(PROFILE_HISTORY_DIR, str(profile_id))
            self._refresh_profiles()
        except ValueError as exc:
            self.show_error(str(exc))

    def export_report(self, report_format: str) -> None:
        if not self.current_questionnaire:
            self.show_error("Calcola o carica un questionario prima dell'export.")
            return
        company = slug(
            str((self.current_questionnaire.get("answers") or {}).get("company_name") or "company")
        )
        extension = "pdf" if report_format == "pdf" else "docx"
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Esporta report",
            str(ROOT / f"compliance-report-{company}.{extension}"),
            f"{extension.upper()} (*.{extension})",
        )
        if not filename:
            return
        try:
            evaluation = build_export_evaluation(
                {"questionnaire_payload": self.current_questionnaire}
            )
            data = (
                build_pdf_report(evaluation, language=self.language)
                if report_format == "pdf"
                else build_docx_report(evaluation, language=self.language)
            )
            Path(filename).write_bytes(data)
            self.setWindowTitle(f"Dr. G.D.P.R. & AI Act navigator - {Path(filename).name}")
        except ValueError as exc:
            self.show_error(str(exc))

    def ask_dr_a(self) -> None:
        if not self.current_questionnaire:
            self.show_error("Calcola un profilo prima di fare domande a Dr. A.")
            return
        message = self.chat_input.toPlainText().strip()
        if not message:
            return
        self.chat_input.clear()
        self.chat_view.append(self.chat_message_html(self.t("you"), message, user=True))
        worker = FunctionWorker(self._build_chat_reply, message, self.current_questionnaire)
        worker.signals.finished.connect(self.on_chat_reply)
        worker.signals.failed.connect(self.show_error)
        self.thread_pool.start(worker)

    def _build_chat_reply(
        self, message: str, questionnaire_payload: dict[str, Any]
    ) -> tuple[str, list[dict[str, Any]], str]:
        context = evaluate_payload(questionnaire_payload)
        validation_context = dict(context)
        validation_context["active_user_message"] = message
        chat_request = DR_A_AGENT.prepare_request(
            validation_context,
            message,
            self.chat_history[-8:],
            build_sources=build_chat_sources,
            select_sources=select_supported_sources,
            build_messages=build_chat_messages,
        )
        if chat_request.blocked_reply:
            return message, [], chat_request.blocked_reply
        validation_context["selected_chat_sources"] = chat_request.sources
        reply = generate_grounded_reply(chat_request.messages, validation_context)
        return message, DR_A_AGENT.cited_sources(chat_request.sources, reply), reply

    def on_chat_reply(self, result: tuple[str, list[dict[str, Any]], str]) -> None:
        message, sources, reply = result
        self.chat_history.extend(
            [{"role": "user", "content": message}, {"role": "assistant", "content": reply}]
        )
        source_html = ""
        if sources:
            source_html = (
                "<ul>"
                + "".join(
                    f'<li><a href="{escape_html(str(source.get("url", "")))}">'
                    f"{escape_html(str(source.get('title', 'Fonte')))}</a></li>"
                    for source in sources
                )
                + "</ul>"
            )
        self.chat_view.append(
            self.chat_message_html(os.getenv("ASSISTANT_NAME", DEFAULT_ASSISTANT_NAME), reply)
            + source_html
        )

    def _update_model_status(self) -> None:
        status = local_model_runtime_status()
        available = (
            status.get("model_configured")
            and status.get("model_reachable")
            and status.get("model_available") is not False
        )
        self.model_status.setText(
            self.desktop_text("model_ready") if available else self.t("qwen_missing")
        )

    def show_error(self, message: str) -> None:
        if isinstance(message, LocalModelError):
            message = str(message)
        QMessageBox.warning(self, "Dr. A", str(message))
        if self.assessment_state == "running":
            self.set_assessment_state("dirty")


def main() -> int:
    os.environ.setdefault("ASSISTANT_NAME", DEFAULT_ASSISTANT_NAME)
    os.environ.setdefault("LOCAL_MODEL_NAME", os.getenv("QWEN_MODEL", "qwen2.5:14b-instruct"))
    os.environ.setdefault(
        "LOCAL_MODEL_ENDPOINT",
        os.getenv("QWEN_ENDPOINT", "http://localhost:11434/v1/chat/completions"),
    )
    app = QApplication(sys.argv)
    window = DesktopDashboard()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
