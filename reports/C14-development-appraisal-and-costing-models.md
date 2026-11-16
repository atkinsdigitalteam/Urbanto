# C14: Development appraisal and costing models

Researched 2026-10-30. Brief file unavailable; scope taken from the task line. The shared web-search budget ran out part way through, so later facts come from pages opened directly by URL (see Choices made).

## Answer

Studio should build a monthly residual appraisal engine that copies the conventions UK-trained valuers expect from ARGUS Developer and that the RICS standard describes. The engine works in months. It assumes 100 % debt on land and costs. Interest is charged at a nominal annual rate divided by 12, with separate debit and credit rates and a setting for how often interest compounds. It solves for the land price that hits a target profit on cost. It reports profit on cost (the same ratio EstateMaster calls development margin), profit on GDV (gross development value), a project IRR (internal rate of return) without finance, and NPV (net present value). Construction cost is spread on an S-curve, by default Beta(2,2), F = 3x² − 2x³. Cost rates come from a UAE benchmark library, per m² of GFA (gross floor area), that records each rate's source, edition, data date and basis. The public benchmarks disagree a lot. For UAE high-rise residential, the lowest published lows are AED 4,410/m² (Turner & Townsend, Q1 2024) and the highest published highs are USD 3,400/m², about AED 12,478 (AECOM, Q3 2024 data). Turner & Townsend's 2025 average for Dubai high-rise apartments is AED 5,500/m². I built and measured a worked Dubai tower: 30,000 m² GFA, GDV AED 397.2 m, debit rate 7.34 % (3-month EIBOR, the Emirates Interbank Offered Rate, 4.34 % on 30 Oct 2026, plus an assumed 3 % margin). It gives a residual land value (RLV) of AED 76.4 m, finance of AED 44.0 m, profit on cost 20.0 %, profit on GDV 16.7 % and a project IRR of 17.3 % a year. The figures check by hand, and the finance loop reproduces the interest in a published ARGUS cash flow exactly. The main caveat: which cost source you pick moves RLV more than any ±10 % sensitivity. Using AECOM's Q3 2024 midpoint instead of the Turner & Townsend rate takes RLV from AED +76 m to −59 m. Studio must show the source, date and basis of every rate and let users pick and escalate rates. It should not ship a single "UAE cost per m²". UAE off-plan payment plans (buyers paying instalments during construction) also change finance a lot (RLV +22 % in an illustrative case), and the escrow rules were not verified.

## UAE construction cost benchmarks 2024 to 2026, by building type and source

All figures were read on 2026-10-30. USD figures are converted to AED at the 3.67 rate that AECOM and Currie & Brown state ([[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf)[[12]](https://curriebrown.foleon.com/archive/uae-2025-q3/building-asset-costs)). The conversion is mine. "City" is the city the source names. "UAE" means the source gives no city.

**Basis key.** Each code describes how one source defines its rate. The main table refers to these codes.

| Code | Source and basis as published |
|---|---|
| TT-MI24 | Turner & Townsend (T&T) UAE market intelligence Q1 2024 PDF, © March 2024. AED/m², high and low. The PDF does not state the area basis or what is included ([[1]](https://assets.foleon.com/eu-central-1/de-uploads-7e3kk3/48604/uaemi_24_construction_cost_performance.58a8c5990842.pdf)). |
| TT-GCMI | T&T Global construction market intelligence (GCMI) 2025 averages, republished in UAEMI 2025 ([[2]](https://marketintelligence.turnerandtownsend.com/uaemi-2025/construction-cost-performance)). The page labels them only "AED". The GCMI 2026 methodology defines cost per m² as "measured to the outer perimeter of external walls" (a gross area). It includes preliminaries, substructure, frame, envelope, finishes, fittings and services. It excludes external works, landscaping, professional fees, demolition, loose FF&E (furniture, fixtures and equipment), land, finance, taxes and car parking. Accuracy is ±10 % ([[6]](https://publications.turnerandtownsend.com/global-construction-market-intelligence-2026/methodology)). I assume the 2025 edition used the same definition (not verified). |
| TT-TALL | T&T tall buildings guide, Dubai, "2025 key cost ranges". GIA (gross internal area), shell and core. "Costs exclude finishes, demolition, external works and utilities" ([[4]](https://reports.turnerandtownsend.com/tall-buildings-construction-guide-2026/dubai)). |
| TT-ICMS | T&T International Construction Market Survey (ICMS) 2024, in USD. Seen only in search-result text from AGBI, because the page returned 403. Secondary source. Basis not seen ([[7]](https://www.agbi.com/analysis/construction/2024/06/building-construction-costs-dubai-riyadh-doha-abu-dhabi/)). |
| AECOM | AECOM Middle East Property & Construction Handbook, Dubai column, USD/m². The 2024 edition uses Q3 2023 costs and the 2025 edition uses Q3 2024 costs. Rates are averages of competitive tenders analysed by AECOM. They include construction works and main contractor preliminaries and OH&P (overheads and profit). They exclude external works, site infrastructure, enabling works, basements, podiums and car parks, contingencies, utility connections, fees, land, finance, LEED Silver and above, and VAT. Residential rates include fit-out, MEP (mechanical, electrical and plumbing) and lifts. Office rates are shell and core plus lobby and core finishes. Hotel rates include fit-out and kitchen equipment and exclude OS&E (operating supplies and equipment) ([[8]](https://publications.aecom.com/MEH/static/69a84a66cc94f48d41d456bfc959f519/4714f9cc02b32c869d15d7378fcb142e.pdf)[[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf)). |
| C&B | Currie & Brown UAE market overview Q3 2025, AED and USD, low and high. The data timestamp is 2025-08-07 ([[13]](https://flo.uri.sh/visualisation/22778655/embed?auto=1)). The area basis is not stated on the page ([[12]](https://curriebrown.foleon.com/archive/uae-2025-q3/building-asset-costs)). |
| SH | Stonehaven UAE Construction Cost Benchmarking Report 2025 (PDF created 2025-04-09). Rates are per m² of GFA unless stated. The low end reflects low-to-medium specification and the high end medium-to-high. They exclude third-party contributions, client finance, insurance, VAT, land, municipality connection charges, master infrastructure fees, developer legal fees, inflation and professional fees. Hotels exclude loose furniture and OS&E. Retail excludes tenant fit-out ([[15]](https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf)). |
| KF | Knight Frank UAE construction landscape H1 2025, from a newsroom summary dated 22 Sep 2025. Basis not stated. The full report sits behind a form ([[16]](https://www.knightfrank.ae/newsroom/article/2025/9/uae-construction-landscape-h1-2025)[[17]](https://www.knightfrank.ae/research/reports/uaes-construction-landscape)). |

**Rates by building type** (read 2026-10-30 for every row)

| Building type | Source | Edition / data date | City | Range as published | AED/m² equivalent | Basis |
|---|---|---|---|---|---|---|
| Residential high-rise | T&T [[1]](https://assets.foleon.com/eu-central-1/de-uploads-7e3kk3/48604/uaemi_24_construction_cost_performance.58a8c5990842.pdf) | UAEMI Q1 2024 | UAE | AED 4,410–5,390 /m² | 4,410–5,390 | TT-MI24 |
| Residential high-rise | T&T [[7]](https://www.agbi.com/analysis/construction/2024/06/building-construction-costs-dubai-riyadh-doha-abu-dhabi/) | ICMS 2024 (secondary) | Dubai | USD 1,334 /m² | 4,896 | TT-ICMS |
| Residential high-rise | T&T [[2]](https://marketintelligence.turnerandtownsend.com/uaemi-2025/construction-cost-performance) | GCMI 2025 | Dubai / Abu Dhabi | AED 5,500 / 5,500 (average) | 5,500 | TT-GCMI |
| Residential 20–60 storeys | T&T [[4]](https://reports.turnerandtownsend.com/tall-buildings-construction-guide-2026/dubai) | 2025 ranges (2020: AED 3,800–4,800) | Dubai | AED 5,000–6,450 /m² (over 60 floors: 6,000–7,500) | 5,000–6,450 | TT-TALL (shell and core) |
| Residential high-rise | AECOM [[8]](https://publications.aecom.com/MEH/static/69a84a66cc94f48d41d456bfc959f519/4714f9cc02b32c869d15d7378fcb142e.pdf) | 2024 handbook, Q3 2023 | Dubai | USD 1,900–3,000 /m² | 6,973–11,010 | AECOM |
| Residential high-rise | AECOM [[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf) | 2025 handbook, Q3 2024 | Dubai | USD 2,100–3,400 /m² | 7,707–12,478 | AECOM |
| Residential high-rise | C&B [[13]](https://flo.uri.sh/visualisation/22778655/embed?auto=1) | Q3 2025 | UAE | AED 5,750–8,840 (luxury branded 7,800–16,200) | 5,750–8,840 | C&B |
| Residential high-rise (G+40) | Stonehaven [[15]](https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf) | 2025 | UAE | AED 7,100–9,700 /m² | 7,100–9,700 | SH |
| Apartments (all) | Knight Frank [[16]](https://www.knightfrank.ae/newsroom/article/2025/9/uae-construction-landscape-h1-2025) | Q2 2025 | UAE | AED 4,300–9,500 per sqm | 4,300–9,500 | KF |
| Mid-rise apartments | AECOM [[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf) | Q3 2024 (Q3 2023: USD 1,200–1,800) | Dubai | USD 1,500–2,200 /m² | 5,505–8,074 | AECOM |
| Mid-rise apartments | C&B [[13]](https://flo.uri.sh/visualisation/22778655/embed?auto=1) | Q3 2025 | UAE | AED 4,050–6,600 | 4,050–6,600 | C&B |
| Mid-rise apartments (G+12) | Stonehaven [[15]](https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf) | 2025 | UAE | AED 5,500–7,200 (G+4: 4,200–6,000) | 5,500–7,200 | SH |
| Villas | T&T [[1]](https://assets.foleon.com/eu-central-1/de-uploads-7e3kk3/48604/uaemi_24_construction_cost_performance.58a8c5990842.pdf) | Q1 2024 | UAE | medium AED 4,950–6,050; prestige 10,800–13,200; townhouses 4,230–5,170 | as published | TT-MI24 |
| Villas | AECOM [[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf) | Q3 2024 (Q3 2023: USD 1,200–1,900) | Dubai | USD 1,400–2,500 /m² ("typical master plan community") | 5,138–9,175 | AECOM |
| Villas | C&B [[13]](https://flo.uri.sh/visualisation/22778655/embed?auto=1) | Q3 2025 | UAE | AED 3,830–16,510 (luxury branded 8,220–16,300) | as published | C&B |
| Villas | Stonehaven [[15]](https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf) | 2025 | UAE | standard 4,000–5,000; mid-market 4,900–8,500; luxury 8,400–18,200; super luxury 18,000–31,000 | as published | SH |
| Villas | Knight Frank [[16]](https://www.knightfrank.ae/newsroom/article/2025/9/uae-construction-landscape-h1-2025) | Q2 2025 | UAE | standard AED 4,200; high-end AED 11,000 per sqm | as published | KF |
| Offices | T&T [[1]](https://assets.foleon.com/eu-central-1/de-uploads-7e3kk3/48604/uaemi_24_construction_cost_performance.58a8c5990842.pdf) | Q1 2024 | UAE | CBD up to 20 floors (A-grade) AED 5,130–6,270; high-rise prestige 6,390–7,810 | as published | TT-MI24 |
| Offices | T&T [[2]](https://marketintelligence.turnerandtownsend.com/uaemi-2025/construction-cost-performance) | GCMI 2025 | Dubai / Abu Dhabi | CBD up to 20 floors AED 6,200 / 6,000 | as published | TT-GCMI |
| Offices 20–60 storeys | T&T [[4]](https://reports.turnerandtownsend.com/tall-buildings-construction-guide-2026/dubai) | 2025 | Dubai | AED 5,500–6,500 (over 60: 5,900–7,000) | as published | TT-TALL |
| High-rise office, shell and core | AECOM [[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf) | Q3 2024 (Q3 2023: USD 1,600–2,500) | Dubai | USD 1,800–3,100 /m² | 6,606–11,377 | AECOM |
| High-rise office, shell and core | C&B [[13]](https://flo.uri.sh/visualisation/22778655/embed?auto=1) | Q3 2025 | UAE | AED 5,960–9,260 | as published | C&B |
| High-rise office, shell and core | Stonehaven [[15]](https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf) | 2025 | UAE | AED 7,100–9,500 | as published | SH |
| Commercial buildings | Knight Frank [[16]](https://www.knightfrank.ae/newsroom/article/2025/9/uae-construction-landscape-h1-2025) | end H1 2025 | UAE | AED 5,500–7,300 psm | as published | KF |
| Retail mall | T&T [[1]](https://assets.foleon.com/eu-central-1/de-uploads-7e3kk3/48604/uaemi_24_construction_cost_performance.58a8c5990842.pdf) | Q1 2024 | UAE | large shopping centre incl. mall AED 5,310–6,490 | as published | TT-MI24 |
| Retail mall | AECOM [[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf) | Q3 2024 | Dubai | regional USD 1,700–1,900; super regional 1,700–2,200 | 6,239–8,074 | AECOM (excludes tenant fit-out) |
| Retail mall | C&B [[13]](https://flo.uri.sh/visualisation/22778655/embed?auto=1) | Q3 2025 | UAE | regional AED 5,110–6,600; large regional 5,850–8,100 | as published | C&B |
| Retail mall, shell and core | Stonehaven [[15]](https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf) | 2025 | UAE | regional AED 5,300–7,100; large regional 6,000–8,650 | as published | SH |
| Hotel 3-star / budget | T&T [[1]](https://assets.foleon.com/eu-central-1/de-uploads-7e3kk3/48604/uaemi_24_construction_cost_performance.58a8c5990842.pdf)[[2]](https://marketintelligence.turnerandtownsend.com/uaemi-2025/construction-cost-performance) | Q1 2024 / GCMI 2025 | UAE / Dubai and Abu Dhabi | AED 5,400–6,600 / AED 6,500 average | as published | TT-MI24 / TT-GCMI |
| Hotel 3-star / budget | AECOM, C&B, Stonehaven [[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf)[[13]](https://flo.uri.sh/visualisation/22778655/embed?auto=1)[[15]](https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf) | Q3 2024 / Q3 2025 / 2025 | Dubai / UAE / UAE | USD 2,000–2,300 / AED 6,600–8,840 / AED 7,000–9,450 | 7,340–8,441 / as published | AECOM / C&B / SH |
| Hotel 4-star / mid-market | AECOM, C&B, Stonehaven [[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf)[[13]](https://flo.uri.sh/visualisation/22778655/embed?auto=1)[[15]](https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf) | Q3 2024 / Q3 2025 / 2025 | Dubai / UAE / UAE | USD 2,300–3,200 / AED 7,880–10,640 / AED 8,850–12,180 | 8,441–11,744 / as published | AECOM / C&B / SH |
| Hotel 5-star / up-market | T&T [[1]](https://assets.foleon.com/eu-central-1/de-uploads-7e3kk3/48604/uaemi_24_construction_cost_performance.58a8c5990842.pdf)[[2]](https://marketintelligence.turnerandtownsend.com/uaemi-2025/construction-cost-performance) | Q1 2024 / GCMI 2025 | UAE / Dubai and Abu Dhabi | AED 8,820–10,780 / AED 10,500 average | as published | TT-MI24 / TT-GCMI |
| Hotel 5-star / up-market | AECOM, C&B, Stonehaven [[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf)[[13]](https://flo.uri.sh/visualisation/22778655/embed?auto=1)[[15]](https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf) | Q3 2024 / Q3 2025 / 2025 | Dubai / UAE / UAE | USD 3,200–4,600 / AED 10,640–16,920 / AED 12,000–17,500 | 11,744–16,882 / as published | AECOM / C&B / SH |
| Hotel resort | T&T, AECOM, C&B [[1]](https://assets.foleon.com/eu-central-1/de-uploads-7e3kk3/48604/uaemi_24_construction_cost_performance.58a8c5990842.pdf)[[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf)[[13]](https://flo.uri.sh/visualisation/22778655/embed?auto=1) | Q1 2024 / Q3 2024 / Q3 2025 | UAE / Dubai / UAE | AED 11,250–13,750 / USD 4,100–5,100 / AED 12,460–16,920 | 11,250–13,750 / 15,047–18,717 / as published | TT-MI24 / AECOM / C&B |
| Schools | T&T [[1]](https://assets.foleon.com/eu-central-1/de-uploads-7e3kk3/48604/uaemi_24_construction_cost_performance.58a8c5990842.pdf) | Q1 2024 | UAE | primary and secondary AED 5,760–7,040 | as published | TT-MI24 |
| Schools | AECOM [[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf) | Q3 2024 (Q3 2023: USD 1,500–2,300) | Dubai | USD 1,600–2,700 /m² | 5,872–9,909 | AECOM (fixed fit-out only) |
| Schools | C&B, Stonehaven [[13]](https://flo.uri.sh/visualisation/22778655/embed?auto=1)[[15]](https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf) | Q3 2025 / 2025 | UAE | AED 5,430–8,410 / traditional 6,000–7,900, moderate 7,800–9,600, progressive 9,250–12,500 | as published | C&B / SH |
| Hospital | T&T [[1]](https://assets.foleon.com/eu-central-1/de-uploads-7e3kk3/48604/uaemi_24_construction_cost_performance.58a8c5990842.pdf) | Q1 2024 | UAE | general hospital AED 10,800–13,200 | as published | TT-MI24 |
| Hospital | AECOM [[8]](https://publications.aecom.com/MEH/static/69a84a66cc94f48d41d456bfc959f519/4714f9cc02b32c869d15d7378fcb142e.pdf)[[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf) | Q3 2023 / Q3 2024 | Dubai | district hospital USD 2,400–4,100 / 2,700–4,500 | 8,808–15,047 / 9,909–16,515 | AECOM (excludes medical equipment) |
| Car parks | AECOM, Stonehaven [[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf)[[15]](https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf) | Q3 2024 / 2025 | Dubai / UAE | multi-storey USD 700–1,100, basement 1,100–1,600 / multi-storey AED 2,500–3,600, basement 3,600–4,500 (BUA, built-up area) | 2,569–4,037, 4,037–5,872 / as published | AECOM / SH |
| Office fit-out (medium) | AECOM, C&B, Stonehaven [[9]](https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf)[[13]](https://flo.uri.sh/visualisation/22778655/embed?auto=1)[[15]](https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf) | Q3 2024 / Q3 2025 / 2025 | Dubai / UAE / UAE | USD 1,800–2,300 / AED 6,280–7,670 / AED 5,900–7,200 | 6,606–8,441 / as published | AECOM / C&B / SH |
| Infrastructure | Stonehaven [[15]](https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf) | 2025 | UAE | highways AED 1,250–5,000 per metre; bridges 8,028–15,645 /m²; infrastructure and utilities AED 160–450 per m² of site area | as published | SH |

**City averages, rankings and gated reports**

| Source | Edition / date | Dubai | Abu Dhabi | Access |
|---|---|---|---|---|
| T&T ICMS 2024 [[7]](https://www.agbi.com/analysis/construction/2024/06/building-construction-costs-dubai-riyadh-doha-abu-dhabi/) | 2024 | USD 1,874 /m² average | USD 1,844 /m² | Seen only as search-result text from AGBI (page 403) |
| T&T GCMI 2025 [[2]](https://marketintelligence.turnerandtownsend.com/uaemi-2025/construction-cost-performance) | 2025 | USD 1,926 /m², rank 74 | USD 1,872 /m², rank 76 | Public web page |
| T&T GCMI 2026 [[5]](https://turnerandtownsend.com/insights/global-construction-market-intelligence-2026/)[[6]](https://publications.turnerandtownsend.com/global-construction-market-intelligence-2026/methodology) | 8 Jul 2026, data for Q1 2026 | not found on the public pages | not found | Methodology is public; no UAE figures on the pages read |
| Arcadis International Construction Costs 2025 [[18]](https://connect.arcadis.com/international-construction-costs-report-2025) | 2025 | n/a | n/a | Behind a form (email, name, job title, company) |
| Arcadis International Construction Costs 2026 [[19]](https://en.aletihad.ae/amp/news/business/4678838/abu-dhabi--dubai-rank-among-world-s-most-cost-competitive-co)[[20]](https://www.albayan.ae/economy/business/1525453) | press 14 Jul 2026 | rank 68, index 99 (Amsterdam = base) | rank 69, index 99 | Per-m² figures not public in the articles |
| AECOM handbook 2026 (20th edition) [[11]](https://meconstructionnews.com/66251/aecom-launches-20th-edition-of-its-middle-east-property-construction-handbook/amp) | early 2026 | not found | not found | Announced; no public PDF found. The publications page lists 2025 as the latest ([[10]](https://publications.aecom.com/MEH/)) |
| Compass Project Consulting H1 2026 [[21]](https://compass-pc.com/news-blog/h1-2026-construction-costs-benchmarks)[[22]](https://meconstructionnews.com/68769/geopolitical-uncertainty-sharpens-focus-on-construction-costs-across-ksa-and-the-uae-says-compass) | 14 Aug 2026 | ranges behind a download pop-up | same | Not read |
| RLB, Linesight, Cushman & Wakefield, JLL, Colliers | — | not found | not found | No public UAE per-m² cost guide found before the search budget ran out |

**How the sources differ (from the tables above)**

- For the same building type, Turner & Townsend is the lowest source and AECOM the highest. Take Dubai high-rise residential. The T&T 2025 average is AED 5,500. AECOM's Q3 2024 range is AED 7,707–12,478. The AECOM low is 40 % above the T&T average. None of the sources explains the gap. The basis notes show part of it. AECOM's residential rate includes fit-out, MEP and lifts. T&T's tall-building rate is shell and core on GIA, excluding finishes. T&T's GCMI includes finishes but excludes external works, fees and parking.
- Dates differ by up to two years. AECOM 2024 = Q3 2023 costs. AECOM 2025 = Q3 2024 costs. T&T MI = Q1 2024. Stonehaven = early 2025. Knight Frank = Q2 2025. C&B = Q3 2025. Within one publisher, AECOM's Dubai high-rise range rose from USD 1,900–3,000 to USD 2,100–3,400 between the two editions, which is +11 % at the low end and +13 % at the high end. T&T's tall-building residential range rose from AED 3,800–4,800 (2020) to AED 5,000–6,450 (2025).
- Only Stonehaven states GFA outright. T&T GCMI states a gross, outer-face-of-wall measure. The T&T tall-buildings guide uses GIA. NRM 1 rates are per m² of GIFA (gross internal floor area), and NRM 1's cost/m² of GIFA excludes main contractor preliminaries and OH&P ([[42]](https://www.rics.org/content/dam/ricsglobal/documents/standards/NRM-1_Oct2022_Update.pdf)). AECOM and T&T GCMI rates include them.
- City split: only T&T publishes Dubai and Abu Dhabi separately. The 2025 averages are the same for apartments (AED 5,500) and differ for offices (6,200 against 6,000) and car showrooms (9,750 against 8,750) ([[2]](https://marketintelligence.turnerandtownsend.com/uaemi-2025/construction-cost-performance)).

## Detail

### ARGUS Developer conventions

I found no public ARGUS Developer manual from Altus Group. I therefore inferred the conventions from published ARGUS Developer printouts in UK council viability documents, and I checked them by recalculation. The product page confirms the scope. ARGUS Developer evaluates "the residual land value of a development site". It lets users "Sensitise costs, revenues, timing and interest rates". It models "flexible debt, equity and JV structures". It also forecasts cash flows and updates them with actuals ([[28]](https://www.altusgroup.com/solutions/argus-developer)).

**Residual appraisal structure.** The Runnymede appendix (ARGUS Developer 8.20.003, dated 07/01/2025) prints the standard summary in this order ([[25]](https://www.runnymede.gov.uk/downloads/file/2828/appendix-2-rbc-current-methodology)):

1. REVENUE: sales valuation (units, ft², sales rate per ft², gross sales), then NET REALISATION £5,951,700.
2. OUTLAY, ACQUISITION COSTS: "Residualised Price" £1,820,630 and Stamp Duty 4.00 %. "Residualised" means the land price was solved for, not entered.
3. CONSTRUCTION COSTS (ft² × build rate), PROFESSIONAL FEES (architect 12.00 %), MARKETING & LETTING (marketing 3.00 %).
4. FINANCE: a timescale of Pre-Construction 3 months, Construction 12 and Sale 6, with start months; "Debit Rate 6.750%, Credit Rate 0.000% (Nominal)"; then finance split into Land £153,856 and Construction £79,519.
5. TOTAL COSTS £4,951,814, PROFIT £999,886, then Performance Measures: Profit on Cost% 20.19 %, Profit on GDV% 16.80 %, "IRR% (without Interest)" 32.69 %.

I recalculated both ratios. 999,886 / 4,951,814 = 20.19 % and 999,886 / 5,951,700 = 16.80 % ([outputs/00_argus_decode.md](assets/C14/outputs/00_argus_decode.md)). So ARGUS **profit on cost uses total costs including finance**, and profit on GDV uses net realisation. The Broxbourne appraisal (ARGUS Developer 6.00.008, 2018, old) adds three more measures: Profit on NDV% (net development value), Development Yield% (on rent) and Equivalent Yield% (Nominal and True). It also adds a disposal-fee block (sales agent 1.5 %, legal fee per unit) ([[26]](https://www.broxbourne.gov.uk/downloads/file/1640/financial-viabiity-appraisal)).

**Cash-flow timing and finance method (measured).** Broxbourne's phased cash flow prints monthly costs, a "Debit Rate 6.50%" row, a "Credit Rate 0.10%" row, "Finance Costs (All Sets)" and "Cumulative Total C/f Monthly". I put its first nine months of costs into my finance loop and compared the result with the printed interest ([[26]](https://www.broxbourne.gov.uk/downloads/file/1640/financial-viabiity-appraisal), [appraisal.py `verify_argus`](assets/C14/appraisal.py)):

| compounding in my loop | interest, months 1–9 | max difference from printed |
|---|---|---|
| monthly | 0 9,481 9,532 9,584 9,636 9,744 9,993 12,554 14,740 | 123 |
| every 3 months | 0 9,481 9,481 9,583 9,583 9,640 9,991 12,498 14,617 | **0** (cumulative within 1) |
| printed by ARGUS | 0 9,481 9,481 9,583 9,583 9,640 9,991 12,498 14,617 | — |

By hand, month-2 interest is 1,750,298 × 6.50 % / 12 = 9,480.78, printed as 9,481. This file's conventions are therefore as follows:

- "Nominal" means the annual rate divided by 12 for each month.
- Interest is charged on the balance brought forward, so a cost starts to bear interest in the month after it is incurred.
- Accrued interest is capitalised every three months (quarterly compounding).
- Interest is rolled up, not paid.
- A credit rate applies to positive balances.

The compounding setting itself is not printed. I inferred it from the match. A C# port of the loop gives the same result ([DevFinanceCheck.cs](assets/C14/DevFinanceCheck.cs), run with .NET 8.0.427 on Linux: `k=3: ... max |diff| vs ARGUS = 0`):

```csharp
for (int t = 0; t < n; t++)
{
    if (t > 0)
    {
        double i = ib * (ib < 0 ? debit : credit) / 12.0;  // nominal rate / 12
        interest[t] = -i; accrued += i;
    }
    cum[t] = prev + net[t] - interest[t]; prev = cum[t];
    ib += net[t];                                          // bears interest from next month
    if ((t + 1) % k == 0) { ib += accrued; accrued = 0; }  // k = 1 monthly, 3 quarterly
}
```

**Rolled-up compared with paid interest.** Both printouts roll interest up into the debt and deduct it from proceeds at the end. That is the "100 per cent financing ... rolled up" practice RICS describes ([[37]](https://www.rics.org/content/dam/ricsglobal/documents/to-be-sorted/Valuation%20of%20development%20property_ready%20for%20approvals.pdf) B1.2.8.3). A Braintree viability seminar says the finance cost is "calculated automatically by the Argus programme, based on the finance rate, development duration and cashflow timing". I saw this only as search-result text ([[27]](https://www.braintree.gov.uk/downloads/file/1394/viability-technical-seminar-galliard-homes)).

**S-curve distribution.** RICS lists straight-line and S-curve as the two common cost shapes in cash-flow models ([[37]](https://www.rics.org/content/dam/ricsglobal/documents/to-be-sorted/Valuation%20of%20development%20property_ready%20for%20approvals.pdf) B1.2.4.4). I could not verify ARGUS Developer's own list of distribution options or the formula behind its "S-curve" from Altus documentation.

**Profit on cost compared with profit on GDV.** Profit on cost = profit / (all costs including finance and land). Profit on GDV = profit / net realisation. A fixed profit on cost of 20 % equals 16.7 % on GDV, because 0.20 / 1.20 = 0.1667. The Runnymede file shows 20.19 % and 16.80 %. UK planning guidance quotes the hurdle on GDV: "an assumption of 15-20% of gross development value (GDV) may be considered a suitable return" for plan making ([[38]](https://www.gov.uk/guidance/viability), paragraph 019, updated 16 Dec 2025).

### EstateMaster DF conventions

ARGUS EstateMaster is Altus's Australian-origin product, and DF is its Development Feasibility module. The product page lists "Residual land values", "KPI insights", "Scenario analysis", "Risk assessment", "Project funding" and "Professional reporting" ([[33]](https://www.altusgroup.com/argus/products/argus-estatemaster/development-feasibility)). Altus's feasibility guide, written for EstateMaster users, sets out the conventions:

- **Development margin = Net profit / Total development cost.** Total development cost is estimated "including interest on 100% borrowings" ([[29]](https://www.altusgroup.com/featured-insights/property-development-feasibility/part-1-study-fundamentals/), 16 Jul 2026). This is the same ratio as ARGUS profit on cost and RICS "profit on cost" ([[37]](https://www.rics.org/content/dam/ricsglobal/documents/to-be-sorted/Valuation%20of%20development%20property_ready%20for%20approvals.pdf) glossary).
- **RLV:** "the maximum a developer can pay for a site and still hit a target profit". The formula given is "Revenue – Costs (including developer's margin, excluding land) = Residual Land Value" ([[31]](https://www.altusgroup.com/featured-insights/property-development-feasibility/part-3-land-valuations/), 11 Aug 2026).
- **IRR:** "the discount rate at which the net present value equals zero" ([[29]](https://www.altusgroup.com/featured-insights/property-development-feasibility/part-1-study-fundamentals/)).
- **Construction loan:** staged drawdowns "from slab to completion". Interest is not paid during construction: "the interest is added to the amount you owe at the end of each month", which is monthly capitalisation. The guide also defines LVR (loan-to-value ratio) = loan / value, and lists "Brokerage and loan fees" as a finance cost ([[32]](https://www.altusgroup.com/featured-insights/property-development-feasibility/part-5-financing/), 9 Jan 2025).
- **S-curve:** a DF overview video transcript says users choose whether costs follow an S-curve, defined on its own tab, and that DF then works out the financing. I saw this only as search-result text, because the transcript returned 403 ([[35]](https://amara.org/subtitles/tgh3DmtsU9tC/en/11/download/EstateMaster%20%20%20Development%20Feasibility%20DF%20overview.en.sbv)).
- **Probabilistic analysis:** ARGUS EstateMaster "supports advanced sensitivity analysis and Monte Carlo simulations, revealing the probability ranges for key outcomes" (promotional article, 12 Jan 2026) ([[34]](https://content.readymedia.com.au/article/navigating-market-uncertainty-with-confidence-the-new-tool-empowering-property-developers)).
- **Hurdles in practice:** an NSW viability report by HillPDA used EstateMaster with an 18 % IRR and a 20 % development margin as hurdles. I saw this only as search-result text, because the download failed ([[52]](https://apps.planningportal.nsw.gov.au/prweb/PRRestService/DocMgmt/v1/PublicDocuments/DATA-WORKATTACH-FILE%20PEC-DPE-EP-WORK%20PP-2022-2519!20250424T011054.904%20GMT)).

Term map for Studio's labels:

| Concept | ARGUS Developer label | EstateMaster / Altus guide label | RICS term |
|---|---|---|---|
| Land price solved for a target | Residualised Price [[25]](https://www.runnymede.gov.uk/downloads/file/2828/appendix-2-rbc-current-methodology) | Residual land value [[31]](https://www.altusgroup.com/featured-insights/property-development-feasibility/part-3-land-valuations/) | Residual site value / residual land value [[37]](https://www.rics.org/content/dam/ricsglobal/documents/to-be-sorted/Valuation%20of%20development%20property_ready%20for%20approvals.pdf) |
| Profit / total costs incl. finance | Profit on Cost% | Development margin [[29]](https://www.altusgroup.com/featured-insights/property-development-feasibility/part-1-study-fundamentals/) | Profit on cost |
| Profit / sales value | Profit on GDV%, Profit on NDV% [[26]](https://www.broxbourne.gov.uk/downloads/file/1640/financial-viabiity-appraisal) | not verified | Profit on value (on NDV) |
| Return before finance | IRR% (without Interest) | IRR (project) | IRR, "a project return, i.e. before finance" (7.2.4) |

### RICS guidance

**Valuation of development property** (1st edition, October 2019, effective 1 February 2020; first issued as a guidance note and now an RICS professional standard). It is to be read with the Red Book, especially IVS 410 ([[36]](https://www.rics.org/profession-standards/rics-standards-and-guidance/sector-standards/valuation-standards/valuation-of-development-property)[[37]](https://www.rics.org/content/dam/ricsglobal/documents/to-be-sorted/Valuation%20of%20development%20property_ready%20for%20approvals.pdf)). Points that matter for software:

- The residual formula is "gross development value (GDV) - total development costs (including profit) = residual land value" (6.1.1). The residual can instead be the profit when the land price is fixed (6.1.2).
- There are two applications. The **DCF (discounted cash flow)** application gives "the NPV will be a current estimate of the residual land value", with profit expressed as IRR (6.2.1–6.2.2). The **basic residual** application is the static version (6.3).
- DCF needs period-by-period assumptions, "which might be monthly or quarterly" (6.2.4). Nominal cash flows need nominal rates and real cash flows need real rates. Different discount rates for different parts of the cash flow are acceptable (6.2.5).
- "The simplest form of risk analysis is sensitivity analysis" (7.1.4). Scenario modelling comes next (7.1.5), then simulation with probabilities. The valuer must set out the rational basis for the chosen variations and probabilities (7.1.6).
- Finance: "appraisal theory is clear that interest and finance on borrowings should not appear in a formal discounted cash flow" (B1.2.8.1). In practice it does, with "100 per cent financing of both costs and land value ... rolled up through the development" (B1.2.8.3). Interest on land runs over the whole development period (7.2.3).
- There are three ways to estimate building-cost interest (B2.2.2.3): a full cash flow; half the costs over the whole period; or all the costs over half the period. These are measured below.
- Contingency is "usually reflected as a percentage of the building contract sum". It may double-count risk that is already in a risk-adjusted discount rate (B1.2.5).

**Assessing viability in planning under the NPPF 2019 for England.** The RICS page I tried returned 404, so I did not verify this guidance's edition or content ([[39]](https://www.rics.org/profession-standards/rics-standards-and-guidance/sector-standards/land-standards/assessing-viability-in-planning-under-the-national-planning-policy-framework-2019-for-england)). The government guidance it supports is public. Benchmark land value is "existing use value plus" (EUV+), and a 15–20 % of GDV return "may be considered suitable" for plan making ([[38]](https://www.gov.uk/guidance/viability), paragraphs 014 and 019). This applies to England, not the UAE. It matters only because UK-trained appraisers bring these habits.

**Red Book.** RICS Valuation – Global Standards, 2025 edition, effective 31 January 2025, incorporating the IVS (International Valuation Standards) also effective 31 January 2025 ([[40]](https://www.rics.org/profession-standards/rics-standards-and-guidance/sector-standards/valuation-standards/red-book/red-book-global)). If Studio outputs are used for a Red Book valuation, the valuer, not the software, owns the method and assumptions.

**NRM 1 (order of cost estimates).** The current edition is October 2021, published 28 Oct 2021 and reissued October 2022 as practice information ([[41]](https://www.rics.org/profession-standards/rics-standards-and-guidance/sector-standards/construction-standards/nrm)). Its Table 2.1 sets the order of a cost estimate ([[42]](https://www.rics.org/content/dam/ricsglobal/documents/standards/NRM-1_Oct2022_Update.pdf)):

| # | NRM 1 constituent | Where the benchmark guides put it |
|---|---|---|
| 1–2 | Facilitating works, building works (GIFA × rate or functional units) | NRM 1 "cost/m² of GIFA" covers item 2 only |
| 3–6 | + main contractor preliminaries, + OH&P = works cost estimate | Included in AECOM and T&T GCMI rates. T&T 2025: Dubai prelims 12 % (2,500 m² job) to 14 % (50,000 m²), OH&P 12 % to 10 % ([[2]](https://marketintelligence.turnerandtownsend.com/uaemi-2025/construction-cost-performance)) |
| 7–10 | + project and design team fees, + other project costs = base cost estimate (no risk, no inflation) | Excluded by every benchmark source above |
| 11–12 | + risk allowances (design, construction, employer change, employer other) = cost limit excl. inflation | Excluded (AECOM excludes contingencies) |
| 13–16 | + tender inflation, + construction inflation = cost limit incl. inflation | Excluded (Stonehaven excludes inflation) |
| 17 | VAT assessment | Excluded |

So a Studio rate library must say which NRM 1 line each rate stops at. An NRM 1 building-works rate taken at face value from an all-in benchmark would double-count preliminaries and OH&P, which add about 25 % in Dubai on T&T's 2025 figures.

### Residual land value method

The method is the RICS formula above. In a cash flow, land is solved, not entered, because land drives its own acquisition fees, arrangement fee and interest. My solver finds the land price L where profit − target × total costs = 0, using Brent's method on a bracket of ±GDV. This is the Studio equivalent of ARGUS's "Residualised Price". Two measured results from the worked example ([outputs/02_base_appraisal.md](assets/C14/outputs/02_base_appraisal.md)):

| Method | Target | RLV, AED |
|---|---|---|
| ARGUS-style: 100 % debt at 7.34 %, profit on cost | 20 % on cost | 76,442,533 |
| RICS DCF: no finance lines, NPV of project flows at target IRR = 0 | 15 % IRR | 86,280,983 |
| RICS DCF | 20 % IRR | 66,233,500 |

The two methods agree when the DCF target equals the project IRR implied by the ARGUS-style land price (17.32 %). The reported "land value" therefore depends on which convention a user picks, and Studio should label it.

### IRR and NPV

**Definitions.** RICS defines IRR as the rate at which all future project cash flows, discounted, give an NPV of zero. It defines NPV as the sum of the discounted net cash flows ([[37]](https://www.rics.org/content/dam/ricsglobal/documents/to-be-sorted/Valuation%20of%20development%20property_ready%20for%20approvals.pdf) glossary). numpy-financial's `irr` returns the *periodic* rate r that solves Σ vₜ/(1+r)ᵗ = 0. It finds the roots of the polynomial with `np.roots`. When there are several real roots, its default `_irr_default_selection` keeps the roots whose sign matches the larger total, then returns the one smallest in magnitude. I read this in the installed version 1.1.0; it is also in the public source ([[47]](https://github.com/numpy/numpy-financial/blob/main/numpy_financial/_financial.py)). Excel's XIRR discounts each payment by its actual date on "a 365-day year". It starts from a guess of 10 %, iterates until accurate "within 0.000001 percent", and returns #NUM! after 100 tries or if there is no positive and negative flow ([[46]](https://support.microsoft.com/en-us/office/xirr-function-de1242ec-6477-445b-b11b-a303ad9adc9d)).

**Periodic compared with XIRR (measured** on the worked example's unfinanced monthly flows, [outputs/09_irr_conventions.md](assets/C14/outputs/09_irr_conventions.md)):

| Measure | Value |
|---|---|
| Monthly IRR | 1.3401 % per month |
| × 12 (nominal annual) | 16.08 % |
| (1 + r)¹² − 1 (effective annual) | 17.3214 % |
| XIRR, first-of-month dates, 365-day year | 17.3248 % |

Quoting 12 × the monthly IRR understates the effective return by 1.24 points. XIRR and the effective annual rate differ only by calendar day counts. Studio should report the effective annual rate and name the convention.

**Multiple IRRs.** The number of IRRs "can never be more than the number of changes in sign of cash flow" (Descartes' rule of signs). The modified IRR (MIRR) is a common remedy ([[48]](https://en.wikipedia.org/wiki/Internal_rate_of_return), third party). UAE off-plan schemes produce exactly this pattern: buyer deposits in (+), construction out (−), handover balance in (+). Measured example, yearly flows +30, −120, +100:

| Check | Result |
|---|---|
| All real IRRs (np.roots) | 18.35 % and 181.65 % |
| numpy_financial.irr returns | 18.35 % |
| NPV at 0 % / 10 % / 50 % / 250 % | +10.00 / +3.55 / −5.56 / +3.88 |

By hand: 30g² − 120g + 100 = 0 gives g = (120 ± √2400)/60, so g = 1.1835 or 2.8165. A single "IRR" for such a project is misleading. Studio should detect more than one sign change, list every root, and lead with NPV.

### S-curves

RICS describes the S-curve as costs that are "quite small at the beginning ..., relatively accelerate in the middle and reduce towards the end". It says the shape may need advice from construction professionals ([[37]](https://www.rics.org/content/dam/ricsglobal/documents/to-be-sorted/Valuation%20of%20development%20property_ready%20for%20approvals.pdf) B1.2.4.4). Formulas implemented in [appraisal.py](assets/C14/appraisal.py). Here x is the fraction of construction time elapsed and F(x) is the cumulative fraction of cost spent:

| Curve | F(x) | Notes |
|---|---|---|
| Straight line | x | The RICS alternative to an S-curve |
| Sine | (1 − cos πx) / 2 | Symmetric, zero slope at both ends |
| Beta(a, b) CDF | regularised incomplete beta function, from the density Γ(a+b)x^(a−1)(1−x)^(b−1) / (Γ(a)Γ(b)) ([[50]](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html)) | a < b front-loads, a > b back-loads |
| Beta(2, 2) | 3x² − 2x³ | Γ(4)/(Γ(2)Γ(2)) = 6, and ∫₀ˣ 6t(1−t) dt = 3x² − 2x³ |
| DHSS (Hudson 1978) | x + Cx² − Cx − (6x³ − 9x² + 3x)/K | Formula as commonly reproduced. I did not open the original paper or its published C, K tables (not verified) |

Two properties of the DHSS form, derived and checked numerically:

- With C = 0 and K = 3 it reduces exactly to 3x² − 2x³, the Beta(2,2) curve.
- F′(x) is a concave quadratic. Spending therefore never goes negative on [0, 1] only if F′(0) = 1 − C − 3/K ≥ 0 and F′(1) = 1 + C − 3/K ≥ 0. That means **K ≥ 3 and |C| ≤ 1 − 3/K**. My first test, with C = 0.5 and K = 3, gave F(0.1) = −0.017, a negative spend. Studio must validate DHSS parameters.

The task also names Bromilow, and Kenley and Wilson's logit model is another published curve. I did not open either source, so I give no formulas from them (not verified).

Cumulative values ([outputs/01_s_curves.md](assets/C14/outputs/01_s_curves.md), extract):

| x | straight | sine | Beta(2,2) = DHSS C=0, K=3 | Beta(2,3) | Beta(3,2) | DHSS C=−0.2, K=5 | DHSS C=+0.2, K=5 |
|---|---|---|---|---|---|---|---|
| 0.2 | 0.200 | 0.095 | 0.104 | 0.181 | 0.027 | 0.174 | 0.110 |
| 0.5 | 0.500 | 0.500 | 0.500 | 0.688 | 0.312 | 0.550 | 0.450 |
| 0.8 | 0.800 | 0.905 | 0.896 | 0.973 | 0.819 | 0.890 | 0.826 |

**Effect on finance (measured,** [outputs/06](assets/C14/outputs/06_curve_compounding_offplan.md)). Symmetric curves (straight line, sine, Beta(2,2)) give almost the same finance cost: AED 44.10 m, 44.00 m and 44.01 m. Their average spend date is the same, mid-construction. Skewed curves matter. Front-loaded Beta(2,3) gives AED 46.97 m and back-loaded Beta(3,2) gives AED 41.05 m. That moves RLV between AED 73.6 m and 79.3 m, about ±3.7 %. The shape choice matters less than its skew.

### Finance costs

**Land finance.** RICS adds interest on land "over the whole of the development period" (7.2.3) ([[37]](https://www.rics.org/content/dam/ricsglobal/documents/to-be-sorted/Valuation%20of%20development%20property_ready%20for%20approvals.pdf)). ARGUS prints land and construction finance as separate lines (Land £153,856, Construction £79,519) ([[25]](https://www.runnymede.gov.uk/downloads/file/2828/appendix-2-rbc-current-methodology)). In my worked example land is bought in month 0. Interest on the land, its acquisition costs and the arrangement fee starts at AED 501,549 in month 1, on AED 82.0 m.

**Construction loan drawdown.** Drawdowns are staged, and interest is added monthly ([[32]](https://www.altusgroup.com/featured-insights/property-development-feasibility/part-5-financing/)). The three RICS approximations compared with a cash flow, for construction-related costs of AED 187.1 m at 7.34 % (measured):

| Method | Interest, AED |
|---|---|
| Cash flow, Beta(2,2), monthly compounding, pre-construction fees from month 1 | 17,818,404 |
| RICS: half the costs over the whole 30-month period | 18,780,572 |
| RICS: all the costs over half the period | 17,922,236 |

The "half the period" shortcut lands within 0.6 % of the S-curve cash flow. The "half the costs" shortcut overstates interest by 5.4 %.

**Compounding period (measured).** On the same project, monthly compounding gives AED 44.01 m. Quarterly, as in the decoded ARGUS file, gives AED 43.78 m. Annual gives AED 42.95 m. RLV changes by at most AED 1.0 m. The setting must be visible and must match the lender's terms.

**Arrangement and other finance fees.** RICS lists "fees regarding the arrangement of development funding", the lender's monitoring surveyor and legal fees as costs ([[37]](https://www.rics.org/content/dam/ricsglobal/documents/to-be-sorted/Valuation%20of%20development%20property_ready%20for%20approvals.pdf) B1.2.6). Altus lists "brokerage and loan fees" ([[32]](https://www.altusgroup.com/featured-insights/property-development-feasibility/part-5-financing/)). **I found no published UAE arrangement-fee percentage or lender margin.** The worked example assumes 1 % and EIBOR + 3.00 %.

**Rate benchmarks with dates:**

| Benchmark | Value | Date | Source |
|---|---|---|---|
| UAE 3-month interbank rate (EIBOR) | 4.34 % (previous day 4.30 %) | 30 Oct 2026 | Trading Economics, citing the Central Bank of the UAE (secondary) [[43]](https://tradingeconomics.com/united-arab-emirates/interbank-rate) |
| UAE policy interest rate | 3.90 % | Oct 2026 | same [[43]](https://tradingeconomics.com/united-arab-emirates/interbank-rate) |
| CBUAE EIBOR page | not read (Cloudflare 403) | — | [[44]](https://www.centralbank.ae/en/forex-eibor/eibor-rates/) |
| US federal funds target range (the AED trades at 3.67 per USD [[12]](https://curriebrown.foleon.com/archive/uae-2025-q3/building-asset-costs)) | 4.75–5.00 % (19 Sep 2024), 4.50–4.75 (8 Nov 2024), 4.25–4.50 (19 Dec 2024), 4.00–4.25 (18 Sep 2025), 3.75–4.00 (30 Oct 2025), 3.50–3.75 (11 Dec 2025), 3.75–4.00 (17 Sep 2026, +25 bp) | as shown | Federal Reserve [[45]](https://www.federalreserve.gov/monetarypolicy/openmarket.htm) |
| UK ARGUS examples (not UAE) | debit 6.75 %, credit 0 % (Jan 2025); debit 6.50 %, credit 0.10 % (2018) | as shown | [[25]](https://www.runnymede.gov.uk/downloads/file/2828/appendix-2-rbc-current-methodology)[[26]](https://www.broxbourne.gov.uk/downloads/file/1640/financial-viabiity-appraisal) |

**UAE off-plan funding (measured, illustrative).** The ARGUS and RICS convention is 100 % debt, with sales on completion. If a tower is sold off-plan, buyers pay instalments during construction, which changes the funding. I modelled an assumed plan of 10 % at launch, 30 % spread over construction and 60 % at handover, applying receipts against the debt. Finance fell from AED 44.0 m to 26.6 m, peak debt from AED 315.3 m to 164.1 m, and RLV rose from AED 76.4 m to 93.1 m (+22 %). This ignores escrow rules that limit how buyer money can be used. I did not verify those rules (see Risks).

### UAE cost benchmarks: dates, escalation and normalisation

Benchmarks dated 2023 to 2025 must be indexed to the appraisal date. Published escalation figures:

| Item | Figure | Source |
|---|---|---|
| UAE tender price inflation (TPI) | 1.9 % in 2024; 3.3 % forecast for 2025 | Stonehaven, via T&T [[2]](https://marketintelligence.turnerandtownsend.com/uaemi-2025/construction-cost-performance)[[15]](https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf) |
| T&T inflation (GCMI 2025) | Dubai 6.0 % (2024), 5.0 % (2025), 4.0 % (2026); Abu Dhabi 5.0 % each year | [[2]](https://marketintelligence.turnerandtownsend.com/uaemi-2025/construction-cost-performance) |
| UAE survey respondents, 2024–2025 | "3-5% growth, especially in the mixed-use/residential market" | [[3]](https://marketintelligence.turnerandtownsend.com/uaemi-2025/construction-market-outlook) |
| Currie & Brown | 3–4 % a year, 1–2 % a quarter (Q3 2025); about 3 % for 2026 | [[12]](https://curriebrown.foleon.com/archive/uae-2025-q3/building-asset-costs)[[14]](https://curriebrown.foleon.com/group/global-cost-report-2026/middle-east) |
| Currie & Brown 2026 material moves | cement +16 %, concrete +10 %, reinforcement steel +8 % since January | [[23]](https://www.zawya.com/en/projects/uae-construction-market-holds-firm-as-delivery-landscape-shifts-says-expert-1459393) |
| Arcadis 2026 | Abu Dhabi 3.5–4.5 % through end of 2026 | [[19]](https://en.aletihad.ae/amp/news/business/4678838/abu-dhabi--dubai-rank-among-world-s-most-cost-competitive-co) |
| Dubai construction cost index | +5.2 % year on year, Q1 2026 | AGBI, search-result text only, not verified [[24]](https://www.agbi.com/real-estate/2026/07/rising-costs-squeeze-uae-real-estate-margins/) |
| Compass H1 2026 | UAE conditions "do not yet justify an upward adjustment" to benchmark rates | [[22]](https://meconstructionnews.com/68769/geopolitical-uncertainty-sharpens-focus-on-construction-costs-across-ksa-and-the-uae-says-compass) |

To normalise a rate:

1. Convert the currency (AED 3.67 per USD).
2. Convert the area basis (GFA, GIA or GIFA).
3. Mark what the rate includes against the NRM 1 lines: preliminaries and OH&P, fit-out, basements and podiums, external works.
4. Index from the source's data date to the appraisal start.

The sources disagree on 2026 escalation, from "no upward adjustment" to +5.2 %. Studio should make escalation a user input with these figures as cited presets.

### Sensitivity presentation

RICS sets out the hierarchy: sensitivity, then scenarios, then simulation, with the basis stated ([[37]](https://www.rics.org/content/dam/ricsglobal/documents/to-be-sorted/Valuation%20of%20development%20property_ready%20for%20approvals.pdf) 7.1.4–7.1.6). ARGUS Developer sensitises costs, revenues, timing and interest rates ([[28]](https://www.altusgroup.com/solutions/argus-developer)). Altus's guide says sensitivity analysis "helps you understand how changes to individual inputs might affect the feasibility" ([[30]](https://www.altusgroup.com/featured-insights/property-development-feasibility/part-2-risk-and-return/)). EstateMaster adds Monte Carlo ([[34]](https://content.readymedia.com.au/article/navigating-market-uncertainty-with-confidence-the-new-tool-empowering-property-developers)). A tornado diagram is a horizontal bar chart sorted so that "the largest bar appears at the top". It suits deterministic one-way sensitivity ([[49]](https://en.wikipedia.org/wiki/Tornado_diagram), third party). All tables below are measured on the worked example.

**Two-way table: RLV (AED million) against sale price and build cost** ([outputs/04](assets/C14/outputs/04_two_way_sensitivity.md))

| RLV, AED m | price −10 % (1,476 psf) | −5 % (1,558) | base (1,640) | +5 % (1,722) | +10 % (1,804) |
|---|---|---|---|---|---|
| build −10 % (AED 4,950/m²) | 68.8 | 80.5 | 92.3 | 104.0 | 115.8 |
| build −5 % (5,225) | 60.9 | 72.6 | 84.4 | 96.1 | 107.8 |
| **build base (5,500)** | 53.0 | 64.7 | **76.4** | 88.2 | 99.9 |
| build +5 % (5,775) | 45.0 | 56.8 | 68.5 | 80.3 | 92.0 |
| build +10 % (6,050) | 37.1 | 48.9 | 60.6 | 72.3 | 84.1 |

**The same grid as profit on cost, with land fixed at AED 76.4 m.** This is the view a developer who has already bought the land needs.

| Profit on cost | price −10 % | −5 % | base | +5 % | +10 % |
|---|---|---|---|---|---|
| build −10 % | 16.0 % | 22.1 % | 28.3 % | 34.4 % | 40.4 % |
| build base | 8.4 % | 14.2 % | **20.0 %** | 25.7 % | 31.4 % |
| build +10 % | 1.8 % | 7.2 % | 12.7 % | 18.1 % | 23.5 % |

**Tornado: one-way RLV swings, sorted** ([outputs/05](assets/C14/outputs/05_tornado.md), base AED 76.4 m)

| Input (downside / upside) | Downside, AED m | Upside, AED m | Swing | Bar |
|---|---|---|---|---|
| Sale price ±10 % | −23.5 | +23.5 | 47.0 | ############################## |
| Build cost ±10 % | −15.8 | +15.8 | 31.7 | #################### |
| Efficiency (saleable/GFA) 70 % / 80 % | −15.7 | +15.7 | 31.3 | #################### |
| Target profit on cost 25 % / 15 % | −9.8 | +10.6 | 20.4 | ############# |
| Debit rate +2 / −2 points | −9.4 | +10.2 | 19.7 | ############# |
| Construction 36 / 24 months | −5.7 | +6.0 | 11.6 | ####### |
| Contingency 10 % / 2.5 % | −7.5 | +3.8 | 11.3 | ####### |
| Fees 10 % / 6 % | −3.0 | +3.0 | 5.9 | #### |
| Sales period 12 / 3 months | −3.5 | +1.7 | 5.2 | ### |

**The input no tornado shows: which benchmark source you use** ([outputs/07](assets/C14/outputs/07_benchmark_source_sensitivity.md))

| Cost source (high-rise residential) | AED/m² used | RLV, AED m | RLV % of GDV |
|---|---|---|---|
| T&T ICMS 2024 (USD 1,334, secondary) | 4,896 | 93.8 | 23.6 % |
| T&T Q1 2024 midpoint | 4,900 | 93.7 | 23.6 % |
| **T&T GCMI 2025 Dubai (base)** | 5,500 | **76.4** | 19.2 % |
| T&T tall buildings 2025 midpoint (shell and core) | 5,725 | 70.0 | 17.6 % |
| Currie & Brown Q3 2025 midpoint | 7,295 | 24.8 | 6.2 % |
| Stonehaven 2025 G+40 midpoint | 8,400 | −7.2 | −1.8 % |
| AECOM Q3 2024 midpoint | 10,092 | −59.3 | −14.9 % |

**Monte Carlo** ([outputs/08](assets/C14/outputs/08_monte_carlo.md)). 2,000 runs, seed 14, inputs independent:

- price ~ Triangular(−10 %, 0, +10 %);
- build cost ~ Triangular(−5 %, 0, +15 %);
- debit-rate change ~ Triangular(−1, 0, +2) points;
- construction 27–36 months, uniform.

Results: P10 AED 51.9 m, P50 68.4 m, P90 83.7 m, mean 68.1 m. 74.1 % of runs fall below the single-point RLV of 76.4 m, because the cost and rate inputs are skewed upward. A single-point appraisal with "most likely" inputs therefore overstates the median land value here.

What to present: a two-way grid with the base cell highlighted and the step sizes stated, a tornado sorted by swing, and for Monte Carlo the distributions, correlations, run count and seed (RICS 7.1.6 asks for the basis to be stated) plus P10/P50/P90 and a histogram.

### Worked appraisal (measured)

Script: [assets/C14/appraisal.py](assets/C14/appraisal.py). Run it with `python3 appraisal.py` (Python 3.13, numpy-financial 1.1.0, scipy). The whole run, including the Monte Carlo, took 4.3 s here. It writes [outputs/](assets/C14/outputs/) including the full [monthly cash flow CSV](assets/C14/outputs/base_cashflow_monthly.csv).

**Assumptions**

| Input | Value | Source or assumption |
|---|---|---|
| GFA | 30,000 m² (G+30 tower) | Assumption |
| Saleable / GFA | 75 % | Assumption. AECOM gives 75–80 % net:gross for UAE offices ([[8]](https://publications.aecom.com/MEH/static/69a84a66cc94f48d41d456bfc959f519/4714f9cc02b32c869d15d7378fcb142e.pdf)) |
| Sale price | AED 1,640 /ft² = AED 17,653 /m² | Knight Frank, Dubai average apartment price Q4 2024 ([[51]](https://www.knightfrank.ae/newsroom/article/2025/3/dubai-residential-market-review---q4-2024)) |
| Build cost | AED 5,500 /m² GFA | T&T GCMI 2025, Dubai apartments high rise ([[2]](https://marketintelligence.turnerandtownsend.com/uaemi-2025/construction-cost-performance)) |
| Contingency | 5 % of construction | Assumption |
| Professional fees | 8 % of construction + contingency; 20 % in pre-construction, the rest on the S-curve | Assumption. UK ARGUS examples use 8 % and 12 % ([[25]](https://www.runnymede.gov.uk/downloads/file/2828/appendix-2-rbc-current-methodology)[[26]](https://www.broxbourne.gov.uk/downloads/file/1640/financial-viabiity-appraisal)) |
| Marketing; sales agent | 3 % of GDV; 1.5 % of GDV | Assumption, as in the Runnymede and Broxbourne examples |
| Land acquisition costs | 4 % of land | Assumption (UAE transfer fee not verified) |
| Arrangement fee | 1 % of land + construction + contingency, month 0 | Assumption |
| Debit / credit rate | 7.34 % nominal (EIBOR 4.34 % + 3.00 %) / 0 % | EIBOR from [[43]](https://tradingeconomics.com/united-arab-emirates/interbank-rate); margin assumed |
| Compounding | monthly (quarterly tested) | Assumption |
| Timing | land month 0; pre-construction 6 months; construction 30; sales receipts 6 months after completion; start Jan 2027 | Assumption |
| Construction S-curve | Beta(2,2), F = 3x² − 2x³ | Choice (see S-curves) |
| Target | 20 % profit on cost | Assumption (equals 16.7 % on GDV, inside the 15–20 % band in [[38]](https://www.gov.uk/guidance/viability)) |

**S-curve applied.** Construction plus contingency (AED 173.25 m) is spread as month m's share = F(m/30) − F((m−1)/30).

**Results** ([outputs/02](assets/C14/outputs/02_base_appraisal.md))

| Item | AED |
|---|---|
| GDV (22,500 m² × 17,653) | 397,187,910 |
| Construction / contingency / fees | 165,000,000 / 8,250,000 / 13,860,000 |
| Marketing / agent / arrangement fee | 11,915,637 / 5,957,819 / 2,496,925 |
| **Residualised land price** | **76,442,533** (AED 2,548 /m² GFA; 19.2 % of GDV) |
| Acquisition costs | 3,057,701 |
| Finance (7.34 %, monthly) | 44,009,309 |
| Total costs incl. finance | 330,989,925 |
| Profit | 66,197,985 |
| Profit on cost / on GDV | 20.00 % / 16.67 % |
| Peak debt | 315,271,597 (month 36) |
| Project IRR without finance | 1.3401 % monthly; 17.32 % effective; XIRR 17.32 % |
| Project NPV at 10 / 15 / 20 % | +36.4 m / +10.3 m / −10.7 m |

**Monthly cash flow extract** ([outputs/03](assets/C14/outputs/03_cashflow_and_hand_checks.md))

| Month | Date | Land+acq.+arr. fee | Build+contingency | Fees | Mkt+agent | Revenue | Interest | Cumulative balance |
|---|---|---|---|---|---|---|---|---|
| 0 | 2027-01 | 81,997,160 | 0 | 0 | 0 | 0 | 0 | −81,997,160 |
| 7 | 2027-08 | 0 | 564,667 | 36,139 | 0 | 0 | 537,457 | −89,005,847 |
| 8 | 2027-09 | 0 | 1,642,667 | 105,131 | 0 | 0 | 544,419 | −91,298,064 |
| 21 | 2028-10 | 0 | 8,649,667 | 553,579 | 0 | 0 | 1,107,707 | −191,407,433 |
| 36 | 2030-01 | 0 | 564,667 | 36,139 | 661,980 | 0 | 1,909,010 | −315,271,597 |
| 37 | 2030-02 | 0 | 0 | 0 | 1,654,950 | 66,197,985 | 1,928,411 | −252,656,973 |
| 42 | 2030-07 | 0 | 0 | 0 | 1,654,950 | 66,197,985 | 0 | +66,197,985 |

**Hand checks** (all match the model to the fils):

- First construction month: F(1/30) = 3(1/30)² − 2(1/30)³ = 0.0032593. × 173,250,000 = **564,666.67**.
- Construction month 15: F(15/30) − F(14/30) = 0.0499259. × 173,250,000 = **8,649,666.67**.
- Month-8 interest: 89,005,847.46 × 7.34 % / 12 = **544,419.10**.
- Profit on cost: 66,197,985 / 330,989,925 = **20.0000 %**. Profit on GDV: 66,197,985 / 397,187,910 = **16.6667 %**.
- The closing balance in month 42 (+66,197,985) equals profit. The money account and the summary agree.

## Risks and open questions

- **Benchmark basis is often unstated.** T&T MI 2024 and 2025, Currie & Brown and Knight Frank do not state the area basis on the pages read. Converting between bases is guesswork until the publishers are asked.
- **Gated and missing sources.** Arcadis ICC 2025 and 2026, Knight Frank's full report, Compass H1 2026 and AECOM 2026 were not read. No public UAE cost guide was found from RLB, Linesight, Cushman & Wakefield, JLL or Colliers before the search budget ran out. A 29 Jun 2026 Al Khaleej snippet gave USD 1,709 (Dubai) and 1,675 (Abu Dhabi) per m², but I could not identify its source, so I excluded it.
- **ARGUS and EstateMaster manuals are not public.** The ARGUS conventions here are decoded from two printouts (2018 and 2025, UK). The quarterly compounding I found is that file's setting, not necessarily the default. ARGUS's S-curve formula is not verified.
- **DHSS, Bromilow and Kenley–Wilson papers were not opened.** The DHSS form is as commonly reproduced, and published C, K values were not verified.
- **UAE finance terms not found:** lender margins over EIBOR, arrangement-fee percentages, LTC (loan-to-cost) limits, and how the escrow rules (Dubai's off-plan escrow law) restrict the use of buyer instalments. These drive the +22 % off-plan RLV effect and need legal and lender input.
- **Not verified:** the EIBOR value comes from a secondary site, because the CBUAE page was blocked. The land transfer fee (4 %) is an assumption. Dubai's Q1 2026 +5.2 % cost-index figure is search-result text only.
- **The Knight Frank Q4 2024 price is a Dubai-wide average.** It is not a scheme-specific price. The worked example is illustrative and not a valuation.
- **No Windows or Excel testing.** XIRR equivalence was checked against Microsoft's documented formula, not against Excel itself. The C# loop was run on Linux with .NET 8.

## Sources

1. United Arab Emirates market intelligence Q1 2024: Construction cost performance (PDF). Turner & Townsend. https://assets.foleon.com/eu-central-1/de-uploads-7e3kk3/48604/uaemi_24_construction_cost_performance.58a8c5990842.pdf. Read 2026-10-30.
2. UAEMI 2025: Construction cost performance. Turner & Townsend. https://marketintelligence.turnerandtownsend.com/uaemi-2025/construction-cost-performance. Read 2026-10-30.
3. UAEMI 2025: Construction market outlook. Turner & Townsend. https://marketintelligence.turnerandtownsend.com/uaemi-2025/construction-market-outlook. Read 2026-10-30.
4. Tall buildings construction guide 2026: Dubai. Turner & Townsend. https://reports.turnerandtownsend.com/tall-buildings-construction-guide-2026/dubai. Read 2026-10-30.
5. Global construction market intelligence 2026. Turner & Townsend. https://turnerandtownsend.com/insights/global-construction-market-intelligence-2026/. Read 2026-10-30.
6. GCMI 2026: Methodology. Turner & Townsend. https://publications.turnerandtownsend.com/global-construction-market-intelligence-2026/methodology. Read 2026-10-30.
7. Building construction costs: Dubai, Riyadh, Doha, Abu Dhabi (June 2024). AGBI. https://www.agbi.com/analysis/construction/2024/06/building-construction-costs-dubai-riyadh-doha-abu-dhabi/. Read 2026-10-30. Not verified: page blocked (403); search-result text only; secondary: summarises T&T ICMS 2024.
8. Middle East Property & Construction Handbook 2024 (PDF). AECOM. https://publications.aecom.com/MEH/static/69a84a66cc94f48d41d456bfc959f519/4714f9cc02b32c869d15d7378fcb142e.pdf. Read 2026-10-30.
9. Middle East Property & Construction Handbook 2025 (PDF). AECOM. https://publications.aecom.com/MEH/static/139fc9b5b274c6caf1d87e3b50d09986/d27cf1d4b4d53952da9145c18188bcfa.pdf. Read 2026-10-30.
10. Middle East Property & Construction Handbook (publications page). AECOM. https://publications.aecom.com/MEH/. Read 2026-10-30.
11. AECOM launches 20th edition of its Middle East Property & Construction Handbook. Middle East Construction News. https://meconstructionnews.com/66251/aecom-launches-20th-edition-of-its-middle-east-property-construction-handbook/amp. Read 2026-10-30. Third party.
12. UAE market overview report Q3 2025: Building asset costs. Currie & Brown. https://curriebrown.foleon.com/archive/uae-2025-q3/building-asset-costs. Read 2026-10-30.
13. Currie & Brown building asset cost table (Flourish data embed used by [12]). https://flo.uri.sh/visualisation/22778655/embed?auto=1. Read 2026-10-30.
14. Global cost report 2026: Middle East. Currie & Brown. https://curriebrown.foleon.com/group/global-cost-report-2026/middle-east. Read 2026-10-30.
15. UAE Construction Cost Benchmarking Report 2025 (PDF). Stonehaven. https://www.stonehaven.ae/application/files/8217/4418/3667/UAE_Benchmark_Report_2025.pdf. Read 2026-10-30.
16. UAE construction landscape H1 2025 (newsroom, 22 Sep 2025). Knight Frank. https://www.knightfrank.ae/newsroom/article/2025/9/uae-construction-landscape-h1-2025. Read 2026-10-30.
17. UAE's construction landscape (report page, behind a form). Knight Frank. https://www.knightfrank.ae/research/reports/uaes-construction-landscape. Read 2026-10-30.
18. International Construction Costs report 2025 (sign-up page). Arcadis. https://connect.arcadis.com/international-construction-costs-report-2025. Read 2026-10-30. Report behind a form; not read.
19. Abu Dhabi, Dubai rank among world's most cost-competitive (14 Jul 2026). Aletihad. https://en.aletihad.ae/amp/news/business/4678838/abu-dhabi--dubai-rank-among-world-s-most-cost-competitive-co. Read 2026-10-30. Secondary: summarises Arcadis ICC 2026.
20. Dubai and Abu Dhabi among the lowest in the world for construction cost (Arabic). Al Bayan. https://www.albayan.ae/economy/business/1525453. Read 2026-10-30. Secondary: summarises Arcadis ICC 2026.
21. H1 2026 construction costs benchmarks (14 Aug 2026). Compass Project Consulting. https://compass-pc.com/news-blog/h1-2026-construction-costs-benchmarks. Read 2026-10-30. Figures behind a download pop-up; not read.
22. Geopolitical uncertainty sharpens focus on construction costs across KSA and the UAE, says Compass (17 Aug 2026). Middle East Construction News. https://meconstructionnews.com/68769/geopolitical-uncertainty-sharpens-focus-on-construction-costs-across-ksa-and-the-uae-says-compass. Read 2026-10-30. Third party.
23. UAE construction market holds firm as delivery landscape shifts, says expert (2026). Zawya / TradeArabia. https://www.zawya.com/en/projects/uae-construction-market-holds-firm-as-delivery-landscape-shifts-says-expert-1459393. Read 2026-10-30. Secondary: summarises a Currie & Brown report.
24. Rising costs squeeze UAE real estate margins (July 2026). AGBI. https://www.agbi.com/real-estate/2026/07/rising-costs-squeeze-uae-real-estate-margins/. Read 2026-10-30. Not verified: page blocked (403); search-result text only.
25. Appendix 2: RBC current methodology (ARGUS Developer 8.20.003 appraisal, 07/01/2025). Runnymede Borough Council. https://www.runnymede.gov.uk/downloads/file/2828/appendix-2-rbc-current-methodology. Read 2026-10-30. Third party (an ARGUS user, not Altus).
26. Financial viability appraisal, Cheshunt Sports Village (ARGUS Developer 6.00.008). Broxbourne Borough Council. https://www.broxbourne.gov.uk/downloads/file/1640/financial-viabiity-appraisal. Read 2026-10-30. Old (2018); third party.
27. Viability technical seminar (Galliard Homes). Braintree District Council. https://www.braintree.gov.uk/downloads/file/1394/viability-technical-seminar-galliard-homes. Read 2026-10-30. Search-result text only; third party.
28. ARGUS Developer. Altus Group. https://www.altusgroup.com/solutions/argus-developer. Read 2026-10-30.
29. Property development feasibility, Part 1: Study fundamentals (L. Newcombe, 16 Jul 2026). Altus Group. https://www.altusgroup.com/featured-insights/property-development-feasibility/part-1-study-fundamentals/. Read 2026-10-30.
30. Property development feasibility, Part 2: Risk and return (3 Jan 2025). Altus Group. https://www.altusgroup.com/featured-insights/property-development-feasibility/part-2-risk-and-return/. Read 2026-10-30.
31. Property development feasibility, Part 3: Land valuations (11 Aug 2026). Altus Group. https://www.altusgroup.com/featured-insights/property-development-feasibility/part-3-land-valuations/. Read 2026-10-30.
32. Property development feasibility, Part 5: Financing (9 Jan 2025). Altus Group. https://www.altusgroup.com/featured-insights/property-development-feasibility/part-5-financing/. Read 2026-10-30.
33. ARGUS EstateMaster: Development feasibility. Altus Group. https://www.altusgroup.com/argus/products/argus-estatemaster/development-feasibility. Read 2026-10-30.
34. Navigating market uncertainty with confidence (12 Jan 2026). Ready Media. https://content.readymedia.com.au/article/navigating-market-uncertainty-with-confidence-the-new-tool-empowering-property-developers. Read 2026-10-30. Third party, promotional.
35. EstateMaster Development Feasibility (DF) overview, video transcript. Amara. https://amara.org/subtitles/tgh3DmtsU9tC/en/11/download/EstateMaster%20%20%20Development%20Feasibility%20DF%20overview.en.sbv. Read 2026-10-30. Not verified: page blocked (403); search-result text only.
36. Valuation of development property (standard page). RICS. https://www.rics.org/profession-standards/rics-standards-and-guidance/sector-standards/valuation-standards/valuation-of-development-property. Read 2026-10-30.
37. Valuation of development property, 1st edition, October 2019 (PDF). RICS. https://www.rics.org/content/dam/ricsglobal/documents/to-be-sorted/Valuation%20of%20development%20property_ready%20for%20approvals.pdf. Read 2026-10-30.
38. Planning practice guidance: Viability (updated 16 Dec 2025). UK Government. https://www.gov.uk/guidance/viability. Read 2026-10-30.
39. Assessing viability in planning under the NPPF 2019 for England. RICS. https://www.rics.org/profession-standards/rics-standards-and-guidance/sector-standards/land-standards/assessing-viability-in-planning-under-the-national-planning-policy-framework-2019-for-england. Read 2026-10-30. Not verified: 404.
40. Red Book Global Standards. RICS. https://www.rics.org/profession-standards/rics-standards-and-guidance/sector-standards/valuation-standards/red-book/red-book-global. Read 2026-10-30.
41. RICS NRM. RICS. https://www.rics.org/profession-standards/rics-standards-and-guidance/sector-standards/construction-standards/nrm. Read 2026-10-30.
42. NRM 1: Order of cost estimating and cost planning for capital building works (October 2022 update, PDF). RICS. https://www.rics.org/content/dam/ricsglobal/documents/standards/NRM-1_Oct2022_Update.pdf. Read 2026-10-30.
43. United Arab Emirates three-month interbank rate. Trading Economics. https://tradingeconomics.com/united-arab-emirates/interbank-rate. Read 2026-10-30. Secondary: cites the Central Bank of the UAE.
44. EIBOR rates. Central Bank of the UAE. https://www.centralbank.ae/en/forex-eibor/eibor-rates/. Read 2026-10-30. Not verified: blocked by Cloudflare (403).
45. Open market operations (FOMC target range changes). Federal Reserve. https://www.federalreserve.gov/monetarypolicy/openmarket.htm. Read 2026-10-30.
46. XIRR function. Microsoft Support. https://support.microsoft.com/en-us/office/xirr-function-de1242ec-6477-445b-b11b-a303ad9adc9d. Read 2026-10-30.
47. numpy-financial `_financial.py` (irr and `_irr_default_selection`). NumPy project, GitHub. https://github.com/numpy/numpy-financial/blob/main/numpy_financial/_financial.py. Read 2026-10-30. The page was truncated in the fetch; full logic read in the installed package, version 1.1.0.
48. Internal rate of return. Wikipedia. https://en.wikipedia.org/wiki/Internal_rate_of_return. Read 2026-10-30. Third party.
49. Tornado diagram. Wikipedia. https://en.wikipedia.org/wiki/Tornado_diagram. Read 2026-10-30. Third party.
50. scipy.stats.beta. SciPy documentation. https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html. Read 2026-10-30.
51. Dubai residential market review Q4 2024 (6 Mar 2025). Knight Frank. https://www.knightfrank.ae/newsroom/article/2025/3/dubai-residential-market-review---q4-2024. Read 2026-10-30.
52. HillPDA affordable housing viability report (Pymble), NSW Planning Portal. https://apps.planningportal.nsw.gov.au/prweb/PRRestService/DocMgmt/v1/PublicDocuments/DATA-WORKATTACH-FILE%20PEC-DPE-EP-WORK%20PP-2022-2519!20250424T011054.904%20GMT. Read 2026-10-30. Not verified: download failed (HTTP 400); search-result text only; third party.

## Choices made

- I inferred, as the shared brief instructs, that Studio is a Windows C#/.NET urban-design app for the GCC with 3D massing, a live Excel link, a table view and a node editor. I did not see Studio's code. The recommendations say "if Studio does X".
- I treated "ARGUS conventions" as what ARGUS Developer prints and calculates. I inferred them from two UK printouts because the manual is not public. The quarterly compounding found in the 2018 file is reported as that file's setting.
- I mapped hotel classes across sources as 3-star ≈ budget, 4-star ≈ mid-market and 5-star ≈ up-market. Resort is kept separate.
- I converted USD to AED at 3.67, the rate AECOM and Currie & Brown state, not at a more precise peg.
- The worked example's base cost rate is T&T GCMI 2025 (AED 5,500). That source states its basis and its city, and it is the most widely republished. The other sources are run as a separate sensitivity rather than averaged.
- Inputs without a UAE source (margin over EIBOR, arrangement fee, contingency, fees, timing, efficiency, transfer fee, target profit) are labelled assumptions in the script and the assumptions table. They are not presented as typical values.
- I used Beta(2,2) as the default S-curve because it has a closed form that can be checked by hand, and it equals DHSS with C = 0, K = 3.
- Interest is charged on the balance brought forward, with costs bearing interest from the following month, because that reproduces the ARGUS printout exactly.
- In the Monte Carlo I used independent triangular inputs, 2,000 runs and seed 14. That is enough to show the presentation and the skew effect, not a calibrated risk model.
- The web-search budget (shared by all agents) ran out mid-research. After that I opened known URLs directly (RICS, gov.uk, Fed, Microsoft, Altus, Trading Economics) and did no further searching. RLB, Linesight and the property consultancies may still have public cost guides.
- Charts are given as tables with text bars rather than images, to keep assets small and text-based.

## What Studio should do

1. **[M] [COMPLETES]** Attach a sourced cost-rate library to the existing 3D massing, so each use's GFA gets a low, base and high construction cost. Store source, edition, data date, city, currency, area basis, NRM 1 coverage (includes preliminaries and OH&P? fit-out? basements?) and date read for every rate, and default to showing several sources side by side. AECOM's Q3 2024 high-rise midpoint (AED 10,092) is 1.8 times T&T's 2025 average (AED 5,500), and switching source moved RLV from AED +94 m to −59 m (table section; "Sensitivity presentation").
2. **[S] [COMPLETES]** If Studio has the live Excel link, push the appraisal's monthly cash flow (the layout of [base_cashflow_monthly.csv](assets/C14/outputs/base_cashflow_monthly.csv)) and the assumptions sheet through it. Valuers and quantity surveyors can then check the interest, the S-curve and the ratios in Excel ("Worked appraisal").
3. **[S] [COMPLETES]** In Studio's table view or node outputs, add the RLV two-way grid (price × cost), the profit-on-cost grid at a fixed land price, and a tornado sorted by swing. These are the standard presentations and cheap once the engine exists ("Sensitivity presentation").
4. **[L] [NEW]** Build a residual appraisal engine with ARGUS-compatible conventions: monthly periods; nominal rate / 12; debit and credit rates; a compounding setting (1, 3 or 12 months); interest on the balance brought forward; land and construction interest reported separately; land solved for target profit on cost or GDV. Use the decoded Broxbourne months (interest matched exactly) and the Runnymede ratios as unit tests ("ARGUS Developer conventions"; the C# snippet).
5. **[S] [NEW]** Add an S-curve library: straight line, sine, Beta(a,b) and DHSS. Validate DHSS (K ≥ 3, |C| ≤ 1 − 3/K) and default to Beta(2,2). Show the curve and the spend per period ("S-curves").
6. **[S] [NEW]** Report IRR as XIRR (365-day) and as an effective annual rate from the monthly IRR, never as 12 × monthly. When cash flows change sign more than once, list all roots and lead with NPV ("IRR and NPV").
7. **[S] [NEW]** Make the finance rate "EIBOR + margin" with an as-of date and source field, and make arrangement fees and margin explicit inputs. UAE lender terms were not found, so no default should look authoritative ("Finance costs").
8. **[M] [NEW]** Add UAE off-plan payment plans as a funding source (deposits, construction instalments, handover), with escrow constraints after legal review. It changed finance by 40 % and RLV by 22 % in the illustrative case ("Finance costs").
9. **[S] [NEW]** Add cost escalation from each rate's data date to the appraisal start, with the cited 2024–2026 figures as presets and the user's choice shown on outputs ("UAE cost benchmarks: dates, escalation and normalisation").
10. **[M] [NEW]** Add a Monte Carlo mode with stated distributions, correlations, run count and seed. Output P10, P50 and P90 and a histogram. Point estimates overstated the median RLV here: 74 % of runs fell below the base ("Sensitivity presentation").
