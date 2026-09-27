#!/usr/bin/env bash
# Run OpenROAD's public enclosure assertions with two complete executables.
set -euo pipefail

: "${OPENROAD_BEFORE:?Set OPENROAD_BEFORE to the absolute original executable path}"
: "${OPENROAD_AFTER:?Set OPENROAD_AFTER to the absolute corrected executable path}"
for executable in "$OPENROAD_BEFORE" "$OPENROAD_AFTER"; do
  if [[ "$executable" != /* || ! -x "$executable" ]]; then
    echo "Expected an executable absolute path: $executable" >&2
    exit 2
  fi
done

fixture_sha=6b3d456caab98deb34a1511327299d42fbcf9065
source_url="https://raw.githubusercontent.com/MahmoudNedalSubLaban/OpenROAD/$fixture_sha"
repro_dir=$(mktemp -d "${TMPDIR:-/tmp}/openroad-enclosure.XXXXXX")
echo "Outputs: $repro_dir"
cd "$repro_dir"
mkdir -p generated_via_enclosure Nangate45

for case in edge positive valid; do
  curl --fail --silent --show-error --location \
    "$source_url/src/pdn/test/generated_via_default_${case}.tcl" \
    -o "generated_via_default_${case}.tcl"
done
for file in audit.tcl run.tcl floorplan.def edge_macro.lef positive_macro.lef valid_macro.lef; do
  curl --fail --silent --show-error --location \
    "$source_url/src/pdn/test/generated_via_enclosure/$file" \
    -o "generated_via_enclosure/$file"
done
curl --fail --silent --show-error --location "$source_url/test/helpers.tcl" -o helpers.tcl
curl --fail --silent --show-error --location \
  "$source_url/test/Nangate45/Nangate45.lef" -o Nangate45/Nangate45.lef

sha256sum "$OPENROAD_BEFORE" "$OPENROAD_AFTER"
for arm in before after; do
  if [[ "$arm" == before ]]; then executable=$OPENROAD_BEFORE; else executable=$OPENROAD_AFTER; fi
  for case in edge positive valid; do
    expected=0
    if [[ "$arm" == before && "$case" != valid ]]; then expected=1; fi
    status=0
    RESULTS_DIR="$repro_dir/$arm" "$executable" -no_splash -no_init -exit \
      "generated_via_default_${case}.tcl" >"${arm}_${case}.log" 2>&1 || status=$?
    echo "$arm $case: exit=$status, expected=$expected"
    outcome="$arm/generated_via_default_$case/outcome.txt"
    cat "$outcome"
    [[ "$status" -eq "$expected" ]]
    grep -qx "invalid_enclosure_instances=$expected" "$outcome"
    grep -qx 'vdd_status=0' "$outcome"
    grep -qx 'vss_status=0' "$outcome"
  done
done
for artifact in result.def via_geometry.tsv via_enclosures.tsv; do
  cmp "before/generated_via_default_valid/$artifact" \
      "after/generated_via_default_valid/$artifact"
done
echo "PASS: both defects reproduced, correction verified, valid-control files identical."
echo "A passing corrected test can mean rejection of an illegal via, not a replacement connection."
