# Recording-template source

Canonical authoring files live in `standard_protocol_website/src` in the local transplant-protocol workspace. This snapshot preserves the generator and its two assets with the published website.

The generator consumes the existing pathway `index` and `sources` data and writes 46 blank HTML/Markdown templates plus seven ZIP research kits. It adds documentation fields without changing clinical criteria.

Regenerate the canonical site with `python3 build.py`, export with `tools/build_portal.py <canonical-dist>`, then run `tools/validate_portal.py <canonical-dist>` and `tools/validate_recording_templates.py`. Review browser navigation, copy, download and print before publication.

No completed patient forms belong in this repository.
