import os
import glob
import sys

import yaml

DEFAULT_SOURCE = {
    "source_active_1": True,
    "source_organisation_1": "United Nations Global SDG Database (UNSD/UN DESA Statistics Division)",
    "source_url_1": "https://unstats.un.org/sdgs/unsdg/",
    "source_url_text_1": "UN Global SDG Database",
    "source_statistical_classification_1": "Official statistics",
    "source_geographical_coverage_1": "Kenya (global series)",
    "source_contact_1": "",
    "source_release_date_1": "",
    "source_next_release_1": "",
}

SOURCE_KEYS_PREFIXES = ("source_active_", "source_organisation_", "source_url_", "source_url_text_")

def has_any_source(d: dict) -> bool:
    # If any common source keys exist, we assume user is managing sources per-indicator
    for k in d.keys():
        if k.startswith(SOURCE_KEYS_PREFIXES):
            return True
    return False

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder = os.path.join(root, "indicator-config")
    files = sorted(glob.glob(os.path.join(folder, "*.yml")) + glob.glob(os.path.join(folder, "*.yaml")))

    if not files:
        print(f"[apply_default_sources] No YAML files found in {folder}")
        return 0

    changed = 0
    skipped = 0

    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        if not isinstance(data, dict):
            print(f"[apply_default_sources] Skipping non-dict YAML: {path}")
            skipped += 1
            continue

        # If the indicator already has any source fields, do nothing.
        if has_any_source(data):
            skipped += 1
            continue

        # Add default source fields at the end.
        for k, v in DEFAULT_SOURCE.items():
            data[k] = v

        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(
                data,
                f,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False,
                width=120,
            )

        changed += 1

    print(f"[apply_default_sources] Updated: {changed}, Skipped: {skipped}, Total: {len(files)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
