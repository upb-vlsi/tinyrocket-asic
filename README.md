# TinyRocket ASIC

An open-source 32-bit RISC-V research SoC built with Chipyard for the IHP SG13CMOS5L
130 nm process, featuring SPI, GPIO, and UART, targeting QFN32 packaging.
The implementation uses Hammer, Yosys, and OpenROAD.

## Collaboration

The tapeout is a joint project of the **System and Circuit Technology (SCT)**
group and the **Digital Integrated Systems and Circuits** group at
**Paderborn University**.

**Project contact:** Lars Luchterhandt
([lars.luchterhandt@uni-paderborn.de](mailto:lars.luchterhandt@uni-paderborn.de)).

## Project Status

**Minimum MPW submission prepared: `IHP__RVSoC6706`.** The release GDS and
matching netlists use the top cell `RVSoC6706`. This repository retains its
existing name, `tinyrocket-asic`; the IHP submodule request uses the generated
submission identifier.

The minimum delivery follows IHP's instructions of 9 November 2026. Full source
publication and additional documentation will follow. This delivery is not a
claim of complete signoff or a reproducible source-to-GDS build.

- [Submission metadata](doc/info.json)
- [Release notes and files](release/v.1.0.0/ReleaseNote.md)
- [Physical-verification status](doc/Verification.md)

Validate the release files and their provenance with:

```bash
python3 scripts/validate_submission.py
```

This checks submission-file consistency, not electrical or physical signoff.

The project targets the **November 2026 IHP SG13CMOS5L MPW shuttle**. The design
has not yet completed tapeout signoff or silicon validation. Features and
implementation targets below describe the current configuration and may change
before tapeout.

## SoC Overview

| Component | Configuration |
| --- | --- |
| Processor | Single 32-bit Rocket core implementing RV32IAC with Zicsr, Zifencei, and Zihpm |
| On-chip memory | SRAM scratchpad for program and data storage |
| BootROM | Firmware for loading a program from external SPI flash into the scratchpad |
| SPI controller | Three chip selects: CS0 for boot flash, CS1 and CS2 for additional devices |
| GPIO controller | Two general-purpose IO pins |
| UART controller | Asynchronous serial interface with TX and RX |
| Debug module | JTAG interface for processor debugging |

**Implementation targets:** 100 MHz core clock, IHP SG13CMOS5L (130 nm),
and QFN32 packaging.

## Implementation and Verification

The SoC is generated using **Chipyard and Rocket Chip**. **Hammer** orchestrates
both implementation and physical verification, integrating **Yosys** for synthesis,
**OpenROAD** for floorplanning, placement, clock-tree synthesis, routing, and
timing analysis, and **KLayout** for design rule checking (DRC). For
layout-versus-schematic (LVS) checking, Hammer invokes **Magic** to extract the
layout netlist and **Netgen** to compare it against the reference netlist.
Technology and verification collateral come from the **IHP Open PDK**.

## License and Acknowledgments

Project-owned content in this repository is licensed under the
[Apache License 2.0](LICENSE). Third-party components retain their respective
licenses and attribution requirements; those licenses are not replaced by the
license of this repository.

This project builds on Chipyard, Rocket Chip, Hammer, Yosys, OpenROAD, KLayout,
Magic, Netgen, and the IHP Open PDK. We acknowledge their developers and the
IHP open-source MPW program.
