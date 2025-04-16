# F-Zero GX Emblem Printer

Other tools exist to allow you to directly convert an image to an emblem save file. However, this won't work on the GameCube emulator on Switch 2 (at least at launch) since save editing won't be possible. This project takes an image and creates a list of commands to run inside the emblem editor, allowing for automated printing. Printing takes much more time than converting files (around an hour), but it should work with a suitable TAS interface allowing for custom emblems on an unmodified Switch 2.

## Current flow
- Read image and downscale it to 62x62
- Sort all pixels into groups based off RGB "distance" to GX's pre-defined colours
- Sort each group using a simple nearest-neighbour algorithm (5D: x, y, r, g, b, with colour dimensions having some bias applied) to minimise required moves
- Generate required moves

## TODO
- Refactor
- Investigate bias more on nearest-neighbour - best value for colour dimensions and possibly a second value for x/y
- Is sorting into groups the best approach? Try sorting every pixel with nearest-neighbour rather than using pre-defined colours
- Proof of concept on hardware (some kind of GCN TAS interface, or preferably a Bluetooth Switch TAS interface and BlueRetro). Arduino?
- Frontend