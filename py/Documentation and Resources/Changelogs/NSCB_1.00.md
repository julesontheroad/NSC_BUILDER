# NSC_Builder v1.00c - Changelog

![DeviceTag](https://img.shields.io/badge/Device-SWITCH-e60012.svg)  ![LanguageTag](https://img.shields.io/badge/languages-python_batch_html5_javascript-blue.svg)

## *Further improvements over the MTP features*
**Resources**

DBI 135 was launched, you can get it directly from the kefir pack:

https://github.com/rashevskyv/switch/releases/tag/462

It can also be downloaded individually as nro or nsp here.

[DBI_1.35.nsp](https://github.com/julesontheroad/NSC_BUILDER/raw/master/py/Documentation%20and%20Resources/DBI/135/DBI_0591703820420000.nsp)

[DBI_1.35.nro](https://github.com/julesontheroad/NSC_BUILDER/raw/master/py/Documentation%20and%20Resources/DBI/135/DBI.nro)

You can find information on how to setup NSCB libraries, google drive auth tokens and 1 fichier auth tokens here:

https://github.com/julesontheroad/NSC_BUILDER/blob/master/py/Documentation%20and%20Resources/Changelogs/NSCB_0.99.md

Here's also a little readme with some DBI information:

https://github.com/julesontheroad/NSC_BUILDER/tree/master/py/Documentation%20and%20Resources/DBI

## *Changelog*
### 1.00c Fixes

Fixes to functions in mtp_gdrive.py where the use of curses prevented some prints on filters.

Fixed indentation in mtpsp and mtpxci library which derived in **"No module named 'mtpsp'"** and **"No module named 'mtxci'"** errors in the exe builds.

### 1.00b Fixes

Fixed issue where on some systems some search filters wouldn't show the message asking for an input.

Fixed bug introduced by 1.00 that would stop the databases update in the middle of the process.

If you already setup 1.00 just override ztools by the 1.00c version. There's no changes in the config files.

### 1. Added NSCB.exe

NSCB.exe is a small .net console app that opens NSCB.bat inside itself when it's in the same folder. It supports Drag and Drop for auto mode and allows to hook NSCB to the windows bar or the start section in windows 10. First version doesn't support configurations though a second one will at least allow redirection via a config file.

Information on how to setup NSCB.exe and source here. By recompiling the source you can change the icon or paths NSCB.exe points into. I'll add some configuration choices in the future.

https://github.com/julesontheroad/NSC_BUILDER/tree/master/py/Documentation%20and%20Resources/NSCB.exe

### 2. Direct xci and xcz installation over mtp from local sources

NSCB 1.0 can install now nsp, nsz, xci, xcz over usb-mtp with the help of DBI directly on the switch without preconversion. It supports multiprogram xci and multicontent xci too.

Multicontent xci or nsp will virtually be separated in several files which will trigger different installations per content.

Checking on content installed for each content in the multifile wasn't yet implemented but will be on 1.01.

### 3. Direct nsp installation patching from local sources and standard crypto option

If activated NSCB 1.0 will patch directly the stream during installation without preconversion to lower keygeneration if the reported FW on the Switch is lower than the required by the installed files.

Additionally a standard crypto option was implemented, if activated trough the configuration files will always be installed as ticketless, removing titlerights on the fly.

### 4. Direct xci and multi xci creation directly on the SD over mtp from local sources

With NSCB 1.0 xci and multixci can be created directly on the SD from xci and nsp sources. If sources include nsz or xcz the xci will be created first locally on the PC and transfer to the Switch.

The reason for this behavior is that zstd decompression and re-encryption wasn't yet implemented on the mtp api hook.

### 5. Added folder-walker on all modes for local and remote Resources

Folder walker will allow you to search on any folder on pc or google drive. The first folder-walker step is searching a folder, if the folder is the final folder on the path it will change automatically to the file phase.

In case the folder isn't the end of the path you change to file phase by pressing "E" as the file-picker instructions specify. On the local sources walker a second option is offered "R" or recursive, this option will show files in current folder and in it's subdirectories, beware since it'll be slower if there's hundreds of thousands of files between the directory and subdirectories.

The walker will filter file extensions depending on the supported extensions on each mode, while mtp filetransfer won't hide extensions other modes may only show nsp,nsz,xci,xcz, ... depending on what each mode supports.

Folder-Walker also supports search filters and file sorting by size, date and name.

### 6. Added local library support for all NSCB modes

Al local modes will now use the local libraries if setup, With support for search filters and file sorting by size, date and name.

### 7. Added server and interface trigger on the main NSCB bat

This function will only work properly if **run minimized** is activated. Both will work properly with the noconsole option too but **run minimized** is needed.

Note: When moving from noconsole to console-attached versions of server and interface run the option twice, the first time after the change is possible that output doesn't show on the console, from the second time onwards you should be able to see output properly.

### 8. Bugfixing and small stuff

- Fixed issues when launching the interface with custom browsers.
- Fixed issues on server, specifically ssl keys loading and changed the preset so it uses http://localhost:9001 by defect and shows the console.
- Added FW 10.1 RSV strings
- Added versions.json to DB and consolidation between versions.txt and versions.json. Also added protection to versions.txt in case the one in the source is corrupted.
- Several small bugfixes here and there
