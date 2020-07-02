
/**
 * Author: Evan Putnam
 * Description: This is an arduino sketch to handle audio visualization with the
 * sound.py file I created in this repo.  It communicates over serial to update the information
 * present.
 * 
 * The circuit is very simple and just puts the data out on a pin.  The lights are externally powered.
 * They also have one cable running to ground on the arduino.
 */
//Make sure you have the FastLED library installed.
#include <FastLED.h>

#define LED_PIN     4
#define NUM_LEDS    128

//Array of RGB
CRGB leds[NUM_LEDS];

//Two values used to swap in and out light 'profiles'
static int glob_count = 0;
static int light_type = 0;
bool DEBUG = true;

/**
 * Seting up the light interface and begining fast serial transmission.
 */
void setup() {
  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
  Serial.begin(115200);
  delay(1000);
}

/**
 * Loop takes a count and indexes into a led to set the color.
 * Color profiles change every 500 cycles.
 */
void loop() {

  
  int count = 0;
  while(true) {
      if(Serial.available() > 0){
        //int val = 254;
        int val = Serial.read();
        if(val == 255 || count == NUM_LEDS){
          break;  
        }
        switch(light_type){
          case 0:
            leds[count] = CRGB(val, 2, 2);
            break;
          case 1:
            leds[count] = CRGB(val, val, 2);
            break;
          case 2:
            leds[count] = CRGB(val, 2, val);
            break;
          case 3:
            leds[count] = CRGB(2, val, 2);
            break;
          case 4:
            leds[count] = CRGB(2, 2, val);
            break; 
        }
        
        count += 1;
      }
  }

  glob_count += 1;
  if(glob_count == 500){
    light_type += 1;
    glob_count = 0;
    if(light_type > 4){
      light_type = 0;  
    }
  } 

  FastLED.show();

  
}
