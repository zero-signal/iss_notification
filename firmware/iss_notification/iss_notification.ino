/*
 * iss_notification.ino
 * -------------------- 
 *
 * Version 0.1, February 2014
 *
 * Simple sketch to receive commands from over a serial port and use IR codes
 * to change the colour of an LED strip. Can be used to alert the user of the 
 * position of the International Space Station (ISS).
 *
 * Copyright (C) 2014 - Zerosignal (zerosignal1982@gmail.com)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Tested:   arduino 1.0.5
 * Requires: IRremote library 
 *
 *           (written by Ken Shirriff, for more information see:
 *            https://github.com/shirriff/Arduino-IRremote)
 */
 
#include <IRremote.h>
 
#define CMD_DELIM_BEGIN        0x24
#define CMD_DELIM_END          0x21

#define ISS_STATE_RECEDING     0x41
#define ISS_STATE_APPROACHING  0x42
#define ISS_STATE_CLOSING      0x43
#define ISS_STATE_INCOMING     0x44
#define ISS_STATE_IMMINENT     0x45
#define ISS_STATE_OVERHEAD     0x46
#define ISS_STATE_TEST         0x5A

#define LED_STRIP_RED          0xFF1AE5
#define LED_STRIP_ORANGE       0xFF2AD5
#define LED_STRIP_YELLOW       0xFF0AF5
#define LED_STRIP_GREEN        0xFF9A65
#define LED_STRIP_BLUE         0xFFA25D

#define LED_TRANSMIT_BITS      32

#define SERIAL_READ_BYTES      3

#define DEFAULT_LED_TIMER      10000

byte curr_cmd;
byte serial_buf[SERIAL_READ_BYTES];

unsigned long last_val       = LED_STRIP_RED;
unsigned long curr_val       = LED_STRIP_RED;
unsigned long blink_val      = LED_STRIP_RED;
unsigned long last_blink_val = LED_STRIP_RED;

unsigned long start_blink_time = 0;
unsigned long last_blink_time  = 0;

unsigned int led_timer = DEFAULT_LED_TIMER;

boolean blink_leds = false;

IRsend irsend;

void setup() {
  Serial.begin(9600); 
}

/*
 * Reads 'commands' sent over the serial port and based on the command change the colour of an LED
 * strip by sending pre-recorded IR codes. Commands are simple ASCII character values (A through F, 
 * and Z for test sequence).
 * 
 * Valid commands have a leading '$' and trailing '!' character in a rudimentary attempt to ensure
 * a valid command was received. Based on the commmand the sketch then sends the corresponding IR
 * codes to change the colour of an LED strip light. 
 * 
 * Generally at a state transition the LEDS blink between the preset colours to catch your attention
 *
 */
void loop() {
  if (Serial.available() == SERIAL_READ_BYTES) {
    
    if((Serial.readBytes((char *) serial_buf, SERIAL_READ_BYTES)) == SERIAL_READ_BYTES){
      
      if(serial_buf[0] == CMD_DELIM_BEGIN && serial_buf[2] == CMD_DELIM_END) {
        curr_cmd = serial_buf[1];
        
        blink_leds = true;
        blink_val  = last_val;
        led_timer  = DEFAULT_LED_TIMER;         
        
        switch(curr_cmd){
          case ISS_STATE_RECEDING:
            curr_val = LED_STRIP_RED;
            
            if(last_val == ISS_STATE_RECEDING){
               blink_leds = false;
            }
            break;
          case ISS_STATE_APPROACHING:
            curr_val = LED_STRIP_ORANGE;           
            break;
          case ISS_STATE_CLOSING:
            curr_val = LED_STRIP_YELLOW;          
            break;
          case ISS_STATE_INCOMING:
            curr_val = LED_STRIP_GREEN;           
            break;
          case ISS_STATE_IMMINENT:
            last_val = LED_STRIP_YELLOW;
            curr_val = LED_STRIP_GREEN;             
            blink_val = LED_STRIP_BLUE;
            led_timer = (6 * DEFAULT_LED_TIMER);
            break;
          case ISS_STATE_OVERHEAD:
            curr_val = LED_STRIP_BLUE;             
            blink_leds = false;
            break;
          case ISS_STATE_TEST:
            test_leds();
            break;                      
        }
      }
    }
  }

  if(curr_val != last_val){  
    if(blink_leds){
      start_blink_time = millis();
      last_blink_time  = start_blink_time;
      last_blink_val   = curr_val;
    }
    send_code(curr_val);
    last_val = curr_val;
  }
  
  if(blink_leds){
    unsigned long curr_time = millis();
    
    if((curr_time - start_blink_time) > led_timer){
      blink_leds = false;
      send_code(curr_val);  
    }
    else {
      if((curr_time - last_blink_time)  > 500){
        if(last_blink_val == curr_val){
          send_code(blink_val);
          last_blink_val = blink_val;
        }  
        else {
          send_code(curr_val);
          last_blink_val = curr_val; 
        }
        last_blink_time = millis();
      }
    }
  }
  
  delay(50);
}

/*
 * Sends the code to change the LED strip colour. In this case we are using the NEC
 * protocol. 
 *
 */
void send_code(unsigned long code){
     irsend.sendNEC(code, LED_TRANSMIT_BITS); 
}

/*
 * Simple test sequence to ensure lights are working upon initial connection from driver script,
 * Triggered by sending '$Z!' command over serial port.
 * 
 * Always resets the default colours to LED_STRIP_RED
 *
 */
void test_leds(){
  for(byte i = 0; i < 2; i++){
    send_code(LED_STRIP_RED);
    delay(200);
    send_code(LED_STRIP_ORANGE);
    delay(200);
    send_code(LED_STRIP_YELLOW);
    delay(200);
    send_code(LED_STRIP_GREEN);
    delay(200);
    send_code(LED_STRIP_BLUE);
    delay(200); 
  }
  curr_val = LED_STRIP_RED;
  last_val = LED_STRIP_RED;
  
  send_code(curr_val); 
}
