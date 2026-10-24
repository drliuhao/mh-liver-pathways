# Electronic recording-template source

Canonical authoring files are in `standard_protocol_website/src` in the local transplant-protocol workspace. This snapshot preserves the generator, typed-field configuration, HTML renderer and browser assets with the published site.

Build the canonical site with `python3 build.py`, export with `tools/build_portal.py <canonical-dist>`, then run `tools/validate_portal.py <canonical-dist>`, `tools/validate_recording_templates.py`, and `node tools/test_electronic_forms.cjs`.

Browser validation uses synthetic data only: dropdowns, decimals and integer zero, repeat entries, sign-off reset, JSON save/reopen, completed note, print and CSV. No completed clinical records belong in this repository.
