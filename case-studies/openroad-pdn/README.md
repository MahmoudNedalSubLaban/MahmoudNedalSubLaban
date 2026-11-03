# OpenROAD: catching malformed generated vias

**Mahmoud Sub Laban · C++ / physical design / regression testing**

[Issue #11538](https://github.com/The-OpenROAD-Project/OpenROAD/issues/11538)
· [PR #11539](https://github.com/The-OpenROAD-Project/OpenROAD/pull/11539)
· [Merged patch](https://github.com/The-OpenROAD-Project/OpenROAD/pull/11539/files)

**Updated November 3, 2026:** merged into OpenROAD `master` on November 2
through PR #11539. The upstream merge commit is
[`ef9b2931350bd98c18cc9ca97ad56808cc04e6d1`](https://github.com/The-OpenROAD-Project/OpenROAD/commit/ef9b2931350bd98c18cc9ca97ad56808cc04e6d1).
This identifies the integrated source; inclusion in a numbered release has
not been verified. The measurements below retain their original tested revisions.

## What failed?

During my master's research, a power-grid investigation exposed malformed
generated-via geometry. A public synthetic reproduction accepted a **140 nm
cut with a 20 nm landing** in one direction: **60 nm protruded on each side**.
A second reproduction had 5 nm enclosure where its synthetic rule required
10 nm. Native supply-connectivity checks passed in both cases; connectivity
alone did not establish legal geometry.

![Measured one-dimensional enclosure schematic: the edge case has a 140 nm cut and 20 nm landing, giving minus 60 nm margin per side; the positive case has a 140 nm cut and 150 nm landing, giving 5 nm margin where 10 nm is required.](enclosure-geometry.svg)

*Measured schematic, not a layout screenshot: only the affected y dimension
is shown, horizontally. Both landing layers share these y extents. The plot
uses [OpenDB rectangle measurements](measured-enclosures.csv); it does not
depict a replacement connection.*

## Why did it fail?

The final generated-via check requested applicable enclosure rules but omitted
the VIARULE default when no cut-layer override existed. An empty rule list then
passed validation. Integer halving and manufacturing-grid snapping could also
round a small negative margin to an apparently legal zero.

## What changed?

The merged correction changes `src/pdn/src/via.cpp`: use the default
independently for each landing **only when no applicable overriding rule exists**,
and preserve negative margins with floor division and signed grid snapping.
Existing override selection and legal landing-extension attempts remain.
This follows the default/override distinction in the
[LEF/DEF reference, Via Rule Generate](https://coriolis.lip6.fr/doc/lefdef/lefdefref/LEFSyntax.html).

## How was it tested?

The original Tcl regressions inspect actual OpenDB cut and landing rectangles,
independently of PDN's fit predicate. Both defect assertions fail on the original
complete executable and pass with the correction. The valid control's DEF and
geometry tables are byte-identical. The existing stacked-via override test
passes unchanged.

The September local PDN suite passed **207/207 tests**, including three new
tests. That run used previously built, verified binaries with checked
production-source equivalence; it was not a fresh Bazel build. Its pinned
reproduction and measured figure remain below.

The later **October 24 validation** added native C++ regressions in the
existing PDN test targets:

- **289/289 Bazel targets passed in three fresh executions each**, covering
  PDN, PSM, RAM and `repair_setup_reroute1`, with test-result reuse disabled.
- With the same via-test source, unpatched upstream passed **205/211**;
  the correction passed **211/211**. The six defect tests failed in all three
  unpatched runs.
- With the same connection-test source, unpatched upstream passed **74/77**;
  the correction passed **77/77**. The three enclosure-rejection tests failed
  in all three unpatched runs.

Positive controls covered valid overrides, locked/pinned containment, tapered
stacks, legal landing extension, obstruction ripup and direction-dependent
widening. Independent OpenDB rectangle checks also identified five undersized
connection fixtures; adequate-landings controls and rejection regressions
preserve both behaviors.

These results belong to tested head
`0eaf08712f2bee52fbbd2493ed67cd9f53d559e6`, incorporating upstream
`6f3f28cc85407d71ba64a550cca194d8a6a01c1c`, not a new execution of the November
merge commit. See the [public validation record](https://github.com/The-OpenROAD-Project/OpenROAD/pull/11539)
and [October reproduction instructions](https://github.com/MahmoudNedalSubLaban/OpenROAD/blob/0eaf08712f2bee52fbbd2493ed67cd9f53d559e6/src/pdn/test/generated_via_enclosure/README.md).
Test counts describe regression targets, not independent chip designs.

### Reproduce the original demonstration

These September source pins reproduce the original small geometry cases and
figure. They are intentionally unchanged; the corrected revision here is an
earlier implementation, not the final upstream merge.

Build two complete OpenROAD executables with matching dependencies using the
[upstream build instructions](https://github.com/The-OpenROAD-Project/OpenROAD/blob/80c6be93c28244f9f72840852a667daef764a4ff/docs/user/Build.md):

| Demonstration arm | Source commit |
| --- | --- |
| Original | `80c6be93c28244f9f72840852a667daef764a4ff` |
| Corrected | `6b3d456caab98deb34a1511327299d42fbcf9065` |

Then use Bash, curl and those executables:

```bash
git clone https://github.com/MahmoudNedalSubLaban/MahmoudNedalSubLaban.git
cd MahmoudNedalSubLaban/case-studies/openroad-pdn
export OPENROAD_BEFORE=/absolute/path/to/original/openroad
export OPENROAD_AFTER=/absolute/path/to/corrected/openroad
bash reproduce.sh
```

The script fetches only pinned public test files, reuses OpenROAD's existing
regression assertions and writes to a fresh temporary directory. Existing
library notices are retained. Expected exits for edge/positive/valid are
`1/1/0` before and `0/0/0` after; invalid generated-instance counts are `1/1/0`
before and `0/0/0` after. Native VDD/VSS checks pass in these small cases.
Inspect `via_geometry.tsv` for rectangle bounds and margins. No private netlist,
checkpoint, restricted input package or prebuilt database is required.

The [upstream regression README](https://github.com/MahmoudNedalSubLaban/OpenROAD/blob/6b3d456caab98deb34a1511327299d42fbcf9065/src/pdn/test/generated_via_enclosure/README.md)
also contains direct commands and interpretation. To regenerate this figure:
`python -m pip install matplotlib==3.10.7` and `python draw_geometry.py`.

## What remains unresolved?

Rejecting an illegal via does **not** guarantee a replacement connection.
Already-disconnected test networks can report more disconnected shapes after
illegal links are rejected. This fix does not resolve the separate DFT68
`PDN-0179` construction failure documented in the PR, or establish universal
PDN repair. No full-chip PPA improvement, process DRC, IR-drop, electromigration
or electrical sign-off is claimed.

## Related checker work

[PR #11698](https://github.com/The-OpenROAD-Project/OpenROAD/pull/11698) addresses
a separate detailed-routing checker issue: importing individual via figures
outside a worker's context can produce a false spacing marker. The proposed
fix filters imported figures by that context and tests the existing
`FlexGCWorker` fixture directly. **It remains open as of November 3, 2026**;
it is not part of the merged PDN fix. Neither contribution is a claim of
improved macro placement or full-chip routing quality.
