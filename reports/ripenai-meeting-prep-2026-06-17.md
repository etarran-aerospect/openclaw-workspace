# RipenAI Meeting Prep - June 17, 2026

## Meeting Goal

Position AeroSpect as the California vineyard deployment and data-integration partner for RipenAI, not as a competing sensing platform.

The strongest message:

> RipenAI can measure grape ripeness directly at the bunch/fruit scale. AeroSpect can help turn those measurements into vineyard-scale maps, sampling designs, block-level recommendations, and grower-facing harvest planning workflows in California.

## What RipenAI Appears To Be

RipenAI is a Queen Mary University of London initiative led by Prof. Lei Su and Dr. Xuechun Wang. Their public materials describe a portable optical sensor plus machine-learning system for non-destructive grape ripeness detection.

Public claims:

- Portable optical sensing, likely visible/NIR or related spectral sensing.
- Measures how grapes absorb/reflect different wavelengths as chemical composition changes during ripening.
- Uses AI/ML models to estimate ripeness directly on the vine.
- Intended outputs include instant field-level ripeness readings, harvest recommendations, and possibly sugar/acidity prediction.
- Their website explicitly mentions drone and robot compatible hardware.
- They are seeking vineyards, agritech companies, and orchards for pilot work.
- Early field work appears tied to Saffron Grange Vineyard in Essex and a robotics integration project with Extend Robotics.

Useful sources:

- RipenAI website: https://ripenai.uk/
- EurekAlert/QMUL release: https://www.eurekalert.org/news-releases/1114771
- Talker coverage with technical description: https://talker.news/2026/04/07/ai-powered-grape-ripeness-detector-aims-to-revolutionize-wine-industry/
- Dr. Xuechun Wang QMUL profile: https://www.sems.qmul.ac.uk/staff/xu.wang/

## People On The Call

- Prof. Lei Su - Professor of Photonics at Queen Mary University of London. Public release quotes him on RipenAI shaping smart harvesting where timing and precision matter.
- Dr. Xuechun Wang - Postdoctoral researcher, machine learning and intelligent sensors. Public profile lists Prof. Lei Su as supervisor and RipenAI link.
- Huan Wang - commercial development director, likely focused on translation, pilot structure, IP/commercial fit, and partnership path.
- Dave Page - RipenAI Executive Chair, likely focused on market, partnerships, scale, and business model.

## AeroSpect Value Proposition

### 1. California Pilot Access

AeroSpect is already working in premium and production vineyards in Napa/Northern California and has credibility with winegrowers, including Gallo's research division. That gives RipenAI a faster path to:

- California field data.
- Real vineyard operational feedback.
- Multiple management styles and production goals.
- Premium winegrape conditions outside the UK.
- A credible North American pilot story.

### 2. Spatial Context Around Point Measurements

RipenAI's sensor likely produces very high-value point or bunch-level measurements. The problem is that harvest decisions are made across blocks, rows, zones, and crews.

AeroSpect can supply the vineyard-scale context:

- Multispectral vigor maps.
- Thermal/water stress maps.
- Canopy variability zones.
- Block/row geospatial layers.
- Historical flight layers.
- Sampling zone design.
- GIS outputs growers can actually use.

Best phrasing:

> Your sensor can tell us what is happening at the fruit. Our maps can help decide where to measure, how to scale those measurements across a block, and how to convert them into harvest zones.

### 3. Better Model Calibration And Validation

Scientists will care about this. Avoid vague claims. Make the technical point:

- Remote sensing does not directly replace Brix/TA/pH/phenolic measurements.
- But it can stratify vineyards by canopy vigor, water status, exposure, and spatial variability.
- That means fewer wasted measurements and better coverage of variability.
- RipenAI measurements can become ground truth/labels for spatial models.
- Drone layers can become covariates for predicting ripeness progression or harvest readiness zones.

Good technical framing:

> We are interested in whether proximal ripeness measurements plus drone-derived spatial covariates can improve block-level maturity interpolation and harvest-zone classification compared with either data stream alone.

### 4. Grower Workflow Translation

Scientists may build the sensor; growers need decisions:

- Where should I sample next?
- Which rows are ahead/behind?
- Is a block uniform enough to pick together?
- Should we split pick?
- How should harvest labor and winery intake be staged?
- Which vineyard variability explains ripeness variability?

AeroSpect can help define those products because it already translates imagery into grower-facing maps and decisions.

## Partnership Concepts To Propose

### Option A - California Pilot Site Partner

AeroSpect helps identify one or more vineyard blocks in Napa/Sonoma/Lodi/Central Valley, supports field logistics, and collects drone imagery during the ripening window.

Deliverable:

- A joint pilot comparing RipenAI readings, destructive lab samples, and AeroSpect drone-derived spatial layers.

### Option B - Sampling Design Collaboration

AeroSpect creates vigor/water-stress/terrain/block zones before RipenAI field visits, then tests whether stratified sampling improves model calibration and vineyard coverage.

Deliverable:

- A practical sampling protocol for RipenAI deployment in commercial vineyards.

### Option C - Data Fusion / Harvest-Zone Mapping

Combine RipenAI readings with drone layers to produce ripeness prediction maps or categorical harvest-readiness maps.

Deliverable:

- Grower-facing map layers: early/target/late zones, recommended follow-up sampling points, and candidate split-pick zones.

### Option D - North American Commercialization Partner

AeroSpect supports customer discovery, vineyard introductions, pilot execution, and adaptation to California grower workflows.

Deliverable:

- A California-facing pilot package and case study.

## Technical Questions To Ask

Ask these calmly and specifically. They will signal that you understand the science and deployment risk.

1. What is the sensor modality and spectral range?
   - Visible, NIR, multispectral LEDs, spectrometer, fluorescence, or other?

2. What targets are you predicting?
   - Brix/TSS, titratable acidity, pH, anthocyanins, phenolics, ripeness class, harvest-readiness score?

3. What are current validation metrics?
   - RMSE for Brix/TA/pH, classification accuracy, cultivar-specific performance, cross-vineyard generalization.

4. How many cultivars and seasons are in the training set?
   - This matters because grape spectral models often struggle across cultivar, season, site, and management differences.

5. How do you handle illumination and field variability?
   - Shading, berry orientation, sun angle, temperature, dust, bloom, canopy occlusion, cluster exposure.

6. Is the model cultivar-specific, region-specific, or intended to generalize globally?

7. What ground truth protocol are you using?
   - Lab method, sample size per block, berry/bunch/vine/block scale, timing relative to sensor measurement.

8. What spatial resolution does the output represent?
   - Berry, bunch, vine, panel, row, block, or management zone.

9. How do you envision drone compatibility?
   - Mounted sensor on UAV, drone-guided sampling, drone imagery as context, or autonomous robotic integration?

10. What would a successful California pilot need to prove?
    - Technical accuracy, grower usefulness, cost savings, labor planning, commercial repeatability.

## Important Scientific Caveats

Use these to sound credible, not negative:

- Drone multispectral/thermal imagery generally senses canopy condition, not grape chemistry directly.
- Brix and acidity can decouple from canopy vigor under irrigation, crop load, cultivar, clone, rootstock, and heat events.
- Ripeness models usually need multi-season and multi-cultivar calibration to avoid overfitting.
- Field optical sensing has practical issues: illumination, berry orientation, cluster exposure, temperature, and sampling representativeness.
- The value is not "drone predicts everything"; the value is integrated sampling and spatial decision support.

## Strong Talk Track

Start with this:

> I see RipenAI as solving the hardest ground-truth problem in maturity monitoring: measuring fruit chemistry non-destructively and repeatedly. AeroSpect's role would be complementary. We can provide the vineyard-scale spatial layer around those measurements: where variability exists, where to sample, how to interpolate measurements into zones, and how to turn results into maps that growers can act on for harvest planning.

Then:

> In California, the commercial need is not just knowing whether a handful of clusters are ripe. Growers need to know whether the block is spatially uniform, where the lagging and leading zones are, whether a split pick makes sense, and how to plan labor and winery intake. That is where pairing RipenAI's proximal sensing with drone-derived vigor and thermal maps could be powerful.

Then propose:

> A practical first step could be a small California pilot: one or two vineyard blocks, drone flights during the ripening window, RipenAI readings and standard lab samples across stratified zones, then a comparison of point measurements versus fused drone-plus-RipenAI harvest-zone maps.

## What To Avoid

- Do not imply AeroSpect can already predict fruit chemistry from drones alone.
- Do not overclaim that NDVI equals ripeness.
- Do not ask them for a broad partnership without a pilot shape.
- Do not make the conversation only about drones. Their core invention is proximal grape sensing; respect that.
- Do not lead with sales. Lead with validation, deployment, and grower decision-making.

## One-Sentence Partnership Pitch

AeroSpect can help RipenAI validate and commercialize its grape ripeness sensing in California by pairing non-destructive fruit-level measurements with vineyard-scale drone maps, sampling design, and harvest-planning workflows growers can act on.

## Suggested Close

> If there is interest, I would be happy to help define a California pilot around one or two vineyard blocks this season: AeroSpect would handle drone mapping, spatial zone design, and grower-facing outputs, while your team provides the RipenAI sensing protocol and model outputs. The scientific question would be whether the combined dataset improves maturity mapping and harvest-zone decisions compared with traditional sampling alone.

