# vctpi

This tool is the result of reverse-engineering the I2C bus of a Panasonic CRT and can be used to communicate with Micronas VCT video controller through i2c using a Raspberry Pi. A detailed explanation of the process can be found on [this wiki](https://github.com/charlysan/crt_stuff/wiki/I2C-Data-Injection-In-Panasonic-CRT).


## Table of contents
- [Disclaimer](#disclaimer)
- [Requirements](#requirements)
- [Installation](#installation)
- [Connection to the TV](#connection-to-the-tv)
- [Usage](#usage)
  - [Access VCT registers](#access-vct-registers)
    - [Read 16bit register at sub-address `0x4B` from VSP (`0x58`):](#read-16bit-register-at-sub-address-0x4b-from-vsp-0x58)
    - [Write word `0x81 0x08` to register located at sub-address `0x4B` of VSP (`0x58`):](#write-word-0x81-0x08-to-register-located-at-sub-address-0x4b-of-vsp-0x58)
  - [Access external EEPROM memory](#access-external-eeprom-memory)
    - [Read byte (page 0, offset 0x10) from external EEPROM that is mapped from address 0x50 to 0x57](#read-byte-page-0-offset-0x10-from-external-eeprom-that-is-mapped-from-address-0x50-to-0x57)
    - [Ready byte (page 3, offset 0xFA) from external EEPROM:](#ready-byte-page-3-offset-0xfa-from-external-eeprom)
    - [Write byte to external EEPROM (page 0, offset 0x10):](#write-byte-to-external-eeprom-page-0-offset-0x10)
    - [Dump external EEPROM memory to binary file](#dump-external-eeprom-memory-to-binary-file)
    - [Read EEPROM memory from offset 0x10 to offset 0x1F](#read-eeprom-memory-from-offset-0x10-to-offset-0x1f)
    - [Read EEPROM memory from offset 0x100 to offset 0x10F (page 1)](#read-eeprom-memory-from-offset-0x100-to-offset-0x10f-page-1)
    - [Read first 32 bytes from EEPROM memory](#read-first-32-bytes-from-eeprom-memory)
    - [Write EEPROM memory from binary file (can be used to restore TV settings)](#write-eeprom-memory-from-binary-file-can-be-used-to-restore-tv-settings)
  - [Multi purpose commands](#multi-purpose-commands)
    - [Pull `SCL` low for 5 seconds (this can be used to put IC in bootloader mode)](#pull-scl-low-for-5-seconds-this-can-be-used-to-put-ic-in-bootloader-mode)


## Disclaimer

This tool is provided under the MIT License and is intended for experimental use. Users are advised to proceed at their own risk. The author assumes no responsibility or liability for any damage, data loss, hardware malfunction, or any issues that may render your TV inoperable as a result of using this tool. By using this tool, you acknowledge and accept that the author shall not be held responsible for any adverse effects or issues arising from its use.

## Requirements

- Raspberry Pi
- Python 3.11 or above
- [pigpio](https://abyz.me.uk/rpi/pigpio/python.html)
  


## Installation

1. Install `pigpio` following [this instructions](https://abyz.me.uk/rpi/pigpio/download.html)
2. Clone this repository:
```
git clone https://github.com/charlysan/vctpi.git
```
3. Run `pigpio` daemon
```
sudo pigpiod
```

## Connection to the TV

By default, [vcti2clib](https://github.com/charlysan/vctpi/blob/main/vcti2clib/vcti2c.py#L6), is using the following pinout:
```
SDA_GPIO_PIN = 2
SCL_GPIO_PIN = 3
```

You need to connect those two lines, along with GND, to TV's i2c service port.

## Usage

The tool can be used to read/write to VCT registers, as well as read/write to external memories connected to the bus.

**WARNING**: you must never run a read/write command while i2c bus is busy, this means that you first need to put the controller in bootloader mode. To put the controller in bootloader mode you have to turn the TV on while `SCL` is being pulled low.


### Access VCT registers

#### Read 16bit register at sub-address `0x4B` from VSP (`0x58`):
```
python vct_cli.py --rwas 0x58 0x4b
0x81 0x00
```

#### Write word `0x81 0x08` to register located at sub-address `0x4B` of VSP (`0x58`):
```
python vct_cli.py --wwas 0x58 0x4b 0x81 0x08
```

### Access external EEPROM memory

#### Read byte (page 0, offset 0x10) from external EEPROM that is mapped from address 0x50 to 0x57

```
python vct_cli.py --rbo 0x50 0x10
0x36
```

#### Ready byte (page 3, offset 0xFA) from external EEPROM:
```
python vct_cli.py --rbo 0x53 0xfa
0x10
```

#### Write byte to external EEPROM (page 0, offset 0x10):
```
python vct_cli.py --wbo 0x50 0x10 0x37
```

#### Dump external EEPROM memory to binary file
```
python vct_cli.py --rmr 0x50 0x57 > e2_dump.bin
```

#### Read EEPROM memory from offset 0x10 to offset 0x1F
```
python vct_cli.py --rmb 0x50 0x10 0x1f | xxd -g 1
00000000: 36 10 02 01 00 10 02 0f 90 a1 00 00 00 08 05 00  6...............
```

#### Read EEPROM memory from offset 0x100 to offset 0x10F (page 1)
```
python vct_cli.py --rmb 0x51 0x00 0x0f | xxd -g 1
00000000: 1b 00 06 00 b9 00 06 00 ba 00 06 00 bb 00 06 00  ................
```

#### Read first 32 bytes from EEPROM memory
```
python vct_cli.py --rmr 0x50 0x51 | xxd -g 1
00000000: bd 10 00 00 04 00 00 00 00 00 00 00 00 00 00 46  ...............F
00000010: 36 10 02 01 00 10 02 0f 90 a1 00 00 00 08 05 00  6...............
00000020: 80 00 06 00 81 00 06 00 82 00 06 00 83 00 06 00  ................
00000030: 84 00 06 00 85 00 06 00 86 00 86 09 87 00 06 00  ................
00000040: 88 10 06 00 89 00 06 00 8a 10 06 00 8b 00 06 00  ................
00000050: 8c 00 06 00 8d 00 06 00 8e 00 06 00 8f 10 06 00  ................
00000060: 90 00 06 00 91 00 06 00 92 00 06 00 93 00 06 00  ................
00000070: 94 00 06 00 95 00 06 00 96 00 06 00 97 00 06 00  ................
00000080: 98 00 06 00 99 00 06 00 9a 00 06 00 9b 00 06 00  ................
00000090: 9c 10 06 00 9d 00 06 00 9e 00 06 00 9f 10 06 00  ................
000000a0: a0 00 06 00 a1 00 06 00 a2 00 06 00 a3 00 06 00  ................
000000b0: a4 00 06 00 a5 00 06 00 a6 00 06 00 a7 00 06 00  ................
000000c0: a8 00 06 00 a9 00 06 00 aa 00 06 00 ab 00 06 00  ................
000000d0: ac 00 06 00 ad 00 06 00 ae 00 06 00 af 00 06 00  ................
000000e0: b0 00 06 00 b1 00 06 00 b2 00 06 00 b3 00 06 00  ................
000000f0: b4 00 06 00 b5 00 06 00 b6 00 06 00 b7 00 06 00  ................
00000100: 1b 00 06 00 b9 00 06 00 ba 00 06 00 bb 00 06 00  ................
00000110: bc 00 06 00 bd 00 06 00 be 00 06 00 bf 00 06 00  ................
00000120: c0 00 06 00 c1 00 06 00 c2 00 06 00 c3 00 06 00  ................
00000130: c4 00 86 f6 c5 00 06 00 c6 00 86 f6 c7 00 06 00  ................
00000140: c8 00 06 00 c9 00 06 00 ca 00 06 00 cb 00 06 00  ................
00000150: cc 00 06 00 cd 00 06 00 ce 00 06 00 cf 00 06 00  ................
00000160: d0 00 06 00 d1 00 06 00 d2 00 06 00 d3 00 06 00  ................
00000170: d4 00 06 00 d5 00 06 00 d6 00 06 00 d7 00 06 00  ................
00000180: d8 00 06 00 d9 00 06 00 da 00 06 00 db 00 06 00  ................
00000190: dc 00 06 00 dd 00 06 00 de 00 06 00 df 00 06 00  ................
000001a0: e0 00 06 00 e1 00 06 00 e2 00 06 00 e3 00 06 00  ................
000001b0: e4 00 06 00 e5 00 06 00 e6 00 06 00 e7 00 06 00  ................
000001c0: e8 00 06 00 e9 00 06 00 ea 00 06 00 eb 00 06 00  ................
000001d0: ec 00 86 f6 ed 00 06 00 ee 00 06 00 ef 00 06 00  ................
000001e0: f0 00 06 00 f1 00 06 00 f2 00 06 00 f3 00 06 00  ................
000001f0: f4 00 06 00 f5 00 06 00 f6 00 06 00 f7 00 06 00  ................
```

#### Write EEPROM memory from binary file (can be used to restore TV settings)
```
python vct_cli.py --wmf 0x50 0x57 ./e2_dump.bin
```

### Multi purpose commands

#### Pull `SCL` low for 5 seconds (this can be used to put IC in bootloader mode)
```
python vct_cli.py --pull-scl 0 5
```
