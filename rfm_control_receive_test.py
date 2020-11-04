#!/usr/bin/python3

##############################################################
# Sending data within a control loop using LoRa radios
# Author: Mauricio
##############################################################

import time
import asyncio
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import adafruit_ssd1306
import adafruit_rfm9x

# Button A
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP

# Button B
btnB = DigitalInOut(board.D6)
btnB.direction = Direction.INPUT
btnB.pull = Pull.UP

# Button C
btnC = DigitalInOut(board.D12)
btnC.direction = Direction.INPUT
btnC.pull = Pull.UP

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height

# Configure LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0)
rfm9x.tx_power = 23
prev_packet = None

start = time.time()

message = "waiting.."

def tic():
    return 'at %1.2f seconds' % (time.time() - start)

async def display_hz4():
    global message
    print('Display 4 Hz loop started work: {}'.format(tic()))
    time3 = time.time()
    while True:
        display.show()
        display.text('Rx: ', 0, 0, 1)
        display.text(message, 25, 0, 1)
        await asyncio.sleep(0)
        if time.time() > time3 + 0.25:
            # timer ends after one second
            print('Display 4 Hz loop ended work: {}'.format(tic()))
            time3 = time.time()

async def receive_hz4():
    global message
    print('Receive 4 Hz loop started work: {}'.format(tic()))
    time2 = time.time()
    while True:
        # check for packet rx
        packet = rfm9x.receive()
        if packet is not None:
            # Display the packet text and rssi
            display.fill(0)
            prev_packet = packet
            message = str(prev_packet, "utf-8")

        await asyncio.sleep(0)
        if time.time() > time2 + 0.25:
            # timer ends after one second
            print('Rx 4 Hz loop ended work: {}'.format(tic()))
            time2 = time.time()

def main():
    ioloop = asyncio.get_event_loop()
    tasks = [ioloop.create_task(display_hz4()), ioloop.create_task(receive_hz4()) ]
    ioloop.run_until_complete(asyncio.wait(tasks))
    ioloop.close()

if __name__ == "__main__":
    main()
