# MSK Measurement Toolkit (v1.6)

Offline, single-file toolkit (now at /toolkit/) of literature-based musculoskeletal measurement calculators with how-to diagrams and a measure-on-image tool. Research and education use only; not a medical device.

**Covers:** scoliosis and sagittal alignment (Cobb, Risser, kyphosis, SRS-Schwab, coronal balance, RVAD), craniocervical junction (ADI/PADI, BDI/BAI, Powers ratio, condyle-C1 interval, Spence), chemical shift signal drop (marrow, adrenal SII and ASR), shoulder (CC interval, AC joint, acromiohumeral interval, Hamada), pelvis and hip (flamingo views, LCEA, Tonnis, extrusion index, ACEA, alpha angle), distal radius (tilt, inclination, height, step-off, teardrop, Lafontaine) foot (hallux valgus angles, hindfoot alignment angle and moment arm, Meary's angle, calcaneal pitch) and the pediatric foot (talocalcaneal angles and index, talus-first metatarsal and tibiocalcaneal angles, deformity patterns and terminology).

## Editing
All cutoffs, labels, diagrams and citations live in the **TOOLKIT DATA** script block near the top of `index.html`. Copy an existing calculator object to add a measurement; the engine block below it never needs editing. Images loaded into the measure tool stay in the browser and are never uploaded.

**Measuring on an image (v1.2):** the Start page has a drop/paste zone. In the measure view, pick a measurement and the tool prompts each landmark in turn (prompts live in `GUIDES` in the data block), snaps points to the nearest edge, straightens each line along the edge it follows, then grades the result and draws it on the image as soon as the last point is placed. It does not detect anatomy on its own; the user places every landmark.

No patient data is included.

**Synthetic practice samples (v1.4):** every calculator with image measurements has a drawn, radiograph-style practice image (`SMP` block in the data section) with a known answer and a preset pixel spacing. After you measure, the result panel compares your value with the answer key, and "Show answer lines" draws the correct lines. These images are generated shapes, not patient data.

**Knee module (v1.5):** patellar height (Insall-Salvati with radiograph and MRI cutoffs, modified Insall-Salvati, Caton-Deschamps, Blackburne-Peel, patellotrochlear index), trochlear depth, sulcus angle, lateral trochlear inclination, and TT-TG distance with optional TT-PCL. Three new measure types support these: a three-point vertex angle (sulcus angle), an offset along a reference line (TT-TG, TT-PCL), and a five-point depth from a reference line (trochlear depth). Each has guided landmark steps and a synthetic practice image with an answer key.

**Body map (v1.5):** the Start page has a clickable body figure, the same one used on the Cases page. Tapping a highlighted region (spine, shoulder, pelvis and hip, knee, wrist, ankle and foot) filters the measurement tiles to that region; section pills, search and the top tabs still work.

**Part of the website:** this file is copied as-is into the build, then `scripts/toolkit-chrome.mjs` (an Astro integration registered in `astro.config.mjs`) adds the site header, nav and footer copied from the built home page, the site fonts and palette, and a "Teaching case" link on each toolkit section that a case on the Cases page points to (via `toolkit_link: toolkit/#<section>` in `src/data/cases.yaml`). Header or footer edits in `Base.astro` carry over automatically. Opening this file directly (or `astro dev`) shows the toolkit without the site chrome.
