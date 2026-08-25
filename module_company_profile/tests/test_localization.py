import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCALES_DIR = ROOT / "module_company_profile" / "dashboard" / "assets" / "js" / "i18n" / "locales"
CORE_JS = ROOT / "module_company_profile" / "dashboard" / "assets" / "js" / "core.js"
I18N_CORE_JS = ROOT / "module_company_profile" / "dashboard" / "assets" / "js" / "i18n" / "core.js"
EVENTS_JS = ROOT / "module_company_profile" / "dashboard" / "assets" / "js" / "events.js"
EXPECTED_LOCALES = {
    "bg",
    "cs",
    "da",
    "de",
    "el",
    "en",
    "es",
    "et",
    "fi",
    "fr",
    "ga",
    "hr",
    "hu",
    "it",
    "lt",
    "lv",
    "mt",
    "nl",
    "pl",
    "pt",
    "ro",
    "sk",
    "sl",
    "sq",
    "sv",
}
MUST_TRANSLATE_UI_KEYS = {
    "profile_saved",
    "profile_loaded",
    "confirm_delete_profile",
    "profile_deleted",
    "select_two_profiles",
    "score_change",
    "added_tags",
    "removed_tags",
    "resolved_controls",
    "new_missing_controls",
    "comparison_ready",
    "report_download_started",
    "report_disclaimer",
    "early_warning_title",
    "early_warning_notice",
    "source_status",
    "progress_tab",
    "progress_title",
    "progress_intro",
    "progress_disclaimer",
    "control_coverage",
    "priority_distribution",
    "snapshot_trend",
    "deadline_outlook",
}


def load_locale(path: Path) -> tuple[str, dict]:
    source = path.read_text(encoding="utf-8")
    match = re.search(
        r'window\.ComplianceLocales\["([a-z]{2})"\]\s*=\s*(\{.*\});\s*$',
        source,
        flags=re.DOTALL,
    )
    if not match:
        raise AssertionError(f"Invalid locale module: {path.name}")
    return match.group(1), json.loads(match.group(2))


class LocalizationIntegrityTests(unittest.TestCase):
    locales: dict[str, dict]

    @classmethod
    def setUpClass(cls):
        cls.locales = dict(load_locale(path) for path in sorted(LOCALES_DIR.glob("*.js")))

    def test_all_supported_locales_are_present(self):
        self.assertEqual(EXPECTED_LOCALES, set(self.locales))

    def test_every_locale_contains_the_complete_ui_contract(self):
        required_keys = set(self.locales["en"]["ui"])
        for code, locale in self.locales.items():
            with self.subTest(locale=code):
                self.assertEqual(required_keys, set(locale["ui"]))
                self.assertTrue(all(str(value).strip() for value in locale["ui"].values()))

    def test_every_non_italian_questionnaire_has_the_same_keys(self):
        required_keys = set(self.locales["en"]["questionnaire"])
        self.assertEqual(107, len(required_keys))
        for code, locale in self.locales.items():
            if code == "it":
                continue
            with self.subTest(locale=code):
                self.assertEqual(required_keys, set(locale["questionnaire"]))
                self.assertTrue(
                    all(str(value).strip() for value in locale["questionnaire"].values())
                )

    def test_every_locale_contains_the_complete_dynamic_result_dictionary(self):
        required_keys = set(self.locales["en"]["results"])
        self.assertEqual(48, len(required_keys))
        for code, locale in self.locales.items():
            with self.subTest(locale=code):
                self.assertEqual(required_keys, set(locale["results"]))
                self.assertTrue(all(str(value).strip() for value in locale["results"].values()))

    def test_recent_ui_features_are_not_silently_left_in_english(self):
        english = self.locales["en"]["ui"]
        for code, locale in self.locales.items():
            if code == "en":
                continue
            with self.subTest(locale=code):
                untranslated = {
                    key for key in MUST_TRANSLATE_UI_KEYS if locale["ui"][key] == english[key]
                }
                self.assertFalse(untranslated)

    def test_locale_sources_do_not_contain_common_mojibake_sequences(self):
        broken_sequences = ("Ã ", "Ã¨", "Ã©", "Ã¬", "Ã²", "Ã¹", "â€™", "â€œ", "â€")
        for path in sorted(LOCALES_DIR.glob("*.js")):
            with self.subTest(locale=path.stem):
                source = path.read_text(encoding="utf-8")
                self.assertFalse(
                    any(sequence in source for sequence in broken_sequences),
                    f"Broken UTF-8 text found in {path.name}",
                )

    def test_zero_scores_and_italian_dynamic_results_have_rendering_support(self):
        core_source = CORE_JS.read_text(encoding="utf-8")
        i18n_source = I18N_CORE_JS.read_text(encoding="utf-8")
        italian_results = self.locales["it"]["results"]
        self.assertIn('String(value ?? "")', core_source)
        self.assertNotIn("relevance_tags.slice(0, 3)", core_source)
        self.assertIn("trResult(score.label)", core_source)
        self.assertIn("trResult(item.message)", core_source)
        self.assertIn("localeResultTranslations", i18n_source)
        self.assertEqual(
            "Nessun avviso rilevante dalle risposte attuali",
            italian_results["No major warning from current answers"],
        )
        dpia_message = italian_results[
            "The selected answers indicate DPIA screening factors, but the "
            "questionnaire alone does not establish that a full DPIA is mandatory. "
            "A DPIA is required when the planned processing is likely to result in "
            "high risk; prior consultation follows only when the DPIA identifies high "
            "residual risk without adequate mitigation."
        ]
        self.assertIn("la consultazione preventiva segue solo", dpia_message)

    def test_dynamic_snapshot_placeholders_remain_localizable(self):
        events_source = EVENTS_JS.read_text(encoding="utf-8")
        self.assertEqual(2, events_source.count('data-i18n="saved_profiles"'))
        self.assertEqual(2, events_source.count('data-i18n="compare_with"'))


if __name__ == "__main__":
    unittest.main()
