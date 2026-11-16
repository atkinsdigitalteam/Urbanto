| Floor(s) | Level | Internal components (m2) | Wall band m2 | Balconies m2 |
|---|---|---|---:|---:|
| B2-B1 (2 floors) | basement | parking 3,760, parking_lobby 40, stairs 80, lift_shaft 40, service_shaft 50, plant 300, storage 100, waste_room 40 | 83.64 | 0 |
| G | ground | retail 2,200, lobby 250, lobby 200, loading 300, boh 150, stairs 80, lift_shaft 40, service_shaft 50, statutory_room 100, toilets 50 | 71.64 | 0 |
| L1 | podium_parking | parking 2,900, parking_lobby 40, stairs 80, lift_shaft 40, service_shaft 50, plant 110, void 200 | 71.64 | 0 |
| L2-L3 (2 floors) | podium_parking | parking 3,100, parking_lobby 40, stairs 80, lift_shaft 40, service_shaft 50, plant 110 | 71.64 | 0 |
| L4-L5 (2 floors) | podium | office 2,850, corridor 100, toilets 150, stairs 80, lift_shaft 40, service_shaft 50, plant 150 | 71.64 | 0 |
| L6 | amenity | gym 600, pool_services 150, corridor 50, stairs 80, lift_shaft 40, service_shaft 50 | 38.04 | 0 |
| L7-L36 (29 floors) | tower | apartment 860, corridor 80, stairs 40, lift_shaft 25, service_shaft 20, lobby 20, refuse_chute 5, elec_cupboard 10 | 40.14 | 80+40 |
| L22 | mep | mep_floor 935, stairs 40, lift_shaft 25, service_shaft 20, lobby 20, refuse_chute 5, corridor 15 | 40.14 | 0 |
| Roof | roof | roof_plant 150, stairs 20 | 15.24 | 0 |

## Inputs
Plot 5,000 m2; 40 floor records; units 319; GEA 63,934.6; GIA 62,080.0; balconies 3,480; parking area 16,620 m2 -> 554 bays at 30.0 m2 (DBC net geometry 21.25 m2)

| Rule set | GFA m2 | FAR | Efficiency (32,840 / GFA) | Typical tower floor GFA | Typical floor efficiency (860 / floor) |
|---|---:|---:|---:|---:|---:|
| Dubai (DBC) | 40,004 | 8.00 | 82.1% | 1,037.9 | 82.9% |
| Abu Dhabi (N-25 reading) | 42,668 | 8.53 | 77.0% | 1,088.2 | 79.0% |
| Abu Dhabi (A.8 reading) | 52,667 | 10.53 | 62.4% | 1,088.2 | 79.0% |
| Saudi (MOMRAH) | 58,427 | 11.69 | 56.2% | 1,220.1 | 70.5% |
| London (GEA) | 63,935 | 12.79 | 51.4% | 1,100.1 | 78.2% |
| Singapore (URA) | 46,452 | 9.29 | 70.7% | 1,149.1 | 74.8% |
| London GIA (reference) | 62,080 | 12.42 | 52.9% | 1,060.0 | 81.1% |
| IPMS 1 (reference) | 67,415 | 13.48 | 48.7% | - | - |
| Dubai built-up area (DBC A.5.2.2, reference) | 65,105 | 13.02 | 50.4% | - | - |

Singapore: balconies 3,480 m2; 7% bonus cap 2,095 m2; balcony GFA beyond cap 1,385 m2; excess parking over Zone 2 upper bound (352) counted as GFA: 6,060 m2 -> GPR incl. excess 10.50

| Parking rule set | Type | Residential | Office | Retail | Total | Provided bays | Gap | Note |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Dubai (DBC) | minimum | 348 | 114 | 32 | 494 | 554 | +60 |  |
| Abu Dhabi (CBD) | rate (DoT) | 353 | 168 | 60 | 581 | 554 | -27 |  |
| Abu Dhabi (non-CBD) | rate (DoT) | 377 | 182 | 60 | 619 | 554 | -65 |  |
| Saudi (MOMRAH) | minimum | 479 | 127 | 49 | 655 | 554 | -101 |  |
| London (CAZ / PTAL 5-6) | maximum | 0 | 0 | 0 | 0 | 554 | +554 | disabled bays >= 10 now, +23 later |
| London (Outer, PTAL 2-3) | maximum | 246 | 68 | 54 | 368 | 554 | +186 |  |
| Singapore (Zone 2) | range | - | - | - | 274-352 | 554 | +202 over upper bound | |
| Singapore (Zone 3) | range | - | - | - | 293-366 | 554 | +188 over upper bound | |

Population: DBC Table D.5 rates -> 759.8 persons; NDSS bedspaces -> 928; NDSS minimum sizes met: {'studio': True, '1BR': True, '2BR': True, '3BR': True}
Density 1,520 persons/ha (plot basis) -> Dubai DM high-density table
| Facility (Dubai DM, >220 p/ha) | Population threshold | Share of one facility | Land at m2/person |
|---|---:|---:|---:|
| Daily mosque | 4,000 | 19.0% | 228 m2 |
| Family park | 4,000 | 19.0% | 570 m2 |
| Friday mosque | 12,000 | 6.3% | 175 m2 |
| Kindergarten | 12,000 | 6.3% | 190 m2 |
| Primary school | 12,000 | 6.3% | 494 m2 |
| District park | 12,000 | 6.3% | 532 m2 |
| Intermediate school | 20,000 | 3.8% | 319 m2 |
| Secondary school | 30,000 | 2.5% | 251 m2 |
| Government health centre | 30,000 | 2.5% | 167 m2 |
| Hayy (quarter) park | 30,000 | 2.5% | 304 m2 |
Abu Dhabi mosque regs with the Dubai population as proxy: worshippers 266, min GFA 479 m2, parking 9 (1 per 30 worshippers)
Saudi coverage check: ground 69.8% vs 65 % max; podium upper floors 69.8% vs 75 % max
Singapore DU check (inferred): residential GFA excl. bonus 29,933 / 85 = 352 DU allowed vs 319
