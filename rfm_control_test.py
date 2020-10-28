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

def tic():
    return 'at %1.2f seconds' % (time.time() - start)

async def hz1():
    print('1 Hz loop started work: {}'.format(tic()))
    time2 = time.time()
    while True:
        # do work here
        await asyncio.sleep(0)
        packet = None
        # draw a box to clear the image
        display.fill(0)
        display.text('RasPi LoRa', 35, 0, 1)

        # check for packet rx
        packet = rfm9x.receive()
        if packet is None:
            display.show()
            display.text('- Waiting for PKT -', 15, 20, 1)
        else:
            # Display the packet text and rssi
            display.fill(0)
            prev_packet = packet
            packet_text = str(prev_packet, "utf-8")
            print("Rx: ", packet_text)
            display.text('RX: ', 0, 0, 1)
            display.text(packet_text, 25, 0, 1)
            time.sleep(1)

        if not btnA.value:
            # Send Button A
            display.fill(0)
            button_a_data = bytes("Button A!\r\n","utf-8")
            rfm9x.send(button_a_data)
            display.text('Sent Button A!', 25, 15, 1)
        elif not btnB.value:
            # Send Button B
            display.fill(0)
            button_b_data = bytes("Button B!\r\n","utf-8")
            rfm9x.send(button_b_data)
            display.text('Sent Button B!', 25, 15, 1)
        elif not btnC.value:
            # Send Button C
            display.fill(0)
            button_c_data = bytes("Button C!\r\n","utf-8")
            rfm9x.send(button_c_data)
            display.text('Sent Button C!', 25, 15, 1)

        display.show()
        
        if time.time() > time2 + 1:
            # timer ends after one second
            print('1 Hz loop ended work: {}'.format(tic()))
            time2 = time.time()


def main():
    ioloop = asyncio.get_event_loop()
    tasks = [ioloop.create_task(hz1())]
    ioloop.run_until_complete(asyncio.wait(tasks))
    ioloop.close()

if __name__ == "__main__":
    main()
