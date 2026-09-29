# 🌊 Wastewater Treatment Process Flow & Mass Balance

## 1. Process Train Description

The facility employs the conventional **Activated Sludge Process (ASP)** with downstream tertiary media polishing and UV disinfection, designed to treat typical domestic municipal wastewater.

```mermaid
graph TD
    INF["Raw Municipal Wastewater"] -->|Coarse Solids| SCR["Mechanical Bar Screens"]
    SCR -->|Grit Removal| GRT["Vortex Grit Chambers"]
    GRT -->|Screened Influent Flume| AER["Biological Aeration Basins"]
    
    BLW["Centrifugal Air Compressors"] ==>|Compressed Air| AER
    
    AER -->|Mixed Liquor (MLSS)| SPL["Hydraulic Splitter Vault"]
    SPL -->|50% Flow| CL1["Secondary Clarifier CL-01"]
    SPL -->|50% Flow| CL2["Secondary Clarifier CL-02"]
    
    CL1 -->|Settled Sludge| PMP["Sludge Pump Station"]
    CL2 -->|Settled Sludge| PMP
    
    PMP ==>|RAS Line (85%)| AER
    PMP ==>|WAS Line (15%)| DIG["Anaerobic Digesters"]
    
    DIG -->|Stabilized Solids| DEW["Centrifuge Dewatering & Cake Bunker"]
    DIG -->|Methane Gas| FLARE["Biogas Flare Stack"]
    
    CL1 -->|Clarified Liquid| TER["Tertiary Sand Filters"]
    CL2 -->|Clarified Liquid| TER
    
    TER -->|Filtered Liquid| UV["Serpentine UV Disinfection Channels"]
    UV -->|Disinfected Effluent| OUT["Parshall Flume Outfall"]
    OUT -->|Stepped Cascade| WET["Wetland Retention Lagoon"]
```

---

## 2. Mass Balance & Water Quality Degradation

The table below details the progressive transformation of water quality parameters through each physical and biological stage:

| Parameter | Raw Influent | Post-Aeration | Post-Clarifier | Post-Tertiary UV | Final Wetland | Total Removal |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **BOD₅ (mg/L)** | 260 | 75 | 22 | 3.5 | < 2.0 | **99.4%** |
| **TSS (mg/L)** | 310 | 3,200 (MLSS) | 18 | 2.1 | < 1.0 | **99.7%** |
| **Turbidity (NTU)** | 340 | 120 | 18 | 0.9 | 0.4 | **99.9%** |
| **Dissolved Oxygen (mg/L)**| 0.2 | 2.5 – 3.2 | 1.8 | 4.2 | > 6.5 | **Enriched** |
| **Fecal Coliform (CFU/100mL)**| 10⁷ | 10⁶ | 10⁴ | < 20 | < 2 | **99.999%** |

---

## 3. Solids Handling Circuit

1. **Return Activated Sludge (RAS)**:
   * Biological floc containing viable *Zoogloea ramigera*, nitrifying *Nitrosomonas*, and *Nitrobacter* bacteria is gathered from the clarifier bottom hoppers.
   * Recycled at **75% to 100% of forward influent flow** back to the aeration basin head to maintain a Mixed Liquor Suspended Solids (MLSS) concentration of **2,500 – 3,500 mg/L**.
2. **Waste Activated Sludge (WAS)**:
   * Excess biological growth is wasted from the system to maintain a Mean Cell Residence Time (MCRT) of **8 to 12 days**.
   * Pumped via the heavy industrial brown pipe to **Anaerobic Digesters TK-101 and TK-102** operating at mesophilic temperatures (37°C / 98°F).
3. **Biogas & Dewatered Biosolids**:
   * Anaerobic digestion yields biogas containing **62% Methane ($CH_4$) and 38% Carbon Dioxide ($CO_2$)**.
   * Biogas is channeled to the enclosed flare stack with automatic pilot ignition for safe emissions control.
   * Digested sludge is dewatered to a **24% dry-solids cake** staged in the three-sided concrete bunker for agricultural soil amendment.
