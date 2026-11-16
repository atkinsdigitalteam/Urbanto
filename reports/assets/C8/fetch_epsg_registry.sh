#!/bin/sh
# Fetch the EPSG online registry record for each code checked in C8 (apps.epsg.org REST API, read 2026-10-30).
mkdir -p epsgapi
for c in 4326 32636 32637 32638 32639 32640 3997 4270 27039 27040 4303 30339 30340 5843 4204 2318 20436 20437 20438 20439 20440 8818 8836 8837 8838 8839 8840 9333 9356 9357 9358 9359 9360 9335 4614 2932 4285 28600 4286 2099 27038; do
  curl -sS -m 30 "https://apps.epsg.org/api/v1/CoordRefSystem/$c/" -H "Accept: application/json" -o epsgapi/$c.json
done
python3 -I epsg_api_summary.py epsgapi
