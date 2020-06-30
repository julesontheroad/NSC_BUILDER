# DBI 1.25 from RASHEVSKYV
https://github.com/rashevskyv/switch/releases/tag/456

## 1. What's DBI?

DBI is a installer in a similar fashion as old tinfoil by Adubbz with extended functions and a MTP responder mode that allows access to the Nintendo Switch via the MTP protocol to transfer files between Switch and pc and to get several information from the switch like installed games, storage used, firmware on the Switch, etc...
Included is the tested 1.25 version of DBI + an nsp that includes the full romfs (not a redirector), use what you prefer but the nsp allows going home without closing the install, is safer to the nand and can be overclocked with sys-clk to improve performance.

## 2. Why do you include this on your github?

Since NSC_Builder 0.99 beta NSCB features a new "m" mode which is a mtp manager meant mainly for DBI though a couple of functions work with blawar's tinfoil.

## 3. Why make a mtp installer?

While mtp means you can install directly from the windows manager that has several caveats. For example the mtp protocol means that a transfer bigger than 4GB needs to be transfered without a specific size which makes the windows explorer error on timeout though the transfer is actually completed. By keeping track of the stream NSCB can close the transfers when actually completed.
Other interesting function that NSCB makes use of is to search for new updates on games installed and autoupdate the console via SD, keep track of the used space while installing, reclaim space by deleting new updates, etc... It also supports direct installation from remote locations via USB like google drive and 1fichier.

## 4. Full list of features
1.- Installer
  * Installation via queue for nsp, nsz (directly) and xci (preconversion)
  * Select installation medium (SD\EMMC)
  * Pre-verification of files (disabled,level2,hash verification)
  * Check space on device before installing each file and optionally change installation medium (SD\EMMC) if the other has space left and the targetted one runs off space.
  * Check keygeneration required by files vs fw reported from console, skip installation if the keygeneration required is bigger than the available. Optionally patch the file pre-installation.
  * Optionally check if game is already installed and skip installation if that's the case.
  * Optionally check if the same update id is installed, check version installed and if the installed version is bigger skip installation while if it's smaller predelete the old update to reclaim space and procede to the installation.
  * Optionally install prepatched nsps when attempting to install a nsp that requires a higher keygeneration.
  * Preconvert xci\xcz to install on the system.
2.- Remote location installer
  * Install nsp and nsz directly from google drive and 1fichier
3.- Auto-updater.
  * Take a local library or google drive library and check if it has new updates or dlcs for the installed games, if it does autoupdate the console.
  * Note: If you installed games previously on this mtp sesion disconnect the mtp responder first and reconnect again to get accurate information since installed games data is parsed once per session.
4.- File-Transfer.
  * DBI allows transfers of more than 4GB via mtp autoarchiving in Nintendo format, that means the transfer mode can transfer with ease xcis or movies to the setup locations on the SD.
5.- Uninstaller.
  * Identifies installed games,updates and dlcs and allows them to be removed via a selector.
6.- Content dumper.
  * Allows to dump games, updates and dlcs to the setup libraries.
7.- Archived games cleaner.
  * Identifies archived games and allows to clean them up.
8.- Information
  * Device information
  * Check installed and archived games
  * Search new updates and dlcs for the installed games and xcis on the SD versus nutdb
  * Search new updates and dlcs for the  archived games versus nutdb 
9.- Savegames
  * Detect empty registries and clean them up
  * Dump savegames
10.- Generate SX autoloader files 
  * Can generate sx autoloader cache files for any path on the SD if titleid is listed. That includes non scanned paths. 
  * Can generate sx autoloader cache files for any path on a HDD if connected and send them to the appropiate folder on the SD.
  * Note: Wgile the autoloader works on archived files and installed placeholders the placeholder takes priority so the xcis are loaded after an error, that's the reason the placeholder won't be created automatically.
  * Note 2: As an alternative NSCB can create xci placeholders, which will load a gamecard placeholder which is appropiate for the autoloader. This xcis will be loaded to a path scanned by rommenu and can be deleted after.
  * Note 3: Alternatively you can make the first xci mounting from sx installer file browser.

## 5. How to setup each library type

## 6. How to setup auth for google drive

## 7. How to setup auth for 1fichier

## 8. Does it support tinfoil?

During the initial testings I couldn't get tinfoil to be recognize by the api, unlike nx-mtp and DBI installer. This changed by using the driver present in this nut released:
https://github.com/blawar/nut/releases/tag/v2.7
Either way even with the driver I had issues in several functions, and my installer just makes tinfoil hang up so the support is limited to the info functions, which will tell you the new updates for the device if using tinfoil. 
Future versions may support tinfoil with a mixed approach by using the usb installation protocol to install and the mtp api to get console information.

## 9. Limitations

Currently NSCB can't make installations from patched streams, this means installing xci files or keygeneration patched files. This is something that will be worked on future versions.
Direct remote installation from 1fichier and google drive doesn't support pre-verification this will be solved soon. The reason being I didn't finish porting verification to the NSCB google drive API.