# LeLight Home Assistant integration

Based on [v1ack/smartLightConnector](https://github.com/v1ack/smartLightConnector)

There are at least 3 apps with the same light control

|         **Icon**          |         **Name**          |     **package**      |
|:-------------------------:|:-------------------------:|:--------------------:|
| ![](.github/gm_light.jpg) |      GM Smart Light       |   com.hm.simpleble   |
| ![](.github/lelight.jpg)  |      Le Smart Light       | cn.lelight.smart.lzg |
|   ![](.github/le+.jpg)    | Le+ Pro (simple ble mode) |   com.lelight.pro    |

If your lamp works with any of the above apps, this integration is for you

## Configuration

1. Connect your lamp to any of the above apps
2. Find `Current ID (mode)` in app settings
3. Install this integration and restart Home Assistant
4. Find `LeLight` in Home Assistant integration list
5. Insert ID from step 2 to `ID` field
