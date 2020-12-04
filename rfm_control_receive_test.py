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
import sys
import logging

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

# log file
logfile = "rcv_app.log"
logging.getLogger("asyncio")
logging.basicConfig(format="%(asctime)s - %(message)s", filename=logfile, level=logging.WARNING)
logging.info("LoRa Distance Test Start - Receiving.")

# stats to log
rcv_packets = 0

# start global timer
start = time.time()

message = ""

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
        if time.time() > time3 + 1:
            # timer ends after one second
            print('Display 4 Hz loop ended work: {}'.format(tic()))
            time3 = time.time()
            display.fill(0)

async def receive_hz4():
    global message, rcv_packets
    print('Receive 4 Hz loop started work: {}'.format(tic()))
    time2 = time.time()
    while True:
        # check for packet rx
        packet = rfm9x.receive()

        # if packet is received
        if packet is not None:
            rcv_packets += 1
            logging.warning("Sent: %d", rcv_packets)
            prev_packet = packet
            message = str(packet, "utf-8")
        else:
            packet = None
            message = "..."

        await asyncio.sleep(0)
        if time.time() > time2 + 0.25:
            # timer ends after one second
            print('Rx 4 Hz loop ended work: {}'.format(tic()))
            time2 = time.time()

def main():
    ioloop = asyncio.get_event_loop()
    tasks = [ioloop.create_task(receive_hz4()), ioloop.create_task(display_hz4()) ]
    ioloop.run_until_complete(asyncio.wait(tasks))
    ioloop.close()

if __name__ == "__main__":
    main()
