#!/usr/bin/python3

#########################################
# Sending data within a control loop using LoRa radios
# Author: Mauricio
#########################################

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
logfile = "send_app.log"
logging.basicConfig(format="%(asctime)s - %(message)s", filename=logfile, level=logging.WARNING)
logging.getLogger("asyncio")
logging.warning("LoRa Distance Test Start - Sending.")

# global counter for interval sending
countdown_start = 20
countdown = 20

# stats to log
sent_packets = 0
distance = 0

# start global timer
start = time.time()

message = str(sent_packets) + str(distance)
message_bytes = bytes(message,"utf-8")

def tic():
    return 'at %1.2f seconds' % (time.time() - start)

async def distance_hz1():
    global distance
    print('Distance 1 Hz loop started work: {}'.format(tic()))
    time4 = time.time()
    while True:
        # Update distance variable -100m
        if not btnA.value:
            if distance > 0:
                distance -= 100
            else:
                distance = 0
        # Update distance variable +100m
        if not btnB.value:
            if distance >= 0:
                distance += 100
            else:
                distance = 0

        # await sleep is 1
        await asyncio.sleep(1)
        if time.time() > time4 + 1.0:
            # timer ends after one second
            print('Distance 1 Hz loop ended work: {}'.format(tic()))
            time4 = time.time()

async def display_hz1():
    global message, sent_packets, distance, countdown, countdown_start
    print('Display 1 Hz loop started work: {}'.format(tic()))
    time3 = time.time()
    countdown = countdown_start
    while True:
        countdown = countdown_start if countdown < 0 else countdown
        display.show()
        display.text('Tx Chosen: ', 0, 0, 1)
        display.text(str(distance), 0, 10, 1)
        display.text(str(countdown), 0, 20, 1)

        if not btnC.value:
            if countdown != 0:
                countdown = countdown_start

        await asyncio.sleep(0)
        if time.time() > time3 + 1.0:
            # timer ends after one second
            print('Display 1 Hz loop ended work: {}'.format(tic()))
            time3 = time.time()
            display.fill(0)
            countdown -= 1

async def send_hz1():
    global message, sent_packets, distance, countdown
    print('Tx 1 Hz loop started work: {}'.format(tic()))
    time2 = time.time()
    while True:
        await asyncio.sleep(0)
        if time.time() > time2 + countdown_start:
            countdown = countdown_start
            for _ in range(10):
                message = str(sent_packets) +":"+ str(distance)
                message_bytes = bytes(message,"utf-8")
                rfm9x.send(message_bytes)
                print(message)
                sent_packets += 1
                logging.warning("Sent: %d:%d", sent_packets,distance)
                # timer ends after one second
                print('Tx 1 Hz loop ended work: {}'.format(tic()))
                time.sleep(1)

            time2 = time.time()

def main():
    logging.warning("Main.")
    ioloop = asyncio.get_event_loop()
    tasks = [ ioloop.create_task(send_hz1()), ioloop.create_task(display_hz1()), ioloop.create_task(distance_hz1()) ]
    ioloop.run_until_complete(asyncio.wait(tasks))
    ioloop.close()

if __name__ == "__main__":
    main()

