# NSC_Builder v1.01 - Changelog

![DeviceTag](https://img.shields.io/badge/Device-SWITCH-e60012.svg)  ![LanguageTag](https://img.shields.io/badge/languages-python_batch_html5_javascript-blue.svg)

## *Support for DBI newer DBI versions (>155)*

**Resources**

DBI 156 was launched, you can get it directly from the kefir pack:

https://github.com/rashevskyv/switch/releases/

It can also be downloaded individually as nro or nsp here.

[DBI_156.nsp](https://github.com/julesontheroad/NSC_BUILDER/raw/master/py/Documentation%20and%20Resources/DBI/156/DBI_0591703820420000.nsp)

[DBI_156.nro](https://github.com/julesontheroad/NSC_BUILDER/raw/master/py/Documentation%20and%20Resources/DBI/156/DBI.nro)

You can find information on how to setup NSCB libraries, google drive auth tokens and 1 fichier auth tokens here:

https://github.com/julesontheroad/NSC_BUILDER/blob/master/py/Documentation%20and%20Resources/Changelogs/NSCB_0.99.md

Here's also a little readme with some DBI information:

https://github.com/julesontheroad/NSC_BUILDER/tree/master/py/Documentation%20and%20Resources/DBI

## *1.01-b - Changelog*
### 1. Fixed issue in interface where nsz and xcz fails to show the files section
### 2. Improved titledb version consolidation between databases

* Fixed issue where versions.txt got downloaded from tinfoil.io for instead of my titledb repository
* Added nutdb.json as a source for versions.txt consolidation

### 3. Made changes to google drive requests on mtp

### 4. Fixed issue where batch verification won't hash xcz files

## *1.01 - Changelog*

### 1. Support for DBI 155 and 156 new mtp setup

DBI installation setup and save management changes on 155, this release supports both older DBI versions and newer ones.

### 2. Added option to backup saves for installed games only

This option only has an effect on **DBI>155**, matching a newer DBI function.

### 3. Added xci and xcz installation from google drive remotes

This option will support installation of multiprogram and normal xci|xcz files from google drive. **It won't support multiprogram files** from google drive on this version, these kind of files are supported for local installation on any format or as nsp|nsz.

Known multiprogram files are Super Mario 3D All-Stars, Grandia Collection, Hotline Miami Collection, ...

### 4. Added fixed xci location configurations for mtp mode

User can now setup the locations DBI will scan on the SD card to find xci files on the **zconfig\mtp_xci_locations.txt**, this file already includes standard xci locations. If this file is removed DBI will scan the whole SDCard so it's not recommended to remove it but to add or delete locations to it if needed.

### 5. Added option to MTP - AUTOUPDATE DEVICE FROM LIBRARY to check from game registry instead of installed

When selection from game registry is activated the autostart is set to false and user will be asked to manually select what games to update via the file picker.

This function won't check which games are installed or xci on the SDCard, instead it will use the game registry that includes archived games and registered xci files, independently of their location. This will show files that are on a HDD for example.

### 6. Fix issues installing certain files from google drive because of special characters

File id is now added to text file, also files ids are now stored in json files on cache mode.

### 7. File Selector now allows to select multiple files at once

The tkinter file selector that uses windows browser now allows to select multiple files at once if they are on the same folder.

### 8. Added additional information on the "Files" tab on the interface

- Added ability to show multiple the titleid for each nca file for local files on the web Interface on the "Files tab"
- Added ability to show multiple the buildid for each program file for local files on the web Interface on the "Files tab". This is showned in a section at the bottom of the "Files" tab

![Picture](https://i.ibb.co/6WR2hnq/exefs.png)

### 9. Corrected patched multiprogram files VERIFICATION

Multiprogram files with removed titlerights will give a false corruption positive for html manual files, this issue has been corrected. A patched file is a file with titlerights removed or keygeneration changes

### 10. Ability to not autoupdate DATABASES

If database configuration is setup to a number higher than **9999 hours** the autoupdate function is turned off. No autoupdate zip already includes this setup.

### 11. Other changes and bugfixes:

- Updated keygeneration strings to **FW 10.2.0**
- Tickets that don't follow the proper standard now issue a warning instead of preventing titlerights removal on some functions.
- Fixed hang on interface when a buildid is not readable on certain situations.
- Added better representation of xci certificates on nut info.
- Faster library calls on python version which should speed up the batch menus.
- Fix for #169 where some language combinations break correct language tag addition due to change on python semantics.
- Other small bugfixes
