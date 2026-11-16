#!/usr/bin/env bash
# Runs the share-mode matrix: one process holds sample.xlsx open, another probes it.
set -u
export DOTNET_ROOT=/opt/dotnet PATH=/opt/dotnet:$PATH DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1
BIN="$(dirname "$0")/bin/Release/net8.0/XlsxShareProbe"
W=$(mktemp -d)
for share in none None Read ReadWrite; do
  "$BIN" make "$W/sample.xlsx"
  if [ "$share" = none ]; then
    echo "### no other process holds the file"
  else
    "$BIN" hold "$W/sample.xlsx" "$share" 60 > "$W/hold.log" &
    HP=$!
    until grep -q HOLDING "$W/hold.log" 2>/dev/null; do sleep 0.1; done
    echo "### holder: FileStream(FileAccess.ReadWrite, FileShare.$share)"
  fi
  "$BIN" probe "$W/sample.xlsx"
  [ "$share" != none ] && kill $HP 2>/dev/null && wait $HP 2>/dev/null
done
rm -rf "$W"
