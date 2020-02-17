# Automation of bluetooth captures
Automation of bluetooth captures originated from Android devices.

## Devices

**controler (MAC):**
Orchestrate all the communication and commands sent to other devices

**Watch:**
Where touches are automated

**Phone:**
Where touches are automated (TODO)

**Ellisys laptop (WINDOWS):**
Launch and issues command to ellisys soft.

## Requirements

On the **controller (MAC)**:
  1. monkeyrunner (comes with the Android studio)

      1. Download address: https://developer.android.com/studio
      2. Shoud be located in : */Users/<user>/Library/Android/sdk/tools/bin/monkeyrunner*
      3. Need to set Path variable to it.

  2. adb (Android Debug Bridge):

      1. Should also come with Android Studio
      2. Shoud be located in : */Users/<user>/Library/Android/sdk/platform-tools*


On the **Ellisys laptop (Windows)**:
  1. AutoIt3
  2. Ellisys software
  3. Ellisys hardware


On the **watch**:
  1. Developper mode enabled
  2. adb enable
  3. adb over wifi enabled
  4. (Optional but better) go to the watch screen with no apps running in background


### Quick start


Steps:

On the **controler**:

  1. Go to the Automation directory on the controler
  2. Connect the watch to the controler: `adb connect <ip>:5555`
  3. make sure it is connected: `adb devices`
  4. run: `monkeyrunner simulation.py`


On **Ellisys laptop**:

  1. Power and once the light is blue, connect to ellisys hard. to ellisys soft.
  2. go to Automation directory  
  3. run `python ellisys_to_controler.py`

On the watch:

  1. Nothing. Better to not touch it.

## Troubleshooting

#### Ellisys

1. **Ellisys hard. is not recognized by ellisys soft.** In this case, try to shutdown ellisys hard wait 5 sec turn on and wait for the blue light comming then connect to the computer with the cable  


#### Watches

1. If multiple watches are used, make sure they are recognized in wearOS app. otherwise somme applications does not detect them
