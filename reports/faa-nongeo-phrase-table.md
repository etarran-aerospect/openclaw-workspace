# Non-Geo BVLOS Phrase Table (working draft)

- Source corpus: FAA Part 107 waivers issued page (1,891 rows; 771 include §107.31), scraped through Jan 2026 rows currently published.
- This table is **phrase-driven** and conservative; many broad-scope waivers may not include explicit non-geo wording in public CoW PDF text.

| Issue | Waiver ID | Operator | Reg | Confidence | Phrase hit(s) | PDF |
|---|---|---|---|---|---|---|
| 2023-11-03 | 107W-2023-02725 | ReadyMonitor, LLC | 107.31 | High | non-geo | https://www.faa.gov/sites/faa.gov/files/107W-2023-02725_Jesse_Stepler_CoW.pdf |
| 2022-09-14 | 107W-2022-01839 | Alliance Engineering + Planning, LLC | 107.31, 107.33(b)(c)(2) | Context | lja-lineage (Robert Wilhite) | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01839_Robert_Wilhite_CoW.pdf |
| 2024-09-13 | 107W-2024-02438 | LJA | 107.31, 107.33(b)&(c)(2) | Context | lja-lineage (Robert Wilhite) | https://www.faa.gov/sites/faa.gov/files/107W-2024-02438%20Robert%20Wilhite%20-%20CoW.pdf |
| 2025-11-13 | 107W-2025-03708 | LJA | 107.31, 107.33 | Context | lja-lineage (Robert Wilhite) | https://www.faa.gov/sites/faa.gov/files/107W-2025-03708-Robert-Wilhite-CoW.pdf |

## Notes
- `High` = explicit target phrase found in public PDF text (`non-geo`, `non-geographic`, or `not geographically limited`).
- `Context` = included because operator lineage/public claims indicate non-geo scope, even if the exact phrase does not appear in public CoW text.
- Public FAA data does not provide an official `non-geo` flag, so exact official counts require FAA confirmation or manual legal review of each waiver package.
