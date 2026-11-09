# Physical verification scope

This is the minimum submission requested by IHP on 9 November 2026, not a
declaration of complete electrical or physical signoff. No waiver is assumed.

| Check | Recorded result |
| --- | --- |
| Native CMOS5L minimum/precheck DRC | 0 markers |
| Density | 0 markers |
| Antenna | 0 markers |
| Full native DRC | 50 `Pad.fR_TM1` findings; IHP disposition pending |
| Raw LVS | Not passing; IO/substrate/tap discrepancies remain under discussion |
| Prefill STA at 100 MHz | Worst setup slack +0.257126 ns, hold +0.044691 ns in the reviewed corner sweep |
| Qualified floating-fill timing | Not established by the current extraction path |
| Silicon validation and package qualification | Not completed |

The DRC databases and unedited logs are under
`../RVSoC6706-main/verification/drc/`. They name `ChipTop`, the pre-submission
top name. `release-identity.json` proves that the release conversion changes
only the top-cell name and reverses to the exact original GDS bytes. No shapes,
layers, cells below the root, coordinates, properties or timestamps changed.
These reports were not rerun under the new name and are not presented as such.

The source layout includes the seal ring, standard/IO fillers and dummy-metal
fill. The referenced netlist is the routed Verilog LVS reference, not an
extracted layout netlist or a CDL file. It is intended for the existing
Magic/Netgen comparison flow. A KLayout LVS workflow must not treat it as SPICE.

Original LVS scope blackboxes SRAM boundaries and excludes specified physical
cells. Diagnostic comparisons are not a blanket raw LVS pass. Additional
reports, reproduction scripts and source/dependency publication follow later.

The recorded 2600 x 2600 um bounding box includes the sealring hierarchy.
It corresponds to 6.76 mm2. See `layout-inspection.json` for individual layer
bounds; the foundry determines the relevant registration/billing boundary.
