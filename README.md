# F-Zero GX Emblem Printer

Other tools exist to allow you to directly convert an image to an emblem save file. However, this won't work on the GameCube emulator on Switch 2 (at least at launch) since save editing won't be possible. This project takes an image and creates a list of commands to run inside the emblem editor, allowing for automated printing. Printing takes much more time than converting files (around an hour), but it should work with a suitable TAS interface allowing for custom emblems on an unmodified Switch 2.

## Current flow
- Read image and downscale it to 62x62
- Sort the pixels using a simple nearest-neighbour algorithm to minimise required moves
- Generate required moves

## TODO
- Investigate better travelling salesman solutions
- Improve C-stick delay reset. Up/down is wasting inputs - if 2 adjacent sliders or all 3 need updating, they should be done at the same time
- Proof of concept on hardware (some kind of GCN TAS interface, or preferably a Bluetooth Switch TAS interface and BlueRetro). Arduino?
- Frontend