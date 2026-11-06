# Property Photo QA Workbench

Before publishing a catalogue, review its photography as a batch: broken files, images below your requested size, exact duplicates, visual similarity candidates and potentially private GPS metadata. The result is a portable HTML contact sheet with property filters, plus a JSON issue report.

## Start

Python 3.10+ and Pillow 10–12:

```sh
pip install .
property-photo-qa ./photos --out ./review --mapping examples/mapping.csv
```

Open `review/report.html` in your browser. Exit0 means no configured flags, exit1 means review is required, exit2 means invalid invocation. Photos remain unchanged. No network, upload, tracking, account or API key is used by the audit. The report contains embedded thumbnails; keep it private when your photos are private.

## What reviewers can do

Filter the contact sheet by property or review flagged files only. Inspect original relative file names, dimensions and issue categories. Review exact-byte duplicate pairs separately from visually similar candidates. A cross-property flag draws attention to shared images assigned to different property IDs; shared amenity or stock imagery may be legitimate.

Mapping CSV columns are `relative_path,property_id`, using forward slashes. Every mapping path must be unique; unmapped files remain `unassigned`. Unused mappings are reported. Thresholds are caller choices, not a portal's required standard. JPEG, PNG, WebP and TIFF are supported.

## Limits worth understanding

Exact duplicates use SHA-256. Similarity uses a 64-bit difference hash and is a candidate-generation heuristic: plain walls, repeated layouts and heavily edited copies can confuse it. No automatic deletion, copyright decision, room classification or quality score is produced. There is no blur or authenticity claim.

EXIF orientation is applied only to generated thumbnails; original bytes remain untouched. GPS is reported as a boolean, never as coordinates. Ordinary thumbnails are re-encoded without original metadata. The configured per-file byte limit is30MB; Pillow's decompression-bomb limits remain enabled. At most1000 images per audit by default; pairwise matching is quadratic, so split larger catalogues deliberately. Do not point the scanner at a folder being modified by an untrusted process.

## Development

`python -m unittest discover -s tests -v` exercises corruption, duplicates, GPS flags, mapping conflicts, report escaping and unchanged source files. [Report contract](docs/report.md) · [Privacy and review workflow](docs/privacy.md).

Developed by [NovAsia Estate](https://novasia.estate/), a publisher of property guides and research for Cambodia, Thailand and Bali. This tool contains no inventory or market claims. MIT licensed.
