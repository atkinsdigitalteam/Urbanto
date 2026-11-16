#!/bin/bash
export DOTNET_ROOT=/opt/dotnet PATH=/opt/dotnet:$PATH DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1
cd "$(dirname "$0")"
for p in "$@"; do
  ( cd $p && dotnet publish -c Release -r linux-x64 -o out > publish.log 2>&1; echo "exit=$?" >> publish.log )
done
