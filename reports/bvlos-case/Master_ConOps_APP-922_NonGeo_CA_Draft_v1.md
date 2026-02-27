# Master Concept of Operations (ConOps) — APP-922 Non-Geo California Agricultural BVLOS

**Document ID:** CONOPS-APP922-CA-NONGEO-v1  
**Date:** 2026-02-25  
**Operator:** Ethan Tarran / Vineyard Drone Services  
**UAS System:** DJI Dock 2 + DJI Matrice 3D/3TD + FlightHub 2  
**Requested Waiver Scope:** 14 CFR §107.31 and associated VO-support operations consistent with §107.33 as applicable  
**Operating Region:** State of California (qualified agricultural sites only)

---

## 1) Purpose and Operational Intent
This ConOps defines day-only BVLOS agricultural monitoring operations over qualified commercial vineyard/permanent-crop properties in California. Operations are non-site-specific only after each proposed site is qualified through the Site Qualification Procedure in Section 8.

The operation excludes residential/urban dense-population use cases and is limited to private or access-controlled agricultural operating areas.

---

## 2) Operational Envelope (Hard Limits)
- Day operations in VMC only.
- Max altitude: 400 ft AGL (site/mission may impose lower cap).
- Operations confined to approved Operational Volume (OV).
- Geofence/geocage enabled before launch.
- RPIC must be in CONUS for CA operations.
- VO support required unless equivalent approved mitigation is documented.
- Abort/terminate on traffic conflict, surveillance degradation, C2 degradation, or unresolved non-participant ingress.

---

## 3) Crew and Command Structure
### 3.1 RPIC (Remote)
- Final authority for launch/continue/terminate/recover decisions.
- Monitors aircraft telemetry, geofence status, C2 health, and alerts.
- Executes avoidance/contingency actions upon VO callout or system alert.

### 3.2 Visual Observer (On-site)
- Located at pre-qualified vantage location(s) with required viewshed.
- Performs continuous airspace/ground surveillance.
- Provides mandatory traffic and hazard callouts using standard phraseology.

### 3.3 Communications
- Primary: cellular voice or dedicated radio (defined in site survey).
- Backup: alternate channel (second phone/radio path).
- Loss of both channels => immediate mission termination and recovery.

---

## 4) Detect-and-Avoid (DAA) Concept
### 4.1 DAA Layers
1. **Primary tactical DAA:** On-site VO visual scan and immediate callouts.  
2. **Supplemental awareness:** ADS-B In / AirSense cooperative target cues.  
3. **Procedural containment:** route constraints + geofence/geocage + abort matrix.

### 4.2 Minimum Detection Distance Standard
For manned aircraft conflict evaluation, minimum practical detection objective is:
- **>= 0.5 statute mile (target)** for approach/crossing traffic, or
- Any earlier distance required by site conditions to support immediate avoidance.

If the VO cannot maintain sufficient surveillance quality to support timely avoidance, operation shall not launch or shall terminate immediately.

### 4.3 Avoidance Action Matrix
On traffic/hazard callout RPIC executes one of:
- Hold in place,
- Descend within approved OV,
- Immediate return/recovery,
- Immediate land at pre-identified LRS/contingency area.

Default is conservative termination/recovery when ambiguity exists.

---

## 5) Route of Flight and Operational Volume Management
- Routes are preplanned and constrained within approved OV.
- Route planning checks include boundaries, no-fly constraints, obstacle clearance, and C2 coverage expectations.
- Any route change that alters risk assumptions requires update/review of site survey and hazard log before flight.

---

## 6) Ground Risk Controls
- Operations limited to private/access-controlled agricultural properties or controlled ROW.
- Non-participant exclusion by procedural controls and preflight clearing.
- Operation terminated if non-participant ingress cannot be resolved.

---

## 7) C2 Reliability and Lost Link
- Preflight C2 health verification in GCS/FlightHub.
- Site qualification includes C2 coverage validation method (planning evidence and/or measured checks).
- Lost-link behavior set to safe contingency (RTH or equivalent approved profile).
- Repeated C2 anomalies trigger site requalification before further operations.

---

## 8) Site Qualification Procedure (SQP) — Non-Geo California
A site must be qualified and documented before initial operations. Records retained and available to FAA upon request.

### 8.1 Qualification Criteria
Each site must document at minimum:
- Site identity (address and/or lat/long).
- Airspace class (Class G unless COA obtained).
- Boundaries and OV definition.
- Roadways/access points and non-participant exposure.
- Highest obstacles and obstruction profile.
- VO position(s), viewshed factors, and required VO count.
- Dock/LRS locations.
- C2 signal sufficiency across route/OV.
- Max downrange distance from dock/GCS.
- Airports/heliports/aviation activity within 3 SM.
- ADS-B In usage and limitations.
- Applicable mitigations for identified hazards.

### 8.2 Qualification Workflow
1. Conduct documented site survey (form in Appendix A).  
2. Compare survey results against hazard log/risk analysis baseline.  
3. Add new hazards and mitigations where needed.  
4. Determine Go/No-Go for initial qualification.  
5. RPIC sign/date approval; retain records.

### 8.3 Requalification Triggers
- Significant infrastructure or land-use change.
- New aviation activity nearby.
- Material route/OV change.
- Repeated safety event/contingency trigger.

---

## 9) Weather and Environmental Minimums
- Day VMC only.
- No launch under degraded visibility or conditions reducing VO effectiveness (smoke/glare/haze).
- Terminate/recover if conditions degrade below acceptable margin.

---

## 10) Compliance Statement
- All unwaived Part 107 requirements remain in effect.
- Part 89 requirements remain in effect.
- This ConOps applies only to operations matching the qualified site profile and operational constraints herein.

---

## 11) Records Retention
The following are retained for each qualified site and operation cycle:
- Site Qualification Form,
- Route/OV map references,
- Risk analysis updates,
- Crew briefing/checklists,
- Significant events and corrective actions.

Retention period: for the duration of operations at the site and available to FAA upon request.

---

## Appendix A — Required Form
Use: `Site_Qualification_Form_APP-922_CA_v1` (separate document).
