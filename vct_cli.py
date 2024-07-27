import sys 
import signal
import argparse
import time

from vcti2clib.vcti2c import VCTI2C, bytearray_to_hex

def signal_handler(sig, frame, vct: VCTI2C):
    print('\nProcess terminated by user')

    sys.exit(0)

def parse_arguments():
        example_text = r'''Examples:

        vct_cli --rbo 0x50 0x10
        vci_cli --wbo 0x50 0x10 0x36
        vci_cli --pull-scl 0 3
        '''
        
        parser = argparse.ArgumentParser(
            description="VCT cli tool can be used to talk to VCT49xl ICs",
            epilog=example_text,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument('--version',
                            action="version",
                            version="v0.1 (July 26th, 2024)")

        parser.add_argument('--rbo', nargs=2, metavar=('address', 'offset'), action=MultiParamsAction, help="Read byte from address offset", default=None)
        parser.add_argument('--wbo', nargs=3, metavar=('address', 'offset', 'data'), action=MultiParamsAction, help="Write byte to address offset", default=None)
        parser.add_argument('--rwas', nargs=2, metavar=('address', 'sub_address'), action=MultiParamsAction, help="Read word from address/sub-address", default=None)
        parser.add_argument('--wwas', nargs=4, metavar=('address', 'sub_address', 'high_word', 'low_word'), action=MultiParamsAction, help="Write word from address/sub-address (addr, sub-addr, high,low)", default=None)
        parser.add_argument('--rbas', nargs=2, metavar=('address', 'sub_address'), action=MultiParamsAction, help="Read byte from address/sub-address", default=None)
        parser.add_argument('--wbas', nargs=3, metavar=('address', 'sub_address', 'write_byte'), action=MultiParamsAction, help="Write byte from address/sub-address (addr, sub-addr, byte)", default=None)
        parser.add_argument('--rmb', nargs=3, metavar=('address', 'offset_start', 'offset_end'), action=MultiParamsAction, help="Read EEPROM Memory page block", default=None)
        parser.add_argument('--rmr', nargs=2, metavar=('address_start', 'address_end'), action=MultiParamsAction, help="Read EEPROM Memory range", default=None)
        parser.add_argument('--wmf', nargs=3, metavar=('start_addr', 'end_addr', 'file_path'), action=MultiParamsAction, help="Write to EEPROM memory address range from binary file", default=None)
        
        parser.add_argument('--pull-scl', nargs=2, metavar=('level', 'delay'), action=MultiParamsAction, help="Pull SCL line to logic level", default=None)
        parser.add_argument('--pull-fa1', nargs=2, metavar=('level', 'delay'), action=MultiParamsAction, help="Pull FA1 line to logic level", default=None)

        args = parser.parse_args(
            args=None if sys.argv[1:] else ['--help'])

        return args

def main():
    vct = None
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, vct))

    args = parse_arguments()
    vct = VCTI2C()

    if args.pull_fa1:
        level, delay = args.pull_fa1
        vct.pull_fa1(int(level), delay=float(delay))

    if args.pull_scl:
        level, delay = args.pull_scl
        vct.pull_scl(int(level), delay=float(delay))

    if args.rbo:
        arg1, arg2 = args.rbo
        addr = parse_byte(arg1)
        offset = parse_byte(arg2)

        vct = VCTI2C()

        data = vct.read_byte_from_addr_subaddr(addr, offset)
        print(bytearray_to_hex(data))

    elif args.wbo:
        arg1, arg2, arg3 = args.wbo
        addr = parse_byte(arg1)
        offset = parse_byte(arg2)
        data_byte = parse_byte(arg3)

        vct = VCTI2C()
        data = vct.write_byte_to_addr_subaddr(addr, offset, data_byte)

        print(bytearray_to_hex(data))
       
    elif args.rmb:
        arg1, arg2, arg3 = args.rmb
        addr = parse_byte(arg1)
        offset_start = parse_byte(arg2)
        offset_end = parse_byte(arg3)

        vct = VCTI2C()
        data = vct.read_block_from_addr_offset(addr, offset_start, offset_end)
        for data_byte in data:
            sys.stdout.buffer.write(data_byte)
        
    elif args.rmr:
        arg1, arg2 = args.rmr
        addr_start = parse_byte(arg1)
        addr_end = parse_byte(arg2)
        vct = VCTI2C()
        data = vct.read_block_from_addr_range(addr_start, addr_end) 
        for page in data:
            for data_byte in page:
                sys.stdout.buffer.write(data_byte)
    
    elif args.rbas:
        arg1, arg2 = args.rbas
        addr = parse_byte(arg1)
        sub_addr = parse_byte(arg2)

        vct = VCTI2C()
        data = vct.read_byte_from_addr_subaddr(addr, sub_addr)
        print(bytearray_to_hex(data)) 
    
    elif args.wbas:
        arg1, arg2, arg3 = args.wbas
        addr = parse_byte(arg1)
        sub_addr = parse_byte(arg2)
        write_byte = parse_byte(arg3)

        vct = VCTI2C()
        data = vct.write_byte_to_addr_subaddr(addr, sub_addr, write_byte)
        print(bytearray_to_hex(data)) 
    
    elif args.rwas:
        arg1, arg2 = args.rwas
        addr = parse_byte(arg1)
        sub_addr = parse_byte(arg2)

        vct = VCTI2C()
        data = vct.read_word_from_addr_subaddr(addr, sub_addr)
        print(bytearray_to_hex(data)) 
    
    elif args.wwas:
        arg1, arg2, arg3, arg4 = args.wwas
        addr = parse_byte(arg1)
        sub_addr = parse_byte(arg2)
        high_word= parse_byte(arg3)
        low_word = parse_byte(arg4)

        vct = VCTI2C()
        data = vct.write_word_to_addr_subaddr(addr, sub_addr, high_word, low_word)
        print(bytearray_to_hex(data)) 

    elif args.wmf:
        arg1, arg2, arg3 = args.wmf 
        addr_start = parse_byte(arg1)
        addr_end = parse_byte(arg2)
        file_path = arg3
        buffer = []
        try:
            with open(file_path, "rb") as f:
                byte_count = 0
                byte = f.read(1)
                while byte:
                    buffer.append(byte)
                    byte_count += 1
                    byte = f.read(1)
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
        except Exception as e:
            print(f"Error: {e}")
        
        vtc = VCTI2C()
        data = vtc.write_block_to_addr_range(addr_start, addr_end, buffer)

    if vct:
        vct.__del__()

def parse_byte(data):
    try:
        if data.startswith("0x"):
            return int(data, 16)
        else:
            return int(data, 10)
    except ValueError:
        print("Invalid input (%s). Please use integer or hex string (e.g. 0x4d)" % data)
        exit(-1)

class MultiParamsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


if __name__ == "__main__":
    main()