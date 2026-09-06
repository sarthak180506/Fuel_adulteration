# Lab Safety Checklist — Fuel Sample Handling

> **Read before Phase 1 begins. Person D is responsible for verifying this is followed at every lab session.**

## Before Starting
- [ ] Notify lab safety officer that flammable liquids (petrol/diesel) will be used
- [ ] Confirm fire extinguisher (CO₂ class) is in the room and accessible
- [ ] Ensure room ventilation is on — fume hood preferred
- [ ] No open flames, sparks, or ignition sources within 3 metres of sample area
- [ ] Wear: nitrile gloves, safety goggles, lab coat

## Sample Preparation
- [ ] Use only grounded, conductive containers for petrol/diesel (prevent static buildup)
- [ ] Measure volumes using calibrated syringes — label every sample immediately
- [ ] Seal unused fuel containers immediately after dispensing
- [ ] Do not leave fuel samples open longer than 30 seconds (vapour accumulation)

## Electrical Setup
- [ ] All ESP32 connections inspected before powering on near sample chamber
- [ ] Sample chamber PTFE-lined and sealed — no direct fuel contact with PCB/wiring
- [ ] Ground the ESP32 chassis to bench earth before any measurement

## During Measurement
- [ ] Do not lean over open sample chamber during measurement
- [ ] Log each reading in `docs/experiment_log.md` immediately
- [ ] If you smell strong fumes: stop, seal samples, ventilate, wait 5 minutes

## After Each Session
- [ ] Dispose of used fuel samples per institute chemical waste protocol
- [ ] Wipe sample chamber with isopropanol-dampened cloth
- [ ] Rinse chamber with clean petrol/diesel before next sample (prevent cross-contamination)
- [ ] Update `docs/experiment_log.md` with session summary

## Emergency
- **Spill:** absorb with dry sand/vermiculite, do NOT use water on petrol/diesel
- **Fire:** CO₂ extinguisher only; evacuate, call emergency services
- **Contact:** wash skin with soap/water for 15 min; eyes: flush 15 min, seek medical attention
