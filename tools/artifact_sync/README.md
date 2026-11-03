# Artifact synchronization

Current Word and PowerPoint masters are held in the sibling V19_consistent_release_2026-11-03 directory. The exact private inventories, frozen review proposals, authoring receipts and validation reports remain in this local directory and Artifact_Sync_2026-11-02; they are excluded from Git. Source methods: sync_words.py, prepare_decks.py, package_deck.py and build_release.py. PowerPoint text and added cards were authored with the presentation artifact API and merged into original packages to preserve native objects.

Run tools/test_artifact_sync.py before publishing. Clinical source changes require updating affected current artifacts and renewing tools/artifact_release_manifest.json; the test does not substitute for clinical reconciliation.
