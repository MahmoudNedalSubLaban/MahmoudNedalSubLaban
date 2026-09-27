# Mahmoud Sub Laban

Master's research in macro placement and physical design, with a focus on
reproducible experiments and implementation correctness.

## Open-source contribution

### OpenROAD: generated-via enclosure validation

I investigated a PDN via-validation defect and submitted a targeted C++ fix
with regression tests. The correction preserves legitimate technology-rule
overrides while rejecting malformed generated geometry.

**[Read the illustrated case study →](case-studies/openroad-pdn/README.md)**

[Bug report #11538](https://github.com/The-OpenROAD-Project/OpenROAD/issues/11538)
· [Pull request #11539](https://github.com/The-OpenROAD-Project/OpenROAD/pull/11539)
· [Public regression inputs](https://github.com/MahmoudNedalSubLaban/OpenROAD/tree/6b3d456caab98deb34a1511327299d42fbcf9065/src/pdn/test/generated_via_enclosure)

As of September 27, 2026: **submitted, pending upstream review**. Local PDN
regressions pass 207/207; the GitHub DCO check passes. Build/lint workflows await
maintainer approval. See the PR for the current status.
