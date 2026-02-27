# FAA BVLOS §107.31 Waiver Recheck (phrase-based)

Phrase logic:
- Keep when text contains plural locations phrase, or Multi-location / Non-Geo / nationwide language.
- Remove when only singular location limitation phrase is present and no override language.

- Input rows scanned: 226
- Non-geo positives: 10
- Geo-single removed: 54
- Excluded (no explicit phrase): 162

## Non-geo positives

| Issue | Waiver ID | Company | Reason | PDF |
|---|---|---|---|---|
| 2023-11-03 | 107W-2023-02725 | ReadyMonitor, LLC | multi[-\s]?location; non[-\s]?geo | https://www.faa.gov/sites/faa.gov/files/107W-2023-02725_Jesse_Stepler_CoW.pdf |
| 2025-04-23 | 107W-2025-00848-Heath-McLemore-CoW | Florida Power & Light Company | nationwide | https://www.faa.gov/sites/faa.gov/files/107W-2025-00848-Heath-McLemore-CoW.pdf |
| 2025-05-07 | 107W-2025-00857-Heath-McLemore-CoW | Florida Power & Light Company | nationwide | https://www.faa.gov/sites/faa.gov/files/107W-2025-00857-Heath-McLemore-CoW.pdf |
| 2022-05-10 | 107W-2022-00350 | Asylon | operations conducted under this waiver are limited to the locations described in the waiver application; limited to the  | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-00350_Brent_McLaughlin_CoW.pdf |
| 2022-07-19 | 107W-2022-01284 | Davey Resource Group | operations conducted under this waiver are limited to the locations described in the waiver application; limited to the  | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01284_Rachel_Miller_CoW.pdf |
| 2022-12-14 | 107W-2022-00386 | InDro Robotics Inc. | operations conducted under this waiver are limited to the locations described in the waiver application; limited to the  | https://www.faa.gov/sites/faa.gov/files/107W-2022-00386_Philip_Reece_CoW.pdf |
| 2023-02-07 | 107W-2022-02628 | Aims Community College | operations conducted under this waiver are limited to the locations described in the waiver application; limited to the  | https://www.faa.gov/sites/faa.gov/files/107W-2022-02628_Jacob_Marshall_CoW.pdf |
| 2023-04-28 | 107W-2023-00465 | Phillip A.B. McCoy | operations conducted under this waiver are limited to the locations described in the waiver application; limited to the  | https://www.faa.gov/sites/faa.gov/files/107W-2023-00465_Phillip_McCoy_CoW.pdf |
| 2023-05-25 | 107W-2023-01262 | Asylon | operations conducted under this waiver are limited to the locations described in the waiver application; limited to the  | https://www.faa.gov/sites/faa.gov/files/107W-2023-01262_Brent_McLaughlin_CoW.pdf |
| 2024-01-10 | 107W-2024-00078 | Zipline International Inc. | operations conducted under this waiver are limited to the locations described in the waiver application; limited to the  | https://www.faa.gov/sites/faa.gov/files/107W-2024-00078_Eugene_McGuinness_CoW.pdf |

## Geo-single removed

| Issue | Waiver ID | Company | Reason | PDF |
|---|---|---|---|---|
| 2022-02-08 | 107W-2022-00025 | Christopher Duncan | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-00025_Christopher_Duncan_CoW.pdf |
| 2022-04-04 | 107W-2022-00214 | Massachusetts Dept of Transportation - Aeronautics Division UAS | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-00214_Jeffrey_DeCarlo_CoW.pdf |
| 2022-04-07 | 107W-2022-00254 | Unmanned Safety Institute | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-00254_Devin_Allen_CoW.pdf |
| 2022-04-20 | 107W-2022-00623 | Northern Plains UAS Test Site | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-00623_Erin_Roesler_CoW.pdf |
| 2022-05-03 | 107W-2022-00219 | SkyBridge Tactical | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-00219_Bryan_Andrews_CoW.pdf |
| 2022-05-13 | 107W-2022-00607 | New Jersey Transit Corporation | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-00607_Andrew_Schwartz_CoW.pdf |
| 2022-07-01 | 107W-2022-01172 | 42air | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01172_Russell_Randol_CoW.pdf |
| 2022-07-01 | 107W-2022-01204 | Kansas State University | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01204_Spencer_Schrader_CoW.pdf |
| 2022-07-07 | 107W-2022-01103 | American Water | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01103_Christopher_Kahn_CoW.pdf |
| 2022-07-18 | 107W-2022-00970 | Asylon | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-00970_Brent_McLaughlin_CoW.pdf |
| 2022-07-18 | 107W-2022-01031 | Evergy | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01031_Michael_Kelly_CoW.pdf |
| 2022-07-18 | 107W-2022-01129 | Thomas Walls | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01129_Thomas_Walls_CoW.pdf |
| 2022-07-18 | 107W-2022-01194 | Weather Modification LLC | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01194_Alex_Sailsbury_CoW.pdf |
| 2022-08-12 | 107W-2022-01705 | The MITRE Corporation | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01705_Carrie_Rebhuhn_CoW.pdf |
| 2022-09-01 | 107W-2022-01798 | Soaring Eagle Technologies | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01798_Noah_Ruiz_CoW.pdf |
| 2022-09-06 | 107W-2022-01785 | Southern Company Services INC | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01785_Johnathan_Hitchcock_CoW.pdf |
| 2022-09-14 | 107W-2022-01839 | Alliance Engineering + Planning, LLC | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01839_Robert_Wilhite_CoW.pdf |
| 2022-09-22 | 107W-2022-01841 | Valmont | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01841_Joseph_George_CoW.pdf |
| 2022-10-17 | 107W-2022-01952 | Koch Industries Inc | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01952_Tim_Shanfelt_CoW.pdf |
| 2022-10-19 | 107W-2022-01953 | Koch Industries Inc | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/faa_migrate/part-107-waiver/media/107W-2022-01953_Tim_Shanfelt_CoW.pdf |
| 2022-10-20 | 107W-2022-01958 | Skydio Inc. | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2022-01958_Nicole_Bonk_CoW.pdf |
| 2022-10-25 | 107W-2022-02032 | Electric Power Board of Chattanooga | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2022-02032_Gregory_Phillips_CoW.pdf |
| 2022-10-26 | 107W-2022-02126 | AviSight | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2022-02126_William_Odonnell_CoW.pdf |
| 2022-10-27 | 107W-2022-02234 | Pacific Gas and Electric | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2022-02234_Kellen_Kirk_CoW.pdf |
| 2022-11-01 | 107W-2022-02235 | Pacific Gas and Electric | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2022-02235_Kellen_Kirk_CoW.pdf |
| 2022-11-03 | 107W-2022-02312 | Asylon | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2022-02312_Brent_McLaughlin_CoW.pdf |
| 2022-11-17 | 107W-2022-02062 | Thomas Swoyer | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2022-02062_Thomas_Swoyer_CoW.pdf |
| 2023-02-07 | 107W-2023-00074 | Areion UAS | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-00074_John_Huguley_CoW.pdf |
| 2023-02-08 | 107W-2023-00001 | Asylon | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-00001_Brent_McLaughlin_CoW.pdf |
| 2023-03-06 | 107W-2023-00071 | SkyBridge Tactical | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-00071_Bryan_Andrews_CoW.pdf |
| 2023-03-28 | 107W-2023-00403 | Tesla Inc | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-00403_Alistair_Weddell_CoW.pdf |
| 2023-03-30 | 107W-2023-00258 | Aerodyne Measure | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-00258_Andy_Justicia_CoW.pdf |
| 2023-04-28 | 107W-2023-00278 | BGE UAS | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-00278_Andrew_McCauley_CoW.pdf |
| 2023-05-25 | 107W-2023-00847 | Xcel Energy | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-00847_Thomas_Stegge_CoW.pdf |
| 2023-05-25 | 107W-2023-00993 | Xcel Energy | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-00993_Thomas_Stegge_CoW.pdf |
| 2023-06-05 | 107W-2023-00812 | Austin Seback | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-00812_Austin_Seback_CoW.pdf |
| 2023-06-06 | 107W-2023-01236 | Areion UAS | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-01236_John_Huguley_CoW.pdf |
| 2023-07-12 | 107W-2023-01367 | Jose Leandro | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-01367_Jose_Leandro_CoW.pdf |
| 2023-07-13 | 107W-2023-00822 | ERAU UAS-S Research | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-00822_Nickolas_Macchiarella_CoW.pdf |
| 2023-07-28 | 107W-2023-01602 | Caltrans DOC | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-01602_Aaron_Chamberlin_CoW.pdf |
| 2023-07-28 | 107W-2023-01641 | Florida Power & Light Company | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-01641_Eric_Schwartz_CoW.pdf |
| 2023-07-30 | 107W-2023-01075 | ComEd | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-01075_Victor_Migliore_CoW.pdf |
| 2023-08-02 | 107W-2023-01290 | Skydio Inc. | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-01290_Nicole_Bonk_CoW.pdf |
| 2023-08-04 | 107W-2023-01907 | Areion UAS | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-01907_John_Huguley_CoW.pdf |
| 2023-08-22 | 107W-2023-01737 | Pilot Institute | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-01737_Jason_Wood_CoW.pdf |
| 2023-10-19 | 107W-2023-02605 | Choctaw Nation of Oklahoma | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-02605_Marcus_Hartman_CoW.pdf |
| 2023-10-25 | 107W-2023-02015 | EpiSci | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-02015_Rohit_Pillai_CoW.pdf |
| 2024-01-31 | 107W-2023-02566 | Data Blanket | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-02566_Gur_Kimchi_CoW.pdf |
| 2024-02-27 | 107W-2023-03407 | American Robotics, Inc. | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-03407_James_Gonzalez_CoW.pdf |
| 2024-02-28 | 107W-2023-03494 | Big Sky Aerial Solutions | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-03494_Austin_Seback_CoW.pdf |
| 2024-02-29 | 107W-2023-03403 | HighPoint AeroTechnologies | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2023-03403_John_McClelland_CoW.pdf |
| 2024-03-13 | 107W-2024-00023 | COLSA | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2024-00023_Christopher_Cline_CoW.pdf |
| 2024-05-03 | 107W-2024-00795 | EpiSci | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2024-00795_Rohit_Pillai_CoW.pdf |
| 2024-06-07 | 107W-2024-00700 | SEAKdrones LLC | singular location limitation phrase | https://www.faa.gov/sites/faa.gov/files/107W-2024-00700_Dennis_Sylvia_CoW.pdf |