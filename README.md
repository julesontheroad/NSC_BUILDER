# Nintendo Switch Cleaner and Builder (NSC_Builder)
![DeviceTag](https://img.shields.io/badge/Device-SWITCH-e60012.svg)  ![LanguageTag](https://img.shields.io/badge/languages-python_batch_html5_javascript-blue.svg)

**Temporarly archived:** Currently i don't have the time to work on this repository, i will reopen it and reactivate issues if i have something to commit or time to work regularly on the project. The titledb fork will still continue to update and i will probably compile a new version including the latest master, don't think it had much changes since the last release i did but i'd probably compile it to include the latest keygeneration changes.

**Update:** Leaving it open for commits.

## 1. Description

**Nintendo Switch Cleaner and Builder**: A multi-purpose tool for interacting with Switch game files - a "Switch-Army Knife". Written in Python, Batch, and HTML. Originally developed to remove titlerights and create multicontent NSP/XCI files, though over time has expanded to have significantly more features, specializing in batch processing and file information.

NSC_Builder is based on the work of blawar’s nut.py and LucaFraga’s hacbuild. The core library, which is known as `squirrel`, was originally a nut fork, though over time it has added significant functionality and can be considered its own program. NSCB versions > 0.8 no longer rely on hacbuild for XCI generation, rather using its own code.

## 2. What does it mean to *REMOVE TITLERIGHTS*?
This is also known as converting to use *standard crypto* - it means that you have repacked the contents to be installable without a ticket being added to the Switch's database. Theoretically, standard crypto files leave a smaller traceable footprint on your console, provided you're not sending other telemetry to Nintendo. Important: This does NOT mean you can run preloads or dumped content that doesn't have a ticket (sometimes seen as NSX files).


## 3. What can I do with this program?

Current version of the program allows you to:

1.- Make **multi-content** xci or nsp files.

2.- **Erase titlerights** encryption from nsp files.

3.- **Build xci files** without the “update partition” which means they take less space on your storage.

4.- Take off **deltas** from updates

5.- **Split multi content** back into xci or nsp files

6.- Change the packing of the content between xci and nsp

7.- **Lower the Required System Version** to the actual encryption of the game.

8.- Lower the masterkey needed to decrypt a game.

9.- **Check out information** from a xci and nsp, including the Firmware needed to be able to execute it, the game info, the size of the nca content…

10.- **Check data from nacp and cnmt files** without extracting them from nsp\xci

10.- Repack xci and nsp content in formats compatible with **fat32**

11.- **Mass build** xci files and nsp files in single and multi content format

12.- **Rename** nsp,xci files to match it's content

13.- **Verify** nsp, nsx, nsz, xci and nca files

14.- Output information in text format

15.- **Extract content** of nsp files and secure partition of xci files

16.- Set jobs for later in multi mode

17.- Separate jobs by based-titleid in multi mode

18.- **Remove bad characters from filenames** (sanitize) or convert asian names to romaji

19.- Extract nca file contents for base games and dlcs or extract ncas as plaintext

20.- **Joiner** for xc*,ns* and 0* fat32 files

21.- **Compression** of nsp files into .nsz files

22.- **Graphical interface** for file information trough a gui running on chromium\chrome for local files and files on google drive

23.- **Restoration** of nsp\xci modified with NSC_Builder to their original game nca files.

## 3.1 With the help of DBI installer it can:

24.- **Install or transfer files** to mtp via switch locally, from google drive (auth and links) or from 1fichier

25.- **Generate and transfer** xcis and multicontent xcis from pc to switch

26.- **Autoupdate** your Nintendo Switch locally or from google drive

27- **Search new updates and dlcs** for your installed games via nutdb for your installed games and xci in the gamecard

28- **Dump your saves or games** from your Nintendo Switch

29- **Uninstall** your games and delete archived games/placeholders

30- **Generate and transfer SX autoloader files** for automounting your xcis for SD and HDD locations for scannable locations and non scannable by SX OS

31- **Cleanup duplicated SX OS autoloader files** to avoid collision between SD and HDD files

## 4. Batch modes:

The batch has 2 modes:

- **auto mode:** you drag nsp files individually or folders with several files over the batch to enter in auto mode.

- **manual mode:** you double click the batch and you can build a list of files to process.

The behavior of the auto-mode is configured trough the “Configuration menu in manual mode”.

## 5. Manual mode options:

- **MODE 0: Configuration mode.** Let’s you configure the way the program works in both auto and manual mode.
- **MODE 1: Indidual packing.** Let’s you process a list of files and pack them individually
  * Pack as nsp\xci
  * Supertrimm\Trimm\Untrimm xci files
  * Rename xci or nsp files
  * Rebuild nsp files in cnmt order and add cnmt.xml
  * Verify nsp,xci files
- **MODE 2: Multi packing.** Let’s you pack a list of files in a single xci or nsp file.
  * Separate files by basedid
  * Set up jobs for later
  * Process previous jobs
- **MODE 3: Multi-Content-Splitter.** Let’s you separate content to nsp and xci files.
- **MODE 4: File-Info.** Let’s you see and export several info about nsp and xci files
  * Data about included files in nsp\xci
  * Data about content ids in file
  * Nut info as implemented by nut by blawar
  * Information about firmware requirements and other game data
  * Read cnmt file from meta nca
  * Read nacp file from control nca
  * Read npdm file from program nca
  * Verify files with ability of detecting NSCB changes over them
- **MODE 5: Database Mode.** Let’s you mass output information
- **MODE 6: Advanced Mode.**
  * Extracts all contents from a nsp\xci
  * Extracts all contents from a nsp\xci in raw mode
  * Extracts all contents from a nsp\xci in plaintext
  * Extracts files from nca inside a nsp\xci  
  * Patches a game that requires s link sccount
- **MODE 7: File joiner mode.** Joins fat32 splitted files  
- **MODE 8: Compression\Decompression**
  * Compress nsp files into nsz format
  * Decompress nsz files into nsp files
- **MODE 9: File Restoration Mode.** Restores modified files that are verifiable
- **L: Legacy Mode.** Old functions
- **D: GOOGLE DRIVE MODE:**
  * Download Files from google drive
    * Normal Download Function
    * Search filter and library selection
    * Download xci files trimmed or supertrimmed
    * Download nsz files decompressed
  * Check information about the files
- **M: MTP MODE:**
  * Game installation from local files or remote libraries
  * File transfer from local files or remote libraries
    * Normal transfer
    * Generate xci and transfer
    * Generate multi-xci and transfer
  * **Autoupdate** the device via local libraries or google drive libraries
  * **Dump or uninstall files**
    * Dump installed content from the device to the pc
    * Uninstall installed content on the device
    * Delete archived games or placeholders entries from pc
  * **Backup Savegames** in zips following JKSV format
  * **Show device information**
    * Device information shared via mtp
    * Show installed games and xci on device
    * Show new updates and dlc for installed games and xci on device. For accuracy xci has to follow NSCB format including the content_number tags
    * Show archived games/placeholders registries
    * Show list of available updates and dlcs for archived games
  * **Generate SX autoloader files**
    * Generate files for xci on the sd
    * Generate files for xci in a hdd, optionally push and run a collision check with the SD files
    * Push SX autoloader files from library folder
    * Run collision check, cleanup unused SD autoloader files, cleanup colliding autoloader files pointing to HDD (In case a xci with that id is already in the SD)

## 6. Configuration mode:

#### Auto Mode options. (Affects only Auto-Mode)

##### I. REPACK configuration

- NSP
- XCI
- BOTH

##### II. FOLDER'S TREATMENT

- Repack folder's files individually (single-content file)
- Repack folder's files together (multi-content file)

##### III. RSV patching configuration

- Patch Required System Version if it’s bigger than encryption
- Don’t patch Required System Version if it’s bigger than encryption

##### IV. KEYGENERATION configuration

- Set the maximum keygeneration (encryption) the files are allowed to have.

##### V. Global options. (Affects how the program works globally)

##### VI. Text and background COLOR

- Let’s you choose the colours of the cmd window

##### VII. WORK FOLDER's name

- Let’s you choose the name of the work folder

##### VIII. OUTPUT FOLDER's name

- Let’s you choose the name and location of the output folder

##### IX. DELTA files treatment

- Let’s you choose if you’re going to pack delta NCA files or not. Set to false by default.

##### X. AUTO-EXIT configuration
- Let’s you choose if the cmd window closes after completing the job.

##### XI. KEY-GENERATION PROMPT

- Let’s you choose if you want to see a prompt asking you to patch RSV and keygeneration in manual mode.

##### XII. File stream BUFFER

- Buffer for file-stream operations

##### XIII. File FAT32\EXFAT options

Pack xci or nsp in fat32 compatible formats or exfat format.

- Change CARD FORMAT to exfat (Default)
- Change CARD FORMAT to fat32 for SX OS (xc0 and ns0 files)
- Change CARD FORMAT to fat32 for all CFW (archive folder)

##### XIV. How to ORGANIZE output files (currently unused for new modes)

- Organize files separetely (default)
- Organize files in folders set by content

##### XV. Set New Mode or Legacy Mode

- Use new more advance methods (default)
- Use old file processing methods

##### XVI. ROMANIZE names when using direct-multi

- Convert names to romaji (default)
- Read names from file and keep asian namings when they're read

##### XVII. TRANSLATE descriptions from game-info using google translator

- FALSE (default)
- TRUE. Translate japanese, chinese and korean descriptions.

##### XVIII. WORKERS use multi threading for renames and database building

- 1 (default\DEACTIVATED)
- YOUR NUMBER. Uses several workers to do multiple renames or create multiple database strings at the same time

## 7. Gui for file  information:

- **NSCB File_Info** is a html based gui that gives a graphic interface to NSCB info.
  Yes, it has game-icons, pictures and that stuff you guys like.

- Current functions are:

  * **Game Information**. Combines data read from file with eshop data from nutdb
  * **Description:** Description from the eshop (nutdb)
  * **Image Gallery:** Pictures from the eshop (nutdb)
  * **BaseID File-Tree:** Shows the lates version for dlcs and updates associated to the game (nutdb)
  * **Titles:** Advanced Files List from NSCB-new
  * **NACP Reader** from NSCB
  * **NPDM Reader** from NSCB
  * **CNMT Reader** from NSCB
  * **Verification** from NSCB, till Level 2 so it's loaded fast. Use normal NSCB for hashing for now.
  * **Game Information**. Combines data read from file with eshop data from nutdb
  * **Libraries**. Load files from local libraries or google drive, having the library locations setup previously
  * **Direct Links**. Read information from direct links.

- You'll notice some information like BuildIDs is added now, the cnmt was made more readable and I added detection for multiprogram games like Grandia and Hotline Miami

- **Known Issues:**

  * CSS probably needs some work, specially for fullscreen.
  * Upper corner menu is a placeholder
  * NPDM decryption is failing in some games, is on my TODO list
  * Multicontent files (generally xci) may need some work to improve parsing speeds
  * Not reading yet splitted files (ns*,xc*,0*) but will add that soon

- **TODO:**

  * Output css to a file for theming
  * Language translations
  * Porting NSCB functions
  * Let user choose nutdb files

- **How to use:**

  * If you have Chrome or Chromium Installed you're good to go.
  * If you don't want to install those browsers you can use chromium portable.
	1. Get the last version for your system here: https://chromium.woolyss.com/
	2. Create a folder in ztools called "Chromium"
	3. Decompress the chromium files somewhere in your pc and execute "chrlauncher 2.5.6 (64-bit).exe" or whatever is called in your zip to get the needed files downloaded
	4. Move all files to ztools\Chromium and rename "chrlauncher 2.5.6 (64-bit).exe" to "chrlauncher.exe". This takes priority over a chrome\chromium installation
  * Once you have all setup just execute "Interface.bat"
	5. Rememeber you need to fill keys_template.txt in ztools but I imagine you already know that
- I use python:		   
  * Just get latest python 3 and install these dependencies:
	urllib3 unidecode tqdm bs4 tqdm requests image pywin32 pycryptodome pykakasi googletrans chardet eel bottle
  * Now the tricky part, I use the unreleased version of eel that isn't in pypy so go here https://github.com/ChrisKnott/Eel Download the master, seek the folder where  your eel installation is and overwrite the files with the ones in the master.
	If you have trouble finding it try doing again pip install eel it'll tell you is up to date and installed in 'X' folder.
  * Then execute "Interface.bat"
- I use linux or mac:			  
  * Well i tested it on linux and i'll give you a build at a later time, have to admit I didn't test anything on mac though i imagine it works
  * Install python and:
	urllib3 unidecode tqdm bs4 tqdm requests image pycryptodome pykakasi googletrans chardet eel bottle
  * Basically same as before ignoring pywin32 that NSCB uses to set the archive bit in folders
  * Replace the eel files for the ones in the master like explained above.
  * Run squirrel with:
	squirrel.py -lib_call Interface start
  * Or wait a few days for a build if you don't like python

## 8. File_Info Gui examples:

![Picture](https://i.ibb.co/12kCsDk/FI1.png)
![Picture2](https://i.ibb.co/R93H02v/FI3.png)
![Picture3](https://i.ibb.co/HCfTdxj/FI11.png)

## 9. Important

This program attempts to modify the minimum data possible in nsp and xci files, due to that reason it requires signature patches to ignore both signatures at NCA headers. Firmwares that already include them are:
- SX OS
- ReiNX
- For atmosphere you'll need the appropiate sigpatches, which should include the acid patches

To install multi-nsp you need a installer compatible with them. Reported compatible installers are:
- SX OS rom-menu
- SX OS installer
- Blawar’s tinfoil or Lithium:
http://tinfoil.io/Download#download
- DBI Installer from DuckBill
https://github.com/rashevskyv/switch/releases/
- Awoo Installer
https://github.com/Huntereb/Awoo-Installer

To install ncz files you need:
- SX OS installer
- Blawar’s tinfoil:
https://github.com/digableinc/tinfoil
- DBI Installer from DuckBill
https://github.com/rashevskyv/switch/releases/tag/456
- Awoo Installer
https://github.com/Huntereb/Awoo-Installer

## 10. Requirements

- A computer with a Window's OS is needed
- Fill keys_template.txt on the ztools folder and rename it to keys.txt
  You can get a full keyset with Lockpick if your console is at FW6.2 or
  A friend can lend you the needed keys.
  If you want to add the xci_header_key a friend will need to lend it to you.
  https://github.com/shchmue/Lockpick/releases
- The mtp function requires 4.0 or upper but was built with 4.7.2 net frameworks as target. Recommended versions of net frameworks are 4.7.2 and 4.8.0

## 11. Limitations
- You can't make multi-content xci files with more than 8 games. It'll give error when loading in horizon. I suspect it may be a qlauncher limitation so it could work with theme mods but INTRO didn't test it.
Note: This means “games”, updates and dl car not hold by that limitation.
- Title-rights remove dlcs give a message prompt of incomplete content for some games from 6.0 onwards, that message can be skipped and the dlcs will work fine despite the prompt.
- Currently the mtp mode can't patch\convert games on the fly, it requires implementing the ability of patching streams or send the files via sockets from squirrel. One of the 2 options will be implemented in the future.

## 12. Thanks and credits to

**NSC_Builder is based on**

a.) Nut: Without the work of "blawar" one of the most talented Switch sceners nothing of this would be possible at this point.
https://github.com/blawar/nut

b.) Hacbuild: The xci repacking functions are based on hacbuild's code, made by LucaFraga

- Original hacbuild: https://github.com/LucaFraga/hacbuild) by LucaFraga

- Revised hacbuild by me: https://github.com/julesontheroad/hacbuild

c.) The mtp mode relies heavily on DBI installer by DUCKBILL. Specifically it was tested with DBI 1.25

- DBI is included in kefir CFW pack: https://github.com/rashevskyv/switch/releases

- DBI 1.25 is first included in this release: https://github.com/rashevskyv/switch/releases/tag/456

- A copy od DBI can also be found as nro and nsp in the NSCB master's folder called "DBI"

d.) nsz,xcz and ncz specification by blawar: https://github.com/blawar/nsz

e.) Big thx to 0Liam for his constant help.

f.) pyNCA3,pyNPDM,pyPFS0,pyRomFS libraries adapted from pythac (made by Rikikooo)

g.) an adaptation of Pysos from dagnelies is used for some operations: https://github.com/dagnelies/pysos

**Also thanks to:**

Nicoboss for the original nsp and xci compression idea:
https://github.com/nicoboss/nsZip/

AnalogMan. He made splitNSP.py, figured the needed block size for Horizon format splitted nsps (wich differs from the splitted xci block size) and the need to archive the folders)
https://github.com/AnalogMan151/splitNSP/releases

Thx to MadScript77 his great suggestions,specially the idea of profiles for the batch.

Thx to 0mn0 and the old SH crew for always being helpful.

Thx to evOLved, Cinnabar and a certain dragon for their help and good suggestions.

Also thanks to all members from gbatemp, elotrolado.net and my friends at discord ;)


*2020 - JulesOnTheRoad - https://github.com/julesontheroad/NSC_BUILDER*
