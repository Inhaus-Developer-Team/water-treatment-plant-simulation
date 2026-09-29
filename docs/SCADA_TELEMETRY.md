# 📡 SCADA Instrumentation & Telemetry Points

## 1. Instrument List & Sensor Tags

The 3D digital twin incorporates telemetry instrument points mapped to real-world wastewater supervisory control and data acquisition (SCADA) standards.

| Tag | Equipment / Zone | Instrument Type | Engineering Range | Control Action |
|---|---|---|:---:|---|
| **FIT-101** | Raw Influent Flume | Ultrasonic Level / Flow Meter | 0 – 35 MGD | Influent pacing & screen auto-rake initiation |
| **AIT-201** | Aeration Basin 1 | Optical Dissolved Oxygen (DO) Probe | 0.0 – 10.0 mg/L | Modulates blower VFDs to maintain 2.0 mg/L DO |
| **PIT-202** | Air Gantry Bridge Header | Piezoresistive Pressure Transmitter | 0 – 15 psig | High-pressure relief & compressor staging |
| **SLD-301** | Clarifier CL-01 | Sludge Blanket Interface Sonar | 0.0 – 4.5 m | Adjusts RAS pump rate to prevent blanket rising |
| **SLD-302** | Clarifier CL-02 | Sludge Blanket Interface Sonar | 0.0 – 4.5 m | Adjusts RAS pump rate to prevent blanket rising |
| **DP-401** | Tertiary Sand Filter 1 | Differential Pressure Sensor | 0 – 12 psi | Triggers automatic backwash cycle at 8 psi |
| **UVI-402** | UV Disinfection Channel | Germicidal Radiometer (254nm) | 0 – 100 mW/cm² | Alarm on lamp fouling or low UV dose |
| **AIT-501** | Parshall Flume Outfall | Turbidimeter (Nephelometric) | 0.0 – 50.0 NTU | Permitted compliance tracking (< 1.0 NTU) |
| **FIT-502** | Parshall Flume Outfall | Non-Contact Ultrasonic Level | 0 – 30 MGD | Certified effluent discharge flow totalization |
| **TT-601** | Anaerobic Digester TK-101 | RTD Temperature Element | 20 – 60 °C | Regulates boiler heat exchanger loop (37°C target)|
| **PIT-602** | Biogas Collection Header | Pressure Transmitter | -5 to +25 in H₂O | Activates biogas flare burner at +12 in H₂O |

---

## 2. Interactive Raycasting Subsystem Inspector

The 3D simulation includes a live raycaster inspector HUD:
* **Interaction**: Clicking any structure, tank, pipe, or bridge in the scene activates the raycaster.
* **Telemetry Display**: Retrieves the unit's `userData.subsystem` and `userData.spec` attributes, updating the lower-left HUD card with live specifications and 3D world coordinates.
* **3D Pin Synchronization**: Coordinates billboard pin callouts directly over unit centroid positions.
