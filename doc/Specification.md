# RVSoC6706 specification

| Feature | Implemented configuration |
| --- | --- |
| Processor | One 32-bit Rocket core; RV32IAC, Zicsr, Zifencei, Zihpm |
| Instruction cache | 4 KiB |
| Executable scratchpad | 16 KiB at 0x80000000 |
| Boot | SPI-flash image loader; debug boot supported |
| SPI | One controller, CS0/CS1/CS2; CS0 boot flash; shared SCK/DQ pins |
| GPIO | Two bidirectional pins |
| UART | TX/RX; dedicated RX synchronizer |
| Debug | JTAG, two hardware triggers, debug-requested system reset |
| Interrupts | CLINT and PLIC |
| Clock target | 100 MHz; see verification scope, not a measured silicon rating |
| Process/package | SG13CMOS5L; QFN32 requested |
| Layout bounds | 2600 x 2600 um including sealring hierarchy |
| Nominal supplies | 1.2 V core and 3.3 V IO; not absolute-maximum specifications |

GPIO, UART and SPI register bases are 0x10010000, 0x10020000 and 0x10030000.
The mapped SPI-flash read window starts at 0x20000000. The generated device
tree in ChipTop.dts retains the source configuration name and provides the
authoritative address map. Only the submission top-cell name was changed.

The three chip selects do not provide three independent SPI buses. Software
must serialize accesses and restore flash-controller settings after other
slave transactions. A PCB/BOM has not yet been qualified.
