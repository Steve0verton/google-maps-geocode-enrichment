# Changelog

All notable changes to this repository will be documented in this file.

The format of this Changelog is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). This changelog and project repository adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Don’t let your friends dump git logs into changelogs.

## Unreleased

The project is **archived**. This entry records a documentation and repository-hygiene
pass only — no application code was modified, and nothing in `lib/`, `cluster/` or `test/`
changed behaviour.

### Changed
- Repository transferred from `Steve0verton` to the **`overtonlabs`** organization. GitHub
  redirects the previous URL, and the GitHub Pages site moved to
  <https://overtonlabs.github.io/google-maps-geocode-enrichment/>.
- README now opens with an **archival notice** and a **Project Status** section stating what
  the project was built against (Python 3.6, PostgreSQL 11, Kafka 2.x, Docker Compose v1)
  and which parts of the ecosystem have since moved on.
- README "Python Requirements" no longer claims the application needs "the latest version of
  Python". The runtime is pinned to `python:3.6` in `lib/Dockerfile`; the container image is
  what actually runs the code.

### Fixed
- **Broken README link.** The Geocode Library build step linked to
  `./lib/geocode_lib/Dockerfile`, which has never existed. The file is `./lib/Dockerfile`.
- **Two broken in-page anchors.** The table of contents linked to `#reflocation-table` and
  the Technical Component Overview to `#reflocation`. GitHub preserves underscores when it
  generates heading anchors, so the correct target is `#ref_location-table`. Both links had
  silently gone nowhere.
- **Kafka partition commands.** `docker exec -it infra_kafka_1` assumes Docker Compose v1
  container naming (v2 uses hyphens), and `kafka-topics.sh --zookeeper` was removed in Kafka
  3.0. Both commands are kept for the historical record with the modern equivalent shown
  alongside.

### Documented
These are pre-existing defects, now written down rather than repaired. Repairing them would
require running the stack end-to-end, which is no longer possible with the pinned images.
- **Seeded sample data loads two columns swapped.** `test/postgres_db/init.sql` declares
  `location_type` before `enrichment_api_response`; both sample CSVs order them the other
  way. `seed.sh` uses `COPY … CSV HEADER`, which maps columns **by position** — the header
  row is skipped, not used for matching. Both columns are `jsonb`, so the load succeeds and
  the values land in each other's column.
- **`ref_location_sample_10k.csv` cannot be loaded into the current table** — it has 44
  columns against the table's 45, predating the `location_type` column.
- **`test/geocode_lib/` is a byte-for-byte duplicate of `lib/geocode_lib/`** with nothing
  keeping the two in sync.
- **API credentials are documented as going into a git-tracked file.** The README's
  instruction to place a live Google Maps key and database password in
  `cluster/app/docker-compose.yml` now carries a warning. This is the first item in
  `TODO.md` and was never resolved.

### Added
- `.github/workflows/ci.yml` — validates that every Python file parses, every YAML file is
  well-formed, and every relative link, image and in-page anchor in the Markdown resolves.
  It deliberately does **not** attempt to run the application: the pinned stack cannot be
  provisioned on a current runner, and the module requires a live Google Maps API key and a
  PostgreSQL instance. A green badge here means the repository is internally consistent, not
  that the enrichment pipeline works.
- README badges for CI status, licence, Python version and archival status.
- `.gitattributes` enforcing the LF line endings the README's own **Standards** section
  requires, which nothing previously enforced.
- `.gitignore` entries for `__pycache__/`, `.env`, virtual environments and build artefacts.

## 1.0.0 (January 1, 2020)
[Full Changelog](https://github.com/overtonlabs/google-maps-geocode-enrichment/commit/099b1c1e4b7c01f7f16f5869d2615126dc6d9999)
### Added
- Initial fork based on module from 6 Degree Intelligence solution
