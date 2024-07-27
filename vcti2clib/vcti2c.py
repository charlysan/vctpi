import pigpio
import time 


class VCTI2C(object):
    SDA_GPIO_PIN = 2
    SCL_GPIO_PIN = 3
    FAI_GPIO_PIN = 17
    I2C_SPEED = 100000

    def __init__(
        self,
        SDA=SDA_GPIO_PIN,
        SCL=SCL_GPIO_PIN,
        FA1=FAI_GPIO_PIN,
        I2C_SPEED = I2C_SPEED,
    ):
        self.SDA = SDA 
        self.SCL = SCL
        self.FA1 = FA1
        self.I2C_SPEED = I2C_SPEED

        # Initialize gpio
        self.gpio = pigpio.pi()

        # Set input pullups
        self.gpio.set_pull_up_down(self.FA1, pigpio.PUD_UP)
        self.gpio.set_pull_up_down(self.SDA, pigpio.PUD_UP)
        self.gpio.set_pull_up_down(self.SCL, pigpio.PUD_UP)

        # i2c pins as input by default
        self.gpio.set_mode(self.SDA, pigpio.INPUT)
        self.gpio.set_mode(self.SCL, pigpio.INPUT)
        self.gpio.set_mode(self.FA1, pigpio.OUTPUT)

    def __del__(self):
        # close i2c handler
        try:
            self.gpio.bb_i2c_close(self.SDA)
        except Exception:
            pass
        try:
            self.gpio.stop()
        except Exception:
            pass

    def set_i2c_speed(self, speed_khz):
        self.I2C_SPEED = speed_khz

    def pull_fa1(
        self, 
        level,
        delay = 0
    ):
        self.gpio.write(self.FA1, level)

        if delay != 0:
            time.sleep(delay)
            level = level ^ 1
            self.gpio.write(self.FA1, level)

    def pull_scl(
        self, 
        level,
        delay,
    ):
        self.gpio.write(self.SCL, level)
        time.sleep(delay)

        # Restore pin mode
        self.gpio.set_mode(self.SCL, pigpio.INPUT)

    def read_byte_from_addr_subaddr(self, addr, sub_addr):
        """Read one byte from addr/sub_addr or addr/offset"""
        self.gpio.bb_i2c_open(self.SDA, self.SCL, self.I2C_SPEED)
        cmd = [4, addr, 2, 7, 1, sub_addr, 3]
        _, data = self.gpio.bb_i2c_zip(self.SDA, cmd)

        cmd = [4, addr, 2, 6, 1, 3, 0]
        _, data = self.gpio.bb_i2c_zip(self.SDA, cmd)
        self.gpio.bb_i2c_close(self.SDA)
        return data
    
    def write_byte_to_addr_subaddr(self, addr, sub_addr, data):
        """Write one byte from addr/sub_addr or addr/offset"""
        self.gpio.bb_i2c_open(self.SDA, self.SCL, self.I2C_SPEED)
        cmd = [4, addr, 2, 7, 2, sub_addr, data, 3, 0]
        _, data = self.gpio.bb_i2c_zip(self.SDA, cmd)
        self.gpio.bb_i2c_close(self.SDA)
        return data

    def read_word_from_addr_subaddr(self, addr, sub_addr):
        """Read a word from addr/sub_addr"""
        self.gpio.bb_i2c_open(self.SDA, self.SCL, self.I2C_SPEED)
        cmd = [4, addr, 2, 7, 1, sub_addr, 3]
        _, data = self.gpio.bb_i2c_zip(self.SDA, cmd)

        cmd = [4, addr, 2, 6, 2, 3, 0]
        _, data = self.gpio.bb_i2c_zip(self.SDA, cmd)
        self.gpio.bb_i2c_close(self.SDA)
        return data

    def write_word_to_addr_subaddr(self, addr, sub_addr, word_high, word_low):
        """Read a word from addr/sub_addr"""
        self.gpio.bb_i2c_open(self.SDA, self.SCL, self.I2C_SPEED)
        cmd = [4, addr, 2, 7, 3, sub_addr, word_high, word_low, 3, 0]
        _, data = self.gpio.bb_i2c_zip(self.SDA, cmd)
        self.gpio.bb_i2c_close(self.SDA)
        return data
    
    def write_block_to_addr_range(self, start_addr, end_addr, buffer):
        """Write data block to address range, where buffer is a list of bytes
        [e.g. write_block_to_data_range(0x50, 0x57, data) => write data buffer to address range from 0x50 to 0x57]
        end_addr is only used to validate that the buffer will fit into the specified address range"""
        if len(buffer) > (end_addr - start_addr + 1) * 256:
            print(f"Aborted! buffer cannot fit in that memory space")
            exit(0)

        count = 0
        for addr in range(start_addr, end_addr + 1):
            for offset in range(0, 0xFF + 1):
                data = int.from_bytes(buffer[count], "big")
                self.write_byte_to_addr_subaddr(addr, offset, data)
                print(f"addr: {hex(addr)}, offset: {hex(offset)}, data: {hex(data)}")
                time.sleep(0.001)
                count+=1
                if count >= len(buffer):
                    return 0
        
        return data

    def read_block_from_addr_offset(self, addr, offset_start, offset_end):
        """(VCT External) Read data block from address by specifying start and end offsets 
        [e.g. read_block_from_addr_offset(0x50, 0x00, 0xff) => read 256 bytes from addr 0x50]"""
        data = []
        for offset in range(offset_start, offset_end + 1):
            value = self.read_byte_from_addr_subaddr(addr, offset)
            data.append(value)
        
        return data

    def read_block_from_addr_range(
        self, 
        addr_start, 
        addr_end, 
    ):
        """(VCT External) Read data block from address range 
        [e.g. (0x50, 0x57) => read 8 blocks of 256 bytes each starting at addr 0x50 => 2048 bytes]"""
        data = []
        for page in range(addr_start, addr_end + 1):
            page_data = self.read_block_from_addr_offset(page, 0x00, 0xFF)
            data.append(page_data)
            time.sleep(0.02)

        return data


def bytearray_to_hex(raw_data):
    return ' '.join(['0x{:02X}'.format(byte) for byte in raw_data])
        