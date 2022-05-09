"""
--------------------------------------------------------------------------------
PocketBeagle Heart Rate Module (max30102, bmp280, )
--------------------------------------------------------------------------------
License: MIT
Copyright 2022 Hamza Shili

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------
Software API:

    draw_readings()
        - Updates ili9341 display with sensor readings
        
    max30102_read()
        - Returns "Please, place your finger on sensor" beafore reading the sensor
        - Returns the heart rate value in BPM (beats per minute) and SpO2 in percentage
        - Returns "Unable to detect" upon failure to read from sensor
    
    bmp280_read()
        - Returns temperature and humidity readings in celsius and percent
    
      
  
--------------------------------------------------------------------------
Background Information: 
 
  * Using 2.2" TFT LCD Display with Adafruit's ILI9341 library
    * https://www.adafruit.com/product/1480
    * https://learn.adafruit.com/adafruit-2-8-and-3-2-color-tft-touchscreen-breakout-v2/python-wiring-and-setup
    * https://cdn-shop.adafruit.com/datasheets/ILI9340.pdf
    
    
--------------------------------------------------------------------------------
"""

# Base Imports
import time
import digitalio
import board
import busio

# Display specific imports
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341

# gymax30:02 Sensor Imports


# bmp280 Imports
import adafruit_bmp280

# Initialize the I2C1 ports of the PocketBeagle
config-pin P2_09 i2c
config-pin P2_11 i2c
i2c_bmp280 = 0x70
bmp280_sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c_bmp280)
i2c_max30102 = 0x57
max30102_sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c_max30102)

# Configuration for CS and DC pins on the PocketBeagle SPI0:
rst_LCD   = digitalio.DigitalInOut(board.P1_2)
dc_LCD    = digitalio.DigitalInOut(board.P1_4)
cs_LCD    = digitalio.DigitalInOut(board.P1_6)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Note: Adjust offsets to maintain centered text if adjusting fontsize
FONTSIZE = 24

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create LCD display class.

disp = ili9341.ILI9341(
    spi,
    rotation=90,  # 2.2", 2.4", 2.8", 3.2" ILI9341
    cs=cs_LCD,
    dc=dc_LCD,
    rst=rst_LCD,
    baudrate=BAUDRATE,
)

# Create blank image for drawing, ensure rotation to landscape:
if disp.rotation % 180 == 90:
    height = disp.width
    width = disp.height
else:
    width = disp.width
    height = disp.height

image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
#draw.rectangle((0, 0, width, height), outline=0, fill=(255, 124, 186))
disp.image(image)

# Constants that alter the positioning of text
y_offset = 30
x = 30 # x_offset

# Load Deja Vu TTF font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

#-------------------------------------------------------------------------------
# Component access functions
#-------------------------------------------------------------------------------
        
def draw_readings(BPM, SPO2, temp, humidity):
    """ Updates heart rate and temperature readings on the ILI9341 display.
    BPM: Takes heart rate from max30102_read()
    SPO2: Takes SPO2 concentrations (%) from max30102_read()
    temp: Takes temperature (C) from  bmp280_read()
    humidity: Takes humidity (%) from  bmp280_read()
    """
    # Get rendered font width and height.
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    y = y_offset
    BPM_level = "Heart rate: " + str(BPM) + " (BPM)"
    SPO2_level = "SPO2: " + str(SPO2) + " (%)"
    temp_level = "Temperature: %0.1f C" % temp
    # Farenheit temperature conversion
    temp_f = "Temperature: %0.1f F" % (temp * (9 / 5) + 32)
    humidity_level = "Humidity: %0.1f %%" % humidity

    # Draw each air quality reading, then offset the next one below
    draw.text((x, y), BPM_level, font=font, fill="#FFFFFF")
    y += font.getsize(BPM_level)[1]
    
    draw.text((x, y), SPO2_level, font=font, fill="#FFFFFF")
    y += font.getsize(SPO2_level)[1]
    
    draw.text((x, y), temp_level, font=font, fill="#FFFFFF")
    y += font.getsize(temp_level)[1]
    
    draw.text((x, y), temp_f, font=font, fill="#FFFFFF")
    y += font.getsize(temp_f)[1]
    
    draw.text((x, y), humidity_level, font=font, fill="#FFFFFF")
    y += font.getsize(pm25_level)[1]

    disp.image(image)
    
def max30102_read():
    """ Queries MAX 30102 Sensor
    Outputs BPM and SPO2 readings if reading is successful, "Unable to detect" as a str if not
    """
    pass

def bmp_280read():
    """ Queries BMP Sensor
     Outputs temperature (in celsius) and humidity (%) readings
    """
    return bmp280_sensor.temperature , bmp280_sensor.relative_humidity
        

# ------------------------------------------------------------------------------
# Main Script:
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    # Default value of MAX30102 readings
    bpm_rd = "Please, place your finger on sensor"
    while True:
        # Does not update display until a new valid BPM reading is detected
        if max30102_read() == "Unable to detect":
            pass
        elif max30102_read() != "Unable to detect":
            bpm_rd = max30102_read()[0]
            spo2_rd = max30102_read()[1]
        
        # Update the temperature, and humidity readings.
        temp_rd = bmp_280read()[0]
        humi_rd = bmp_280read()[1]
        draw_readings(bpm_rd, spo2_rd, tvoc_rd, temp_rd, humi_rd)
    