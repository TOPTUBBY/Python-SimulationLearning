# Version control and releases

## Branch convention

- `main`: stable version people should download.
- `develop/v1.4.0`: recommended next release work (create if needed).
- `feature/<name>` / `fix/<name>`: short-lived feature/fix branches; PR into the active development branch.

## Versioning

Use Semantic Versioning (`MAJOR.MINOR.PATCH`) for this **launcher/mirror toolkit**, independent of upstream website version numbers:

- Patch: compatibility/bug fixes without new features.
- Minor: new site, new optional functionality, backwards-compatible improvement.
- Major: breaking layout or config/CLI change.

For every release: update the root `VERSION`, the `VERSION` constant in `tools/clone_runtime.py`, and `CHANGELOG.md`; run tests. Do not copy/mirror third-party assets into git.

## Suggested commands

```bash
python -m unittest discover -s tests -v
git switch main
git pull --ff-only
git switch -c develop/v1.4.0
# edit and test; create PR back to main
git switch main
git pull --ff-only
git tag -a v1.4.0 -m "SimulationLearning v1.4.0"
git push origin main v1.4.0
```

## Release verification checklist

- Tests pass; every `config.json` has unique ID and port.
- Each Launcher opens the expected localhost route and does not open a blank browser page when cache is absent.
- First-run downloads work on a networked Windows PC, with console warnings reviewed.
- Verify each site's main lesson/simulation and reload; close CMD and re-open Launcher.
- Offline test after initial download; identify features requiring live APIs.
- Confirm no `site/`, personal data, credential or vendor license-unknown assets are tracked.
- Update README and changelog, review diff, then merge/tag.
