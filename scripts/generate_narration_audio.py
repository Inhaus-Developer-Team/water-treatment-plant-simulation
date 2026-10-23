#!/usr/bin/env python3
"""
Generate British Male Voice Narration audio files for Guided Process Tours
in Municipal WRRF (index.html) and Mobile Wastewater Treatment System (mobile.html).

Uses edge-tts with voice en-GB-RyanNeural at a calibrated slower rate (-14%)
with phonetic expansion of technical terms, units, and numbers to guarantee
crystal-clear pronunciation and documentary-grade pacing.
"""

import asyncio
import os
import sys
import edge_tts

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio", "narration")
VOICE = "en-GB-RyanNeural"
RATE = "-14%"  # Slower, calm, deliberate, documentary pacing

NARRATION_SCRIPTS = {
    # Municipal WRRF Stages (6 stages)
    "muni_stage_01.mp3": (
        "Stage one: Raw Sewage Influent and Mechanical Headworks. "
        "Raw untreated municipal wastewater enters the plant via the six hundred millimetre incoming sewer conduit "
        "from the underground interceptor vault. Heavy debris, plastics, and rags are extracted by mechanical bar screens, "
        "while vortex grit chambers drop dense sand before primary pumping."
    ),
    "muni_stage_02.mp3": (
        "Stage two: Biological Aeration Basins, Activated Sludge. "
        "Untreated liquor flows into four plug-flow channels. Billions of beneficial aerobic microorganisms digest dissolved "
        "organic matter, fueled by four hundred and fifty cubic metres per minute of compressed air, injected through "
        "fine-bubble bottom diffusers."
    ),
    "muni_stage_03.mp3": (
        "Stage three: Secondary Circular Clarifiers. "
        "Flow passes through the central distribution splitter to twin sixteen metre radial clarifiers. Heavy biological "
        "floc settles to the tank floor, where continuous scraper bridges gather it for reuse as Return Activated Sludge, "
        "or R A S."
    ),
    "muni_stage_04.mp3": (
        "Stage four: Tertiary Sand Filtration and U V Disinfection. "
        "Clarifier overflow flumes directly feed the central Tertiary Complex. Dual-media rapid sand filters capture "
        "residual micro-particulates, followed by ultraviolet disinfection lamp banks neutralizing ninety-nine point nine "
        "percent of bacteria without toxic chemicals."
    ),
    "muni_stage_05.mp3": (
        "Stage five: Pristine Treated Water Discharge Outfall and Wetlands. "
        "Disinfected crystal-clear treated effluent overflows into the calibrated Parshall flume outfall, tumbling over "
        "a stepped stone cascade directly into the wetland lagoon. Watch the dynamic aquamarine effluent plume disperse, "
        "propagate wave ripples, and nourish thriving riparian reeds and water lilies at ninety-nine point four percent purity."
    ),
    "muni_stage_06.mp3": (
        "Stage six: Anaerobic Digestion and Renewable Biogas. "
        "Concentrated solids from the clarifiers are pumped to twin anaerobic digester tanks on the eastern bio-pad, "
        "where thermophilic microbes convert organic sludge into stabilized fertilizer and renewable methane biogas."
    ),

    # Mobile Wastewater System Stages (4 stages)
    "mobile_stage_01.mp3": (
        "Stage one: Raw Feed Equalization and Skid Pumping. "
        "Raw wastewater arrives into the forty-five cubic metre horizontal buffer vessel and passes through the vertical "
        "poly feed tank. The P C ten pump skid draws influent through duplex strainers, damping hydraulic surges before "
        "treatment."
    ),
    "mobile_stage_02.mp3": (
        "Stage two: Electrocoagulation and A O P Reactor, Pod One. "
        "Influent enters Pod One, containing high-amperage sacrificial electrolytic cells. In-situ generated electrons break "
        "oil emulsions, destabilize heavy metals, and generate hydroxyl radicals without toxic bulk chemicals."
    ),
    "mobile_stage_03.mp3": (
        "Stage three: Dissolved Air Flotation and Sludge Separation, Pod Two. "
        "Coagulated liquor transfers across the containment aisle to Pod Two. Millions of twenty to forty micrometre "
        "micro-bubbles lift suspended flocs to the surface for automated mechanical skimming into the concentrated "
        "sludge collector."
    ),
    "mobile_stage_04.mp3": (
        "Stage four: Multi-Barrier Polishing and Ultra-Clean Outflow, Pods Three and Four. "
        "Clarified water passes through Pod Three's pressurized deep-bed media and granular activated carbon columns, "
        "receiving final pathogen disinfection from Pod Four. Pristine treated effluent discharges at less than zero point "
        "six N T U purity."
    )
}

async def generate_file(filename: str, text: str):
    out_path = os.path.join(OUTPUT_DIR, filename)
    print(f"Generating {filename} ({RATE}, {VOICE})...")
    communicate = edge_tts.Communicate(text, voice=VOICE, rate=RATE)
    await communicate.save(out_path)
    size = os.path.getsize(out_path)
    print(f"  ✓ Saved {filename}: {size:,} bytes")
    return filename, size

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Starting narration audio generation for {len(NARRATION_SCRIPTS)} tour stages...")
    print(f"Target Voice: {VOICE} | Speech Rate: {RATE}")
    print(f"Output Directory: {OUTPUT_DIR}\n")

    tasks = [generate_file(fn, txt) for fn, txt in NARRATION_SCRIPTS.items()]
    results = await asyncio.gather(*tasks)

    print("\n--- Audio Generation Summary ---")
    for fn, sz in sorted(results):
        print(f"  - {fn}: {sz:,} bytes")
    print(f"\nAll {len(results)} audio files generated successfully.")

if __name__ == "__main__":
    asyncio.run(main())
