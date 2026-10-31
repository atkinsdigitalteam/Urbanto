# C9: Pedestrian simulation options

Researched 2026-10-30. Brief file briefs/C3 unavailable; scope taken from the task line. Compute costs measured on a synthetic 100,000-plot network in this machine (Linux VM, not Windows).

## Answer

Studio should compute pedestrian accessibility itself, in C#, in-process, and call an external engine only for microscopic crowd simulation. The analyses that matter at masterplan stage are all bounded shortest-path searches on the street graph. They include distance to the nearest amenity and 15-minute coverage, isochrones, plots or floor area reachable within 400 or 800 m, gravity accessibility, local closeness and betweenness as space-syntax-style layers, a Frank- or IPEN-style walkability index, and a macroscopic flow estimate turned into a footway comfort grade. We measured these on a 4-core, 15 GB VM with a synthetic 110 km² network and 100,000 plots (111,025 graph nodes). A plain 149-line C# implementation gave the same medians as scipy. It took 0.04 to 0.14 s for nearest amenity across all plots, and 2.5 to 6.3 s (4 threads) or 9.8 to 10.0 s (1 thread) for the 800 m reach of every plot. A 2,400 m gravity score took 0.35 to 1.3 s and local betweenness at 800 m from every node took 3.9 to 16 s. Peak memory stayed under 120 MB. Python/scipy needed about 100 s for the same reach metric, and networkx would need about 24 hours for exact betweenness. Microscopic engines are a different cost class. JuPedSim (LGPL-3.0-or-later) took 55 to 60 µs per agent-step on a 1 km² street grid, so 10,000 agents need about 55 s of compute per simulated second. Use it out-of-process, or export to MassMotion or LEGION (commercial), only for stations, plazas and event egress. Do not embed cityseer, pandana or sDNA+ (all AGPL-3.0) or depthmapX (GPL-3.0); use them only as validation references. Forma, CityEngine and TestFit document no walkability analysis, and Giraffe offers only a walk-shed isochrone, so this is open ground for Studio. Main caveat: the network is synthetic and other jobs shared the VM (load average 2 to 10). Treat timings as roughly ±2x, and re-measure on real GCC networks on Windows.

## Options table: approaches and engines

Cost key: **M** = measured here (method in Detail), **Q** = quoted by the vendor, **n/m** = not measured. "Own C#" means code Studio would write; the benchmark version is in [assets/C9/WalkBench/Program.cs](assets/C9/WalkBench/Program.cs).

| Approach / engine | What it computes | Licence (checked) | Language; integration from C# | Input needed | Compute cost at 100,000 plots | Suitability for early-stage masterplanning |
|---|---|---|---|---|---|---|
| Network accessibility, own C# | Nearest amenity per category, isochrones, 15-minute coverage | Studio's own code | C#, in-process (`PriorityQueue`, no dependencies) | Street centrelines, plot access points, amenity points | **M** 0.04 to 0.14 s for all plots to nearest of 1,000 amenities; 0.015 to 0.13 s for one origin to the whole network | High: near-instant, easy to explain |
| Reach and gravity, own C# | Plots or floor area within 400/800 m; Σ W·exp(−β·d) | Studio's own code | C#, in-process, `Parallel.For` | As above plus weights (GFA, population) | **M** reach 800 m, all plots: 2.5 to 6.3 s (4 threads), 9.8 to 10.0 s (1 thread). Gravity 2,400 m: 0.35 to 1.3 s | High |
| pandana (UDST) | Radius aggregations, nearest POIs (contraction hierarchies) [[12]](https://udst.github.io/pandana/) | AGPL-3.0-or-later [[13]](https://raw.githubusercontent.com/UDST/pandana/dev/LICENSE.txt)[[14]](https://pypi.org/pypi/pandana/json) | C++ core, Python API [[12]](https://udst.github.io/pandana/); out-of-process only | Node and edge tables, POIs | **M** build 2.7 to 19 s, precompute 3.5 s (800 m) or 27 s (1,600 m), then reach 0.26 to 0.85 s; 1.7 to 4.8 GB RAM | Medium: fast queries, but AGPL and memory |
| cityseer | Localised closeness and betweenness (metric or angular), land-use accessibility, mixed uses, demand-weighted betweenness [[7]](https://github.com/benchmark-urbanism/cityseer-api)[[11]](https://cityseer.benchmarkurbanism.com/metrics/networks) | AGPL-3.0 [[8]](https://raw.githubusercontent.com/benchmark-urbanism/cityseer-api/master/LICENSE.txt) | Python with Rust core [[7]](https://github.com/benchmark-urbanism/cityseer-api); out-of-process | networkx graph, GeoDataFrames | **M** (41,716-node network): centrality 800 m 14.4 s, accessibility 58 s, demand betweenness 1,600 m 35 s; 743 MB | High as a validation oracle; AGPL blocks embedding |
| UNA toolbox (MIT City Form Lab) | Reach, Gravity, Straightness, Betweenness, Patronage [[15]](https://cityform.mit.edu/projects/una-rhino-toolbox) | CC BY-ND 4.0; free for non-profit and for-profit use; source availability not stated [[15]](https://cityform.mit.edu/projects/una-rhino-toolbox) | Rhino plugin; no C# API found | Rhino network and buildings | n/m (needs Rhino) | Medium: designer-friendly but tied to Rhino |
| Space syntax: depthmapX | Spatial network and visibility-graph analysis [[5]](https://github.com/SpaceGroupUCL/depthmapX) (integration, choice [[17]](https://en.wikipedia.org/wiki/Space_syntax)) | GPL-3.0 [[5]](https://github.com/SpaceGroupUCL/depthmapX) | C++/Qt desktop; separate process only | Axial or segment map, or plan | n/m | Medium: recognised method; GPL; manual map preparation |
| sDNA+ (Cardiff University) | Spatial design network analysis, including hybrid metrics [[16]](https://raw.githubusercontent.com/fiftysevendegreesofrad/sdna_plus/main/README.md) | AGPL-3.0 [[16]](https://raw.githubusercontent.com/fiftysevendegreesofrad/sdna_plus/main/README.md) | QGIS, ArcGIS and Grasshopper front ends [[16]](https://raw.githubusercontent.com/fiftysevendegreesofrad/sdna_plus/main/README.md); separate process | Network polylines | n/m | Medium |
| Space-syntax-style centrality, own C# | Local closeness and betweenness at a radius; sampled global betweenness | Studio's own code | C#, in-process | Street graph | **M** local betweenness 800 m from all 111,025 nodes: 3.9 to 8.6 s (4 threads), 14 to 16 s (1 thread). Global, 100 sampled sources: 0.5 to 2.0 s. Exact global: about 30 to 38 min on 1 thread (extrapolated) | High for local; global only sampled |
| Walk Score methodology | 0–100 score from distance to amenities with decay: full points within a 5-minute walk (0.25 miles, about 400 m), none after 30 minutes; plus population density, block length and intersection density [[18]](https://www.walkscore.com/methodology.shtml) | Proprietary, "patented system" [[18]](https://www.walkscore.com/methodology.shtml) | Web API (terms not checked) | Address; vendor POI data | Equivalent own computation = rows 1 and 2 (**M**) | Low as a dependency (IP, data coverage); the concept is useful |
| Frank et al. walkability index | 2·z(intersection density) + z(net residential density) + z(retail FAR) + z(land-use mix entropy) [[19]](https://atl.sites.olt.ubc.ca/files/2011/06/developing-a-walkability-index.pdf) | Published method (2009/2010) | Trivial in C# | Units, residential land, retail floor and land area, intersections, land uses | Areal units: milliseconds. Network buffers: same cost as reach (**M**) | High: Studio holds every input |
| IPEN walkability index | z-sum of residential density, land-use mix and intersection density in 1 km and 500 m network buffers [[21]](https://pubmed.ncbi.nlm.nih.gov/?term=International+variation+in+neighborhood+walkability+transit+and+recreation+environments+IPEN+adult+study) | Published method (2014) | C# | As above | As above (**M**) | High |
| 15-minute city coverage | Share of plots reaching each essential function within 15 minutes [[22]](https://www.mdpi.com/2624-6511/4/1/6/htm) | Concept paper (2021) | C# | Amenities by category, walking speed | **M** one multi-source search per category: 0.04 to 0.14 s, so 6 categories < 1 s | High |
| Macroscopic flow (demand-weighted betweenness, then TfL comfort level) | Link volumes from trip generation, gravity split and shortest paths; crowding = people per hour ÷ 60 ÷ clear width, B+ (9 to 11) recommended [[24]](https://content.tfl.gov.uk/pedestrian-comfort-guidance-technical-guide.pdf) | Method; cityseer implementation AGPL | Own C# (same algorithm class as local betweenness) | Trip rates by land use, footway widths | **M** cityseer: 35 s (41,716 nodes) or 9.5 s (11,025 nodes). Own C#: n/m | Medium-high: needs local trip rates |
| MATSim | Large-scale agent-based transport simulation; walk is one supported mode [[27]](https://www.matsim.org/) | GPL-2.0-or-later [[28]](https://raw.githubusercontent.com/matsim-org/matsim-libs/main/matsim/LICENSE) | Java; separate JVM process | Population plans, network | n/m | Low at early stage |
| SUMO pedestrians | Pedestrian models nonInteracting, striping (default) and a JuPedSim coupling; sidewalks, crossings, interaction with vehicles [[25]](https://sumo.dlr.de/docs/Simulation/Pedestrians.html) | EPL-2.0 [[26]](https://raw.githubusercontent.com/eclipse-sumo/sumo/main/README.md) | C++; separate process | SUMO network with sidewalks and crossings | n/m | Low to medium: junction-level checks |
| JuPedSim | Microscopic: Collision Free Speed and Generalized Centrifugal Force [[4]](https://www.jupedsim.org/stable/); 1.4.2 also ships social force, anticipation velocity and WarpDriver models (inspected in package) | LGPL-3.0-or-later [[2]](https://raw.githubusercontent.com/PedestrianDynamics/jupedsim/master/LICENSE)[[3]](https://pypi.org/pypi/jupedsim/json) | C++ core, Python API [[1]](https://github.com/PedestrianDynamics/jupedsim); out-of-process | Walkable-area polygon, exits, agents, journeys | **M** 55 to 60 µs per agent-step on a 1 km² grid with 100 blocks; 6 µs on a 0.1 km² grid with 9 blocks; single-threaded | Low at masterplan scale; good for plaza and station checks |
| Vadere | Microscopic: optimal steps, gradient navigation, social force models [[29]](https://github.com/pedestrian-dynamics-HM/vadere) | LGPL-3.0 [[30]](https://raw.githubusercontent.com/pedestrian-dynamics-HM/vadere/master/LICENSE) | Java 17; command line `vadere-console.jar` [[29]](https://github.com/pedestrian-dynamics-HM/vadere) | Scenario file | n/m | Low to medium |
| Menge | Modular crowd-simulation research framework [[31]](https://gamma.cs.unc.edu/Menge/) | Apache-2.0 [[32]](https://raw.githubusercontent.com/MengeCrowdSim/Menge/master/LICENSE.txt) | C++ | XML scenarios | n/m | Low: research framework; home page shows © 2013 |
| PEDSIM / libpedsim; pedsim_ros | Microscopic social force [[33]](https://raw.githubusercontent.com/chgloor/pedsim/master/README.md)[[35]](https://raw.githubusercontent.com/srl-freiburg/pedsim_ros/master/README.md) | libpedsim LGPL, application GPL [[33]](https://raw.githubusercontent.com/chgloor/pedsim/master/README.md); pedsim_ros BSD-2-Clause [[34]](https://raw.githubusercontent.com/srl-freiburg/pedsim_ros/master/LICENSE) | C++; pedsim_ros needs ROS | Scenario | n/m | Low: robotics-oriented |
| MassMotion (Oasys), commercial reference | Pedestrian simulation, flow analysis, evacuation; heatmaps, wait and trip times [[36]](https://www.oasys-software.com/products/massmotion/) | Commercial; prices by contact (read 2026-10-30) [[36]](https://www.oasys-software.com/products/massmotion/) | Windows 10 64-bit; SDK; imports FBX, IFC, DWG [[36]](https://www.oasys-software.com/products/massmotion/) | 3D geometry, demand | Not published | Detailed-design reference; export target |
| LEGION (Bentley), commercial reference | Crowd movement and evacuation; counts, flows, densities, journey times, levels of service [[37]](https://www.bentley.com/software/legion/) | From USD 16,330 for a 12-month Virtuoso subscription (read 2026-10-30) [[37]](https://www.bentley.com/software/legion/) | CAD and IFC import; 64 GB RAM required [[37]](https://www.bentley.com/software/legion/) | Venue geometry, demand | Not published | Detailed-design reference; export target |

### Measured cost at 100,000 plots, side by side

Network: 111,025 nodes and 120,091 street segments (one access node per plot). Ranges are repeated runs under different VM load. Full outputs are in [assets/C9/results/](assets/C9/results/).

| Metric | Python scipy (1 process) | Python networkx | C# 1 thread | C# 4 threads (JIT / Native AOT) | cityseer 5.8 (Rust, 4 cores) | pandana 0.8 (C++) |
|---|---|---|---|---|---|---|
| (a1) one origin to whole network | 0.015 s | 0.35 s | 0.015 to 0.13 s (higher figure includes JIT warm-up) | 0.07 to 0.12 / 0.016 to 0.017 s | n/a | n/a |
| (a2) all plots to nearest of 1,000 amenities | 0.031 s | 0.51 s | 0.038 to 0.099 s | 0.10 to 0.14 / 0.04 s | n/a | 0.86 to 1.78 s (`nearest_pois`) |
| (b) reach: plots within 800 m, every plot | 99.7 s (88.9 s with 4 processes) | n/m | 9.8 to 10.0 s | 3.4 to 6.3 / 2.5 to 3.2 s | 58 s on 41,716 nodes; 14.1 s on 11,025 nodes | 0.26 s after 2.7 s build and 3.5 s precompute |
| (c) global betweenness, 100 sampled sources | n/a | 77.3 s (0.77 s per source; exact would be about 23.9 h) | 1.6 to 2.0 s (exact about 30 to 38 min) | 0.75 to 1.37 / 0.54 to 0.58 s | n/a | n/a |
| (c′) local betweenness, 800 m, all nodes | n/m | n/m | 14.0 to 16.0 s | 3.9 to 8.6 / 3.9 to 4.2 s | 14.4 s on 41,716 nodes (closeness and betweenness) | n/a |
| (d) gravity, 2,400 m cut-off, 1,000 amenities | 4.36 s | n/m | 1.05 to 1.32 s | 0.46 to 0.85 / 0.35 to 0.41 s | n/a | 0.12 s at 800 m; 0.73 s at 1,600 m |
| Peak memory | 94 to 549 MB | 195 to 255 MB | 47 to 79 MB | 66 to 119 MB | 743 MB | 1.7 GB (800 m), 4.8 GB (1,600 m) |

## Detail

### Pedestrian flow and walkability approaches

Five families of method answer different questions. They also differ in cost by orders of magnitude.

**Network accessibility (isochrones, reach, gravity indices).** These measure how much a plot can reach on foot along the street network. An isochrone is the set of street points within a walking time of an origin. Reach counts destinations, or sums their weights, within a network radius. A gravity index sums destination weights discounted by distance, A_i = Σ_j W_j·f(d_ij). The UNA toolbox from the MIT City Form Lab ships "Reach, Gravity and Straightness" metrics, plus a "Betweenness metric, which can be used for modeling pedestrian flows" [[15]](https://cityform.mit.edu/projects/una-rhino-toolbox). cityseer computes "street-network centrality, land-use accessibility and mixed uses" "at intervals along streetfronts" [[10]](https://cityseer.benchmarkurbanism.com/). pandana uses contraction hierarchies to "calculate super-fast travel accessibility metrics and shortest paths" [[12]](https://udst.github.io/pandana/). Computationally, all of these are Dijkstra searches: one from each origin, cut off at the radius, or one multi-source search from all destinations of a type.

**Space syntax (integration, choice/betweenness).** Space syntax ranks streets by their configuration. Integration "measures the amount of street-to-street transitions needed from a street segment" to reach all others. Choice is "a 'water-flow' in the street network", in effect betweenness. Its values are exponentially distributed, so a base-2 logarithm is recommended [[17]](https://en.wikipedia.org/wiki/Space_syntax) (secondary source). The same source says integration is often argued to predict pedestrian use: "there is some evidence of this being true", but the method is biased toward long, straight streets [[17]](https://en.wikipedia.org/wiki/Space_syntax). The reference tool is depthmapX, "a multi-platform Spatial Network Analysis Software" under GPLv3 [[5]](https://github.com/SpaceGroupUCL/depthmapX). Its latest release is v0.9.1, dated 9 August with no year shown. The release before, v0.8.0, is from November 2020 [[6]](https://github.com/SpaceGroupUCL/depthmapX/releases). The UNA toolkit and cityseer compute the same family of network centralities. cityseer offers both shortest-path (metric) and simplest-path (angular) variants on primal or dual graphs [[7]](https://github.com/benchmark-urbanism/cityseer-api). sDNA+ is the Cardiff University equivalent, now open source under AGPL-3 [[16]](https://raw.githubusercontent.com/fiftysevendegreesofrad/sdna_plus/main/README.md). Classic space syntax uses topological or angular distance. Our C# benchmark uses metric distance. An angular version needs a dual graph (street segments as nodes, turn angles as weights) but belongs to the same cost class.

**Walkability indices.** Three are widely cited, and they measure different things:

- *Walk Score* awards points "based on the distance to amenities in each category". "Amenities within a 5 minute walk (.25 miles) are given maximum points", with "no points given after a 30 minute walk". It also uses "population density and road metrics such as block length and intersection density" [[18]](https://www.walkscore.com/methodology.shtml). The page calls it "a patented system" and does not publish weights or category lists [[18]](https://www.walkscore.com/methodology.shtml).
- *Frank et al.* built the index from parcel data for the Neighborhood Quality of Life Study. It is "Walkability = [(2 x z-intersection density) + (z-net residential density) + (z-retail floor area ratio) + (z-land use mix)]". Land-use mix is an entropy score across five uses (residential, retail, entertainment, office, institutional), normalised 0 to 1. Intersections count "3 or more legs", and the unit was the census block group [[19]](https://atl.sites.olt.ubc.ca/files/2011/06/developing-a-walkability-index.pdf) (author manuscript, published online 2009; old). The journal page was blocked [[20]](https://bjsm.bmj.com/content/44/13/924).
- *IPEN* (International Physical activity and Environment Network) applied a common protocol in 12 countries. It used "1-km and 500-m street network buffers" around each home. "Walkability z-score equaled the sum of z-scores for residential density, land use mix, and intersection density" [[21]](https://pubmed.ncbi.nlm.nih.gov/?term=International+variation+in+neighborhood+walkability+transit+and+recreation+environments+IPEN+adult+study). That is three components, and no retail FAR, unlike Frank.
- Local variants exist. Peel Region (Ontario) uses equal-weighted indicators at 400, 800 and 1,600 m network distances, and dropped intersection density during PCA screening [[23]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6638586/). There is no single "walkability index" that Studio should treat as the standard.
- *15-minute city.* Moreno et al. (Smart Cities, 2021) frame the city around essential functions within a 15-minute walk or bike ride. Secondary summaries list living, work, commerce, health, education and entertainment. The MDPI page was blocked, so this wording comes from search-result summaries, not the paper [[22]](https://www.mdpi.com/2624-6511/4/1/6/htm). In computing terms, the 15-minute test is one multi-source nearest-amenity search per function, then a threshold.

**Macroscopic flow.** Macroscopic methods estimate pedestrian volumes on links, not individual paths. The masterplan-scale version has three steps. First, generate trips per plot from land use. Then split them across destinations with a gravity model. Finally, route them on shortest paths and add the result per link. cityseer calls this `betweenness_demand`, a "demand-weighted (flow) betweenness from a spatial interaction model" with a "singly (origin-)constrained" split [[11]](https://cityseer.benchmarkurbanism.com/metrics/networks). The flow then becomes a comfort grade. Transport for London's Pedestrian Comfort Level (PCL) uses crowding = "people per hour ÷ 60 ÷ clear footway width in m" (people per metre per minute, ppmm). Grades run from A+ (< 3 ppmm) to E (> 35 ppmm), and "PCL B+ is the recommended level of comfort for all area types" (9 to 11 ppmm) [[24]](https://content.tfl.gov.uk/pedestrian-comfort-guidance-technical-guide.pdf) (First Edition 2010; old). The chain is cheap and fits an early-stage tool: flows come from the plan's land uses, and widths come from Studio's street sections.

**Microscopic agent-based engines.** These move individual agents with collision avoidance in 2D geometry. JuPedSim's documentation names the Collision Free Speed Model and the Generalized Centrifugal Force Model [[4]](https://www.jupedsim.org/stable/). The installed 1.4.2 package also exposes social force, anticipation velocity and WarpDriver models (read from `jupedsim/simulation.py`). Vadere ships the optimal steps, gradient navigation and social force models [[29]](https://github.com/pedestrian-dynamics-HM/vadere). SUMO has three pedestrian models: nonInteracting ("No interaction between pedestrians and vehicles or other pedestrians"), striping (the default, with 0.65 m stripes on sidewalks and crossings), and a JuPedSim coupling that is "a work in progress" [[25]](https://sumo.dlr.de/docs/Simulation/Pedestrians.html). MATSim is a framework for "large-scale agent-based transport simulation" that lists walk among its modes [[27]](https://www.matsim.org/). It models whole days of travel, not footway crowding. Menge [[31]](https://gamma.cs.unc.edu/Menge/) and PEDSIM [[33]](https://raw.githubusercontent.com/chgloor/pedsim/master/README.md) are research and robotics frameworks. pedsim_ros targets "robot navigation experiments with crowded scenes" [[35]](https://raw.githubusercontent.com/srl-freiburg/pedsim_ros/master/README.md). The commercial references are MassMotion from Oasys [[36]](https://www.oasys-software.com/products/massmotion/) and LEGION from Bentley [[37]](https://www.bentley.com/software/legion/). Both target stations, stadia and venues.

### Open-source engines: licence and integration from C#

We read each licence from the project's own LICENSE file or README, fetched from raw.githubusercontent.com, or from PyPI metadata. The GitHub API was blocked in this session.

| Engine | Licence as found | Where read | What it means for a closed-source C# desktop app |
|---|---|---|---|
| depthmapX | "licensed under the GPLv3 licence" | README [[5]](https://github.com/SpaceGroupUCL/depthmapX) | Run only as a separate program the user installs. Do not link or ship it inside Studio. |
| cityseer | GNU Affero GPL v3 | LICENSE.txt [[8]](https://raw.githubusercontent.com/benchmark-urbanism/cityseer-api/master/LICENSE.txt); PyPI "AGPL-3.0", v5.8.0, 2026-07-31 [[9]](https://pypi.org/pypi/cityseer/json) | Same as depthmapX, and AGPL also covers network use. Use for validation only. |
| pandana | GNU Affero GPL v3, © UrbanSim Inc. | LICENSE.txt [[13]](https://raw.githubusercontent.com/UDST/pandana/dev/LICENSE.txt); PyPI "AGPL-3.0-or-later", v0.8, 2026-08-24 [[14]](https://pypi.org/pypi/pandana/json) | As cityseer |
| sDNA+ | "released under GPL Affero version 3" | README [[16]](https://raw.githubusercontent.com/fiftysevendegreesofrad/sdna_plus/main/README.md) | As cityseer |
| UNA Rhino toolbox | CC BY-NoDerivatives 4.0; "free for both non-profit and for-profit work" | Project page [[15]](https://cityform.mit.edu/projects/una-rhino-toolbox) | Free to use in Rhino. No code to embed. Methods are published, so Studio can implement equivalent metrics itself. |
| JuPedSim | LGPL v3 "or any later version" | LICENSE [[2]](https://raw.githubusercontent.com/PedestrianDynamics/jupedsim/master/LICENSE); PyPI LGPLv3+, v1.4.2, 2026-05-21 [[3]](https://pypi.org/pypi/jupedsim/json) | Can be called as a separate process or library under LGPL conditions (relinking, notices). Get legal review before bundling. |
| Vadere | LGPL v3 | LICENSE [[30]](https://raw.githubusercontent.com/pedestrian-dynamics-HM/vadere/master/LICENSE); README [[29]](https://github.com/pedestrian-dynamics-HM/vadere) | Java; separate process |
| MATSim | GPL v2 "or (at your option) any later version" | matsim/LICENSE [[28]](https://raw.githubusercontent.com/matsim-org/matsim-libs/main/matsim/LICENSE) | Java; separate process only |
| SUMO | Eclipse Public License 2.0 | README and LICENSE [[26]](https://raw.githubusercontent.com/eclipse-sumo/sumo/main/README.md) | Separate process; EPL-2.0 is weak copyleft at file level |
| Menge | Apache License 2.0 | LICENSE.txt [[32]](https://raw.githubusercontent.com/MengeCrowdSim/Menge/master/LICENSE.txt) | Permissive, but the project looks dormant (© 2013 home page [[31]](https://gamma.cs.unc.edu/Menge/)) |
| PEDSIM | Application GPL; libpedsim LGPL, "allowing use in commercial and propietary projects" | README [[33]](https://raw.githubusercontent.com/chgloor/pedsim/master/README.md) | libpedsim usable under LGPL |
| pedsim_ros | BSD 2-clause, © 2014–2016 University of Freiburg | LICENSE [[34]](https://raw.githubusercontent.com/srl-freiburg/pedsim_ros/master/LICENSE) | Permissive, but needs ROS |

Python packaging cost is a practical point against out-of-process Python engines. Installing cityseer, jupedsim and pandana with their dependencies into a private folder took **2.1 GB** (measured with `du -sh`). Most of that is geopandas, pandas, shapely, osmnx and numpy. The C# benchmark has no dependencies, and its Native AOT binary was **2.6 MB** (2,590,792 bytes) on Linux x64.

### Measured compute cost at 100,000 plots

**Machine.** KVM virtual machine, Intel Xeon @ 2.10 GHz, 4 cores (1 thread per core), 15 GB RAM, Linux 6.18. Python 3.13.17 with scipy 1.18.1, numpy 2.5.3 and networkx 3.7. .NET SDK 8.0.427. Other research jobs shared the VM, so the 1-minute load average was 2.3 to 9.8 during runs. Each result line records it. On 4 cores, a load above 4 means contention, which is why we report ranges.

**Synthetic network.** [bench_walk.py](assets/C9/bench_walk.py) builds the test network:

- A perturbed street grid: 100 m spacing, ±15 m random jitter on intersections, 8 % of segments removed, and only the largest connected component kept.
- 100,000 plots dropped on random segments at random positions, each on a random side.
- 1 % of plots marked as amenities.

For 100,000 plots this gives a 105 × 105 grid over 110.2 km², about 900 plots per km². That is a GCC villa-suburb density in order of magnitude only; it is our assumption, not a sourced figure. We used two graph variants:

- **fine**: every plot gets its own access node spliced into its street segment, giving 111,025 nodes and 120,091 edges. Plot-to-plot distances are exact.
- **coarse**: each plot attaches to its nearest intersection (KD-tree) with a straight-line offset, as the task suggested, giving 11,025 nodes.

**Metrics.**

- (a1) Single-source Dijkstra over the whole network.
- (a2) All plots to the nearest amenity: one multi-source Dijkstra (`scipy.sparse.csgraph.dijkstra(..., min_only=True)`).
- (b) Reach: the number of plots within 800 m network distance, for every plot (bounded Dijkstra per plot).
- (c) Betweenness: networkx `betweenness_centrality(k=100, weight=...)`; the exact cost is extrapolated as per-source time × nodes.
- (d) Gravity: A_i = Σ_j exp(−β·d_ij) over amenities within 2,400 m, with β = ln 2 / 400 m. β and the cut-off are illustrative parameters, not sourced values. It runs one bounded search per amenity, not per plot, then accumulates.

Each metric ran in its own process so that peak RSS (`ru_maxrss`) is per metric.

```text
# commands (assets/C9/run_all.sh runs the whole series)
python3 bench_walk.py --plots 100000 --graph fine --metric b --workers 1
python3 bench_walk.py --plots 100000 --graph fine --metric c --k 100
# output (results/results_python.jsonl)
{"metric": "b", "graph": "fine", "plots": 100000, "nodes": 111025, "edges": 120091, "area_km2": 110.2,
 "median_plots_within_800m": 1156.0, "time_s": 99.747, "workers": 1, "peak_rss_mb": 549.0, "loadavg_1m": 3.29}
{"metric": "c", "graph": "fine", "plots": 100000, "nodes": 111025, "k": 100, "per_source_s": 0.7735,
 "time_s": 77.346, "exact_extrapolated_s": 85878.0, "workers": 1, "peak_rss_mb": 255.0, "loadavg_1m": 6.16}
```

**C# port.** [WalkBench/Program.cs](assets/C9/WalkBench/Program.cs) has 149 lines and no NuGet packages. It reads the same graph as CSR (compressed sparse row) binaries exported by `bench_walk.py --export`. It runs the same metrics with a bounded Dijkstra that resets only the nodes it touched. Without that, every source would pay an O(N) reset, and scipy's dense output rows have exactly that problem. The core:

```csharp
// Dijkstra from a set of sources, stopping at `limit`. Caller owns dist[] and the touched
// list, so a bounded search costs only what it reaches (no O(n) reset per source).
void Dijkstra(ReadOnlySpan<int> sources, double limit, double[] dist, List<int> touched,
              PriorityQueue<int, double> pq, Action<int, double>? visit = null)
{
    foreach (var s in sources) { dist[s] = 0; touched.Add(s); pq.Enqueue(s, 0); }
    while (pq.TryDequeue(out int u, out double du))
    {
        if (du > dist[u]) continue;            // stale entry
        visit?.Invoke(u, du);
        for (int e = indptr[u]; e < indptr[u + 1]; e++)
        {
            int v = indices[e]; double dv = du + w[e];
            if (dv <= limit && dv < dist[v])
            {
                if (double.IsPositiveInfinity(dist[v])) touched.Add(v);
                dist[v] = dv; pq.Enqueue(v, dv);
            }
        }
    }
}
```

Reach, gravity and betweenness each run this inside `Parallel.For` with thread-local arrays. Betweenness uses Brandes' accumulation over the settle order. We checked correctness two ways:

- The C# medians match the Python results exactly: nearest amenity 200 m, reach 1,156 plots, gravity 10.643.
- On a 1,000-plot graph, exact global betweenness from C# matched networkx to a maximum absolute difference of 0.0 ([validate_bc.py](assets/C9/validate_bc.py)).

```text
$ python3 bench_walk.py --export g100k --plots 100000
$ dotnet build WalkBench -c Release && dotnet WalkBench.dll g100k 4      # JIT, load average 5.1
a1 single-source, whole network            0.073 s  peakWS=42 MB max=10844 m
a2 all plots -> nearest amenity            0.101 s  peakWS=48 MB median=200 m
b  reach: plots within 800 m, all plots     3.417 s  peakWS=64 MB median=1156
d  gravity score, all plots                0.462 s  peakWS=71 MB median=10.643
c  betweenness global, k=100 sources       0.753 s  peakWS=84 MB per-source=0.0075 s
c' betweenness local r=800 m, all nodes     3.854 s  peakWS=84 MB
$ dotnet publish -r linux-x64 -p:PublishAot=true && ./WalkBench g100k 4  # Native AOT, load average 5.3
b  reach: plots within 800 m, all plots     2.459 s  peakWS=49 MB median=1156
c' betweenness local r=800 m, all nodes     4.195 s  peakWS=66 MB
```

**Scaling (fine graph).** The single-search metrics scale linearly. Python reach is super-linear: scipy writes a dense row of length N for every source, so total work grows as N². The C# bounded search stays linear because each plot's 800 m neighbourhood is the same size whatever the network size.

| Plots | Nodes | (a2) nearest amenity, scipy | (d) gravity, scipy | (c) networkx s per source | (b) reach, scipy | (b) reach, C# |
|---|---|---|---|---|---|---|
| 10,000 | 11,156 | 0.002 s | 0.19 s | 0.050 | 1.4 s (1 process) | 1.0 s (1 thread) |
| 25,000 | 27,808 | 0.006 s | 0.72 s | 0.152 | 6.2 s (4 processes) | n/m |
| 50,000 | 55,625 | 0.013 s | 1.77 s | 0.384 | 28.3 s (4 processes) | n/m |
| 100,000 | 111,025 | 0.031 s | 4.36 s | 0.774 | 99.7 s (1) / 88.9 s (4) | 9.8 to 10.0 s (1) / 2.5 to 6.3 s (4) |
| 200,000 | 221,902 | 0.056 s | 10.0 s | n/m | 255 s (4 processes) | 13.3 s (4 threads) |

Notes on the scaling table:

- Four processes barely helped scipy at 100,000 plots. Load was 7.7, and each worker still pays the dense-row cost.
- Peak RSS for the 4-process runs counts only the parent process.
- C# peak working set was 47 to 119 MB at 100,000 plots and 225 MB at 200,000 plots.

**Incremental updates.** The average 800 m search from one plot costs about 0.1 ms on one thread (9.8 s / 100,000 plots). When a user edits one plot, Studio only needs the plots within 800 m of it. For reach, that means updating the counts of plots within 800 m of the edit; for nearest-amenity, rerun one multi-source search. So a full recompute is a background job, and single edits can update interactively.

**Coarse versus fine graph.** Attaching plots to the nearest intersection made reach about 100 times cheaper in Python (0.91 s versus 99.7 s) but changed the answers:

| Result | Coarse (nearest intersection) | Fine (access nodes on segments) | Difference |
|---|---|---|---|
| Median reach | 1,215 plots | 1,156 plots | +5 % |
| Median nearest-amenity distance | 227 m | 200 m | +13 % |

At 100 m blocks the error is tolerable for a quick view. With GCC superblocks it would grow, because plots sit farther from intersections. Studio should build the fine graph; in C# it costs seconds, not minutes.

**External engines on the same network.** [bench_cityseer.py](assets/C9/bench_cityseer.py) and [bench_pandana.py](assets/C9/bench_pandana.py) ran them on the same synthetic network:

- **cityseer 5.8.0.** The network was decomposed into segments of at most 50 m, as cityseer recommends, giving 41,716 nodes, with the 100,000 plots as a data layer:
  - `centrality_shortest` at 800 m (closeness and betweenness, every node, no sampling): **14.4 s**.
  - `compute_accessibilities` for amenities and homes at 800 m: **58 s**.
  - `betweenness_demand` at 1,600 m: **35 s**.
  - Peak memory 743 MB.
  - Without decomposition (11,025 nodes): 1.1 s, 14.1 s and 9.5 s.
- **pandana 0.8**, on the fine graph (111,025 nodes):
  - At an 800 m precompute: contraction-hierarchy build 2.7 s, precompute 3.5 s, then the reach count in **0.26 s**, at a peak of **1.7 GB**.
  - At a 1,600 m precompute: build 19 s (during a load spike), precompute 27 s, peak **4.8 GB**.
  - We did not run 2,400 m at 100,000 plots: pandana stores node pairs within the precompute radius, and memory was already 4.8 GB at 1,600 m.

**Microscopic cost (JuPedSim 1.4.2).** [bench_jupedsim.py](assets/C9/bench_jupedsim.py) builds the walkable area as a street grid at 100 m pitch with 12 m wide streets, so the blocks are holes in the polygon. Agents start at random street points and walk to one of 9 exits. It uses the Collision Free Speed Model with dt = 0.01 s, the default.

| Geometry | Agents | µs per agent-step | Wall-clock s per simulated s |
|---|---|---|---|
| 3 × 3 blocks, 0.10 km² | 1,000 | 6.1 | 0.61 |
| 10 × 10 blocks, 1.02 km² | 1,000 | 59.1 | 5.9 |
| 10 × 10 blocks, 1.02 km² | 10,000 | 55.1 | 55.1 |

What the JuPedSim runs show:

- The cost per agent-step grew about 10 times with geometry complexity but not with agent count, so navigation over a complex polygon dominates.
- The run was single-threaded: `time` showed user 5.57 s against real 5.81 s.
- Extrapolating the measured rate, 10,000 agents for 10 simulated minutes would take about 9 hours of compute.
- Masterplan-scale microscopic simulation (110 km², 100,000 plots) is not an interactive option. The cost is acceptable for a station forecourt or a plaza.

### What Forma, CityEngine, Giraffe and TestFit offer

| Product | Walkability or pedestrian analysis found | Evidence (date) |
|---|---|---|
| Autodesk Forma Site Design | **None for walkability.** Listed analyses: sun hours, shadow, daylight potential, wind (comfort and direction), noise, views, solar energy potential, microclimate, total carbon. The only pedestrian mention is wind, to "ensure pedestrian comfort when planning new public spaces" [[38]](https://blogs.autodesk.com/forma/2026/08/20/what-is-forma-site-design/). A 2023 hackathon extension, "Pathmaker", aims "to predict pedestrian pathways based on residential locations and popular destinations" [[40]](https://aps.autodesk.com/blog/exploring-possibilities-forma-extensions-api). Its MIT-licensed code says users can activate it "in the Forma extensions menu" [[41]](https://raw.githubusercontent.com/spacemakerai/extendathon-pathmaker/main/README.md)[[42]](https://raw.githubusercontent.com/spacemakerai/extendathon-pathmaker/main/LICENSE). | Autodesk blog 2026-08-20; APS blog 2023-12-19. The Forma product-details page was blocked [[39]](https://www.autodesk.com/products/forma/product-details). |
| Esri ArcGIS CityEngine | **None.** Analysis tools are dashboards, measurement ("Measure Distance or Measure Area and Path"), visibility (viewshed, view dome) and scenarios. Nothing on network distance, accessibility or walkability [[43]](https://doc.arcgis.com/en/cityengine/latest/help/help-analysis-overview.htm). | CityEngine 2026.0 help, read 2026-10-30 |
| Giraffe | **Walk-shed isochrone only.** A "Walk-Shed Analysis" app under the Calculations menu, for Enterprise licences. The user picks walk, bike or car and a time in minutes, and the result is saved as a static GeoJSON layer [[44]](https://help.giraffe.build/en/articles/12217035-isochrones). No walkability score found. Pricing: Individual plans from USD 45 per month; Team USD 2,250 per user per year for firms of 5 staff or fewer; Enterprise by quote (read 2026-10-30) [[45]](https://www.giraffe.build/products/analytics). | Help article blocked (403); its text was seen in a search result. Pricing page read 2026-10-30. |
| TestFit | **None found.** The urban-planner page lists Site Solver, Parking Solver, Site Intelligence ("site, environmental and zoning data"), Pro Forma, an MCP connection, zoning, density and yield studies, and live 3D walkthroughs. It does not mention walkability, pedestrians, amenities or accessibility [[46]](https://www.testfit.io/roles/urban-planners). | Page shows "TestFit 5.26", read 2026-10-30 |

Of the four, only Giraffe computes a pedestrian network measure, and that is a single-origin isochrone. None publishes reach, gravity, centrality, a walkability index or pedestrian flow. Vendors may have undocumented or marketplace features; see Risks.

### What Studio should compute itself versus call

**Compute in C#, in-process:**

1. **Walk graph with plot access points.** Every metric depends on it. The fine graph gave nearest-amenity distances 13 % shorter than nearest-intersection snapping.
2. **Nearest amenity per category, isochrones and 15-minute coverage.** One multi-source search per category takes under 0.15 s at 100,000 plots. Isochrone polygons come from cutting edges at the threshold distance.
3. **Reach and gravity at 400, 800 and 1,600 m.** 2.5 to 10 s for every plot, plus about 0.1 ms per edited plot for incremental updates.
4. **Walkability indices.** Frank- and IPEN-style z-score composites are arithmetic over Studio's own data: units, land uses, floor areas and intersections. Studio's data is better than census inputs, because the plan itself is the data.
5. **Local centrality (space-syntax-style).** Local closeness and betweenness at a radius take 3.9 to 16 s for all nodes. Global betweenness should be sampled only: 100 sources take 0.5 to 2 s, while exact would take 30 to 38 minutes.
6. **Macroscopic flow and comfort grades.** Demand-weighted betweenness is the same algorithm with weights. Converting to ppmm and PCL grades needs only footway widths.

Reasons to keep this in-process:

- These are graph searches that cost seconds and under 120 MB.
- Results must update while the user edits.
- The algorithms are textbook. Our version is 149 lines, matched networkx exactly and Native-AOT-compiled to 2.6 MB without changes.
- The ready-made engines that do the same job are AGPL (cityseer, pandana, sDNA+) or GPL (depthmapX). They would also need a Python runtime of about 2 GB.

**Call out to an external engine:**

- **Microscopic crowd dynamics** for hotspots: transit stations, mosque forecourts at Friday prayer, stadium and mall egress, event plazas. Use JuPedSim (LGPL-3.0-or-later) through a separate Python process. Studio would export the walkable-area polygon, exits and agent demand, then read back trajectories or density maps. Alternatively, export IFC, DWG or FBX for MassMotion [[36]](https://www.oasys-software.com/products/massmotion/) or CAD/IFC for LEGION [[37]](https://www.bentley.com/software/legion/) when a client mandates them. These models need calibrated parameters and run for minutes to hours, so re-implementing them would add risk without adding value.
- **Vehicle–pedestrian interaction at junctions:** SUMO (EPL-2.0) as a separate process [[25]](https://sumo.dlr.de/docs/Simulation/Pedestrians.html).
- **City-wide multimodal demand:** MATSim (GPL), as a separate Java process, only if a project already has a MATSim model.
- **"Official" space syntax figures** (axial or angular integration, visibility graphs) when a reviewer asks for them: depthmapX (GPL-3.0) as a separate program the user installs. Studio's metric centrality is similar but not identical.

## Risks and open questions

- **Synthetic network.** Real GCC fabrics have superblocks, cul-de-sacs, gated compounds, highways and few crossings. Cost scales with the number of nodes reached inside the radius, so a dense historic core (for example Deira) costs more per search than our grid. Re-measure on real networks, for example an OSM extract of Dubai and Riyadh districts.
- **Noisy timings.** Other jobs shared the VM (load average 2.3 to 9.8). Runs of the same C# benchmark differed by up to 2.5 times; for example, 4-thread reach ranged from 2.5 to 6.3 s. We did not test on Windows, and AOT size is measured on Linux only.
- **Walking thresholds in GCC heat.** We found no source here for adjusted walking distances or speeds under heat or shade. The 400, 800 m and 15-minute thresholds come from temperate-climate literature [[18]](https://www.walkscore.com/methodology.shtml)[[21]](https://pubmed.ncbi.nlm.nih.gov/?term=International+variation+in+neighborhood+walkability+transit+and+recreation+environments+IPEN+adult+study). Not found; open question.
- **Trip rates for macroscopic flow.** We found no GCC pedestrian trip-generation rates; not found. The PCL scale is from London, 2010 [[24]](https://content.tfl.gov.uk/pedestrian-comfort-guidance-technical-guide.pdf).
- **Walk Score IP.** Walk Score describes its method as "patented" [[18]](https://www.walkscore.com/methodology.shtml). Studio should not call its score "Walk Score" or copy its method without legal review. Frank and IPEN are published methods.
- **Sources we could not open.** The Forma product page [[39]](https://www.autodesk.com/products/forma/product-details), the Giraffe help article [[44]](https://help.giraffe.build/en/articles/12217035-isochrones), the BJSM page [[20]](https://bjsm.bmj.com/content/44/13/924) and the MDPI 15-minute paper [[22]](https://www.mdpi.com/2624-6511/4/1/6/htm) all returned 403. We did not browse the Forma extensions marketplace or the TestFit help centre, so marketplace or undocumented features may exist. The shared web-search budget ran out mid-task, so MATSim's walk routing details (teleported versus network-routed walking) are not covered.
- **Licences.** LGPL (JuPedSim, Vadere, libpedsim) still carries conditions when distributed. AGPL and GPL engines must stay out of the shipped product. This report is not legal advice.
- **Space syntax equivalence.** We did not validate Studio-style metric centrality against depthmapX angular or segment integration. Values will differ.
- **JuPedSim cost.** We measured one configuration (Collision Free Speed Model, default settings). Other models, coarser time steps or simpler geometry will cost differently. We did not confirm a supported C API, so plan on the Python API.
- **pandana at 2,400 m** was not run at 100,000 plots, for memory reasons.

## Sources

1. JuPedSim, GitHub repository README. Forschungszentrum Jülich / PedestrianDynamics. https://github.com/PedestrianDynamics/jupedsim. Read 2026-10-30.
2. JuPedSim LICENSE file. https://raw.githubusercontent.com/PedestrianDynamics/jupedsim/master/LICENSE. Read 2026-10-30.
3. jupedsim package metadata (v1.4.2, uploaded 2026-05-21). PyPI. https://pypi.org/pypi/jupedsim/json. Read 2026-10-30.
4. JuPedSim documentation. https://www.jupedsim.org/stable/. Read 2026-10-30.
5. depthmapX README. SpaceGroupUCL. https://github.com/SpaceGroupUCL/depthmapX. Read 2026-10-30.
6. depthmapX releases. SpaceGroupUCL. https://github.com/SpaceGroupUCL/depthmapX/releases. Read 2026-10-30. (Year of latest release not shown.)
7. cityseer-api repository README. Benchmark Urbanism. https://github.com/benchmark-urbanism/cityseer-api. Read 2026-10-30.
8. cityseer LICENSE.txt. https://raw.githubusercontent.com/benchmark-urbanism/cityseer-api/master/LICENSE.txt. Read 2026-10-30.
9. cityseer package metadata (v5.8.0, 2026-07-31). PyPI. https://pypi.org/pypi/cityseer/json. Read 2026-10-30.
10. cityseer documentation home. Gareth Simons. https://cityseer.benchmarkurbanism.com/. Read 2026-10-30.
11. cityseer `metrics.networks` documentation. https://cityseer.benchmarkurbanism.com/metrics/networks. Read 2026-10-30.
12. Pandana documentation. UrbanSim / UDST. https://udst.github.io/pandana/. Read 2026-10-30.
13. Pandana LICENSE.txt. https://raw.githubusercontent.com/UDST/pandana/dev/LICENSE.txt. Read 2026-10-30.
14. pandana package metadata (v0.8, 2026-08-24). PyPI. https://pypi.org/pypi/pandana/json. Read 2026-10-30.
15. UNA Rhino Toolbox. MIT City Form Lab. https://cityform.mit.edu/projects/una-rhino-toolbox. Read 2026-10-30.
16. sDNA+ README. Cardiff University (Crispin Cooper). https://raw.githubusercontent.com/fiftysevendegreesofrad/sdna_plus/main/README.md. Read 2026-10-30.
17. Space syntax. Wikipedia. https://en.wikipedia.org/wiki/Space_syntax. Read 2026-10-30. Third party; secondary: summarises Hillier and others.
18. Walk Score Methodology. Walk Score. https://www.walkscore.com/methodology.shtml. Read 2026-10-30.
19. Frank L.D., Sallis J.F., Saelens B.E., Leary L., Cain K., Conway T.L., Hess P.M. The Development of a Walkability Index: Application to the Neighborhood Quality of Life Study. Br J Sports Med, published online 29 Apr 2009 (2010;44(13):924–33). Author copy hosted by UBC. https://atl.sites.olt.ubc.ca/files/2011/06/developing-a-walkability-index.pdf. Read 2026-10-30. Old (2009/2010); third-party host.
20. Same article, journal page. BMJ. https://bjsm.bmj.com/content/44/13/924. Not verified: page blocked (403).
21. Adams M.A. et al. International variation in neighborhood walkability, transit, and recreation environments using GIS: the IPEN adult study. Int J Health Geogr 2014;13:43 (PMID 25343966). PubMed record. https://pubmed.ncbi.nlm.nih.gov/?term=International+variation+in+neighborhood+walkability+transit+and+recreation+environments+IPEN+adult+study. Read 2026-10-30. Abstract and figure caption only; full text not read.
22. Moreno C., Allam Z., Chabaud D., Gall C., Pratlong F. Introducing the "15-Minute City". Smart Cities 2021;4(1):93–111. MDPI. https://www.mdpi.com/2624-6511/4/1/6/htm. Not verified: page blocked (403). Details from search-result summaries (secondary).
23. An Objective Walkability Index for Public Health and Planning in Peel Region, Ontario, Canada. PMC. https://pmc.ncbi.nlm.nih.gov/articles/PMC6638586/. Read 2026-10-30.
24. Pedestrian Comfort Guidance for London, Guidance Document, First Edition 2010. Transport for London. https://content.tfl.gov.uk/pedestrian-comfort-guidance-technical-guide.pdf. Read 2026-10-30. Old (2010).
25. SUMO documentation: Simulation/Pedestrians. Eclipse SUMO / DLR. https://sumo.dlr.de/docs/Simulation/Pedestrians.html. Read 2026-10-30.
26. SUMO README (licence section) and LICENSE. Eclipse SUMO. https://raw.githubusercontent.com/eclipse-sumo/sumo/main/README.md. Read 2026-10-30.
27. MATSim home page. MATSim community. https://www.matsim.org/. Read 2026-10-30.
28. MATSim licence file. https://raw.githubusercontent.com/matsim-org/matsim-libs/main/matsim/LICENSE. Read 2026-10-30.
29. Vadere repository README. Munich University of Applied Sciences. https://github.com/pedestrian-dynamics-HM/vadere. Read 2026-10-30.
30. Vadere LICENSE. https://raw.githubusercontent.com/pedestrian-dynamics-HM/vadere/master/LICENSE. Read 2026-10-30.
31. Menge home page. UNC Chapel Hill. https://gamma.cs.unc.edu/Menge/. Read 2026-10-30. Old (© 2013).
32. Menge LICENSE.txt. https://raw.githubusercontent.com/MengeCrowdSim/Menge/master/LICENSE.txt. Read 2026-10-30.
33. PEDSIM README. Christian Gloor. https://raw.githubusercontent.com/chgloor/pedsim/master/README.md. Read 2026-10-30.
34. pedsim_ros LICENSE. Social Robotics Lab, University of Freiburg. https://raw.githubusercontent.com/srl-freiburg/pedsim_ros/master/LICENSE. Read 2026-10-30. Old (2014–2016).
35. pedsim_ros README. https://raw.githubusercontent.com/srl-freiburg/pedsim_ros/master/README.md. Read 2026-10-30.
36. MassMotion product page. Oasys. https://www.oasys-software.com/products/massmotion/. Read 2026-10-30.
37. LEGION product page. Bentley Systems. https://www.bentley.com/software/legion/. Read 2026-10-30.
38. What Is Autodesk Forma Site Design? Uses and Project Types. Autodesk blog, 2026-08-20. https://blogs.autodesk.com/forma/2026/08/20/what-is-forma-site-design/. Read 2026-10-30.
39. Forma Features (product details). Autodesk. https://www.autodesk.com/products/forma/product-details. Not verified: page blocked (403).
40. Høiby H. Exploring possibilities with the Forma Extensions API. Autodesk Platform Services blog, 2023-12-19. https://aps.autodesk.com/blog/exploring-possibilities-forma-extensions-api. Read 2026-10-30.
41. extendathon-pathmaker README. Autodesk (spacemakerai). https://raw.githubusercontent.com/spacemakerai/extendathon-pathmaker/main/README.md. Read 2026-10-30.
42. extendathon-pathmaker LICENSE (MIT, © 2023 Autodesk Platform Services). https://raw.githubusercontent.com/spacemakerai/extendathon-pathmaker/main/LICENSE. Read 2026-10-30.
43. Analysis (overview), ArcGIS CityEngine Resources (2026.0). Esri. https://doc.arcgis.com/en/cityengine/latest/help/help-analysis-overview.htm. Read 2026-10-30.
44. Walk-Shed Analysis (isochrones). Giraffe Help Center. https://help.giraffe.build/en/articles/12217035-isochrones. Not verified: page blocked (403); text taken from a search result.
45. Giraffe Analytics product page (pricing). Giraffe. https://www.giraffe.build/products/analytics. Read 2026-10-30.
46. Site Planning Software for Urban Planners. TestFit. https://www.testfit.io/roles/urban-planners. Read 2026-10-30.

## Choices made

- briefs/C3 was not available. We worked from the task line and the shared batch brief, and used the heading "Pedestrian simulation options" as instructed.
- **Inferences from the shared brief:**
  - Studio is a Windows desktop urban-design app in C#/.NET, with Native AOT under consideration.
  - Its market is the GCC (UAE first).
  - It has 3D massing (from C2).
- **Inferences from the task line:**
  - The task line's "100,000 plots" suggests Studio holds plots and a street network at that scale. This is an inference; we know nothing of Studio's internals.
  - The task line does not say whether Studio's pedestrian side is a flow model or a walkability score. We covered both and treated "pedestrian simulation" as the full range from accessibility to agent-based.
- **Synthetic network parameters (our choice, not sourced):** 100 m grid, ±15 m jitter, 8 % of segments removed, 5 plots per segment on average, 20 m setback, 1 % amenities in one category. We used an 800 m reach radius, a 2,400 m gravity cut-off and β = ln 2 / 400 m. These test cost, not planning standards.
- **Graph variants:** we built a fine graph (an access node per plot) as the main case and a coarse nearest-intersection graph as the task suggested, and report both.
- **Sampling:** betweenness used k = 100 sampled sources; exact cost is extrapolated as per-source time × node count and labelled as such.
- **Measurements beyond the task:** we added a C# port (JIT and Native AOT), cityseer, pandana and JuPedSim, because the compute-versus-call decision rests on in-process C# cost and external engine cost. We added sDNA+ and pandana to the table although the task did not name them.
- **Licences:** read from LICENSE or README files on raw.githubusercontent.com and from PyPI metadata, because the GitHub API was blocked.
- **Blocked vendor pages:** where pages returned 403 we did not retry with altered request headers. We used search-result text and flagged it.
- **Engines not installed or measured:** depthmapX, sDNA+, UNA (needs Rhino), Vadere (Java), MATSim, SUMO, Menge and PEDSIM. Their costs are marked n/m.
- **Space syntax definitions:** we used a secondary source (Wikipedia) because the web-search budget ran out before we found a primary methodology page.
- **Report text:** the C# snippet is ours and illustrative. It is not Studio code.

## What Studio should do

1. **[M] [COMPLETES]** Build a pedestrian graph from Studio's street network (if it has one), splicing an access node per plot into its frontage segment and adding pedestrian-only links. Every metric depends on it, and nearest-intersection snapping overstated nearest-amenity distance by 13 % (Detail: coarse versus fine).
2. **[M] [COMPLETES]** Add in-process C# accessibility layers for the existing plots: nearest amenity per category, isochrones and 15-minute coverage. They run in under 0.15 s at 100,000 plots, so they can update live on edit (Detail: measured cost, metrics a1 and a2).
3. **[M] [COMPLETES]** Add reach and gravity scores at 400, 800 and 1,600 m for every plot, using a parallel bounded Dijkstra on a background thread. A full recompute takes 2.5 to 10 s, and each edited plot updates incrementally in about 0.1 ms (Detail: measured cost, metrics b and d).
4. **[S] [COMPLETES]** Compute Frank- and IPEN-style walkability indices from Studio's own plot data (units, land uses, floor areas, intersections). Show the formula and weights in the properties panel and flag them as not calibrated for the GCC (Detail: walkability indices).
5. **[M] [NEW]** Add local closeness and betweenness at a radius (metric first, angular later) as "network centrality" layers. Offer global betweenness only as a sampled estimate, because exact takes 30 to 38 minutes on one thread (Detail: measured cost, metrics c and c′).
6. **[M] [NEW]** Add a macroscopic pedestrian flow estimate. Generate trips from plot land uses, split them with a gravity model, route them on shortest paths, then convert to people per metre per minute with footway widths and grade against TfL PCL (B+ = 9 to 11 ppmm). Trip rates must be user inputs until GCC rates are sourced (Detail: macroscopic flow; Risks).
7. **[S] [NEW]** Keep AGPL and GPL engines (cityseer, pandana, sDNA+, depthmapX) out of the shipped product. Run cityseer or pandana in CI as reference oracles on test networks; our C# results matched scipy, networkx and pandana medians exactly (Detail: licences; C# port validation).
8. **[M] [NEW]** For hotspots only (stations, plazas, mosque forecourts, event egress), export a walkable-area polygon, exits and demand to JuPedSim, run out-of-process, and read back density maps. Offer IFC, DWG or FBX export for MassMotion or LEGION. Do not attempt masterplan-scale microscopic simulation: 10,000 agents cost about 55 s per simulated second (Detail: microscopic cost).
9. **[S] [NEW]** Position walkability as a differentiator. Forma, CityEngine and TestFit document no walkability analysis, and Giraffe has only a walk-shed isochrone. Re-check vendor marketplaces before claiming it publicly (Detail: what Forma, CityEngine, Giraffe and TestFit offer; Risks).
