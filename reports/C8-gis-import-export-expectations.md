# C8: GIS import and export expectations

Researched 2026-10-30. Brief file unavailable; scope taken from the task line. The shared web-search budget ran out part way through, so later sources were opened directly by URL; gaps are listed under Risks and open questions.

## Answer

Studio should make the coordinate reference system (CRS) an explicit, recorded property of every imported and exported layer, never a guess. Ship a short GCC list with these defaults: Dubai, WGS 84 / Dubai Local TM (DLTM, EPSG:3997). Abu Dhabi, WGS 84 / UTM 40N (EPSG:32640), which Abu Dhabi Municipality's published CAD submission spec requires. Saudi Arabia, KSA-GRF17 / UTM 36N to 40N (EPSG:9356 to 9360), which EPSG records as the unified national system from 2018. Qatar, QND95 / Qatar National Grid (EPSG:2932). I checked every code against the EPSG registry with pyproj 3.8 (EPSG v12.029) and the EPSG online API. The mistakes are large: reading DLTM coordinates as UTM 40N moves a Dubai site 168 km, and labelling Nahrwan 1967 UTM data as WGS 84 moves it 437 m. Two legacy datums, Trucial Coast 1948 and Qatar 1948, have no EPSG transformation at all. For those, PROJ silently applies a zero-shift "ballpark" operation, so Studio must refuse or warn. For exchange, prefer GeoPackage, which is UTF-8 and keeps long field names and the CRS. Shapefile is the defect magnet. In tests it truncated field names to 10 bytes and Arabic text to 254 bytes (138 characters of Arabic text). Arabic field names became unreadable, and a missing .cpg file turned Arabic into mojibake. For heights, the geoid sits about 34 m below the WGS 84 ellipsoid at Dubai and Abu Dhabi, so ellipsoidal and orthometric heights must never be mixed. The main caveat: Abu Dhabi Municipality is the only authority found with a public, detailed submission spec (DWG, AutoCAD 2012 or earlier, UTM 40N, metres, closed polylines, attribute blocks, no Z). For Dubai Municipality, MOMRAH (Saudi Ministry of Municipalities and Housing) and Qatar's Ministry of Municipality I found no public GIS submission standard, so confirm requirements per project.

## GCC coordinate reference systems and what authorities exchange

### Table 1. CRS for the UAE, Saudi Arabia and Qatar (checked against the EPSG registry)

"pyproj" means: `CRS.from_epsg()` in pyproj 3.8.0 / PROJ 9.8.1 / EPSG v12.029 (2025-10-02) printed the name, datum, area of use and `is_deprecated` ([script](assets/C8/crs_check.py), [output](assets/C8/outputs/crs_check.txt)). "API" means the EPSG online registry record at apps.epsg.org, fetched 2026-10-30 ([[1]](https://apps.epsg.org/api/v1/CoordRefSystem/3997/), [script](assets/C8/fetch_epsg_registry.sh), [output](assets/C8/outputs/epsg_api_summary.txt)). The status column gives the EPSG flag, then the real-world status with its source.

| Name | EPSG | Datum (ellipsoid) | Projection | Units | Who uses it | Status | Checked against registry |
|---|---|---|---|---|---|---|---|
| WGS 84 | 4326 | WGS 84 ensemble (WGS 84) | none; axis order latitude, longitude | degree | GeoJSON (RFC 7946) [[39]](https://datatracker.ietf.org/doc/html/rfc7946); KML (GDAL wrote and read it as 4326, measured); AD-SDI basemap service [[16]](https://arcgis.sdi.abudhabi.ae/agshost/rest/services/Hosted/BaseMapEng_LightGray_GCS/MapServer) | valid; current | yes: pyproj (area World, not deprecated) + API (rev. 2022-11-29) |
| WGS 84 / UTM 36N, 37N, 38N | 32636, 32637, 32638 | WGS 84 | TM, CM 33°, 39°, 45°E, k 0.9996, FE 500 000 | m | Saudi Arabia by longitude (the EPSG areas list Saudi Arabia); the KSA-GRF17 equivalents (9356 to 9358) are the national ones | valid; current | yes: pyproj + API (rev. 2022-12-12) |
| WGS 84 / UTM 39N | 32639 | WGS 84 | TM, CM 51°E, k 0.9996, FE 500 000 | m | Abu Dhabi west of 54°E (ADM spec lists the zone 39 central meridian) [[15]](https://www.dmt.gov.ae/adm/-/media/Project/DMT/ADM/E-Library/0001-Oct-2021-Doc/SDDPlanningDataSubmissionSpecifications_v1182.pdf); EPSG area includes Bahrain, Qatar, Saudi Arabia and the UAE | valid; current | yes: pyproj + API |
| WGS 84 / UTM 40N | 32640 | WGS 84 | TM, CM 57°E, k 0.9996, FE 500 000 | m | Abu Dhabi Municipality planning submissions ("Zone: 40 North", datum WGS_1984) [[15]](https://www.dmt.gov.ae/adm/-/media/Project/DMT/ADM/E-Library/0001-Oct-2021-Doc/SDDPlanningDataSubmissionSpecifications_v1182.pdf) | valid; current | yes: pyproj + API |
| WGS 84 / Dubai Local TM (DLTM) | 3997 | WGS 84 | TM, CM 55°20′E (55.333 333°), k 1.0, FE 500 000, FN 0 | m | Dubai Municipality since 1999 [[10]](https://fig.net/resources/proceedings/fig_proceedings/cairo/papers/ts_13/ts13_12_marzooqi_etal.pdf); DM control network [[9]](https://www.dm.gov.ae/survey-department/geodesy/); EPSG source is Dubai RTA (Roads and Transport Authority) | valid; current | yes: pyproj (area "UAE - Dubai municipality") + API (alias "WGS 84 / DLTM", rev. 2020-03-14) + epsg.io [[3]](https://epsg.io/3997) |
| Nahrwan 1967 | 4270 | Nahrwan 1967 (Clarke 1880 RGS) | none | degree | legacy UAE survey and oil-industry data | valid; legacy | yes: pyproj + API (source UK Military Survey) |
| Nahrwan 1967 / UTM 39N | 27039 | Nahrwan 1967 | TM, CM 51°E | m | legacy Abu Dhabi west of 54°E; Qatar offshore | valid; legacy | yes: pyproj + API |
| Nahrwan 1967 / UTM 40N | 27040 | Nahrwan 1967 | TM, CM 57°E | m | Dubai before 1999 ("Clark 1880 ... UTM Zone 40") [[10]](https://fig.net/resources/proceedings/fig_proceedings/cairo/papers/ts_13/ts13_12_marzooqi_etal.pdf); legacy Abu Dhabi Municipality GIS (EPSG transformations sourced from the "Abu Dhabi SDI reference guide") [[7]](https://epsg.io/7002) | valid; legacy | yes: pyproj + API. (27037 and 27038, the Iraq/Kuwait zones, are deprecated per the API.) |
| TC(1948) / UTM 39N, 40N | 30339, 30340 | Trucial Coast 1948 (Helmert 1906) | TM | m | oldest Abu Dhabi and Dubai onshore control | valid; legacy; **no EPSG transformation to WGS 84** (measured below) | yes: pyproj + API |
| Ras Ghumays height | 5843 | Ras Ghumays (vertical) | none | m | Abu Dhabi onshore heights (EPSG source: ADCO) | valid; no PROJ transformation except ballpark | yes: pyproj + API (rev. 2015-01-26) |
| Ain el Abd / UTM 36N to 40N | 20436 to 20440 | Ain el Abd 1970 (International 1924) | TM | m | legacy Saudi; "KOC UTM" in Kuwait | valid, but API remark "Replaced by MTRF-2000 / UTM zone nnN" | yes: pyproj + API |
| Ain el Abd / Aramco Lambert | 2318 | Ain el Abd 1970 | Lambert Conic Conformal 2SP: φ0 25.08951°, λ0 48°E, standard parallels 17° and 33° | m | Saudi Aramco "when area of interest crosses UTM zone boundary" (API remark) | valid; industry | yes: pyproj + API |
| MTRF-2000 / UTM 36N to 40N | 8836 to 8840 | MOMRA Terrestrial Reference Frame 2000 (GRS 1980) | TM | m | MOMRA (now MOMRAH) municipal survey frame | valid, but superseded: the API calls KSA-GRF17 the system "replacing ... MTRF-2000 ... from 2018" | yes: pyproj + API |
| KSA-GRF17 | 9333 | KSA-GRF17 (GRS 1980) | none | degree | national frame, General Authority for Survey and Geospatial Information (GASGI, now GEOSA) | valid; current | yes: pyproj + API (rev. 2021-09-08) + epsg.io [[6]](https://epsg.io/9333) |
| KSA-GRF17 / UTM 36N to 40N | 9356 to 9360 | KSA-GRF17 | TM, k 0.9996, FE 500 000 | m | GEOSA: "Unified national system ... from 2018" (API remark) | valid; current | yes: pyproj + API (rev. 2022-07-29) |
| KSA-VRF14 height; KSA-GRF17 + KSA-VRF14 | 9335; 9520 | KSA-VRF14 (vertical) | none | m | Saudi orthometric heights | valid; current; geoid grid not openly distributed (measured below) | yes: pyproj (both) + API (9335: "Orthometric heights") |
| QND95 / Qatar National Grid | 2932 | QND95 (International 1924) | TM, φ0 24°27′N, CM 51°13′E, k 0.99999, FE 200 000, FN 300 000 | m | Qatar Centre for GIS (EPSG source); "the official system adopted by the state" [[24]](https://www.gulf-times.com/story/418684/qatar-rail-committed-to-complying-with-qnd95) | valid; current | yes: pyproj + API (rev. 2002-06-28) + epsg.io [[4]](https://epsg.io/2932) |
| Qatar 1974 / Qatar National Grid | 28600 | Qatar 1974 (International 1924) | same parameters as 2932 | m | pre-QND95 Qatar data | valid; legacy | yes: pyproj + API + epsg.io [[5]](https://epsg.io/28600) |
| Qatar 1948 / Qatar Grid | 2099 | Qatar 1948 (Helmert 1906) | Cassini-Soldner | m | historical; API: "Replaced by Qatar National Grid (code 28600)" | valid; legacy; no EPSG transformation | yes: pyproj + API |

Not found: a separate EPSG grid for Sharjah, Ajman, Ras Al Khaimah, Fujairah or Umm Al Quwain. EPSG's Nahrwan 1967 / UTM 40N area covers all of them. I found no published statement of what each northern emirate uses today (see Risks).

### Table 2. What each authority hands over and expects back

| Authority | Hands over (data, format, CRS, channel) | Expects back (format, CRS, attributes, channel) | Public spec? |
|---|---|---|---|
| Dubai Municipality (DM) Survey Department / GIS Centre; Dubai Pulse open data | Control coordinates (horizontal and vertical), coordinate transformation and orthometric height conversion as e-services; 76-point first-order network in DLTM [[9]](https://www.dm.gov.ae/survey-department/geodesy/). Open data: Community, Sectors, Entrances, Parks coordinates, Makani [[11]](https://dm.gov.ae/open-data/). Dubai Pulse lists `dm_sectors` as KML sourced from an Esri SDE geodatabase [[12]](https://www.dubaipulse.gov.ae/data/dm-location/dm_sectors-open) | Not found publicly. Open-data terms: "The source of the data must be mentioned when used" [[11]](https://dm.gov.ae/open-data/) | Survey services yes; GIS/CAD submission spec **not found** |
| Dubai Development Authority (DDA) | Approved drawings viewable in Zoning eServices [[14]](https://dda.gov.ae/-/media/436DDFA50D8B4AC1A075607917327616.pdf) | A1 DWF sheets, monochrome, one sheet per file, discipline numbering (A-00-xxx); for third-party survey reports, "digital copy of AutoCAD and polyline diagram drawings" (Circular 400, 2021-09-29) [[14]](https://dda.gov.ae/-/media/436DDFA50D8B4AC1A075607917327616.pdf). CRS not stated | Drawing format yes; CRS/GIS **not found** |
| Abu Dhabi Department of Municipalities and Transport (DMT), Abu Dhabi City Municipality (ADM) Spatial Data Division | "Base Map data" and "planning data" (plots, roads, service corridors) to consultants assigned by government bodies. Application needs a letter of assignment, a site map and a commercial licence [[15]](https://www.dmt.gov.ae/adm/-/media/Project/DMT/ADM/E-Library/0001-Oct-2021-Doc/SDDPlanningDataSubmissionSpecifications_v1182.pdf) | DWG, AutoCAD 2012 or earlier; WGS 84 / UTM 40N in metres; three files (Plot, Roads, Services) plus optional Additional, named `<ProjectID>_<YYYYMMDD>_<AP/MP>_<Plot/Roads/Services/additional>_<ADM/DOT>.dwg`; closed LWPOLYLINE per layer; predefined attribute blocks (for example `PlotNumber`, `SectorNumber`, `UsageCategoryType`, `UsageType`, `SectorNameEnglish`, `SectorNameArabic`); no arcs, splines, hatches, xrefs, elevation or 3D. Automated quality check; non-compliant data "will be rejected" (v1.18.2, 2021-08-02) [[15]](https://www.dmt.gov.ae/adm/-/media/Project/DMT/ADM/E-Library/0001-Oct-2021-Doc/SDDPlanningDataSubmissionSpecifications_v1182.pdf) | **Yes** (68-page PDF) |
| Abu Dhabi Spatial Data Infrastructure (AD-SDI) and GeoPortal | Cached basemap in EPSG:4326, 256 px JPEG tiles, 14 levels from 1:5 000 000 to 1:1 000; no copyright or terms text on the service [[16]](https://arcgis.sdi.abudhabi.ae/agshost/rest/services/Hosted/BaseMapEng_LightGray_GCS/MapServer). Custom datasets through a data-request service hub [[17]](https://sdi.gov.abudhabi/sdi/index.html) | Not found. An AD-SDI "Spatial Reference System" data standard v1.0 (2010) exists but could not be opened [[19]](https://pdfcoffee.com/sdi-data-standard-spatial-reference-system-property-pdf-pdf-free.html) | Partly; not verified |
| Saudi MOMRAH / Balady | "Urban Maps": free Balady web viewer with roads, land use and building requirements; no download or export mentioned [[20]](https://momah.gov.sa/ar/e-services/alkhrayt-alhdryt). Its historic frame is MTRF-2000 ("MOMRA Terrestrial Reference Frame"), now replaced by KSA-GRF17 [[1]](https://apps.epsg.org/api/v1/CoordRefSystem/9358/) | Not found | **Not found** |
| GEOSA (formerly GASGI; EPSG still names it General Commission for Survey) | KSA-GRF17 through 209 KSA-CORS stations, with network RTK at 1 to 3 cm [[23]](https://fig.net/resources/proceedings/fig_proceedings/fig2023/ppt/ts04g/TS04G_al-qahtani_salawu_et_al_12208_ppt.pdf). "KSA Geospatial Standards Overview" (NGC-WP-01, undated) [[21]](https://geosa.gov.sa/en/products/Pages/KSAGeospatialStandards.aspx). National data policies on licensing, pricing and sharing (dated 2024-08-27), with licensing through the Digital Geospatial Services Portal [[22]](https://geosa.gov.sa/en/controlAndcompliance/Pages/Geospatial_Data_Policies.aspx) | Not a permit authority (inference); data-sharing rules are in the policies, whose text I could not see | Standards overview yes; content **not verified** |
| Qatar Ministry of Municipality / Centre for GIS (CGIS) | QND95 and QNG (EPSG source "Qatar Centre for Geographic Information") [[1]](https://apps.epsg.org/api/v1/CoordRefSystem/2932/). Qatar Area Referencing System (QARS) zone, street and building numbers [[26]](https://thepeninsulaqatar.com/article/23/11/2013/numbering-places). GISnet links government agencies [[25]](https://www.esri.com/news/arcnews/spring09articles/qatars-gis.html) | A 2014 ministry circular required consultancies to "comply with the QND95 system" in the Qatar Rail protection zone [[24]](https://www.gulf-times.com/story/418684/qatar-rail-committed-to-complying-with-qnd95). File formats not found | **Not found** |

## Detail

### 1. What each authority hands over and expects back

**Dubai.** The public Dubai Municipality material covers survey services, not data exchange formats. On request it supplies "Control Coordinates (Hz & V)", coordinate transformation and "orthometric height conversion". It also links a "Cm Geoid for Dubai Emirate" document [[9]](https://www.dm.gov.ae/survey-department/geodesy/). The open-data page lists Community, Entrances, Sectors, Parks coordinates and Makani open data. It requires that the source be credited, and the municipality accepts no liability for "data distortion" [[11]](https://dm.gov.ae/open-data/). Dubai Pulse returned HTTP 503 when opened. Its search-result text shows `dm_sectors-open` in KML format, sourced from an "ESRI SDE Geodatabase", created July 2019 [[12]](https://www.dubaipulse.gov.ae/data/dm-location/dm_sectors-open). The Dubai Land Department (DLD) areas lookup includes a `municipality_number` described as the community code [[13]](https://www.dubaipulse.gov.ae/data/dld-transactions/dld_lkp_areas-open). KML means WGS 84 longitude/latitude: GDAL wrote and read KML back as EPSG:4326 in my test (section 6). Expect to reproject Dubai Pulse data to DLTM before overlaying it on DM survey drawings. I found no public DM GIS or CAD submission standard for planning data.

**DDA.** Circular 400 (2021-09-29) is about drawing presentation. It requires DWF, A1, monochrome, one sheet per file, plus an AutoCAD file and a "polyline diagram" for third-party surveys [[14]](https://dda.gov.ae/-/media/436DDFA50D8B4AC1A075607917327616.pdf). It does not state a CRS. Since DDA zones are in Dubai, DLTM is the likely grid, but this is an inference, not a published rule.

**Abu Dhabi (ADM, under DMT).** The "Standards & Specifications for Planning Data Submission (Plot, Roads & Service Corridors)" v1.18.2 is the most complete public spec in the region [[15]](https://www.dmt.gov.ae/adm/-/media/Project/DMT/ADM/E-Library/0001-Oct-2021-Doc/SDDPlanningDataSubmissionSpecifications_v1182.pdf). Key rules, quoted or closely paraphrased:
- "AutoCAD DWG format not later than 2012 release". One drawing unit equals one metre. "Features created in arbitrary coordinate system shall not be accepted."
- Geometries "shall be topologically cleaned and shall not contain any undershoots, overshoots, zero length Polyline, overlapping objects, snapping errors, intersection errors, self intersection errors and duplicates". "Snapping must be made only on vertices".
- "Each closed Polyline object must be a single polygon". No donuts. Arcs, ellipses and splines must be converted to polylines.
- "The drawing objects must not have elevation or width"; no 3D objects; no hatch, xref, groups or proxy objects.
- Attribute blocks are predefined and must not be modified. Domain values are case sensitive.
- The title block must be in English. Sector, zone, road and bridge names have paired `...English` and `...Arabic` attributes.
- Before planning, consultants can collect "reference data directly from SDD" (base map and planning data). Queries go to a GIS service desk email.

**AD-SDI.** The public basemap service is EPSG:4326 cached tiles with no copyright text [[16]](https://arcgis.sdi.abudhabi.ae/agshost/rest/services/Hosted/BaseMapEng_LightGray_GCS/MapServer). The AD-SDI site offers "Explore Spatial Data" and a data-request route [[17]](https://sdi.gov.abudhabi/sdi/index.html). The UAE government portal lists AD-SDI and its sign-in map viewer, plus federal platforms (Union Atlas, 1Map, Bayanat) [[18]](https://u.ae/en/about-the-uae/digital-uae/data/geospatial-data-platforms). The 2010 AD-SDI SRS standard was blocked (HTTP 403). Search-result text says it covers both UTM 39N and 40N [[19]](https://pdfcoffee.com/sdi-data-standard-spatial-reference-system-property-pdf-pdf-free.html) (old; not verified).

**Saudi (MOMRAH, Balady, GEOSA).** Balady's Urban Maps is a free viewer. It shows roads, land use with "building requirements", and third-party points of interest. It lets users share queried results but offers no stated download [[20]](https://momah.gov.sa/ar/e-services/alkhrayt-alhdryt). GEOSA publishes a standards overview "to describe in general terms which international standards" matter [[21]](https://geosa.gov.sa/en/products/Pages/KSAGeospatialStandards.aspx). Its national data policies cover classification, sharing, licensing and pricing [[22]](https://geosa.gov.sa/en/controlAndcompliance/Pages/Geospatial_Data_Policies.aspx). I could not read either document's text. MOMRAH survey and CAD submission requirements were not found before the search budget ran out.

**Qatar.** QND95 is described as "the official system adopted by the state". The Ministry of Municipality (then MMUP) prepared a circular requiring consultancies working in the Qatar Rail protection zone to "comply with the QND95 system" [[24]](https://www.gulf-times.com/story/418684/qatar-rail-committed-to-complying-with-qnd95) (old, 2014). CGIS keeps national GIS standards so "the same GIS standards are used throughout the country". In 2009 "more than 40 government agencies" used GIS, and GISnet was described as "a high-speed network that allows the rapid transfer of data" [[25]](https://www.esri.com/news/arcnews/spring09articles/qatars-gis.html) (old, third party). File-format requirements for building permits were not found.

### 2. Coordinate reference systems and how the codes were checked

**Method.** For each code I ran pyproj and printed name, datum, ellipsoid, projection parameters, units, axis order, area of use and the deprecation flag. Then I fetched the same code from the EPSG online registry REST API (apps.epsg.org) and printed its information source, revision date, remarks and deprecations. The epsg.org HTML pages returned HTTP 403 to my fetch tool. So the API, plus the third-party mirror epsg.io for 3997, 2932, 28600 and 9333, stands in for "opening the code on epsg.org". The API and pyproj agree on every code: all are valid (not deprecated). The only deprecated codes found were the Iraq/Kuwait zones 27037 and 27038 (pyproj; 27038 also confirmed in the API).

```python
from pyproj import CRS
crs = CRS.from_epsg(3997)
print(crs.name, crs.datum.name, crs.area_of_use.name, crs.is_deprecated,
      {p.name: p.value for p in crs.coordinate_operation.params})
# WGS 84 / Dubai Local TM | World Geodetic System 1984 ensemble | UAE - Dubai municipality. | False
# {'Longitude of natural origin': 55.333333333, 'Scale factor at natural origin': 1.0, 'False easting': 500000.0, ...}
```

**UAE.**
- **Dubai.** Dubai Municipality "switched over to the Dubai Local Transverse Mercator Projection (DLTM) system on WGS84 datum" in 1999. It chose not to transform the old "Clark1880/UTM" coordinates, re-observing control by GPS instead [[10]](https://fig.net/resources/proceedings/fig_proceedings/cairo/papers/ts_13/ts13_12_marzooqi_etal.pdf) (old, 2005). DM's geodesy page still describes a "first order" network of 76 control points "using DLTM system", plus more than 18 000 control points [[9]](https://www.dm.gov.ae/survey-department/geodesy/). EPSG transformation 15953 (Nahrwan 1967 to WGS 84 (10), 5 m) carries the remark "Used by Dubai Municipality before 1994" [[2]](https://apps.epsg.org/api/v1/Transformation/15953/).
- **Abu Dhabi.** No Abu Dhabi-specific projected grid exists in EPSG. ADM's current submission spec defines its "coordinate system" as UTM on GCS_WGS_1984, "Zone: 40 North", and also lists the zone 39 central meridian [[15]](https://www.dmt.gov.ae/adm/-/media/Project/DMT/ADM/E-Library/0001-Oct-2021-Doc/SDDPlanningDataSubmissionSpecifications_v1182.pdf). Legacy data sits on Nahrwan 1967. EPSG holds three transformations whose source is the "Abu Dhabi SDI reference guide" (7002 Abu Dhabi island, 7003 west of 54°E, 7004 east of 54°E, each 1 m). 7002's scope is "Abu Dhabi Municipality GIS" [[7]](https://epsg.io/7002). EPSG also holds an oil-company (ADCO) transformation, 6999, at 0.15 m, "Derived in October 2013 at four control points of the ADCO CRF" [[8]](https://epsg.io/27040-6999).
- **Northern emirates.** No source found beyond the EPSG areas of use.

**Saudi Arabia.** Three generations coexist:
- Ain el Abd 1970 (International 1924). Its UTM CRSs are "Replaced by MTRF-2000".
- MTRF-2000, MOMRA's frame.
- KSA-GRF17, the "Unified national system replacing Ain el Abd / UTM ... and MTRF-2000 / UTM ... from 2018" [[1]](https://apps.epsg.org/api/v1/CoordRefSystem/9358/).

The EPSG transformation KSA-GRF17 to WGS 84 (1) is "Valid at 2017.00 and degrading by approximately 2.5cm per year" [[2]](https://apps.epsg.org/api/v1/Transformation/9383/). GEOSA's 2023 FIG (International Federation of Surveyors) presentation lists "Unify the Geodetic Reference Frames within the Kingdom" and "Transition from Static to Dynamic Reference Frame" as future plans [[23]](https://fig.net/resources/proceedings/fig_proceedings/fig2023/ppt/ts04g/TS04G_al-qahtani_salawu_et_al_12208_ppt.pdf). That suggests government networks are not yet on one frame. Aramco's Lambert grid (2318) avoids UTM zone splits for oil-field work. The zone follows from longitude: 36N west of 36°E, 37N from 36°E to 42°E, 38N from 42°E to 48°E, 39N from 48°E to 54°E, and 40N east of 54°E, per the EPSG areas pyproj printed. Riyadh (Kingdom Centre, 46.67°E) is in 38N.

**Qatar.** QND95 / QNG (2932) is current. EPSG's transformation remark says the 7-parameter transformation "defines QND95" and "May be approximated to 1m throughout Qatar by geocentric translation" [[2]](https://apps.epsg.org/api/v1/Transformation/1840/). Qatar 1974 / QNG (28600) uses identical projection parameters, so old and new files look alike. Qatar 1948 / Qatar Grid (2099) is Cassini-Soldner and was replaced by QNG.

### 3. Measured: four landmarks transformed with pyproj

Coordinates are Wikipedia infobox values [[31]](https://en.wikipedia.org/wiki/Burj_Khalifa)[[32]](https://en.wikipedia.org/wiki/Sheikh_Zayed_Grand_Mosque)[[33]](https://en.wikipedia.org/wiki/Kingdom_Centre)[[34]](https://en.wikipedia.org/wiki/Museum_of_Islamic_Art,_Doha). They are rounded to about 10 m, so they illustrate behaviour and are not survey control. Method: `Transformer.from_crs(4326, code, always_xy=True)`, then `get_last_used_operation()` to see which operation PROJ actually applied, with the network off ([script](assets/C8/transform_points.py), [output](assets/C8/outputs/transform_points.txt)). Every round trip back to WGS 84 closed within 1.3 mm.

| Landmark (lon, lat) | Target | Easting (m) | Northing (m) | Operation PROJ chose (EPSG code) | Stated accuracy |
|---|---|---|---|---|---|
| Burj Khalifa, Dubai (55.2742, 25.1972) | 3997 DLTM | 494 040.047 | 2 787 900.182 | conversion only (same datum) | exact |
| | 32640 UTM 40N | 326 112.131 | 2 787 898.865 | conversion only | exact |
| | 27040 Nahrwan / UTM 40N | 325 988.807 | 2 787 480.057 | Nahrwan 1967 to WGS 84 (10) (15953, "used by Dubai Municipality before 1994") | 5 m |
| | 30340 TC(1948) / UTM 40N | 326 110.429 | 2 787 928.843 | **ballpark** (no datum shift) | unknown |
| Sheikh Zayed Grand Mosque, Abu Dhabi (54.474, 24.412) | 32640 UTM 40N | 243 847.379 | 2 702 176.592 | conversion only | exact |
| | 27040 Nahrwan / UTM 40N | 243 725.319 | 2 701 758.876 | Nahrwan 1967 to WGS 84 (12) (6999, ADCO) | 0.15 m |
| | 30340 TC(1948) / UTM 40N | 243 844.870 | 2 702 205.661 | **ballpark** | unknown |
| Kingdom Centre, Riyadh (46.6744, 24.7113) | 32638 UTM 38N | 669 371.681 | 2 734 015.822 | conversion only | exact |
| | 9358 KSA-GRF17 / UTM 38N | 669 371.900 | 2 734 016.029 | KSA-GRF17 to WGS 84 (1) (9383) | 1 m |
| | 8838 MTRF-2000 / UTM 38N | 669 371.681 | 2 734 015.821 | MTRF-2000 to WGS 84 (1) (8822, null shift) | 1 m |
| | 20438 Ain el Abd / UTM 38N | 669 437.271 | 2 734 003.323 | Ain el Abd to WGS 84 (2) (1111, "Accuracy 10m in each axis") | 18 m |
| | 2318 Aramco Lambert | −132 781.050 | −40 888.609 | same (1111) | 18 m |
| Museum of Islamic Art, Doha (51.53926545, 25.2950187) | 2932 QND95 / QNG | 232 565.507 | 393 565.912 | QND95 to WGS 84 (1) (1840, defines QND95) | 0 (by definition) |
| | 28600 Qatar 1974 / QNG | 232 565.716 | 393 566.086 | Qatar 1974 to WGS 84 (3) (1563, Qatar Centre for GIS) | 1 m |
| | 2099 Qatar 1948 / Qatar Grid | 178 338.491 | 90 551.518 | **ballpark** | unknown |
| | 32639 UTM 39N | 554 286.975 | 2 797 724.559 | conversion only | exact |
| | 27039 Nahrwan / UTM 39N | 554 191.479 | 2 797 301.795 | 15937 (Abu Dhabi offshore); the point is outside its area | not valid here |

**Datum-shift accuracy notes (measured; [compare script](assets/C8/compare_transforms.py), [output](assets/C8/outputs/compare_transforms.txt), [list of all candidate operations](assets/C8/outputs/ops_detail.txt)).**
- **PROJ picks per point.** pyproj knows 13 Nahrwan 1967 to WGS 84 operations. `from_crs` reports "unavailable until proj_trans is called", because PROJ chooses by the point's area of use. At the Abu Dhabi mosque it chose ADCO's 6999. The AD-SDI operations agree with it within 0.06 m (7002) and 0.13 m (7004). 7003 (west of 54°E, so the wrong area) differs by 0.58 m, and Dubai's 15953 by 1.04 m. The coarsest candidate (1190, 35 m) lands 101 m away, and the ballpark 226 m away.
- **No published shift.** TC(1948) and Qatar 1948 have no EPSG transformation to WGS 84. PROJ returns a "Ballpark geographic offset" (zero shift), with no warning unless you inspect the operation.
- **Two Saudi paths.** For Ain el Abd to KSA-GRF17, the direct operation (9362, 2 m) and the route through WGS 84 (1111, 18 m) land **11.40 m apart** at Riyadh. A better grid-based operation, 9363 (`ARAMCO_AAA-KSAGRF_6.tac`), is listed but has no download URL in PROJ.
- **Small frame offsets.** MTRF-2000 to KSA-GRF17 shifts Riyadh by 0.57 m (0.414 m east, 0.388 m north). WGS 84 / UTM 38N and KSA-GRF17 / UTM 38N differ by 0.30 m. QND95 and Qatar 1974 QNG coordinates of the same point differ by 0.27 m, small enough for a mislabel to go unnoticed.

**Grid against ground scale (measured with `Proj.get_factors`, [script](assets/C8/defects_measure.py), [output](assets/C8/outputs/defects_measure.txt)).** Area error is k² − 1.

| Place, CRS | Point scale k | Distance error | Area error on a 10 000 m² plot |
|---|---|---|---|
| Burj Khalifa, DLTM | 1.0000004 | 0.4 mm/km | +0.01 m² |
| Burj Khalifa, UTM 40N | 0.9999734 | −26.6 mm/km | −0.53 m² |
| Abu Dhabi mosque, UTM 40N | 1.0004105 | +410.5 mm/km | +8.21 m² |
| Riyadh, KSA-GRF17 / UTM 38N | 0.9999543 | −45.7 mm/km | −0.91 m² |
| Riyadh, wrong zone (UTM 37N) | 1.0070794 | +7.08 m/km | +142.09 m² |
| Doha, QND95 / QNG | 1.0000030 | +3.0 mm/km | +0.06 m² |

DLTM's k = 1 on a central meridian through Dubai is why Dubai's grid distances are effectively ground distances. Abu Dhabi city sits 2.5° from the UTM 40N central meridian, so grid areas there are 0.08 % large.

### 4. Attribute conventions

**Plot and parcel numbering.**
- **Dubai.** Each community has "a unique three-digit number"; in community 376, "the area is located in Sector 3" [[28]](https://www.gulfnews.com/news/gulf/uae/traffic-transport/reading-dubai-s-road-signs-1.254255) (old, 2006, third party). DLD land numbers are numeric and vary by area. The municipality number is a pair (number plus sub-number). Makani is 10 digits [[29]](https://egsh.ae/insights/dubai-property-numbers-ejari-dewa-makani) (third party). Store these three as separate text fields.
- **Abu Dhabi.** ADM keys plots by `PlotNumber` plus `SectorNumber`, with zones and sectors carrying English and Arabic names [[15]](https://www.dmt.gov.ae/adm/-/media/Project/DMT/ADM/E-Library/0001-Oct-2021-Doc/SDDPlanningDataSubmissionSpecifications_v1182.pdf).
- **Saudi Arabia.** The Real Estate General Authority (REGA) registry assigns "a unique 'property number'" and a new title deed to each registered unit [[30]](https://rega.gov.sa/en/media-center/news/rega-calls-on-property-owners-in-five-districts-in-riyadh-city-to-register-their-properties-in-the-real-estate-registry-starting-today). The plan-number and plot-number scheme used on municipal subdivision plans was seen only in property listings, so it is not documented here.
- **Qatar.** QARS gives every building a number within zone and street [[26]](https://thepeninsulaqatar.com/article/23/11/2013/numbering-places). Qatar Post's addressing example is "Zone 38, Street 904" [[27]](https://www.upu.int/UPU/media/upu/PostalEntitiesFiles/addressingUnit/qatEn.pdf). A parcel identification number (PIN) format was not found.

**Rule for Studio:** store every identifier as text, never as a number. Leading zeros and pairs like "number/sub-number" do not survive numeric fields.

**Land-use codes.** ADM's Appendix 2 lists `UsageCategoryType` and `UsageType` pairs "generated as on 10/Nov/2019". I counted 1 218 pairs in 23 categories (utility 182, Temporary 181, public 170, commercial 108, ...). They are case sensitive and include near-duplicates such as `attachedVilla` and `attachedVillas` [[15]](https://www.dmt.gov.ae/adm/-/media/Project/DMT/ADM/E-Library/0001-Oct-2021-Doc/SDDPlanningDataSubmissionSpecifications_v1182.pdf). Studio needs a mapping table from its own land-use classes to each authority's domain, not free text. Dubai, Saudi and Qatar land-use code lists were not found publicly.

**Arabic and English name fields.** ADM pairs `NameEnglish`/`NameArabic` (and `SectorNameEnglish`/`SectorNameArabic`). For roads, `RoadNameArabic` "becomes mandatory if Road name in English is entered" [[15]](https://www.dmt.gov.ae/adm/-/media/Project/DMT/ADM/E-Library/0001-Oct-2021-Doc/SDDPlanningDataSubmissionSpecifications_v1182.pdf). Names such as `SectorNameEnglish` (17 characters) exceed the shapefile limit, so the schema cannot survive a shapefile round trip (next items).

**Encoding: measured** ([script](assets/C8/encoding_test.py), [output](assets/C8/outputs/encoding_test.txt); pyogrio 0.13 with GDAL 3.12.4).

| Case | What happened |
|---|---|
| Shapefile written by GDAL with default options | `.cpg` = `UTF-8`, DBF language driver ID (LDID) byte 0; Arabic reads back correctly |
| Written as Windows-1256 | `.cpg` = `CP1256`; reads back correctly while the `.cpg` is present |
| UTF-8 DBF, `.cpg` deleted | GDAL reports ISO-8859-1 and returns `Ø¨Ø±Ø¬ Ø®Ù...` for "برج خليفة"; read as CP1256 it shows the familiar `ط¨ط±ط¬ ط®ظ„ظٹظپط©` |
| CP1256 DBF, `.cpg` deleted | reads as `ÈÑÌ ÎáíÝÉ`; forcing UTF-8 raises a decode error |
| Arabic field names | `اسم_المجتمع_العربي` was cut at 10 **bytes** in the middle of a UTF-8 letter; **reading the file then failed** with `UnicodeDecodeError`. `ملاحظات` became `ملاحظ` (5 letters = 10 bytes) |
| 240-letter Arabic note (440 bytes) | read back as 138 characters / 253 bytes |
| GeoPackage and file geodatabase (GDAL OpenFileGDB) | all field names (including Arabic), all 240 characters and EPSG:3997 kept |

This matches the documentation:
- **GDAL** reads the `.cpg` first and the DBF language driver ID (LDID) second, treating LDID 87 as ISO-8859-1. It caps field names at 10 characters and auto-extends strings "up to the 255 bytes limit" [[35]](https://gdal.org/en/stable/drivers/vector/shapefile.html).
- **ArcGIS Pro** caps field names at 10 characters and text at 254, where "the field length represents the number of bytes". "By default ... dBASE files support the ANSI character set", and other code pages need the `dbfDefault` registry value [[40]](https://doc.esri.com/en/arcgis-pro/latest/tool-reference/appendices/geoprocessing-considerations-for-shapefile-output.html). Esri adds that "Shapefiles and dBASE files cannot store non-English characters by default" [[41]](https://doc.esri.com/en/arcgis-pro/latest/help/data/shapefiles/working-with-shapefiles-in-arcgis-pro.html).

In .NET 8, `Encoding.GetEncoding(1256)` throws `NotSupportedException` until `CodePagesEncodingProvider` is registered (measured; [C# demo](assets/C8/DbfEncodingDemo.cs), [output](assets/C8/outputs/dbf_encoding_dotnet.txt)):

```csharp
Encoding.RegisterProvider(CodePagesEncodingProvider.Instance); // once at startup
Encoding enc = cpg.ToUpperInvariant() switch {
    "UTF-8" or "UTF8" or "65001" => new UTF8Encoding(false),
    "CP1256" or "1256" or "WINDOWS-1256" => Encoding.GetEncoding(1256),
    _ => Encoding.Latin1 };  // GDAL's assumption when nothing is declared: show a preview and ask
```

**Field-name 10-character limit: measured.** GDAL "launders" names and appends serial numbers. The result: `community_name_en` became `community_`, and `community_name_ar` became `communit_1`. `land_use_code` and `land_use_class` became `land_use_c` and `land_use_1`. The English/Arabic pairing is lost, and which one is which depends on field order. GDAL's docs note that "Starting with GDAL 3.13, `.shp.xml` side-car files are used to set field names potentially longer than 10 characters" [[35]](https://gdal.org/en/stable/drivers/vector/shapefile.html). The GDAL 3.12 used here did not do this.

### 5. Common defects (with measured size where possible)

| Defect | What it looks like | Measured size or test | How to detect |
|---|---|---|---|
| Missing `.prj` | layer has no CRS | GDAL returned CRS `None` once the `.prj` was deleted ([output](assets/C8/outputs/encoding_test.txt)) | refuse to place on map until assigned |
| Wrong `.prj` / wrong datum label | Nahrwan 1967 UTM coordinates labelled WGS 84 | **436.6 m** offset at Burj Khalifa | compare against a known control point or basemap |
| DLTM read as UTM 40N (or the reverse) | site lands near 56.94°E, the Gulf of Oman side, or near 53.61°E | **168.0 km** (DLTM as UTM) and **167.9 km** (UTM as DLTM) | anchor-pin ranking below |
| Swapped axis order | lat/lon stored as lon/lat | Burj Khalifa moves **4 142 km**. Passing (lon, lat) to an EPSG:4326 transformer without `always_xy` gave (−1 479 313, 6 596 674) | values outside the GCC; check axis order of the CRS |
| Wrong UTM zone | Riyadh data in zone 37N | grid scale 1.0071, areas +1.42 % | zone from the longitude of the centroid |
| Z versus no Z | PolygonZ from survey, 2D expected | shapefile reported `Polygon Z`, 2D area unchanged; `force_2d` drops Z ([output](assets/C8/outputs/crs_sniff.txt)). ADM forbids elevation [[15]](https://www.dmt.gov.ae/adm/-/media/Project/DMT/ADM/E-Library/0001-Oct-2021-Doc/SDDPlanningDataSubmissionSpecifications_v1182.pdf) | geometry type and Z range on import |
| Self-intersection (bow-tie) | corners digitised out of order | GEOS: `Self-intersection[494030 2787960]`; signed "area" 0 m², `make_valid` gives 2 parts, 1 800 m² | `is_valid`, `explain_validity` |
| Gap (sliver) between neighbours | parcels 5 cm apart | 0.050 m gap; rounding to a 0.10 m grid made it **0.100 m**, not 0; `snap(B, A, 0.10)` closed it | neighbour distance below tolerance |
| Overlap | 0.3 m overlap | 21 m² overlap; `C.difference(B)` removed it | pairwise intersection area |
| Multipart parcel | one plot number, two polygons | 2 parts; ADM: "Each closed Polyline object must be a single polygon" | part count above 1 |
| Duplicate vertices and spikes | repeated vertex plus a 1 mm spike | 9 coordinates became 8 after `remove_repeated_points`; spike flagged as self-intersection | `remove_repeated_points`, validity |
| Mixed units | DWG in mm, GIS in m | GDAL's DXF writer set `$INSUNITS` = 6 (metres) for a projected layer. ADM requires 1 unit = 1 m | check `$INSUNITS` and coordinate magnitudes |
| Arabic mojibake | `Ø¨Ø±Ø¬` or `ط¨ط±ط¬` patterns | shown above for shapefile. **DXF too:** GDAL wrote an Arabic layer name as UTF-8 bytes under `$DWGCODEPAGE ANSI_1252`, and both GDAL and ezdxf read it back as `Ø¨Ø±Ø¬ Ø®Ù...` ([output](assets/C8/outputs/kml_dxf_test.txt)) | flag Latin-1 letter runs like `Ø`, `Ù` in Arabic fields |

Geometry tests used shapely 2.2 / GEOS 3.14 ([script](assets/C8/geometry_checks.py), [output](assets/C8/outputs/geometry_checks.txt)). Note the trap in the gap row: snapping coordinates to a grid does not close gaps. Only vertex snapping to the neighbour does. This matches ADM's rule that snapping must be "only on vertices".

**Guessing a missing CRS: measured** ([script](assets/C8/crs_sniff.py)). Inverse-projecting a file's coordinates under each candidate CRS and keeping those that land inside the UAE, Saudi or Qatar extents does **not** identify the CRS. DLTM coordinates for Burj Khalifa landed inside a GCC extent under 10 candidates. UTM coordinates fit eight. Only QNG coordinates were distinctive, with three candidates. What works is an anchor: the user drops one pin on the site, and candidates are ranked by distance from it. DLTM came out at 0.000 km, against 167.97 km for UTM 40N and 168.10 km for Nahrwan UTM 40N. The anchor separates grids (tens of km) but not datums (hundreds of metres). Telling WGS 84 from Nahrwan needs a control point or a careful basemap check.

### 6. QGIS and ArcGIS Pro behaviour on import and export

| Topic | QGIS | ArcGIS Pro | GDAL (what Studio would embed) |
|---|---|---|---|
| On-the-fly reprojection | "QGIS supports 'on the fly' CRS transformation for both raster and vector data" [[46]](https://docs.qgis.org/testing/en/docs/user_manual/working_with_projections/working_with_projections.html) | "Empty maps and scenes derive their coordinate systems from the first layer added"; others are "projected in real time using a transformation", which "is not advisable if you are editing data or performing analysis" [[42]](https://doc.esri.com/en/arcgis-pro/latest/help/mapping/properties/specify-a-coordinate-system.html) | none; the caller reprojects |
| Unknown CRS | options: "Leave as unknown CRS (take no action)", "Prompt for CRS", "Use project CRS", "Use default layer CRS" [[46]](https://docs.qgis.org/testing/en/docs/user_manual/working_with_projections/working_with_projections.html) | unknown layers "draw as if the origin of their coordinate system is 0,0", "are not projected on the fly" and "ignore datum transformations" [[44]](https://doc.esri.com/en/arcgis-pro/latest/help/mapping/properties/use-an-unknown-coordinate-system.html) | missing `.prj` gives no SRS; a `.prj` is matched against EPSG [[35]](https://gdal.org/en/stable/drivers/vector/shapefile.html) |
| Datum transformation choice | "By default, QGIS will attempt to use the most accurate transformation available". "Ask for datum transformation if several are available" shows a chooser; a missing grid shows a warning and a download button [[46]](https://docs.qgis.org/testing/en/docs/user_manual/working_with_projections/working_with_projections.html) | "By default, the first transformation in the list is applied", sorted "based on data extents and transformation accuracy"; the Map Properties Transformation tab lists them; some grid files need a separate download [[43]](https://doc.esri.com/en/arcgis-pro/latest/help/mapping/properties/geographic-coordinate-system-transformation.html) | PROJ picks per point by area of use (measured above); ballpark if nothing else exists |
| Shapefile encoding | a QGIS commit moved decoding into QGIS: the declared `.cpg`/LDID is read on open, then the configured encoding is used, and the "Ignore shapefile encoding declaration" option was removed [[48]](https://github.com/nyalldawson/QGIS/commit/85614189333f990ed978126d9a2c9b585d5466e3). A 2018 report says files without `.cpg` were read as UTF-8 by default [[49]](https://github.com/qgis/QGIS/issues/26669) | ANSI by default; other code pages via `dbfDefault` [[40]](https://doc.esri.com/en/arcgis-pro/latest/tool-reference/appendices/geoprocessing-considerations-for-shapefile-output.html) | `.cpg` then LDID; ISO-8859-1 when nothing is declared (measured) |
| GeoPackage | "GeoPackage is the default format for vector data in QGIS" [[47]](https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/supported_data.html) | read, add to maps, create with Create SQLite Database "that conforms to the OGC specification"; "single-user connection"; avoid field names with spaces or non-alphanumeric characters [[45]](https://doc.esri.com/en/arcgis-pro/latest/help/data/databases/work-with-sqlite-databases-in-arcgis-pro.html) | read/write; Arabic names kept (measured) |
| File geodatabase | domains supported [[47]](https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/supported_data.html) | Esri's own format ("ESRI File Geodatabase") [[36]](https://gdal.org/en/stable/drivers/vector/openfilegdb.html) | OpenFileGDB: "Write and update capabilities are supported since GDAL >= 3.6", no third-party SDK; 64-bit integer fields need `TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER` [[36]](https://gdal.org/en/stable/drivers/vector/openfilegdb.html); round trip with Arabic measured OK |
| GeoJSON / KML | (via GDAL) | (via import tools) | RFC 7946 output reprojects to WGS 84 [[38]](https://gdal.org/en/stable/drivers/vector/geojson.html), as the RFC requires; "the 'crs' member ... is no longer used" [[39]](https://datatracker.ietf.org/doc/html/rfc7946). Measured: default GeoJSON kept DLTM metres with a `crs` member; `RFC7946=YES` wrote (55.2738029, 25.1967468); KML came back as EPSG:4326 |
| DXF | not detailed in the manual | (CAD import) | "DXF files are considered to have no georeferencing information"; polygons become HATCH by default; written as AutoCAD 2004; ANSI_1252 assumed [[37]](https://gdal.org/en/stable/drivers/vector/dxf.html). Measured: CRS read back `None`, Arabic layer name garbled |

I did not run QGIS or ArcGIS Pro here (no desktop, no Windows). Their behaviour is quoted from documentation only.

### 7. DEM formats and vertical datums

**Formats.**
- **GeoTIFF and Cloud-Optimized GeoTIFF (COG).** COG is an OGC standard (21-026, v1.0) that defines how a TIFF is laid out so clients can fetch only the parts they need [[54]](https://www.ogc.org/standards/ogc-cloud-optimized-geotiff/). GDAL's COG driver has existed since 3.1. It tiles at 512 px by default, uses LZW compression by default since 3.4, and builds overviews automatically [[55]](https://gdal.org/en/stable/drivers/raster/cog.html).
- **ASCII grid.** Esri ASCII grid ("ASCII interchange format for Arc/Info Grid") is read/write in GDAL. Its CRS comes only from an optional `.prj`, and projection support is "quite limited" [[56]](https://gdal.org/en/stable/drivers/raster/aaigrid.html). Treat ASCII grids like `.prj`-less shapefiles.
- **LAS/LAZ point clouds.** LAZ is lossless LAS compression. LASzip is Apache 2.0 licensed and claims files "only 7-20% of the original size" [[57]](https://laszip.org/). The ASPRS LAS 1.4 specification page returned 404, so how LAS stores its CRS is not verified here.

**Vertical datums: measured** with PROJ's EGM96 and EGM2008 grids fetched from the PROJ content delivery network (CDN) ([script](assets/C8/geoid_check.py), [output](assets/C8/outputs/geoid_check.txt)). Height of the geoid below the WGS 84 ellipsoid (N):

| Place | EGM96 N | EGM2008 N | Difference |
|---|---|---|---|
| Burj Khalifa | −33.725 m | −34.120 m | 0.40 m |
| Sheikh Zayed Grand Mosque | −33.467 m | −33.249 m | 0.22 m |
| Kingdom Centre, Riyadh | −7.602 m | −7.353 m | 0.25 m |
| Museum of Islamic Art, Doha | −29.942 m | −29.843 m | 0.10 m |

What this means:
- GNSS and lidar ellipsoidal heights in Dubai or Abu Dhabi are about 34 m larger than heights above mean sea level. Mixing the two puts terrain 34 m wrong.
- EGM96 against EGM2008 is a 0.1 to 0.4 m question, which matters for drainage and finished-floor levels.
- **Saudi.** PROJ knows two KSA-GRF17 to KSA-VRF14 operations. Both are unavailable because grid `KSA-GEOID21.gra` has no URL and `open_license=False`, so PROJ falls back to a ballpark (zero) vertical shift. At Riyadh that is an error of about 7 m, going by the EGM2008 value.
- **Abu Dhabi.** Ras Ghumays height (5843) has only a ballpark operation in PROJ.
- **Dubai.** Old vertical control used "Port Rashid Datum" [[10]](https://fig.net/resources/proceedings/fig_proceedings/cairo/papers/ts_13/ts13_12_marzooqi_etal.pdf). DM offers orthometric height conversion and a "Cm Geoid" document [[9]](https://www.dm.gov.ae/survey-department/geodesy/).
- **Qatar.** No Qatar vertical CRS appears in EPSG (searched with pyproj).

Local heights therefore need the authority's own conversion.

**Public DEM sources covering the GCC.**

| Source | Resolution | Vertical datum | Format | Licence (read 2026-10-30) |
|---|---|---|---|---|
| Copernicus DEM GLO-30 (TanDEM-X, acquired 2011 to 2015) | 30 m | EGM2008 (EPSG:3855) | GeoTIFF, DTED [[50]](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM); COG on AWS [[51]](https://registry.opendata.aws/copernicus-dem/) | free licence worldwide; must credit DLR, Airbus and EU/ESA, with a "produced using" notice for modified data [[50]](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM). AWS describes it as a surface model including buildings and vegetation [[51]](https://registry.opendata.aws/copernicus-dem/) |
| SRTM 1 arc-second (USGS) | 30 m | EGM96 | DTED, BIL, GeoTIFF | "open distribution"; no separate licence text on the page [[52]](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-digital-elevation-shuttle-radar-topography-mission-srtm-1) |
| ALOS World 3D 30 m (AW3D30) v4.1 (April 2024), JAXA | 1 arc-second, about 30 m | "Height above sea level"; geoid not named | GeoTIFF, 1° tiles | free for "commercial and non-commercial purposes" under JAXA terms; registration needed [[53]](https://www.eorc.jaxa.jp/ALOS/en/dataset/aw3d30/aw3d30_e.htm) |

All three are around 30 m and include buildings or are described as surface models. My judgement is that they suit regional context, not plot-level grading. Plot-level levels should come from the authority's survey or the project's own survey.

### 8. Basemap licensing

| Provider | Key obligations | Caching, offline, derived data | Price (read 2026-10-30) |
|---|---|---|---|
| OpenStreetMap data (ODbL) | Credit "OpenStreetMap" and make clear the data is under the ODbL. Placement rules differ for browsable maps, printed maps and static images [[58]](https://www.openstreetmap.org/copyright). Credit must not require interaction to see. It may collapse after 5 seconds but must stay findable. Print must include the openstreetmap.org/copyright URL (guideline adopted 2021-06-25) [[59]](https://osmfoundation.org/wiki/Licence/Attribution_Guidelines) | "If you alter or build upon our data, you may distribute the result only under the same license" [[58]](https://www.openstreetmap.org/copyright). Images, PDFs and printed maps are usually Produced Works; the guideline adds that for a published Produced Work "the underlying database has to be published as well" (ODbL 4.6) [[60]](https://osmfoundation.org/wiki/Licence/Community_Guidelines/Produced_Work_-_Guideline). Your own data kept as separate feature types or layers can be a Collective Database without share-alike [[61]](https://osmfoundation.org/wiki/Licence/Community_Guidelines/Collective_Database_Guideline_Guideline) | data free |
| tile.openstreetmap.org | stable, identifying User-Agent; visible attribution [[62]](https://operations.osmfoundation.org/policies/tiles/) | bulk download, pre-seeding and "Download city for offline use" are prohibited; honour cache headers (7 days minimum); "no SLA" [[62]](https://operations.osmfoundation.org/policies/tiles/) | free, best effort |
| Google Maps Platform | "clear Google Maps attribution"; for Photorealistic 3D, display all tile attributions in a line [[64]](https://developers.google.com/maps/documentation/tile/policies) | "must not pre-fetch, index, store, or cache any Content" except under stated conditions; prohibits "Offline uses" [[64]](https://developers.google.com/maps/documentation/tile/policies). Place IDs may be stored indefinitely; "Maps JavaScript API results must be displayed on Google Maps" [[65]](https://developers.google.com/maps/documentation/javascript/policies). The Service Specific Terms page could not be read [[66]](https://cloud.google.com/maps-platform/terms/maps-service-terms) | since 2025-03-01: free calls per SKU per month of 10 000 (Essentials), 5 000 (Pro) and 1 000 (Enterprise); Essentials Map Tiles up to 100 000. Plans: USD 100/month (50 000 calls), USD 275/month (100 000), USD 1 200/month (250 000) [[63]](https://mapsplatform.google.com/pricing/) |
| Esri (ArcGIS Location Platform) | data from "Esri and partners such as TomTom, Garmin ... OpenStreetMap contributors" [[71]](https://developers.arcgis.com/documentation/mapping-and-location-services/mapping/basemaps/) | E300 Product-Specific Terms (2025-11-13): "Programmatic use of session tokens (e.g., exporting volumes of basemap tiles) is not permitted"; "Basemap Styles are for use only with ArcGIS Location Platform Basemap Services"; storing geocodes needs a paid subscription. Esri's Google Photorealistic 3D Basemap: "may not extract, or store results in external databases, nor create derivative works" [[70]](https://www.esri.com/content/dam/esrisites/en-us/media/legal/product-specific-terms-of-use/e300.pdf) | 2 million basemap tiles free per month, then USD 0.15 per 1 000. Geocoding not stored: 20 000 free, then USD 0.50 per 1 000; stored: USD 4 per 1 000 [[69]](https://location.arcgis.com/pricing/) |
| Mapbox | ToS (2024-03-31) forbids removing "proprietary notices"; the detail is in Product Terms (PDF, not read) [[68]](https://www.mapbox.com/legal/tos) | offline limits are in separate SDK guides, not read [[67]](https://www.mapbox.com/pricing) | GL JS: 50 000 map loads free, then USD 5.00 to 2.50 per 1 000. Vector tiles: 200 000 free, then USD 0.25 to 0.15 per 1 000. Static tiles: 200 000 free, then USD 0.50 to 0.30. Permanent geocoding: USD 5.00 per 1 000 [[67]](https://www.mapbox.com/pricing) |
| Bing Maps for Enterprise | no new customers since 2024-06-30; "services and product support will end on June 30, 2028"; migrate to Azure Maps [[72]](https://blogs.bing.com/maps/2024-05/Microsoft-Announces-Vision-for-Next-Generation-of-Enterprise-Maps) | n/a | n/a |
| Azure Maps (Gen2) | (terms not read) | page has no caching notes; one tile transaction = 15 tile requests [[73]](https://azure.microsoft.com/en-us/pricing/details/azure-maps/) | free per month: 5 000 base-map tile transactions, 1 000 imagery, 5 000 search, 1 000 routing. Paid rates showed "Contact Us" on the page as fetched [[73]](https://azure.microsoft.com/en-us/pricing/details/azure-maps/) |
| National basemaps | AD-SDI service shows no copyright or terms [[16]](https://arcgis.sdi.abudhabi.ae/agshost/rest/services/Hosted/BaseMapEng_LightGray_GCS/MapServer). Dubai Municipality open data requires naming the source [[11]](https://dm.gov.ae/open-data/). GEOSA licenses data through its geospatial services portal under the 2024 policies [[22]](https://geosa.gov.sa/en/controlAndcompliance/Pages/Geospatial_Data_Policies.aspx). Qatar: not found | unknown; ask per project | not found |

The safe default for a desktop app with offline use is OSM-derived data that Studio hosts or licenses itself, with the ODbL credit shown in the viewport and on exports. Google and Esri imagery or 3D tiles must not be cached, exported or used to derive geometry under the terms quoted above.

## Risks and open questions

- **Search budget.** The shared WebSearch budget was exhausted mid-task. Later sources were opened directly by known URL, so some authority documents may exist that I did not find.
- **No public specs outside Abu Dhabi.** Dubai Municipality, MOMRAH and the Qatar Ministry of Municipality GIS/CAD submission specs were not found. Each needs a direct request.
- **ADM spec age.** ADM spec v1.18.2 dates from 2021, and its land-use domain from 2019. Check for a newer version on the DMT e-library before building an exporter.
- **Northern emirates.** Sharjah, Ajman, Ras Al Khaimah, Fujairah and Umm Al Quwain CRS practice was not found.
- **Unread sources.**
  - AD-SDI SRS standard (2010): HTTP 403.
  - Dubai Pulse dataset pages: HTTP 503.
  - Google Service Specific Terms: page text not retrievable.
  - Mapbox Product Terms PDF: not read.
  - ASPRS LAS 1.4 page: 404.
- **Saudi vertical datum.** KSA-GEOID21 is not openly available to PROJ. Saudi orthometric heights need GEOSA's grid or service.
- **CP1256 `.cpg` label.** Whether ArcGIS Pro honours a `.cpg` that says `CP1256`, as GDAL writes it, was not tested (no Windows).
- **Desktop GIS untested.** QGIS and ArcGIS Pro behaviour is quoted, not tested.
- **Landmark precision.** Landmark coordinates are rounded (about 10 m), so the transformation table shows method and size of effects, not survey truth.
- **KSA-GRF17 drift.** EPSG says KSA-GRF17 to WGS 84 degrades by about 2.5 cm per year from 2017. Long-lived projects need epoch handling if survey-grade.
- **Plot and parcel numbers.** Dubai community-number structure comes from a 2006 news article. Saudi plan/plot numbering and a Qatar PIN were not documented.

## Sources

1. EPSG Geodetic Parameter Registry, REST API, CRS records (41 codes, for example 3997, 9358, 2932). IOGP. https://apps.epsg.org/api/v1/CoordRefSystem/3997/ Read 2026-10-30.
2. EPSG Geodetic Parameter Registry, REST API, transformation records (15953, 6999, 7002 to 7004, 1840, 1562, 1563, 9383, 1111, 1191). IOGP. https://apps.epsg.org/api/v1/Transformation/15953/ Read 2026-10-30.
3. EPSG:3997 WGS 84 / Dubai Local TM. epsg.io (MapTiler). https://epsg.io/3997 Read 2026-10-30. Third party; secondary: summarises the EPSG registry.
4. EPSG:2932 QND95 / Qatar National Grid. epsg.io. https://epsg.io/2932 Read 2026-10-30. Third party; secondary.
5. EPSG:28600 Qatar 1974 / Qatar National Grid. epsg.io. https://epsg.io/28600 Read 2026-10-30. Third party; secondary.
6. EPSG:9333 KSA-GRF17. epsg.io. https://epsg.io/9333 Read 2026-10-30. Third party; secondary.
7. EPSG:7002 Nahrwan 1967 to WGS 84 (13). epsg.io. https://epsg.io/7002 Read 2026-10-30. Third party; secondary.
8. EPSG:27040 with transformation 6999. epsg.io. https://epsg.io/27040-6999 Read 2026-10-30. Third party; secondary.
9. Geodesy. Dubai Municipality Survey Department. https://www.dm.gov.ae/survey-department/geodesy/ Read 2026-10-30.
10. Al Marzooqi, Fashir, Ahmed. Derivation of Datum Transformation Parameters for Dubai Emirate. FIG Working Week 2005, Cairo. https://fig.net/resources/proceedings/fig_proceedings/cairo/papers/ts_13/ts13_12_marzooqi_etal.pdf Read 2026-10-30. Old (2005).
11. Open Data. Dubai Municipality. https://dm.gov.ae/open-data/ Read 2026-10-30.
12. dm_sectors-open dataset. Dubai Pulse. https://www.dubaipulse.gov.ae/data/dm-location/dm_sectors-open Read 2026-10-30. Not verified: page returned HTTP 503; details from search-result text.
13. dld_lkp_areas-open dataset. Dubai Pulse / Dubai Land Department. https://www.dubaipulse.gov.ae/data/dld-transactions/dld_lkp_areas-open Read 2026-10-30. Not verified: HTTP 503; details from search-result text.
14. Circular 400: Drawings Submission Standards (2021-09-29). Dubai Development Authority. https://dda.gov.ae/-/media/436DDFA50D8B4AC1A075607917327616.pdf Read 2026-10-30.
15. Standards & Specifications for Planning Data Submission (Plot, Roads & Service Corridors) v1.18.2 (2021-08-02). Abu Dhabi City Municipality, Town Planning Sector, Spatial Data Division (DMT e-library). https://www.dmt.gov.ae/adm/-/media/Project/DMT/ADM/E-Library/0001-Oct-2021-Doc/SDDPlanningDataSubmissionSpecifications_v1182.pdf Read 2026-10-30.
16. BaseMapEng_LightGray_GCS MapServer. Abu Dhabi SDI ArcGIS REST. https://arcgis.sdi.abudhabi.ae/agshost/rest/services/Hosted/BaseMapEng_LightGray_GCS/MapServer Read 2026-10-30.
17. AD-SDI home. Abu Dhabi Government. https://sdi.gov.abudhabi/sdi/index.html Read 2026-10-30.
18. Geospatial data platforms. UAE Government portal (u.ae). https://u.ae/en/about-the-uae/digital-uae/data/geospatial-data-platforms Read 2026-10-30.
19. SDI Data Standard: Spatial Reference System v1.0 (2010). Abu Dhabi Systems and Information Centre, hosted by pdfcoffee.com. https://pdfcoffee.com/sdi-data-standard-spatial-reference-system-property-pdf-pdf-free.html Read 2026-10-30. Not verified: HTTP 403; old (2010); third-party host; details from search-result text.
20. الخرائط الحضرية (Urban Maps) e-service. Ministry of Municipalities and Housing (MOMRAH). https://momah.gov.sa/ar/e-services/alkhrayt-alhdryt Read 2026-10-30.
21. KSA Geospatial Standards. GEOSA. https://geosa.gov.sa/en/products/Pages/KSAGeospatialStandards.aspx Read 2026-10-30.
22. Geospatial Data Policies. GEOSA. https://geosa.gov.sa/en/controlAndcompliance/Pages/Geospatial_Data_Policies.aspx Read 2026-10-30.
23. Al-Kherayef, Al-Qahtani, Salawu et al. Establishment of KSA-CORS Network, its Performance and Future Plans. GASGI, FIG Working Week 2023. https://fig.net/resources/proceedings/fig_proceedings/fig2023/ppt/ts04g/TS04G_al-qahtani_salawu_et_al_12208_ppt.pdf Read 2026-10-30.
24. Qatar Rail committed to complying with QND95 (2014-12-04). Gulf Times. https://www.gulf-times.com/story/418684/qatar-rail-committed-to-complying-with-qnd95 Read 2026-10-30. Old (2014); third party.
25. Qatar's GIS (ArcNews Spring 2009). Esri. https://www.esri.com/news/arcnews/spring09articles/qatars-gis.html Read 2026-10-30. Old (2009); third party.
26. Numbering places (2013-11-23, updated 2022-01-28). The Peninsula Qatar. https://thepeninsulaqatar.com/article/23/11/2013/numbering-places Read 2026-10-30. Third party.
27. Qatar addressing (08/2024). Universal Postal Union / Qatar Post. https://www.upu.int/UPU/media/upu/PostalEntitiesFiles/addressingUnit/qatEn.pdf Read 2026-10-30.
28. Reading Dubai's road signs (2006-09-08). Gulf News. https://www.gulfnews.com/news/gulf/uae/traffic-transport/reading-dubai-s-road-signs-1.254255 Read 2026-10-30. Old (2006); third party.
29. Dubai property numbers: Ejari, DEWA, Makani. EGSH. https://egsh.ae/insights/dubai-property-numbers-ejari-dewa-makani Read 2026-10-30. Third party.
30. REGA calls on property owners in five districts in Riyadh (2024-03-31). Real Estate General Authority. https://rega.gov.sa/en/media-center/news/rega-calls-on-property-owners-in-five-districts-in-riyadh-city-to-register-their-properties-in-the-real-estate-registry-starting-today Read 2026-10-30.
31. Burj Khalifa. Wikipedia. https://en.wikipedia.org/wiki/Burj_Khalifa Read 2026-10-30. Third party.
32. Sheikh Zayed Grand Mosque. Wikipedia. https://en.wikipedia.org/wiki/Sheikh_Zayed_Grand_Mosque Read 2026-10-30. Third party.
33. Kingdom Centre. Wikipedia. https://en.wikipedia.org/wiki/Kingdom_Centre Read 2026-10-30. Third party.
34. Museum of Islamic Art, Doha. Wikipedia. https://en.wikipedia.org/wiki/Museum_of_Islamic_Art,_Doha Read 2026-10-30. Third party.
35. ESRI Shapefile driver. GDAL. https://gdal.org/en/stable/drivers/vector/shapefile.html Read 2026-10-30.
36. OpenFileGDB driver. GDAL. https://gdal.org/en/stable/drivers/vector/openfilegdb.html Read 2026-10-30.
37. DXF driver. GDAL. https://gdal.org/en/stable/drivers/vector/dxf.html Read 2026-10-30.
38. GeoJSON driver. GDAL. https://gdal.org/en/stable/drivers/vector/geojson.html Read 2026-10-30.
39. RFC 7946: The GeoJSON Format (August 2016). IETF. https://datatracker.ietf.org/doc/html/rfc7946 Read 2026-10-30.
40. Geoprocessing considerations for shapefile output. Esri ArcGIS Pro. https://doc.esri.com/en/arcgis-pro/latest/tool-reference/appendices/geoprocessing-considerations-for-shapefile-output.html Read 2026-10-30.
41. Working with shapefiles in ArcGIS Pro. Esri. https://doc.esri.com/en/arcgis-pro/latest/help/data/shapefiles/working-with-shapefiles-in-arcgis-pro.html Read 2026-10-30.
42. Specify a coordinate system. Esri ArcGIS Pro. https://doc.esri.com/en/arcgis-pro/latest/help/mapping/properties/specify-a-coordinate-system.html Read 2026-10-30.
43. Geographic coordinate system transformation. Esri ArcGIS Pro. https://doc.esri.com/en/arcgis-pro/latest/help/mapping/properties/geographic-coordinate-system-transformation.html Read 2026-10-30.
44. Use an unknown coordinate system. Esri ArcGIS Pro. https://doc.esri.com/en/arcgis-pro/latest/help/mapping/properties/use-an-unknown-coordinate-system.html Read 2026-10-30.
45. Work with SQLite databases in ArcGIS Pro. Esri. https://doc.esri.com/en/arcgis-pro/latest/help/data/databases/work-with-sqlite-databases-in-arcgis-pro.html Read 2026-10-30.
46. Working with Projections. QGIS User Manual (testing). https://docs.qgis.org/testing/en/docs/user_manual/working_with_projections/working_with_projections.html Read 2026-10-30.
47. Supported data formats. QGIS User Manual. https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/supported_data.html Read 2026-10-30.
48. "Always disable GDAL side shapefile encoding handling" (commit). N. Dawson, QGIS (fork mirror). https://github.com/nyalldawson/QGIS/commit/85614189333f990ed978126d9a2c9b585d5466e3 Read 2026-10-30. Commit date not shown on page.
49. Issue #26669 "charset dialog window" (2018-04-21). QGIS GitHub. https://github.com/qgis/QGIS/issues/26669 Read 2026-10-30.
50. Copernicus DEM collection. Copernicus Data Space Ecosystem. https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM Read 2026-10-30.
51. Copernicus DEM. AWS Registry of Open Data. https://registry.opendata.aws/copernicus-dem/ Read 2026-10-30. Third party (redistributor).
52. SRTM 1 Arc-Second Global. USGS EROS. https://www.usgs.gov/centers/eros/science/usgs-eros-archive-digital-elevation-shuttle-radar-topography-mission-srtm-1 Read 2026-10-30.
53. ALOS World 3D 30 m (AW3D30). JAXA EORC. https://www.eorc.jaxa.jp/ALOS/en/dataset/aw3d30/aw3d30_e.htm Read 2026-10-30.
54. OGC Cloud Optimized GeoTIFF Standard (21-026). OGC. https://www.ogc.org/standards/ogc-cloud-optimized-geotiff/ Read 2026-10-30.
55. COG driver. GDAL. https://gdal.org/en/stable/drivers/raster/cog.html Read 2026-10-30.
56. AAIGrid driver. GDAL. https://gdal.org/en/stable/drivers/raster/aaigrid.html Read 2026-10-30.
57. LASzip. laszip.org. https://laszip.org/ Read 2026-10-30.
58. Copyright and License. OpenStreetMap. https://www.openstreetmap.org/copyright Read 2026-10-30.
59. Licence/Attribution Guidelines (adopted 2021-06-25). OSM Foundation. https://osmfoundation.org/wiki/Licence/Attribution_Guidelines Read 2026-10-30.
60. Produced Work Guideline (endorsed 2014-06-06). OSM Foundation. https://osmfoundation.org/wiki/Licence/Community_Guidelines/Produced_Work_-_Guideline Read 2026-10-30.
61. Collective Database Guideline (endorsed 2016-06-17). OSM Foundation. https://osmfoundation.org/wiki/Licence/Community_Guidelines/Collective_Database_Guideline_Guideline Read 2026-10-30.
62. Tile Usage Policy. OSMF Operations. https://operations.osmfoundation.org/policies/tiles/ Read 2026-10-30.
63. Google Maps Platform pricing. Google. https://mapsplatform.google.com/pricing/ Read 2026-10-30.
64. Map Tiles API policies. Google. https://developers.google.com/maps/documentation/tile/policies Read 2026-10-30.
65. Maps JavaScript API policies (updated 2026-10-30). Google. https://developers.google.com/maps/documentation/javascript/policies Read 2026-10-30.
66. Google Maps Platform Service Specific Terms. Google. https://cloud.google.com/maps-platform/terms/maps-service-terms Read 2026-10-30. Not verified: page text not retrievable.
67. Mapbox pricing. Mapbox. https://www.mapbox.com/pricing Read 2026-10-30.
68. Mapbox Terms of Service (updated 2024-03-31). Mapbox. https://www.mapbox.com/legal/tos Read 2026-10-30. Product Terms PDF linked from https://www.mapbox.com/legal/product-terms not read.
69. ArcGIS Location Platform pricing. Esri. https://location.arcgis.com/pricing/ Read 2026-10-30.
70. E300 Product-Specific Terms of Use (2025-11-13). Esri. https://www.esri.com/content/dam/esrisites/en-us/media/legal/product-specific-terms-of-use/e300.pdf Read 2026-10-30.
71. Basemaps. ArcGIS Developers. https://developers.arcgis.com/documentation/mapping-and-location-services/mapping/basemaps/ Read 2026-10-30.
72. Microsoft announces vision for next generation of enterprise maps (2024-05-21). Bing Maps Blog. https://blogs.bing.com/maps/2024-05/Microsoft-Announces-Vision-for-Next-Generation-of-Enterprise-Maps Read 2026-10-30.
73. Azure Maps pricing. Microsoft. https://azure.microsoft.com/en-us/pricing/details/azure-maps/ Read 2026-10-30.

## Choices made

- **Inferences about Studio.** I relied on the shared-brief inferences: Studio is a Windows C# (.NET) urban-design application, possibly Native AOT, aimed at the UAE first, then Saudi Arabia and Qatar, and it has 3D massing. From this task line I also inferred that Studio already imports and exports some GIS and CAD data, because the task asks what authorities "hand over and expect back". No Studio code was seen.
- **Registry check.** "Checked against the registry" was done with pyproj's bundled EPSG v12.029 plus the EPSG REST API at apps.epsg.org. epsg.org HTML pages returned HTTP 403, and epsg.io was used as a secondary mirror for four codes.
- **Landmarks.** I picked Burj Khalifa, Sheikh Zayed Grand Mosque, Kingdom Centre and the Museum of Islamic Art, using Wikipedia infobox coordinates. They show behaviour, not survey accuracy.
- **Default CRS per city.** DLTM for Dubai, UTM 40N for Abu Dhabi (from ADM's spec), KSA-GRF17 UTM by zone for Saudi Arabia (from EPSG remarks), and QND95 / QNG for Qatar. The northern emirates default to UTM 40N for lack of a source; this is a judgement call.
- **Measurement stack.** GDAL measurements used pyogrio 0.13 / GDAL 3.12.4, installed into a private folder. Studio's own GDAL build may differ.
- **Network grids.** I enabled PROJ network access only for the geoid measurement (EGM96/EGM2008 grids from the PROJ CDN). All horizontal transformations ran offline, to mirror a desktop app without grids.
- **Abu Dhabi DMT.** I treated ADM's SDD spec as "DMT's" expectation for Abu Dhabi city. Al Ain and Al Dhafra may differ.
- **Basemaps.** I covered terms that affect a desktop app: caching, offline use and derived data. Per-call prices are given only where the vendor page showed them.

## What Studio should do

1. **[M] [COMPLETES]** Make CRS mandatory on import:
   - Read `.prj`, GeoPackage and file-geodatabase CRS.
   - When it is missing, never assume. Offer the GCC shortlist and rank candidates by distance from a user-placed site pin, since coordinates alone matched up to 10 candidates and the pin isolated DLTM at 0 km against 168 km (section 5).
2. **[S] [COMPLETES]** Ship Table 1 as a built-in CRS list:
   - Defaults: Dubai 3997; Abu Dhabi 32640; Saudi Arabia KSA-GRF17 / UTM by longitude (9356 to 9360, Riyadh 9358); Qatar 2932.
   - Legacy codes (27039/27040, 30339/30340, 20436 to 20440, 8836 to 8840, 28600, 2099) marked "legacy".
   - Store the EPSG code, not just WKT, in projects (Table 1, section 2).
3. **[M] [COMPLETES]** Control datum transformations:
   - Show the operation and its accuracy, and record it in the project.
   - Block or loudly warn on ballpark operations (TC(1948), Qatar 1948, KSA-VRF14 without grid).
   - Let the user pin AD-SDI's 7002 to 7004, Dubai's 15953 or Saudi's 9362, because path choice moved Riyadh by 11.4 m (section 3).
4. **[S] [COMPLETES]** Make shapefile export safe:
   - Always write a UTF-8 `.cpg`. Keep a long-name to 10-character field map in a side file.
   - Never write Arabic field names. Warn when Arabic text exceeds 254 bytes (about 127 letters).
   - On import without `.cpg`, test UTF-8 validity, then offer CP1256 with a preview. Register `CodePagesEncodingProvider` in .NET (section 4).
5. **[M] [COMPLETES]** Make GeoPackage the default GIS exchange format, since it keeps Arabic names, long text and the CRS. Add file-geodatabase write through GDAL's OpenFileGDB (GDAL 3.6 or later) for Esri-based authorities (sections 4 and 6).
6. **[M] [COMPLETES]** Add an "ADM planning submission" export profile matching SDD v1.18.2:
   - three DWGs, AutoCAD 2012 or earlier, WGS 84 / UTM 40N metres;
   - closed LWPOLYLINE, predefined attribute blocks, domain-checked `UsageCategoryType` / `UsageType`, file naming;
   - no Z, arcs or hatches;
   - run the same QC before export (section 1).
7. **[S] [COMPLETES]** Run geometry QC on every import and export: validity, `make_valid`, vertex snapping to neighbours within a set tolerance (not grid rounding), gap and overlap report, multipart and duplicate-vertex flags (section 5).
8. **[S] [COMPLETES]** Report the basis for plot areas (grid or ground). Warn when UTM 40N is used in Abu Dhabi (+0.08 % area) or a wrong UTM zone is detected (+1.4 % in Riyadh) (section 3).
9. **[M] [NEW]** Add vertical datum handling for terrain and point clouds:
   - Tag every height as ellipsoidal, EGM2008 or local, and apply EGM2008 (about −34 m at Dubai) automatically.
   - Require the authority's geoid for Dubai, Ras Ghumays and KSA-VRF14 heights.
   - Offer Copernicus GLO-30 COG as the default regional terrain, with its attribution (section 7).
10. **[S] [NEW]** Add a basemap licence layer:
    - Show attribution in the viewport and on exports.
    - Do not use tile.openstreetmap.org for offline use or pre-seeding.
    - Never cache or export Google or Esri 3D or imagery tiles.
    - Keep an ODbL "collective database" separation between OSM layers and user design data (section 8).
