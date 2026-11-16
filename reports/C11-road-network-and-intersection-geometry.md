# C11: Road network and intersection geometry

Researched 2026-10-30. Brief file unavailable; scope taken from the task line. Dubai RTA's design manual and Abu Dhabi's TR-514 could not be opened, so those cells are mostly "not found".

## Answer

Build the street-section engine on a rule set split into profiles: Abu Dhabi's Urban Street Design Manual (USDM) as the default GCC profile, with the UK Design Manual for Roads and Bridges (DMRB), AASHTO-derived US practice and the NACTO Global Street Design Guide (GSDG) as switchable or advisory profiles, because they disagree on the numbers that matter most. Lanes are 3.3 m in USDM (kerb lanes 3.3 to 3.5 m, 3.5 m on bus routes), 3.65 m on DMRB urban trunk roads, 3.0 m in GSDG (2.7 m at 30 km/h or less), and FHWA calls 10 ft (3.05 m) lanes appropriate in cities. Kerb radii are capped at 5 m in USDM (2 to 5 m in practice) and 1.5 m is preferred in GSDG, while DMRB CD 123 asks for at least 6 m urban, or 10 m plus a 1:5 taper where large vehicles must turn. Roundabouts need an inscribed circle diameter (ICD) of at least 28 m, a circulatory carriageway 1.0 to 1.2 times the entry width, and an entry path radius of at most 70 m (urban compact) under DMRB CD 116, whereas USDM caps a one-lane roundabout at a 20 m outside diameter. Measured with shapely on worked examples: at a USDM Avenue and Street corner, raising the kerb radius from 5 m to 15 m lengthens the in-line crossing from 8.5 m to 20.8 m (past USDM's 13 m limit) and the effective turning radius from 8.2 m to 18.2 m, and a city bus (AASHTO radii, conservative steady-state check) either cuts the kerb below 5 m or swings into the opposing 3.0 m lane; a 32 m compact roundabout passes every CD 116 check I coded (entry path radius 66 m), while a USDM-size 20 m roundabout fails the ICD minimum and deflects entering traffic almost not at all (entry path radius about 330 m). So the engine must run geometry checks (effective radius, swept path, fastest path), not only look up widths. Main caveat: Dubai RTA's Geometric Design Manual and Abu Dhabi's TR-514 could not be opened, the USDM values come from a 2018 copy of chapter 5 and a 2020 Abu Dhabi DMT reproduction of its Table 5.2, and the AASHTO Green Book is paywalled, so the US numbers come from FHWA and state transport department documents.

## Standards comparison: street section and junction parameters

Columns are the five sources the task names. "US (AASHTO, secondary)" is filled from FHWA, TxDOT and WSDOT documents that summarise or follow the Green Book; I did not open the Green Book. The NACTO column uses the NACTO Global Street Design Guide, because the nacto.org Urban Street Design Guide pages returned HTTP 403 [[22]](https://nacto.org/publication/urban-street-design-guide/street-design-elements/lane-width/). Metric first, the source's imperial value in brackets.

| Parameter | Abu Dhabi USDM (UPC 2010, v1 excerpt; Table 5.2 via DMT 2020) | Dubai (RTA GDM 2017; Dubai Municipality TOD Manual 2025) | US: AASHTO Green Book (secondary: FHWA, TxDOT, WSDOT) | NACTO Global Street Design Guide | UK DMRB (CD 109, CD 123, CD 116; CD 127 for lanes) |
|---|---|---|---|---|---|
| General traffic lane width | Travel lanes 3.3 m on Boulevards and Avenues in City, Town, Commercial and Residential contexts; 3.3 to 3.7 m Industrial [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf). Text: "curb lanes shall be 3.5 m, while other lanes widths are 3.3 m" on Boulevards and Avenues [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf). Kerb lane in Table 5.2: Boulevard/Avenue 3.3 to 3.5 m, Street 3.0 to 3.5 m, Access Lane 3.0 to 3.3 m [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf). Shared "yield lane" 3.0 m max [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf) | not found (GDM not publicly downloadable; it is a binding RTA manual [[6]](https://dlp.dubai.gov.ae/Legislation%20Reference/2025/Administrative%20Resolution%20No.%20%28273%29%20of%202025%20Regulating%20Works%20in%20the%20Right%20of%20Way.pdf)) | 10 ft (3.05 m) lanes "appropriate in urban areas"; avoid lanes over 11 ft (3.35 m); no substantive safety difference between 10, 11 and 12 ft lanes on urban arterials at 45 mph or less [[13]](https://www.fhwa.dot.gov/planning/css/design/tactics/chap13.cfm). Green Book table not verified | 3.0 m recommended; 2.7 m where speed is 30 km/h or less; 3.0 to 3.3 m where shared with trucks and buses; kerbside lanes may be 3.3 m; two-way yield lane 4.75 to 5.5 m [[23]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/travel-lanes/geometry/) | Urban all-purpose: 3.65 m (dual 2-lane and single), dual 3-lane middle lane 3.70 m [[12]](https://www.standardsforhighways.co.uk/tses/attachments/10442706-b592-42c8-85f8-2a0c779a8e37). Signal junctions: ahead lanes 3.0 m min (new), 3.65 m max [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c) |
| Turn lane | Left-turn lane at least 3.0 m wide and 24 m long, taper 1:2 [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf) | not found | Median left-turn lane: a 16 ft (4.88 m) median takes the lane plus a 4 ft (1.22 m) divider [[16]](https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-10-cross-sectional-elements/4-10-15-medians.html) | 3 m or narrower if few trucks [[23]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/travel-lanes/geometry/) | Right-turn (ghost island) lane 3.5 m desirable, 3.0 m new, 2.5 m existing; max 5.0 m urban; signal junction turn lanes at least 3.0 m, 1 in 5 taper [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c) |
| Bus lane | Kerb lane used by buses: 3.5 m (Table 5.2 note 3) [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf) | Dedicated bus lanes required in TOD zones; no width given [[7]](https://dmpmedia.dm.gov.ae/uploads/2025/11/Dubai-Transit-Oriented-Development-Manual.pdf). Width not found | not found | Side-running transit lane 3 to 3.3 m; separated side-running 3.3 to 3.5 m; centre-running lanes 3.3 to 3.5 m; centre-median transitway 10 to 12.5 m overall [[30]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-transit-riders/transit-facilities/geometry/) | not found in the CDs read |
| Cycle lane / track | Bicycle lane 1.5 to 2.5 m [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf); cycle track 1.5 to 2.5 m, cycle lane 1.5 to 2.5 m in Table 5.2 [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf) | At least 1.5 m one-way, 3 m two-way, up to 4 m two-way where space allows; physically separated where vehicle speed exceeds 30 km/h [[7]](https://dmpmedia.dm.gov.ae/uploads/2025/11/Dubai-Transit-Oriented-Development-Manual.pdf) | not found (AASHTO bike guide not opened) | Conventional lane at least 1.8 m (4.3 m from kerb to outer lane edge with parking); buffered lane 3.2 m total; raised track at least 1.8 m, 2 m preferred; parking-protected track 2 m plus 1 m buffer [[29]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-cyclists/cycle-facilities/geometry/) | Refuge at least 3.0 m where cyclists cross a slip-lane island [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338). Cycle track widths are in CD 195 (not read): not found |
| Parking lane | 2.7 m parallel; 2.5 m with stakeholder approval; door clearance 0.5 m (parallel) or 0.7 m (angled); angled stalls 2.5 m wide, 5.0 m projection [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf)[[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf) | not found | Urban kerb parking 8 to 9 ft (2.44 to 2.74 m), 7 ft (2.13 m) minimum in non-commercial areas; 12 to 14 ft (3.66 to 4.27 m) where cyclists share it [[17]](https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-10-cross-sectional-elements.html) | 1.8 to 2.5 m; 2.5 m on high-volume or transit streets [[23]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/travel-lanes/geometry/) | not covered (trunk roads) |
| Footway clear width | "Through" zone, City context: Boulevard 2.8 to 4.0 m, Avenue 2.4 to 4.0 m, Street 2.4 to 3.0 m, Access Lane 1.8 to 2.5 m; Town and Commercial Avenue 2.0 to 3.0 m; Residential 1.8 m minimum. Plus frontage 0.5 to 1.5 m, furnishing 1.0 to 3.5 m and edge 0.2 to 2.0 m zones (edge at least 1.5 m next to parking or a cycle track) [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf) | Pedestrian flow zone 1.5 to 3 m; frontage zone 0.2 to 1 m; service (multi-utility) zone 1.5 to 2 m [[7]](https://dmpmedia.dm.gov.ae/uploads/2025/11/Dubai-Transit-Oriented-Development-Manual.pdf) | Clear width not found. "Border" including sidewalk: at least 10 ft (3.05 m) local, 12 ft (3.66 m) collectors, 8 ft (2.44 m) arterials with 12 ft preferred [[17]](https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-10-cross-sectional-elements.html) | Clear path 2.4 m recommended, 1.8 m absolute minimum; commercial 3 m or more; busy commercial sidewalks 8 to 10 m overall [[26]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/sidewalks/geometry/) | not found in the CDs read |
| Median, no refuge or turn pocket | Centre median 2.0 to 6.0 m (5.0 m max on Residential and Industrial Avenues); side median 0.5 to 4.0 m [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf) | Narrow under 4 m, intermediate 4 to 8 m, wide over 8 m; 7.5 m or more lets a car stop while turning or crossing [[8]](https://pdfcoffee.com/1rta-geometric-design-manual-for-dubai-roads-2017pdf-pdf-free.html) (not verified) | Raised medians 4 to 36 ft (1.22 to 10.97 m) in suburban and urban contexts; divider at least 2 ft (0.61 m) [[16]](https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-10-cross-sectional-elements/4-10-15-medians.html) | At least 1.8 m, 2.4 m preferred [[25]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-refuges/) | Urban dual central reserve 1.80 m [[12]](https://www.standardsforhighways.co.uk/tses/attachments/10442706-b592-42c8-85f8-2a0c779a8e37); any part of a junction central island at least 3.5 m [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c) |
| Median with refuge or turn pocket | Refuge at least 2 m (3 m with heavy pedestrian activity); add 3 m for a left-turn lane; on Boulevards and Avenues a 2.0 m refuge is mandatory when a left-turn lane is added [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf)[[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf) | not found | Refuge 6 ft (1.83 m) from face of kerb minimum; 18 ft (5.49 m) median preferred to hold a 6 ft refuge; crossed divider at least 5 ft (1.52 m), landing at least 5 by 6 ft [[16]](https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-10-cross-sectional-elements/4-10-15-medians.html) | Refuge island at least 1.8 m deep, 2.4 m preferred, ideally 10 to 12 m long [[25]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-refuges/); staggered mid-block median at least 3 m [[28]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-crossings/crossing-types/) | Central island at a minor road: 10 m if right turn out allowed, 8.5 m new / 8 m existing if prevented, 14.0 or 16.5 m for long vehicles; opening 15 m or at least 8 m [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c) |
| Kerb / corner radius by street type | Recommended maximum 5 m at urban junctions; build 2 to 5 m, 0.5 m where no turns; turns no faster than 15 km/h; larger only for Civil Defence needs [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf) | "Minimize kerb radii or install kerb extensions"; no value [[7]](https://dmpmedia.dm.gov.ae/uploads/2025/11/Dubai-Transit-Oriented-Development-Manual.pdf) | 90° right turn, edge of pavement, simple curve: P 30 ft (9.14 m), SU 50 ft (15.24 m); WB-40 45 ft (13.72 m) with 4.0 ft offset and 10:1 taper, or 120-40-120 ft three-centred curve [[18]](https://www.txdot.gov/manuals/des/rdw/chapter-13--intersections/13-10-additional-intersection-design-consideration/13-10-1-minimum-turning-radii.html) | Standard 3 to 5 m; 1.5 m preferred in urban settings; over 5 m the exception; turning speed 10 km/h or less [[24]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/corner-radii/) | Priority junction, urban: at least 6 m with no design-vehicle provision, 10 m plus 1:5 taper over 30 m with it; rural 10 m, or 15 m plus 1:10 over 25 m; ghost island 15 m plus 1:6 over 30 m; signal junctions use the same values [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c) |
| Design speed | By street family: not found in the sources read. Turns 15 km/h max; roundabout entry 15, 20 or 30 km/h; driveway entry 15 km/h [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf) | Speed limit 30 km/h in metro station areas, 15 km/h at pick-up and drop-off [[7]](https://dmpmedia.dm.gov.ae/uploads/2025/11/Dubai-Transit-Oriented-Development-Manual.pdf) | not found (design speed tables not verified) | Urban design speed should not exceed 40 km/h; never target 60 km/h or more; 10 to 15 km/h where people walk in the roadway; 30 km/h or less where cyclists mix with traffic [[31]](https://globaldesigningcities.org/publication/global-street-design-guide/design-controls/design-speed/) | Urban: 30 mph (48 km/h) limit → 60B km/h design speed; 40 mph → 70A; 50 mph → 85A; 60 mph → 100A [[9]](https://www.milton-keynes.gov.uk/sites/default/files/2022-04/CD13j%20Highway%20link%20design.PDF) |
| Roundabout inscribed circle diameter (ICD) | Table 5.10: mini and one-lane, maximum outside diameter 20 m, maximum island 15 m; two-lane not given. Figure 5.33 shows a one-lane outside radius R1 of 12.5 to 20 m (conflicts with the table) [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf) | not found | FHWA 2000: mini 13 to 25 m, urban compact 25 to 30 m, urban single-lane 30 to 40 m (WB-15), urban double-lane 45 to 55 m, rural 35 to 40 m and 55 to 60 m [[19]](https://www.fhwa.dot.gov/publications/research/safety/00067/000676.pdf). WSDOT 2024: mini 45 to 80 ft (13.7 to 24.4 m), single-lane 80 to 150 ft (24.4 to 45.7 m), multilane 120 to 165 ft (36.6 to 50.3 m) [[20]](https://wsdot.wa.gov/publications/manuals/fulltext/M22-01/1320.pdf) | Mini-roundabout: about 5 m clearance from the corner to the widest point [[34]](https://globaldesigningcities.org/publication/global-street-design-guide/intersections-4/mini-roundabout/). Other ICD values not found | At least 28 m (normal and compact); compact 28 to 36 m; normal up to 100 m; mini-roundabout up to 28 m with a flush or domed island 1 to 4 m; Table 3.8 minimum ICD by island size (4 m → 28.0 m, 12 m → 32.0 m, 18 m → 36.0 m) [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338) |
| Roundabout entry width | Entry lanes: 1 (mini, one-lane), 2 (two-lane); width not found [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf) | not found | Single-lane entry typically 4.3 to 4.9 m [[19]](https://www.fhwa.dot.gov/publications/research/safety/00067/000676.pdf); WSDOT single-lane 16 to 18 ft (4.9 to 5.5 m), multilane 25 ft (7.6 m) [[20]](https://wsdot.wa.gov/publications/manuals/fulltext/M22-01/1320.pdf) | not found | Lanes at give way 3.0 to 4.5 m; single-lane entry 4.5 m; multi-lane 3.0 to 3.5 m; entry no wider than 10.5 m (single carriageway) or 15 m (dual); at most 4 lanes [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338) |
| Roundabout entry (kerb) radius | "R as per design vehicle" (figure label) [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf) | not found | Capacity rises with entry radius up to 20 m, little beyond; entry path radius R1 should desirably be no larger than the circulating radius R2 [[19]](https://www.fhwa.dot.gov/publications/research/safety/00067/000676.pdf) | not found | 10 to 100 m; at least 20 m on approaches with regular HGVs (except compact); over 20 m adds little capacity, under 15 m reduces it [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338) |
| Circulatory carriageway width | Mini B = 4 to 6 m; one-lane B = 5 to 6 m; two-lane B = 8 m; apron strip b1 = 1 to 1.5 m [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf) | not found | At least the maximum entry width, up to 120% of it [[19]](https://www.fhwa.dot.gov/publications/research/safety/00067/000676.pdf); WSDOT single-lane 14 to 19 ft (4.3 to 5.8 m), multilane 29 ft (8.8 m) [[20]](https://wsdot.wa.gov/publications/manuals/fulltext/M22-01/1320.pdf) | not found | 1.0 to 1.2 times maximum entry width, excluding overrun; normal 15 m max; compact 6 m max [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338) |
| Deflection | "Deflection 1:5 to 1:7" (figure label); maximum entry speed 15 (mini), 20 (one-lane), 30 km/h (two-lane) [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf) | not found | Maximum entry design speed: urban compact 25 km/h, urban single-lane 35 km/h, urban double-lane 40 km/h; fastest path 1.5 m from kerbs, 1.0 m from painted lines; maximum R1 54 m at 30 m ICD, 61 m at 35 m [[19]](https://www.fhwa.dot.gov/publications/research/safety/00067/000676.pdf) | not found | Entry path radius no more than 70 m (compact, 40 mph or less) or 100 m (other); path 2 m wide (1 m clearance), starts 50 m before the give way line, best-fit circle over 25 m; entry angle 20° to 60° [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338) |
| Crossing width and placement | Width not found; pedestrian crossing distance max 13 m; roundabouts: at most two lanes to cross, raised marked crossings on one-lane roundabouts [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf) | not found | Roundabout crosswalks about 20 ft (6.1 m) from the circulating lane edge [[20]](https://wsdot.wa.gov/publications/manuals/fulltext/M22-01/1320.pdf); width not found | At least 3 m and at least the sidewalk width; crossings every 80 to 100 m, never over 200 m [[27]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-crossings/) | Width not found. Crossings beyond the junction radii [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c); at roundabouts, uncontrolled islands within 20 m of give way, signal crossings at 20 m or beyond 60 m [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338) |
| Refuge island width | 2 m (3 m heavy pedestrian activity); roundabout splitter used as refuge at least 3.0 m [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf)[[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf) | not found | 6 ft (1.83 m) minimum [[16]](https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-10-cross-sectional-elements/4-10-15-medians.html); splitter islands narrower than 6 ft may not work as refuges [[20]](https://wsdot.wa.gov/publications/manuals/fulltext/M22-01/1320.pdf) | 1.8 m minimum, 2.4 m preferred [[25]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-refuges/) | Slip-lane refuge at least 2 m; 3.0 m where cyclists cross [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338); refuge nose set back at least 1.5 m from the crossing carriageway edge [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c) |
| Sight distance basics | Unsignalised junctions: clear sight 25.0 m along the major road from the side-street centreline, measured 2.4 m back from the stop line [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf) | not found | Stopping sight distance (SSD) = 1.47Vt + 1.075V²/a, t = 2.5 s, a = 11.2 ft/s²: 25 mph 155 ft (47 m), 30 mph 200 ft (61 m), 40 mph 305 ft (93 m); eye 3.5 ft (1.07 m), object 2.0 ft (0.61 m) [[15]](https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-11-sight-distance.html) | Daylight junctions by removing parking within 6 to 8 m; trees at least 3 m from the junction [[32]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/visibility-sight-distance/) | Desirable minimum SSD 70 m (50 km/h), 90 m (60), 120 m (70), 160 m (85), 215 m (100), 295 m (120); eye 1.05 to 2.0 m, object 0.26 to 2.0 m [[9]](https://www.milton-keynes.gov.uk/sites/default/files/2022-04/CD13j%20Highway%20link%20design.PDF). Priority junction set-back (X) 9 m, minimum 2.4 m (simple) or 4.5 m (other) [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c) |
| Junction spacing | Through-street spacing, City context: Boulevard 400 to 750 m, Avenue 200 to 375 m, Street 100 to 175 m (Table 5.7; other contexts in the Detail) [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf) | not found | not found | Crossings every 80 to 100 m [[27]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-crossings/) | Right/left stagger at least 50 m (no central treatment or ghost island), 40 m (single lane dualling), 60 m (dual) [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c) |

**Where sources differ most:**
- **Lane width:** 3.0 m (GSDG) against 3.3 m (USDM) against 3.65 m (DMRB). FHWA's 10 ft equals GSDG's 3.0 m.
- **Corner radius:** 1.5 m (GSDG preferred) and 5 m maximum (USDM) against 6 to 10 m minimums (DMRB CD 123) and 9 to 15 m edge-of-pavement radii (US, TxDOT).
- **Roundabout size:** a 20 m maximum (USDM one-lane) against a 28 m minimum (DMRB) and 30 to 40 m (FHWA, urban single-lane with a WB-15 truck).
- **Refuge:** 1.8 m (GSDG, TxDOT) against 2.0 m (USDM, DMRB).

## Detail

### What each source is, and how far it can be trusted

**Abu Dhabi USDM.** The manual was written for the Abu Dhabi Urban Planning Council (UPC). It names streets by family: Boulevard (3+3 lanes), Avenue (2+2), Street (1+1) and Access Lane (1+1 or a single shared lane) [[3]](https://www.cnu.org/node/1825).

- The full PDF host returned HTTP 403 [[5]](https://bicycleinfrastructuremanuals.com/manuals4/Abu-Dhabi-StreetDesignManual.pdf).
- I used a chapter 5 copy ("Street Design Elements", pages 24 to 48), uploaded to a third-party site in 2018 [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf).
- I also used the Abu Dhabi Department of Municipalities and Transport (DMT) Outdoor Seating Areas Manual (2020). It reproduces USDM Table 5.2, "Minimum and maximum dimensions", by context (City, Town, Commercial, Residential including Emirati neighbourhoods, Industrial) [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf).

The table's own note says it is for "atypical streets ... only to be used for specific conditions". New streets should use the typical sections in USDM section 5.3, which I could not see. Treat Table 5.2 as the allowed range, not the target value.

The DMT road geometric design manual, TR-514 on the Abu Dhabi Quality and Conformity Council (QCC) site, was unreachable. The connection was reset, and WebFetch got HTTP 503 [[4]](https://jawdah.qcc.abudhabi.ae/en/Registration/QCCServices/Services/STD/ISGL/ISGL-LIST/TR-514.pdf).

**Dubai.** Administrative Resolution No. 273 of 2025 makes the RTA's "Geometric Design Manual for Dubai Roads" binding, together with the Access Management Manual and the Roadside Design Guide. It says the manuals "will be published on the RTA's official website" [[6]](https://dlp.dubai.gov.ae/Legislation%20Reference/2025/Administrative%20Resolution%20No.%20%28273%29%20of%202025%20Regulating%20Works%20in%20the%20Right%20of%20Way.pdf). I could not find an official download. The only copies online are on document-sharing sites, and I did not use them. The single Dubai GDM fact in the table (the median width classes) comes from search-result text quoting one such copy [[8]](https://pdfcoffee.com/1rta-geometric-design-manual-for-dubai-roads-2017pdf-pdf-free.html), and is flagged "not verified". The Dubai Municipality TOD Manual (2025) is official and public. It gives footway zones, cycle widths and speed limits for station areas [[7]](https://dmpmedia.dm.gov.ae/uploads/2025/11/Dubai-Transit-Oriented-Development-Manual.pdf).

**AASHTO.** The Green Book is paywalled. The US column is secondary:
- FHWA's lane-width guidance [[13]](https://www.fhwa.dot.gov/planning/css/design/tactics/chap13.cfm).
- The Texas Department of Transportation (TxDOT) Roadway Design Manual. It cites "AASHTO's A Policy on Geometric Design of Highways and Streets" for design vehicles and turning paths [[14]](https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-3-traffic-characteristics.html)[[18]](https://www.txdot.gov/manuals/des/rdw/chapter-13--intersections/13-10-additional-intersection-design-consideration/13-10-1-minimum-turning-radii.html).
- For roundabouts, the FHWA 2000 informational guide (old) [[19]](https://www.fhwa.dot.gov/publications/research/safety/00067/000676.pdf) and the Washington State DOT (WSDOT) Design Manual, chapter 1320 (2024) [[20]](https://wsdot.wa.gov/publications/manuals/fulltext/M22-01/1320.pdf).

The current national roundabout guide, NCHRP Report 672, displays only page images online, so I could not read its numbers [[21]](https://www.nationalacademies.org/read/22914/chapter/7).

**NACTO.** The Urban Street Design Guide pages on nacto.org returned HTTP 403 [[22]](https://nacto.org/publication/urban-street-design-guide/street-design-elements/lane-width/). The Global Street Design Guide, published by NACTO's Global Designing Cities Initiative, is open and metric. It is the better fit for the GCC anyway, so it fills the NACTO column [[23]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/travel-lanes/geometry/).

**DMRB.** I downloaded CD 116 v2.1.0 (May 2023) [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338), CD 123 v2.1.0 (November 2021) [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c) and CD 127 v1.0.1 (July 2021) [[12]](https://www.standardsforhighways.co.uk/tses/attachments/10442706-b592-42c8-85f8-2a0c779a8e37) from standardsforhighways.co.uk. CD 109 came from a council-hosted copy of Revision 1 [[9]](https://www.milton-keynes.gov.uk/sites/default/files/2022-04/CD13j%20Highway%20link%20design.PDF). DMRB covers UK trunk roads and motorways, so it has little on footways, parking or urban streets. It is written for left-hand traffic. Its roundabout figures have to be mirrored for the UAE.

### Lane widths

The engine needs a per-element width range keyed by street family and context, not one "lane width".

**USDM** separates the kerb lane from the other travel lanes. Section 5.9.1 says kerb lanes "shall be 3.5 m" on Boulevards and Avenues and other lanes 3.3 m [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf). Table 5.2, in the 2020 reproduction, gives the kerb lane as 3.3 to 3.5 m, with 3.5 m "if buses use curb lane as part of a regular transit route" [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf). The two disagree slightly, so the engine should flag a 3.3 m kerb lane on a bus route. The "frontage lane" is a slow service lane between side medians on Boulevards. It is 4.0 to 4.5 m (absolute minimum 3.0 m with stakeholder approval), and the manual treats it as part of the pedestrian realm [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf)[[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf). USDM also caps lane transitions at 1:10, with 1:2 tapers to turn lanes, so that the 13 m maximum crossing distance holds [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf).

**DMRB** sets 3.65 m lanes on urban all-purpose roads (Figure 2.1.1N1g in CD 127) and measures lane widths between the trafficked edges of the edge lines and the centre of the lane lines [[12]](https://www.standardsforhighways.co.uk/tses/attachments/10442706-b592-42c8-85f8-2a0c779a8e37). On tight curves CD 123 widens lanes. A single lane needs 8.4 m at a 10 m inside radius, 5.3 m at 30 m and 3.8 m at 90 m (Table 5.10) [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c). An engine that lets users draw curved streets should apply this kind of widening table.

**GSDG** recommends 3 m, allows 2.7 m at 30 km/h or less, and says "remnant width should not be added to the lane" [[23]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/travel-lanes/geometry/). That last point is a useful rule: surplus right-of-way should go to footways or planting, not wider lanes.

### Kerb radii and corner geometry

USDM separates the "corner radius" (the kerb) from the "turning radius" (the effective path of the vehicle) and asks designers to "calculate effective turning radius and available space for turning, including the space for on-street parking, bicycle lanes, and all travel lanes on the receiving street" [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf).

USDM Table 5.9 sets a design vehicle (regularly accommodated without entering opposing lanes) and a control vehicle (infrequent, which may encroach) for each street family [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf):

| Street family | Design vehicle | Control vehicle |
|---|---|---|
| Boulevard, Avenue | WB-15M semitrailer | WB-33DM double trailer |
| Street | City-Bus M | aerial fire truck |
| Access Lane | SU M | SU M |

USDM also warns that a corner big enough for a WB-15 at 15 km/h lets cars take it at 43 km/h [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf). GSDG uses the same design-vehicle and control-vehicle split [[33]](https://globaldesigningcities.org/publication/global-street-design-guide/design-controls/design-vehicle-control-vehicle/).

DMRB CD 123 takes the opposite starting point. Its corner radii assume the design vehicle can turn: 10 m plus a 1:5 taper over 30 m in urban areas [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c). Where large vehicles are not catered for at signal junctions, it suggests setting stop lines back so they can swing wide [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c). TxDOT's AASHTO-based Table 13-7 gives edge-of-pavement designs measured from outermost lane to outermost lane. A passenger car needs a 30 ft (9.14 m) simple curve for a 90° turn [[18]](https://www.txdot.gov/manuals/des/rdw/chapter-13--intersections/13-10-additional-intersection-design-consideration/13-10-1-minimum-turning-radii.html).

The engine therefore needs both a kerb radius per corner (per street-type pair) and a computed effective radius and swept-path check. The worked example below shows why.

### Roundabout geometry

CD 116 defines three roundabout types by ICD and central island [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338):

| Type | ICD | Central island | Notes |
|---|---|---|---|
| Mini | up to 28 m | flush or domed, 1 to 4 m | island not kerbed |
| Compact | 28 to 36 m | at least 4 m | single-lane entries and exits; circulatory width that stops two cars passing |
| Normal | 28 to 100 m | at least 4 m | |

Its main checks are:
- **ICD (3.5):** at least 28 m, "the smallest roundabout that can accommodate the swept path of the design vehicle". The default design vehicle is a 16.5 m articulated HGV.
- **ICD against island size (Table 3.8):** minimum ICD rises with the central island, from 28.0 m at 4 m to 36.0 m at 18 m. This table is drawn up for a 15.5 m articulated vehicle.
- **Circulatory width (3.6):** 1.0 to 1.2 times the maximum entry width, excluding any overrun area.
- **Entry lanes (3.14):** 3.0 to 4.5 m at the give way line.
- **Flare length (3.17.1):** at least 5 m urban, 25 m rural.
- **Entry angle (3.18.1):** 20° to 60°.
- **Entry kerb radius (3.19):** 10 to 100 m.
- **Entry path radius (3.24 to 3.26):** no more than 70 m on urban compact roundabouts, 100 m elsewhere.

CD 116 calls entry deflection "the most important factor for safety as it governs the speed of vehicles" [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338). The entry path radius is measured on the "fastest path": a 2 m wide path whose centreline keeps 1 m from kerbs. It starts 50 m before the give way line and is fitted with a circle over 25 m. CD 116 adds that "the construction of the path is a matter of personal judgement" [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338). FHWA uses a 1.5 m offset from kerbs [[19]](https://www.fhwa.dot.gov/publications/research/safety/00067/000676.pdf), and WSDOT uses 5 ft (1.5 m) [[20]](https://wsdot.wa.gov/publications/manuals/fulltext/M22-01/1320.pdf). The construction therefore differs between standards.

USDM Table 5.10 is a "Modern Roundabout Criteria Matrix" [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf):

| | Mini | One-lane | Two-lane (signalised) |
|---|---|---|---|
| Maximum entry speed | 15 km/h | 20 km/h | 30 km/h |
| Maximum outside diameter | 20 m | 20 m | not given |
| Maximum island diameter | 15 m | 15 m | not given |
| Circulating lanes | 1 | 1 | 2 |
| Raised crosswalk | maybe | yes | maybe |
| Signalised crosswalk | no | no | yes |

USDM figures give the circulating width B (4 to 6 m mini, 5 to 6 m one-lane, 8 m two-lane) and "deflection 1:5 to 1:7". USDM does not recommend roundabouts with more than two lanes "without initial approval from the UPC" [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf).

The USDM figures are internally inconsistent. Figure 5.33 labels the one-lane outside radius R1 as 12.5 to 20 m, which is a 25 to 40 m diameter, while the table caps the outside diameter at 20 m. The engine should treat the USDM one-lane limit as an open question. A 20 m ICD also fails DMRB's swept-path minimum. FHWA's urban single-lane range for a WB-15 is 30 to 40 m [[19]](https://www.fhwa.dot.gov/publications/research/safety/00067/000676.pdf), and Table 3.8 of CD 116 needs at least 28 m.

### Crossings: zebra and signalised, widths, refuges, raised crossings

- **Crossing type:**
  - CD 116 Table 8.1.3 suggests crossing types at roundabouts where approaches are 40 mph or less, by road class and traffic. On single carriageways: uncontrolled below 8,000 two-way AADT (annual average daily traffic), uncontrolled or zebra at 8,000 to 12,000, zebra above 12,000. On dual carriageways: signal-controlled above 25,000.
  - CD 116 notes that the UK Traffic Signs Manual does not recommend zebras where 85th-percentile speeds are 35 mph or more [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338).
  - GSDG says crossings should be signalised or traffic-calmed on streets with more than one lane per direction or speeds above 30 km/h [[25]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-refuges/).
  - Dubai's RTA has published no crossing-type rules I could open.
- **Width:** GSDG says at least 3 m and at least as wide as the connected sidewalks [[27]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-crossings/). USDM asks for two kerb ramps per corner, each the full width of the crosswalk, and cut-throughs at street level in median refuges rather than ramps [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf). No metric crossing width was found for USDM, Dubai, DMRB or the US sources.
- **Length:** USDM caps the pedestrian crossing distance at 13 m [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf). In the worked example, an 18.2 m Avenue needs its 2.0 m refuge to stay within it.
- **Refuges:**
  - USDM: 2 m, or 3 m with heavy pedestrian activity [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf). Roundabout splitter islands 3.0 m at crossings [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf).
  - GSDG: 1.8 m, preferred 2.4 m, ideally 10 to 12 m long, with a nose past the crossing [[25]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-refuges/).
  - CD 123: refuge noses set back at least 1.5 m from the crossing carriageway edge, and crossings placed beyond the junction radii [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c).
- **Raised crossings:**
  - USDM: one-lane roundabouts "shall have raised, marked crossings". Yield-controlled right-turn slip lanes get a raised crossing at a 15 km/h design speed [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf).
  - The Dubai TOD Manual lists elevated crosswalks among traffic-calming measures [[7]](https://dmpmedia.dm.gov.ae/uploads/2025/11/Dubai-Transit-Oriented-Development-Manual.pdf).
  - GSDG puts vertical speed-control elements 5 to 10 m before a crossing [[28]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-crossings/crossing-types/).
- **Placement at roundabouts:**
  - CD 116: uncontrolled crossing islands within 20 m of the give way line; non-staggered signal crossings "at 20 metres or more than 60 metres" from it [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338).
  - WSDOT: crosswalks "typically ... about 20 feet" (6.1 m) from the circulating lane edge [[20]](https://wsdot.wa.gov/publications/manuals/fulltext/M22-01/1320.pdf).
  - USDM figures label a dimension "L = 5 m" between crossing and circulating edge [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf). This is my reading of the figure, not stated in the text.
- **Spacing:** GSDG: every 80 to 100 m and never over 200 m [[27]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-crossings/).

### Medians and U-turns

Medians in GCC cities carry three loads at once: the refuge, the left-turn pocket and the U-turn.

USDM sizes them additively. Refuge 2 m (3 m with heavy pedestrian activity), plus 3 m for a left-turn lane. A 2.0 m refuge is mandatory on Boulevards and Avenues when left-turn lanes are introduced [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf)[[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf). Its centre median range is 2.0 to 6.0 m [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf).

On U-turns, USDM says they "may be used on Boulevards and Avenues", should be located before crosswalks, and should be signalised "where there are two or more receiving lanes" [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf). The RTA GDM reportedly defines the median gap at a U-turn and classes medians as narrow (under 4 m), intermediate (4 to 8 m) and wide (over 8 m) [[8]](https://pdfcoffee.com/1rta-geometric-design-manual-for-dubai-roads-2017pdf-pdf-free.html) (not verified). TxDOT tells designers to consider U-turn demand when setting median width and to discourage raised medians "where the roadway cross-section is too narrow for U-turns". It points to FHWA's Median U-Turn guide for minimum widths, a figure I could not read [[16]](https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-10-cross-sectional-elements/4-10-15-medians.html)[[18]](https://www.txdot.gov/manuals/des/rdw/chapter-13--intersections/13-10-additional-intersection-design-consideration/13-10-1-minimum-turning-radii.html). DMRB CD 123 prohibits U-turns where a physical central reserve divides a WS2+1 road (a wide single carriageway with 2+1 lanes) [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c).

I measured U-turn feasibility (Part C of the script, method as in Example A). For a 180° turn around a median nose of width M, the receiving width needed beyond the median edge is max(M/2, r_in) + (r_out − r_in) − M/2. Here r_in and r_out are the vehicle's minimum inside and design turning radii (AASHTO via TxDOT [[14]](https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-3-traffic-characteristics.html)). On a USDM Avenue (two 3.3 m receiving lanes, 6.6 m), the output is:

```
   median M    P (car)    CITY-BUS       SU-30       WB-40
        2.0    6.25 ok    11.68 X     11.74 X     11.16 X
        6.0    4.25 ok     9.68 X      9.74 X      9.16 X
       12.0    2.87 ok     6.68 X      6.74 X      6.28 ok
```

A car can U-turn around a 2 m USDM median. A bus or single-unit truck cannot, even around a 12 m median, without a local widening of the far side (usually called a loon) or a wider median. The steady-state assumption makes these figures conservative.

### How Autodesk Civil 3D draws street sections and junctions

- **Assemblies and subassemblies.** An assembly is "a collection of subassemblies that are used to form the basic structure of a 3D corridor model" [[35]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-B01563A3-A7FB-441D-987A-2A2801EEC321.htm).
  - A subassembly is a cross-section component (lane, kerb, footway, ditch) defined by points, links and shapes with codes. Some adapt to superelevation or cut and fill.
  - Conditional subassemblies insert others when conditions are met [[36]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-E9277B4B-CC74-4FD7-ABAD-B1F8B369F5A3.htm).
  - Defaults show Civil 3D is not a standards engine. LaneOutsideSuper has a "Width" parameter, default 3.6 m (12.0 ft), and a target parameter that can tie the lane edge to an offset alignment [[49]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-Subassembly-Ref/files/GUID-C08C2692-1562-4061-A9AD-47AA6DD74152.htm). UrbanSidewalk defaults to a 1.5 m (5.0 ft) sidewalk with optional grass boulevards [[50]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-Subassembly-Ref/files/GUID-61C1448A-7B0A-43D9-B732-AC2BAEE1D3F4.htm).
- **Corridors.** A corridor places assemblies "at incremental locations" along a baseline (alignment plus profile), and builds feature lines, surfaces and quantities. Multiple baselines allow "more complex designs, such as intersections" [[37]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-F2246A0B-809E-4801-97A5-EFACFA05EE46.htm).
- **Intersection wizard.** Intersections are three-way or four-way objects built from two alignments. They use centreline, offset and "curb return" alignments, profiles, and an "assembly set" (an XML file listing the assemblies for each intersection region) [[38]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-0757C2A9-B439-43D3-9EB0-BFB50F237E6A.htm)[[41]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-8B25124A-8354-4229-AAB8-5ADFE16E38C7.htm). The wizard's Geometry Details page creates offset and curb-return alignments and profiles [[39]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-DFA739A3-12B1-4F7A-B431-B81C49DE4A8B.htm).
- **Curb return parameters.** Set per quadrant: type (chamfer, circular fillet or 3-centred arcs), radius, length along the incoming and outgoing roads, curve radius and length for each arc, and optional turn-lane widening with transition details. A "Copy These To All Quadrants" command applies one quadrant's values to all [[40]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-775B4273-813C-4804-9F02-C32AF216D971.htm). This is the parameter set a Studio corner should expose.
- **Roundabouts and Autodesk Vehicle Tracking.**
  - Civil 3D 2025 models roundabouts "according to defined standards" (UK terms: normal and compact). It checks geometry against each standard's minimum and maximum values and shows warnings, which a "Design Check" tool records along with written justifications [[42]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-AA9A4F3D-CEF3-4F6D-8813-E9F47501286A.htm).
  - The roundabout feature came from Vehicle Tracking. Civil 3D adds alignments, profiles and a 3D corridor rebuilt on change [[43]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-092F412E-5926-4258-B05E-618B6E2E9789.htm)[[44]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-C13E11FD-8720-4897-BFAC-E97ADF8D4A76.htm).
  - The standard editor has a fastest-path calculation using V² = 127R(e + f). It exposes start distance, entry, island and exit offsets, and a "Radius Calculation Length" over which it computes "a 3-point arc ... using the start, middle and end points". The help admits "differing methods often give different answers" [[45]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-D4C47FB1-CD7B-4665-B5E0-84870064D449.htm).
  - Design vehicles in the editor are described by overall width, front and rear overhangs, tractor and trailer wheelbases, kingpin offset and drawbar length [[46]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-E5C35EED-3DA5-4C23-AD69-D88717BD21D4.htm).
  - Entry settings include design speed, lane widths for single and multiple lanes, flare length and taper ratio [[47]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-DFAB5C9F-8FF4-437C-A9D3-5A3FFCE3E521.htm).
  - A two-way link to TRL's ARCADY 8 (capacity software) returns capacity results live [[48]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-B0E67422-BB0D-4B3E-9B25-7C300465CC2E.htm).

Lesson for Studio: Civil 3D keeps geometry (alignments, curb returns) apart from section content (assemblies). It encodes compliance as a swappable "standard" file of minimum, default and maximum values per parameter, with warnings rather than hard blocks. The worked examples below reproduce its fastest-path radius method (3-point arc over 25 m) alongside DMRB's best-fit method.

### How others do it

- **Bentley OpenRoads Designer.**
  - Corridors are created on a geometry element and then filled by "template drops" over station ranges [[52]](https://docs.bentley.com/LiveContent/web/OpenRoads%20Designer%20Help-v20/en/newcorridor.html).
  - Repeatable junction pieces are "civil cells": stored collections of geometry, templates and terrain that keep their rules when placed against new reference elements. Bentley lists "traffic islands and pedestrian refuges" as a typical use and says civil cells "help to ensure compliance with design standards" [[51]](https://docs.bentley.com/LiveContent/web/OpenRoads%20Designer%20Help-v20/en/GUID-D27470C6-8D0D-1701-A14A-B6D288F71E8F.html).
  - I found no roundabout-specific tool in the v20 topic list I scanned (not exhaustive).
- **12d Model.** The home page states only "World Leading Software for Surveying, Civil and Water Engineering". Its wiki (12dwiki.com.au) returned HTTP 403 [[61]](https://www.12d.com/). Not verified.
- **Autodesk InfraWorks.** The product page returned HTTP 403 and I found no help table of contents [[62]](https://www.autodesk.com/products/infraworks/overview). Not verified.
- **Streetmix** (open source, AGPL-3.0 since its BSD period [[58]](https://github.com/streetmix/streetmix/blob/7215e1b7b57637a6bc9a28e648b91bbe1033df72/LICENSE)). Each segment type in `segment-lookup.yaml` has a default width and `rules.minWidth` and `maxWidth` in metric and imperial [[56]](https://github.com/streetmix/streetmix/blob/7215e1b7b57637a6bc9a28e648b91bbe1033df72/packages/parts/data/segment-lookup.yaml):

  | Segment | Default | Min | Max |
  |---|---|---|---|
  | Sidewalk | 1.8 m | 1.8 m | |
  | Bike lane | 1.8 m | 1.5 m | |
  | Drive lane | 3.0 m | 2.4 m | 3.6 m |
  | Turn lane | 3.0 m | 2.7 m | 3.6 m |
  | Bus lane | 3.6 m | 3.0 m | 3.9 m |
  | Parking lane | 2.0 m | 2.1 m | 3.0 m |

  - Its warnings code flags "tooNarrow", "tooWide", "outOfBounds" and slope warnings per slice [[57]](https://github.com/streetmix/streetmix/blob/7215e1b7b57637a6bc9a28e648b91bbe1033df72/client/src/streets/warnings.ts).
  - The parking lane's default (2.0 m) is below its own minimum (2.1 m). This shows why rule data needs a test.
  - Streetmix has no junctions.
- **Esri CityEngine.**
  - Streets are graph segments with roadbed lanes and sidewalk lanes; each lane has a width and travel direction [[53]](https://doc.arcgis.com/en/cityengine/2026.0/help/help-layers-street-parameters.htm)[[55]](https://doc.arcgis.com/en/cityengine/2026.0/help/street-lane-parameters.htm).
  - Nodes have a type (Crossing, Junction, Roundabout or Freeway), a "Curb Radius (attr minArcRadius)" settable per corner, and a block-corner style. A roundabout node takes "Roundabout Island Radius" and "Roundabout Street Width" [[54]](https://doc.arcgis.com/en/cityengine/2026.0/help/help-intersection-parameters.htm).
  - It does no standards checking.
- **TestFit, Giraffe, Autodesk Forma.**
  - TestFit's Site Solver offers "customizable road layout, turning radius and topography data" with no published parameters [[59]](https://www.testfit.io/product/site-solver).
  - Giraffe's home page mentions subdivision and parking layouts but no road tools [[60]](https://www.giraffe.build/).
  - Forma's help centre rendered no readable content here [[63]](https://help.autodeskforma.com/hc/en-us).
  - None of the three publishes a street-standards rule set I could find.

Takeaway: engineering tools (Civil 3D, OpenRoads) model full geometry and leave compliance to configurable "standards" or reusable cells. Planning tools (Streetmix, CityEngine) model widths and kerb radii but do not check junction geometry. A GCC masterplanning tool can stand out by putting USDM-level checks into planning-stage geometry.

### Worked example A: corner geometry (USDM Avenue × Street, right-hand traffic)

**Inputs (all quoted).**
- **Avenue, City context:** cycle lane 1.5 m, kerb lane 3.3 m, travel lane 3.3 m per direction, centre median 2.0 m. Kerb-to-kerb 18.2 m.
- **Street, City context:** parking 2.7 m and kerb lane 3.0 m per side. Kerb extensions at the corner 0.5 m narrower than the parking lane (2.2 m), so 7.0 m kerb-to-kerb at the crossing [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf)[[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf).
- **Footway desire line:** the centre of the 2.4 m through zone, 2.4 m behind the kerb (edge 0.2 + furnishing 1.0 + half the through zone 1.2).
- **Vehicles:** AASHTO minimum design turning radius (outer front corner) and minimum inside radius (inner rear wheel) from TxDOT Table 4-1 [[14]](https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-3-traffic-characteristics.html):

  | Vehicle | Outer radius | Inner radius | Note |
  |---|---|---|---|
  | P (car) | 23.8 ft (7.25 m) | 14.4 ft (4.39 m) | |
  | CITY-BUS | 41.6 ft (12.68 m) | 24.5 ft (7.47 m) | closest to USDM's "City-Bus M" |
  | SU-30 | 41.8 ft (12.74 m) | 28.4 ft (8.66 m) | |
  | WB-40 | 39.9 ft (12.16 m) | 19.3 ft (5.88 m) | |

**Method** ([geometry_checks.py](assets/C11/geometry_checks.py), Part A):
1. The footway block is a quadrant whose corner is rounded with `box(...).buffer(-R).buffer(R)`. Kerb-return length and lost footway area are measured from the polygons.
2. The crossing length is the desire line clipped by the two rounded corners. The set-back needed to keep the crossing at kerb-to-kerb width is R − 2.4 m.
3. **Effective turning radius** Re is the largest inner-edge turning circle tangent to the approach lane edge (offset a = 1.5 m, the cycle lane) and the receiving lane edge (b = 0.5 m, from the extension kerb to the travel lane) that does not cut the kerb return. It is found by bisection with shapely (`arc.intersects(footway)`). The closed form is Re = R + a + b + √(2ab), which comes from |C_path − C_kerb| + R = Re with C_path = (b − Re, a − Re) and C_kerb = (−R, −R). The two agree within 0.01 m.
4. **Vehicle check:** the inner edge clears the kerb if Re ≥ r_in. The steady-state swept width (r_out − r_in) must fit the 3.0 m receiving lane for a design vehicle, or both Street lanes (6.0 m) for a control vehicle. Steady state is the full-lock envelope, so it is conservative for a 90° turn.

```python
def effective_radius_closed_form(R, a, b):          # 90-degree corner, kerb return radius R
    return R + a + b + math.sqrt(2 * a * b)         # = bisection result to 0.01 m
fw = box(-60, -60, 0, 0).buffer(-R, join_style="round").buffer(R, join_style="round")
cross = LineString([(-50, -2.4), (57, -2.4)]).difference(union(fw, mirror(fw))).length
```

Command: `python3 -I reports/assets/C11/geometry_checks.py`. Output (full file: [geometry_checks_output.txt](assets/C11/geometry_checks_output.txt)):

```
  R kerb    arc   area  cross setback     Re Re(cf)      P (car)     CITY-BUS        SU-30        WB-40
     0.5   0.79   0.05   7.00    0.00   3.73   3.72         kerb         kerb         kerb         kerb
     2.0   3.14   0.86   7.00    0.00   5.23   5.22           OK         kerb         kerb         kerb
     5.0   7.85   5.40   8.47    2.60   8.23   8.22           OK     +2.21/ok         kerb  +3.28/+0.28
    10.0  15.70  21.59  14.03    7.60  13.23  13.22           OK     +2.21/ok     +1.08/ok  +3.28/+0.28
    15.0  23.55  48.57  20.76   12.60  18.23  18.22           OK     +2.21/ok     +1.08/ok  +3.28/+0.28
  Crossing the Avenue: single stage 18.2 m; with refuge two stages of 8.1 m (USDM max crossing distance 13 m)
```

**Reading the output.**
- **Kerb return:** arc length is πR/2 (7.85 m at R = 5 m). The footway lost grows as R²(1 − π/4): 5.4 m² at 5 m, 48.6 m² at 15 m, per corner.
- **Crossing length:** with the crossing kept on the footway line, it grows from 7.0 m (R ≤ 2.4 m) to 8.5 m at the USDM maximum of 5 m, 14.0 m at the DMRB urban 10 m, and 20.8 m at 15 m. The last two break USDM's 13 m limit. The alternative is to set the crossing back 7.6 m or 12.6 m from the desire line, which pedestrians tend to ignore.
- **Effective radius:** the cycle lane and kerb extension make it 3.2 m larger than the kerb radius at every R. A 2 m kerb already gives a car a 5.2 m inner path, which is enough. This is USDM's and NACTO's argument for small kerb radii.
- **Large vehicles:** the bus needs R ≥ 5 m and the SU-30 needs R ≥ 10 m before their inner edges clear the kerb. Both still cross into the opposing lane of a 3.0 m Street lane at any radius, because their steady-state swept widths (5.2 m and 4.1 m) exceed the lane. Under USDM's own definitions, a City-Bus "design vehicle" on a 3.0 m-lane Street therefore needs either a wider receiving lane, a recessed stop line on the receiving street (GSDG [[23]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/travel-lanes/geometry/)), or reclassification as a control vehicle. The steady-state envelope overstates the swept width of a real 90° turn, so a Studio rule should report "check with swept-path software" rather than "fail".

### Worked example B: roundabout check per DMRB CD 116

**Inputs.**
- **Compact roundabout:** ICD 32 m, central island 12 m (Table 3.8 minimum ICD 32.0 m), single-lane entries 4.5 m wide (3.14.1), circulatory carriageway 5.4 m (1.2 × entry). That leaves a 4.6 m overrun ring for HGVs.
- **Arms and kerbs:** entry kerb radius 15 m, approach half width 3.65 m (CD 127), 3 m splitter islands tapering over 20 m, four arms at 90°.
- **Comparison case:** a "USDM-size" one-lane roundabout. ICD 20 m (Table 5.10 maximum), island 10 m, circulating width 5 m, entry 4.5 m, kerb radius 10 m.

**Method** ([geometry_checks.py](assets/C11/geometry_checks.py), Part B):
1. **Carriageway:** the union of the ICD disc and the arm polygons. Kerb radii are made with `buffer(+Rk).buffer(-Rk)`, which rounds concave corners.
2. **Obstacles:** the overrun perimeter (entry path measured "relative to the perimeter of this area", 3.26.4), the splitter islands and the upstream centre lines.
3. **Free region for the path centreline:** `carriageway.buffer(-1) - obstacles.buffer(1)`. This is a 2 m wide path, so 1 m from kerbs (A1.2).
4. **Fastest through path:** a symmetric clamped cubic spline x(y) from 50 m before to 50 m after the ICD, starting 1 m from the centre line. It is the smoothest path, minimising ∫κ² ds (curvature squared along the path) with scipy SLSQP, subject to the clearance at 300 points being at least 0.
5. **Entry path radius:** the smallest radius over 25 m windows in the left-hand entry curve (CD 116 is drawn for left-hand traffic; mirrored for the UAE, the radius is identical). Three ways: equivalent arc (25 m divided by the heading change), the 3-point arc Civil 3D uses [[45]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-D4C47FB1-CD7B-4665-B5E0-84870064D449.htm), and a least-squares circle on windows wholly inside the curve.

```python
free = carriageway.buffer(-1.0).difference(obstacles.buffer(1.0))      # CD 116 A1.2: 2 m wide path
res = minimize(bending_energy, x0, method="SLSQP",
               constraints=[{"type": "ineq", "fun": clearance}])        # clearance >= 0 at 300 points
r_arc = 25.0 / abs(heading[j] - heading[i])                             # radius over a 25 m window
```

Output:

```
PART B  Compact roundabout to CD 116 (ICD 32 m)
  [PASS] CD 116 3.5: ICD 32.0 >= 28 m
  [PASS] CD 116 3.5.1: compact ICD 32.0 <= 36 m
  [PASS] CD 116 3.7: central island 12.0 >= 4 m
  [PASS] CD 116 3.8/T3.8: ICD 32.0 >= Table 3.8 minimum 32.0 m for a 12.0 m island
  [PASS] CD 116 3.6: circulatory/entry = 1.20 (1.0 to 1.2)
  [PASS] CD 116 3.6.7: compact circulatory width 5.4 <= 6 m
  [PASS] CD 116 3.14: single-lane entry width 4.5 within 3.0 to 4.5 m
  [PASS] CD 116 3.19.1/.2: entry kerb radius 15.0 within 10 to 100 m
  [PASS] CD 116 3.24: entry path radius 66.1 m (25 m equivalent arc; 3-point 63.2 m; least-squares ... 60.0 m) <= 70 m
  [info] FHWA 2000 Exhibit 6-13: max R1 at ICD 32 m ~ 57 m; measured 66 m -> ~44 km/h
PART B  USDM-size one-lane roundabout (ICD 20 m)
  [FAIL] CD 116 3.5: ICD 20.0 >= 28 m
  [FAIL] CD 116 3.8/T3.8: ICD 20.0 >= Table 3.8 minimum 30.8 m for a 10.0 m island
  [FAIL] CD 116 3.24: entry path radius 326.7 m (... 3-point 607.3 m; least-squares ... 414.5 m) <= 70 m
```

Plots: [compact roundabout](assets/C11/roundabout_cd116_compact.png), [USDM-size roundabout](assets/C11/roundabout_usdm_20m.png).

**Reading the output.**
- **The 32 m compact design** passes CD 116, but only just on deflection (66 m against 70 m). The three radius estimators spread from 60 to 66 m, which shows how sensitive the measure is to method. That matches the Civil 3D warning that "differing methods often give different answers" [[45]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-D4C47FB1-CD7B-4665-B5E0-84870064D449.htm).
- **The same design would miss the FHWA guide.** Interpolated from FHWA Exhibit 6-13, the maximum R1 at ICD 32 m is about 57 m. The 66 m path corresponds to about 44 km/h on FHWA's radius and speed pairs, against FHWA's 35 km/h maximum entry speed for urban single-lane roundabouts [[19]](https://www.fhwa.dot.gov/publications/research/safety/00067/000676.pdf).
- **The 20 m roundabout** fails the swept-path size rule and gives almost no deflection. The island plus 1 m clearance (6 m) barely exceeds the 6 m half-width of the approach (splitter plus entry), so the through path is nearly straight. USDM's speed targets (20 km/h entry) cannot be met by geometry alone at that size with 4.5 m entries.
- **Sensitivity:** the result depends on my assumed splitter and entry widths. Narrower entries or a larger mountable island would add deflection. This is why the rule set must compute deflection rather than trust a size table.

### The rule set a street section engine must encode

A machine-readable example with 6 street types and 36 rules is in [street_rules.example.yaml](assets/C11/street_rules.example.yaml). It parses with PyYAML, and every `src` key resolves. Its structure:

1. **Profile and context.** Pick one governing profile per project (USDM, DMRB, GSDG or US) and a context (USDM City, Town, Commercial, Residential, Industrial). Run the others as advisory. Store the traffic side (right for the GCC) and mirror DMRB constructions [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338).
2. **Element catalogue.** Every strip in a section has a type: frontage, through, furnishing and edge zones; cycle track or lane; parking; kerb extension; frontage lane; side median; kerb lane; travel lane; bus lane; turn lane; centre median; refuge. Each has min, max, recommended and absolute-minimum widths, plus a flag where the absolute minimum needs approval. USDM Table 5.2 gives these per family and context [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf). GSDG gives single values [[23]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/travel-lanes/geometry/)[[26]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/sidewalks/geometry/), and DMRB gives fixed 3.65 m lanes [[12]](https://www.standardsforhighways.co.uk/tses/attachments/10442706-b592-42c8-85f8-2a0c779a8e37).
3. **Section rules.**
   - Width in range.
   - Kerb lane 3.5 m on bus routes [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf).
   - Edge zone at least 1.5 m next to parking or a cycle track [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf).
   - Door clearance 0.5 m (parallel) or 0.7 m (angled), and parking only on frontage lanes on Boulevards [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf).
   - Cycle at least 1.5 m one-way and 3 m two-way, separated above 30 km/h [[7]](https://dmpmedia.dm.gov.ae/uploads/2025/11/Dubai-Transit-Oriented-Development-Manual.pdf).
   - Remnant width goes to footway, not lanes [[23]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/travel-lanes/geometry/).
   - Lanes widened on curves of 90 m radius or less per CD 123 Table 5.10 [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c).
4. **Median rules.**
   - Refuge at least 2.0 m (3.0 m heavy pedestrian activity).
   - Add 3.0 m for a left-turn pocket; turn lane at least 3.0 m wide and 24 m long, taper 1:2.
   - Refuge mandatory with left-turn lanes on Boulevards and Avenues [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf)[[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf).
   - Median 2.0 to 6.0 m [[2]](https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf).
   - U-turn feasibility against the design vehicle (Part C method) with a loon option. U-turns before crosswalks, signalised where there are two or more receiving lanes [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf).
5. **Corner rules per street-type pair.**
   - Kerb radius within the profile's band: USDM 2 to 5 m, 0.5 m with no turns [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf); DMRB at least 6 m, or 10 m plus taper [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c); GSDG 1.5 m preferred [[24]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/corner-radii/).
   - Effective radius (R + a + b + √(2ab) at 90°) at least the design vehicle's inside radius [[14]](https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-3-traffic-characteristics.html).
   - Swept path out of opposing lanes for the design vehicle; encroachment allowed for the control vehicle [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf)[[33]](https://globaldesigningcities.org/publication/global-street-design-guide/design-controls/design-vehicle-control-vehicle/).
   - Turning speed 15 km/h or less (USDM) or 10 km/h or less (GSDG).
   - Kerb return type per quadrant: fillet, 3-centred or chamfer, as Civil 3D offers [[40]](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-775B4273-813C-4804-9F02-C32AF216D971.htm).
6. **Crossing rules.**
   - Unbroken crossing length 13 m or less, otherwise a refuge [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf).
   - Width at least the larger of 3 m and the footway width; spacing 80 to 100 m, never over 200 m [[27]](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-crossings/).
   - Placed beyond kerb-radius tangent points; refuge nose 1.5 m set back [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c).
   - At roundabouts: uncontrolled within 20 m of give way; signals at 20 m or beyond 60 m [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338).
   - Raised crossings on one-lane roundabouts and yield slip lanes [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf).
7. **Network rules.**
   - USDM Table 5.7 junction spacing. City: Boulevard 400 to 750 m, Avenue 200 to 375 m, Street 100 to 175 m. Town: 600 to 1,000 m, 300 to 500 m, 140 to 250 m. Commercial and Residential: 1,000 to 1,500 m, 400 to 750 m, 125 to 375 m. Industrial: 800 to 1,500 m, 400 to 750 m, up to 300 m [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf).
   - Junction angles 75° to 90°, offsets at most 15° (USDM Table 5.6) [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf).
   - Driveways at least 30 m from major junctions and 15 m from other junctions and crossings [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf).
   - DMRB staggers of at least 40 to 60 m [[10]](https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c).
   - Sight triangle of 25 m at 2.4 m set-back for unsignalised junctions [[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf), or SSD by design speed [[9]](https://www.milton-keynes.gov.uk/sites/default/files/2022-04/CD13j%20Highway%20link%20design.PDF)[[15]](https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-11-sight-distance.html).
8. **Roundabout rules (CD 116 profile, with USDM advisories)** [[11]](https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338)[[1]](https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf):
   - ICD at least 28 m, at most 36 m compact or 100 m normal.
   - ICD at least the Table 3.8 value for the island size.
   - Circulatory width 1.0 to 1.2 times entry width, at most 6 m compact or 15 m normal.
   - Entry lanes 3.0 to 4.5 m.
   - Entry kerb radius 10 to 100 m (at least 20 m with regular HGVs).
   - Entry angle 20° to 60°.
   - Fastest-path entry radius at most 70 m or 100 m, computed, not drawn.
   - USDM limits as advisory: entry speed, diameter, raised crossings, splitter refuge at least 3.0 m.

YAML excerpt:

```yaml
  - id: corner.effective_radius_vs_vehicle
    check: "effective inner radius (lane offsets included) >= design vehicle min inside radius"
    severity: error
    src: [USDM-5, TXDOT]
  - id: rbt.circulatory_width
    check: "1.0 * max_entry_width <= circulatory width (excl. overrun) <= 1.2 * max_entry_width; compact <= 6; normal <= 15"
    severity: error
    src: [CD116]           # 3.6, 3.6.5, 3.6.7
```

A C# version of the corner rule. I compiled and ran it with .NET 8 on Linux. Its bisection form printed Re = 8.22 m for R = 5 m, the same as Python:

```csharp
// Effective inner turning radius at a 90-degree corner (right turn, right-hand traffic).
// a = approach lane-edge offset from kerb, b = receiving lane-edge offset, R = kerb return radius.
static double EffectiveRadius(double R, double a, double b) => R + a + b + Math.Sqrt(2 * a * b);

static bool FitsDesignVehicle(double R, double a, double b, double rInside, double rOutside,
                              double receivingLaneWidth)
    => EffectiveRadius(R, a, b) >= rInside && (rOutside - rInside) <= receivingLaneWidth;
```

## Risks and open questions

- **Dubai RTA Geometric Design Manual (2017 edition referenced) is binding but not publicly downloadable** [[6]](https://dlp.dubai.gov.ae/Legislation%20Reference/2025/Administrative%20Resolution%20No.%20%28273%29%20of%202025%20Regulating%20Works%20in%20the%20Right%20of%20Way.pdf). Every Dubai lane, kerb radius, roundabout, crossing and sight-distance value is "not found". The median classes come from unverified search text [[8]](https://pdfcoffee.com/1rta-geometric-design-manual-for-dubai-roads-2017pdf-pdf-free.html). Studio needs a licensed copy before shipping a Dubai profile.
- **Abu Dhabi TR-514 (road geometric design) was unreachable** [[4]](https://jawdah.qcc.abudhabi.ae/en/Registration/QCCServices/Services/STD/ISGL/ISGL-LIST/TR-514.pdf). The USDM values come from a v1 chapter 5 copy (2018 upload) and the 2020 DMT reproduction of Table 5.2. The 2020 table mentions the Utility Corridors Design Manual (UCDM) and an "Emirati Neighbourhood" context, so it is newer than v1. Where they differ (kerb lane 3.5 m fixed against 3.3 to 3.5 m), the current edition is unknown. Search results mention a QCC "ADG 23 ... First Edition 2017" version of the USDM, which I did not open.
- **USDM design speed by street family, crossing width, entry width and entry radius: not found.** USDM section 5.3 (typical sections) was not in the excerpt, so the "typical" (as opposed to minimum and maximum) widths are unknown.
- **USDM one-lane roundabout size:** the table says 20 m maximum diameter, Figure 5.33 implies 25 to 40 m. The worked example shows a 20 m ICD gives little deflection and fails DMRB. This needs clarifying with DMT before encoding a hard rule.
- **US values are secondary:**
  - The AASHTO Green Book was not opened. TxDOT and WSDOT may differ from it.
  - FHWA's 2000 roundabout guide is old and superseded by NCHRP Report 672, which I could not read [[21]](https://www.nationalacademies.org/read/22914/chapter/7).
  - AASHTO lane-width tables, design-speed tables and the FHWA Median U-Turn exhibit: not found.
- **NACTO Urban Street Design Guide pages returned 403.** I used the GSDG instead. NACTO US values (feet) were not verified.
- **DMRB footway, cycle-track and refuge values sit in CD 143 and CD 195, which I did not read.** CD 109 came from a council-hosted Revision 1 copy and may be superseded on standardsforhighways.co.uk.
- **Worked-example limits:**
  - The swept-path check uses the steady-state annulus from AASHTO minimum radii. It overstates the width of a real 90° turn and ignores vehicle body dimensions, which were not sourced.
  - The fastest path is a bending-energy optimum, not a designer's drawn line. CD 116 itself calls the construction judgement.
  - Entry-path radius varied 60 to 66 m by estimator.
- **Search budget:** the shared web-search budget ran out mid-task. InfraWorks, 12d and Forma details are "not verified", and I did not search for more Dubai or USDM mirrors.

## Sources

1. Abu Dhabi Urban Street Design Manual, Chapter 5 "Street Design Elements" (pages 24 to 48). Abu Dhabi Urban Planning Council. https://dragonfly-antelope-g8zd.squarespace.com/s/AbuDhabi-USDM-v1-excerpts-compressed2.pdf. Read 2026-10-30. Third-party host of the official document; old (v1, manual adopted 2010; file created 2018).
2. Abu Dhabi Outdoor Seating Areas Manual, Version 2.0 (reproduces USDM Table 5.2 on printed page 15). Department of Municipalities and Transport, 2020. https://www.dmt.gov.ae/-/media/Project/DMT/DMT/E-Library/0001-Manuals/ADODSM/EN/Abu-Dhabi-Outdoor-Seating-Areas-Manual-Version-20.pdf. Read 2026-10-30. Secondary: reproduces the USDM table.
3. Lessons on street design from Abu Dhabi. Robert Steuteville, Congress for the New Urbanism, 2010. https://www.cnu.org/node/1825. Read 2026-10-30. Third party; old (2010).
4. Road Geometric Design Manual TR-514. Abu Dhabi Quality and Conformity Council. https://jawdah.qcc.abudhabi.ae/en/Registration/QCCServices/Services/STD/ISGL/ISGL-LIST/TR-514.pdf. Read 2026-10-30. Not verified: connection reset and HTTP 503.
5. Abu Dhabi Street Design Manual (full PDF). bicycleinfrastructuremanuals.com. https://bicycleinfrastructuremanuals.com/manuals4/Abu-Dhabi-StreetDesignManual.pdf. Read 2026-10-30. Not verified: HTTP 403.
6. Administrative Resolution No. (273) of 2025, Implementing Bylaw on Works in the Right of Way, Article 15. Roads and Transport Authority, Dubai. https://dlp.dubai.gov.ae/Legislation%20Reference/2025/Administrative%20Resolution%20No.%20%28273%29%20of%202025%20Regulating%20Works%20in%20the%20Right%20of%20Way.pdf. Read 2026-10-30.
7. Dubai Transit Oriented Development Manual. Dubai Municipality, 2025. https://dmpmedia.dm.gov.ae/uploads/2025/11/Dubai-Transit-Oriented-Development-Manual.pdf. Read 2026-10-30.
8. RTA Geometric Design Manual for Dubai Roads 2017 (document-sharing copy). pdfcoffee.com. https://pdfcoffee.com/1rta-geometric-design-manual-for-dubai-roads-2017pdf-pdf-free.html. Read 2026-10-30. Not verified: page blocked (HTTP 403); values from search-result text only; third party.
9. DMRB CD 109 Highway link design, Revision 1. Highways England, 2020 (copy hosted by Milton Keynes Council). https://www.milton-keynes.gov.uk/sites/default/files/2022-04/CD13j%20Highway%20link%20design.PDF. Read 2026-10-30. Third-party host; may be superseded.
10. DMRB CD 123 Geometric design of at-grade priority and signal-controlled junctions, Version 2.1.0. National Highways, 29 November 2021. https://www.standardsforhighways.co.uk/tses/attachments/962a81c1-abda-4424-96c9-fe4c2287308c. Read 2026-10-30.
11. DMRB CD 116 Geometric design of roundabouts, Version 2.1.0. National Highways, 31 May 2023. https://www.standardsforhighways.co.uk/tses/attachments/7b5ea157-9b3e-4774-9781-7d1656e83338. Read 2026-10-30.
12. DMRB CD 127 Cross-sections and headrooms, Version 1.0.1. National Highways, 29 July 2021. https://www.standardsforhighways.co.uk/tses/attachments/10442706-b592-42c8-85f8-2a0c779a8e37. Read 2026-10-30.
13. 13. Lane Widths (Context Sensitive Solutions and Design). FHWA, updated 2017. https://www.fhwa.dot.gov/planning/css/design/tactics/chap13.cfm. Read 2026-10-30. Secondary for AASHTO.
14. Roadway Design Manual 4.3 Traffic Characteristics (Table 4-1). Texas DOT. https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-3-traffic-characteristics.html. Read 2026-10-30. Secondary: summarises the AASHTO Green Book.
15. Roadway Design Manual 4.11 Sight Distance. Texas DOT. https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-11-sight-distance.html. Read 2026-10-30. Secondary: summarises AASHTO.
16. Roadway Design Manual 4.10.15 Medians. Texas DOT. https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-10-cross-sectional-elements/4-10-15-medians.html. Read 2026-10-30. Secondary: summarises AASHTO.
17. Roadway Design Manual 4.10 Cross-Sectional Elements. Texas DOT. https://www.txdot.gov/manuals/des/rdw/chapter-4--basic-design-criteria/4-10-cross-sectional-elements.html. Read 2026-10-30. Secondary: summarises AASHTO.
18. Roadway Design Manual 13.10.1 Minimum Turning Radii (Table 13-7). Texas DOT. https://www.txdot.gov/manuals/des/rdw/chapter-13--intersections/13-10-additional-intersection-design-consideration/13-10-1-minimum-turning-radii.html. Read 2026-10-30. Secondary: summarises AASHTO.
19. Roundabouts: An Informational Guide, Chapter 6 Geometric Design (FHWA-RD-00-067). FHWA, 2000. https://www.fhwa.dot.gov/publications/research/safety/00067/000676.pdf. Read 2026-10-30. Old (2000), superseded by NCHRP 672.
20. WSDOT Design Manual M 22-01.23, Chapter 1320 Roundabouts. Washington State DOT, September 2024. https://wsdot.wa.gov/publications/manuals/fulltext/M22-01/1320.pdf. Read 2026-10-30. State DOT practice.
21. Roundabouts: An Informational Guide, Second Edition (NCHRP Report 672), Chapter 6. National Academies, 2010. https://www.nationalacademies.org/read/22914/chapter/7. Read 2026-10-30. Not verified: page shows images only.
22. Urban Street Design Guide: Lane Width. NACTO. https://nacto.org/publication/urban-street-design-guide/street-design-elements/lane-width/. Read 2026-10-30. Not verified: HTTP 403.
23. Global Street Design Guide: Travel Lanes, Geometry. GDCI/NACTO. https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/travel-lanes/geometry/. Read 2026-10-30.
24. Global Street Design Guide: Corner Radii. GDCI/NACTO. https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/corner-radii/. Read 2026-10-30.
25. Global Street Design Guide: Pedestrian Refuges. GDCI/NACTO. https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-refuges/. Read 2026-10-30.
26. Global Street Design Guide: Sidewalks, Geometry. GDCI/NACTO. https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/sidewalks/geometry/. Read 2026-10-30.
27. Global Street Design Guide: Pedestrian Crossings. GDCI/NACTO. https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-crossings/. Read 2026-10-30.
28. Global Street Design Guide: Crossing Types. GDCI/NACTO. https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-pedestrians/pedestrian-crossings/crossing-types/. Read 2026-10-30.
29. Global Street Design Guide: Cycle Facilities, Geometry. GDCI/NACTO. https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-cyclists/cycle-facilities/geometry/. Read 2026-10-30.
30. Global Street Design Guide: Transit Facilities, Geometry. GDCI/NACTO. https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-transit-riders/transit-facilities/geometry/. Read 2026-10-30.
31. Global Street Design Guide: Design Speed. GDCI/NACTO. https://globaldesigningcities.org/publication/global-street-design-guide/design-controls/design-speed/. Read 2026-10-30.
32. Global Street Design Guide: Visibility and Sight Distance. GDCI/NACTO. https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/visibility-sight-distance/. Read 2026-10-30.
33. Global Street Design Guide: Design Vehicle and Control Vehicle. GDCI/NACTO. https://globaldesigningcities.org/publication/global-street-design-guide/design-controls/design-vehicle-control-vehicle/. Read 2026-10-30.
34. Global Street Design Guide: Mini Roundabout. GDCI/NACTO. https://globaldesigningcities.org/publication/global-street-design-guide/intersections-4/mini-roundabout/. Read 2026-10-30.
35. Civil 3D 2025 Help: About Assemblies. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-B01563A3-A7FB-441D-987A-2A2801EEC321.htm. Read 2026-10-30.
36. Civil 3D 2025 Help: About Subassemblies. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-E9277B4B-CC74-4FD7-ABAD-B1F8B369F5A3.htm. Read 2026-10-30.
37. Civil 3D 2025 Help: About Corridor Modeling. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-F2246A0B-809E-4801-97A5-EFACFA05EE46.htm. Read 2026-10-30.
38. Civil 3D 2025 Help: About Intersections. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-0757C2A9-B439-43D3-9EB0-BFB50F237E6A.htm. Read 2026-10-30.
39. Civil 3D 2025 Help: Geometry Details Page (Create Intersection Wizard). Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-DFA739A3-12B1-4F7A-B431-B81C49DE4A8B.htm. Read 2026-10-30.
40. Civil 3D 2025 Help: Intersection Curb Return Parameters Dialog Box. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-775B4273-813C-4804-9F02-C32AF216D971.htm. Read 2026-10-30.
41. Civil 3D 2025 Help: About Assembly Sets. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-8B25124A-8354-4229-AAB8-5ADFE16E38C7.htm. Read 2026-10-30.
42. Civil 3D 2025 Help: About Roundabouts. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-AA9A4F3D-CEF3-4F6D-8813-E9F47501286A.htm. Read 2026-10-30.
43. Civil 3D 2025 Help: About Autodesk Civil 3D Enhancements for Roundabouts. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-092F412E-5926-4258-B05E-618B6E2E9789.htm. Read 2026-10-30.
44. Civil 3D 2025 Help: About Creating Roundabouts. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-C13E11FD-8720-4897-BFAC-E97ADF8D4A76.htm. Read 2026-10-30.
45. Civil 3D 2025 Help: Roundabout Standard Editor, Fastest Path Calculation. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-D4C47FB1-CD7B-4665-B5E0-84870064D449.htm. Read 2026-10-30.
46. Civil 3D 2025 Help: Roundabout Standard Editor, Swept Path Analysis: Design Vehicle. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-E5C35EED-3DA5-4C23-AD69-D88717BD21D4.htm. Read 2026-10-30.
47. Civil 3D 2025 Help: Roundabout Standard Editor, Arm Geometry: Entry. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-DFAB5C9F-8FF4-437C-A9D3-5A3FFCE3E521.htm. Read 2026-10-30.
48. Civil 3D 2025 Help: About the ARCADY-Autodesk Vehicle Tracking Link. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-B0E67422-BB0D-4B3E-9B25-7C300465CC2E.htm. Read 2026-10-30.
49. Civil 3D 2025 Subassembly Reference: LaneOutsideSuper. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-Subassembly-Ref/files/GUID-C08C2692-1562-4061-A9AD-47AA6DD74152.htm. Read 2026-10-30.
50. Civil 3D 2025 Subassembly Reference: UrbanSidewalk. Autodesk. https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-Subassembly-Ref/files/GUID-61C1448A-7B0A-43D9-B732-AC2BAEE1D3F4.htm. Read 2026-10-30.
51. OpenRoads Designer Help v20: Civil Cell Overview. Bentley Systems. https://docs.bentley.com/LiveContent/web/OpenRoads%20Designer%20Help-v20/en/GUID-D27470C6-8D0D-1701-A14A-B6D288F71E8F.html. Read 2026-10-30.
52. OpenRoads Designer Help v20: Create Corridor. Bentley Systems. https://docs.bentley.com/LiveContent/web/OpenRoads%20Designer%20Help-v20/en/newcorridor.html. Read 2026-10-30.
53. ArcGIS CityEngine 2026.0 Help: Segments. Esri. https://doc.arcgis.com/en/cityengine/2026.0/help/help-layers-street-parameters.htm. Read 2026-10-30.
54. ArcGIS CityEngine 2026.0 Help: Nodes. Esri. https://doc.arcgis.com/en/cityengine/2026.0/help/help-intersection-parameters.htm. Read 2026-10-30.
55. ArcGIS CityEngine 2026.0 Help: Lanes. Esri. https://doc.arcgis.com/en/cityengine/2026.0/help/street-lane-parameters.htm. Read 2026-10-30.
56. Streetmix segment-lookup.yaml (commit 7215e1b, 2026-10-23). Streetmix contributors. https://github.com/streetmix/streetmix/blob/7215e1b7b57637a6bc9a28e648b91bbe1033df72/packages/parts/data/segment-lookup.yaml. Read 2026-10-30.
57. Streetmix client/src/streets/warnings.ts (commit 7215e1b). Streetmix contributors. https://github.com/streetmix/streetmix/blob/7215e1b7b57637a6bc9a28e648b91bbe1033df72/client/src/streets/warnings.ts. Read 2026-10-30.
58. Streetmix LICENSE (commit 7215e1b). Streetmix contributors. https://github.com/streetmix/streetmix/blob/7215e1b7b57637a6bc9a28e648b91bbe1033df72/LICENSE. Read 2026-10-30.
59. TestFit Site Solver. TestFit. https://www.testfit.io/product/site-solver. Read 2026-10-30. Vendor marketing page.
60. Giraffe home page and knowledge base. Giraffe. https://www.giraffe.build/ and https://intercom.help/giraffe-knowledgebase-v6/en/. Read 2026-10-30. Vendor pages.
61. 12d home page. 12d Solutions. https://www.12d.com/. Read 2026-10-30. 12d wiki not verified (HTTP 403).
62. Autodesk InfraWorks overview. Autodesk. https://www.autodesk.com/products/infraworks/overview. Read 2026-10-30. Not verified: HTTP 403.
63. Autodesk Forma help centre. Autodesk. https://help.autodeskforma.com/hc/en-us. Read 2026-10-30. Not verified: no readable content.

## Choices made

- **Inferences about Studio (from the shared brief):** a Windows C# (.NET) urban-design and masterplanning application, GCC market (UAE first), with 3D massing (C2). The task line implies Studio draws street networks and sections, so "COMPLETES" items assume an existing road or street drawing tool. I have not seen Studio's code and do not describe it.
- **Right-hand traffic is the default.** DMRB geometry, written for left-hand traffic, is computed in its own frame and mirrored. Radii are unchanged by mirroring.
- **USDM values** come from a v1 chapter 5 copy and from Table 5.2 as reproduced by DMT in 2020. Where the two differ, both are shown and the newer table is used in the rule file.
- **Column filling:** the "AASHTO" column is filled from FHWA, TxDOT and WSDOT and labelled secondary. The NACTO column uses the GSDG because nacto.org returned 403. DMRB lane widths come from CD 127, which the task did not name, because CD 109 defers lane widths to it.
- **Dubai:** I did not use document-sharing copies of the RTA GDM. The one value taken from search-result text is flagged "not verified". I did not try to bypass the 403 on the USDM host. A retry with a browser user agent was refused by the permission system, and I dropped it.
- **Corner example:** USDM City-context minimum widths, a 2.2 m kerb extension (USDM: 0.5 m narrower than parking), and a desire line at the centre of a 2.4 m through zone. AASHTO vehicle radii come from TxDOT. "Effective turning radius" is defined as the inner-edge circle tangent to the lane edges, and the swept path is checked with the steady-state annulus.
- **Roundabout example:** four arms at 90°, 3 m splitters over 20 m, 3.65 m approach half width, one kerb radius for entry and exit, start 1 m from the centre line, and bending-energy minimisation as "smoothest path". Entry radius is reported with three estimators. The USDM comparison case uses a 20 m ICD, 10 m island and 4.5 m entries; USDM gives no entry width.
- **Rule data:** the rule file is YAML with pseudo-code checks, not an executable DSL, to keep it readable. Profiles are kept separate rather than merged into a "strictest of all" set, because the standards conflict (for example corner radius).
- **Not searched further:** after the shared web-search budget ran out, I used only direct fetches of known documentation URLs.

## What Studio should do

1. **[M] [COMPLETES]** Replace single lane widths with a street-type catalogue keyed by profile and context (USDM Table 5.2 first). Give every section element min, max, recommended and absolute-minimum widths with a source, and validate live in the properties panel. Supported by "Lane widths" and the rule set.
2. **[M] [COMPLETES]** Give every junction corner Civil 3D-style kerb-return parameters: fillet, 3-centred or chamfer, per quadrant, with copy-to-all. Show three computed values beside the radius: effective turning radius (R + a + b + √(2ab) at 90°), in-line crossing length and footway area lost. Warn against USDM's 5 m cap and 13 m crossing limit. Supported by "Worked example A" and "How Autodesk Civil 3D draws".
3. **[S] [COMPLETES]** Add crossing objects tied to corners and medians. Auto-propose a refuge when an unbroken crossing exceeds 13 m. Check width (at least 3 m and at least the footway), spacing (80 to 100 m) and placement beyond kerb-radius tangent points. Supported by "Crossings".
4. **[M] [COMPLETES]** Model medians as composites: refuge 2 or 3 m, plus a 3 m turn pocket, plus a U-turn gap. Add a U-turn feasibility check against the design vehicle, offering a loon or wider median when it fails. Supported by "Medians and U-turns" (Part C).
5. **[S] [COMPLETES]** Store design vehicle and control vehicle per street family (USDM Table 5.9), with AASHTO turning radii. Report encroachment as "design vehicle: error, control vehicle: allowed". Supported by "Kerb radii and corner geometry".
6. **[S] [COMPLETES]** Add network checks on the existing road graph: USDM junction spacing by context (Table 5.7), junction angle 75° to 90°, driveway distance from junctions. Supported by "The rule set".
7. **[L] [NEW]** Add a roundabout object with CD 116 checks (ICD, Table 3.8, circulatory to entry ratio, entry kerb radius, entry angle) and a computed fastest-path entry radius, porting the Python method to C# with a geometry library. Show USDM Table 5.10 values as advisories until DMT confirms the one-lane size. Supported by "Worked example B".
8. **[M] [NEW]** Treat swept paths as advisory in Studio: the steady-state annulus now, and an export to Civil 3D / Vehicle Tracking for real swept paths. Never label a junction "compliant", only "passes Studio checks". Supported by "Worked example A" and "Risks".
9. **[S] [NEW]** Ship the rule set as versioned data files with their own tests (each source key resolves; each default lies within its own min and max; Streetmix's 2.0 m parking default below its 2.1 m minimum shows why). Supported by "How others do it".
10. **[S] [NEW]** Before shipping a Dubai profile, get licensed copies of the RTA Geometric Design Manual for Dubai Roads, Abu Dhabi TR-514 and the current USDM edition (QCC ADG 23), and fill the "not found" cells. Supported by "Risks and open questions".
