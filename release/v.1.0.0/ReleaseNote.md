# RVSoC6706: minimum November 2026 submission

Prepared 9 November 2026 in response to IHP's request for immediate delivery
of the GDS and info.json. The source candidate is conservative-route-pruned-v6,
with its final repaired and filled native CMOS5L layout.

- `gds/RVSoC6706.gds.gz`: final candidate layout, renamed from ChipTop.
- `netlist/RVSoC6706.lvs.v`: routed reference with power connections for LVS.
- `netlist/RVSoC6706.sim.v`: routed functional simulation view.
- `doc/`: release documentation and proposed pin assignment.
- `SHA256SUMS`: hashes of the release files.

Only the top name changed in the GDS and the module declaration changed in
each netlist. The original GDS is preserved outside this repository. The
inverse GDS rename is byte-for-byte identical to that original, including
properties and timestamps. See ../../doc/release-identity.json.

Minimum/density/antenna DRC is clean. Full-DRC pad recommendations and native
IO/substrate/tap LVS findings remain for IHP's disposition. This release
number is an artifact identifier, not an assertion of complete signoff.
See ../../doc/Verification.md. No written waivers are included.

Source publication, complete reproduction documentation and remaining
verification evidence will follow. No fabricated-silicon results exist yet.
