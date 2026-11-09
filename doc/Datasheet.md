# RVSoC6706 preliminary datasheet

This document is preliminary and is not a silicon-qualified electrical
datasheet. See Specification.md for implemented functions and Verification.md
for the scope of current evidence.

The QFN32 assignment is in ../release/v.1.0.0/doc/bondplan-connections-DRAFT.csv.
All 32 pins are allocated: 20 signals and 12 supply/ground pins, with three
connections each for VDD, VSS, IOVDD and IOVSS. Each side has power and ground.
Package orientation and assembly approval remain with the bondlab.

Current interface analysis assumes at most 10 MHz JTAG TCK, 5 MHz boot SPI,
and total output loads of 10 pF (output-only) or 12 pF (bidirectional).
These are analysis assumptions, not measured device limits. Nominal supplies
are 1.2 V core and 3.3 V IO. Supply sequencing, regulator tolerances, package
parasitics and board signal integrity must be reviewed before use.
