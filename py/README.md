# Nintendo Switch Cleaner and Builder (NSC_Builder)
https://github.com/julesontheroad/NSC_BUILDER 

## 1. Description

NSC_Builder is the merged Project that continues xci_builder and Nut_Batch_Cleaner.

NSC_Builder is based both in the works of Blawar’s nut.py and Luca Fraga’s hacbuild and powered by “squirrel” a nut’s fork with added functions that removes the CDN based functions from nut while tweaks the title-rights modification functions and adds some useful ones for file management.
From version v0.8 the program doesn’t rely on hacbuild for xci generation and new code was made for a better integration on squirrel.

Squirrel will get a new github repository soon and be packed as exe for NSCB from beta v0.8. Old squirrel code can be seen in the NSCB main repository, new code will be published in it’s own repository at the end of NSCB beta phase after some cleanup it’s done on it’s code.

## 2. What’s the meaning of “REMOVING TITLE RIGHTS”.
When you remove the titlerights encryption from nsp files you can install the games without any need of tickets, which leaves a smaller trackable footprint on your console, providing you aren’t sending telemetry data to Nintendo.
It also helps in the conversion from nsp to xci files allowing to not install tickets externally.

## 3. What can I do with this program?

Current version of the program allows you to:
1.- Make multi-content xci or nsp files.

2.- Erase titlerights encryption from nsp files.

3.- Build xci files without the “update partition” which means they take less space on your storage.

4.- Take off deltas from updates

5.- Split multi content back into xci or nsp files

6.- Change the packing of the content between xci and nsp 

7.- Lower the Required System Version to the actual encryption of the game.

8.- Lower the masterkey needed to decrypt a game.

9.- Check out information from a xci and nsp, including the Firmware needed to be able to execute it, the game info, the size of the nca content…

10.- Check data from nacp and cnmt files without extracting them from nsp\xci

10.- Repack xci and nsp content in formats compatible with fat32

11.- Mass build xci files and nsp files in single and multi content format

12.- Rename nsp,xci files to match it's content

13.- Verify nsp, nsx, xci y nca files

14.- Output information in text format

15.- Extract content of nsp files and secure partition of xci files

16.- Set jobs for later in multi mode

17.- Separate jobs by based-titleid in multi mode

18.- Remove bad characters from filenames (sanitize) or convert asian names to romaji

19.- Extract nca file contents for base games and dlcs or extract ncas as plaintext

20.- Joiner for xc*,ns* and *0 fat32 files

## 4. Batch modes:

The batch has 2 modes:

- auto mode: you drag nsp files individually or folders with several files over the batch to enter in auto mode.

- manual mode: you double click the batch and you can build a list of files to process.

The behavior of the auto-mode is configured trough the “Configuration menu in manual mode”.

## 5. Manual mode options:

- MODE 0: Configuration mode. Let’s you configure the way the program works in both auto and manual mode.
- MODE 1: Indidual packing. Let’s you process a list of files and pack them individually
  * Pack as nsp\xci
  * Supertrimm xci files
  * Rename xci or nsp files
  * Rebuild nsp files in cnmt order and add cnmt.xml
  * Verify nsp,xci files
- MODE 2: Multi packing. Let’s you pack a list of files in a single xci or nsp file.
  * Separate files by basedid
  * Set up jobs for later
  * Process previous jobs
- MODE 3: Multi-Content-Splitter. Let’s you separate content to nsp and xci files.
- MODE 4: File-Info. Let’s you see and export several info about nsp and xci files
  * 1. Data about included files in nsp\xci
  * 2. Data about content ids in file
  * 3. Nut info as implemented by nut by blawar
  * 4. Information about firmware requirements and other game data
  * 5. Read cnmt file from meta nca
  * 6. Read nacp file from control nca
  * 7. Read npdm file from program nca 
  * 8. Verify files with ability of detecting NSCB changes over them
- MODE 5: Database Mode. Let’s you mass output information
- MODE 6: Advanced Mode.
  * 1. Extracts all contents from a nsp\xci
  * 2. Extracts all contents from a nsp\xci in raw mode
  * 3. Extracts all contents from a nsp\xci in plaintext
  * 4. Extracts files from nca inside a nsp\xci   
- L: Legacy Mode. Old functions

## 6. Configuration mode:
### Auto Mode options. (Affects only Auto-Mode)
#### REPACK configuration
- NSP 
- XCI
- BOTH
#### FOLDER'S TREATMENT
- Repack folder's files individually (single-content file)
- Repack folder's files together (multi-content file)
#### RSV patching configuration
- Patch Required System Version if it’s bigger than encryption
- Don’t patch Required System Version if it’s bigger than encryption
#### KEYGENERATION configuration
- Set the maximum keygeneration (encryption) the files are allowed to have.
### Global options. (Affects how the program works globally)
#### Text and background COLOR
- Let’s you choose the colours of the cmd window
#### WORK FOLDER's name
- Let’s you choose the name of the work folder
#### OUTPUT FOLDER's name
- Let’s you choose the name and location of the output folder
#### DELTA files treatment
- Let’s you choose if you’re going to pack delta NCA files or not. Set to false by default.
#### ZIP configuration (currently unused)
- Let’s you choose if you want to create a zip storing some file information. Set to false by default.
#### AUTO-EXIT configuration
- Let’s you choose if the cmd window closes after completing the job.
#### KEY-GENERATION PROMPT
- Let’s you choose if you want to see a prompt asking you to patch RSV and keygeneration in manual mode.
#### File stream BUFFER
- Buffer for file-stream operations
#### file FAT32\EXFAT options
Pack xci or nsp in fat32 compatible formats or exfat format.
- Change CARD FORMAT to exfat (Default)
- Change CARD FORMAT to fat32 for SX OS (xc0 and ns0 files)
- Change CARD FORMAT to fat32 for all CFW (archive folder)
#### How to ORGANIZE output files (currently unused for new modes)
- Organize files separetely (default)
- Organize files in folders set by content
#### Set New Mode or Legacy Mode
- Use new more advance methods (default)
- Use old file processing methods
#### ROMANIZE names when using direct-multi
- Convert names to romaji (default)
- Read names from file and keep asian namings when they're read

## 7. Important

This program attempts to modify the minimum data possible in nsp and xci files, due to that reason it requires signature patches to ignore both signatures at NCA headers. Firmwares that already include them are:
- SX OS
- ReiNX
https://github.com/Reisyukaku/ReiNX/releases
- For Kosmos use joonie86 sigpatches and Hekate5.0 or joonie86 Hekate Mod "a.k.a J"
https://github.com/Joonie86/hekate/releases/tag/5.0.0J
- For atmosphere use the4n sigpatches
https://gbatemp.net/attachments/2-0-0-8-1-0-zip.170607/

To install multi-nsp you need a installer compatible with them. Reported compatible installers are:
- SX OS rom-menu
- SX OS installer
- Blawar’s tinfoil:
https://github.com/digableinc/tinfoil
- Blawar’s lithium:
https://github.com/blawar/lithium

## 8. Requirements 

- A computer with a Window's OS is needed
- Fill keys_template.txt on the ztools folder and rename it to keys.txt
  You can get a full keyset with Lockpick if your console is at FW6.2 or 
  A friend can lend you the needed keys.
  If you want to add the xci_header_key a friend will need to lend it to you.
  https://github.com/shchmue/Lockpick/releases

## 9. Limitations 
- You can't make multi-content xci files with more than 8 games. It'll give error when loading in horizon. I suspect it may be a qlauncher limitation so it could work with theme mods but INTRO didn't test it.
Note: This means “games”, updates and dl car not hold by that limitation.
- Title-rights remove dlcs give a message prompt of incomplete content for some games from 6.0 onwards, that message can be skipped and the dlcs will work fine despite the prompt.

## 7. Thanks and credits to 

NSC_Builder is based on

a.) Nut: Without the work of "blawar" one of the most talented Switch sceners nothing of this would be possible at this point.
https://github.com/blawar/nut

b.) Hacbuild: The xci repacking functions are based on hacbuild's code, made by LucaFraga

- Original hacbuild: https://github.com/LucaFraga/hacbuild) by LucaFraga

- Revised hacbuild by me: https://github.com/julesontheroad/hacbuild

c.) Big thx to 0Liam for his constant help.

d.) pyNCA3,pyNPDM,pyPFS0,pyRomFS libraries adapted from pythac (made by Rikikooo)

Also thanks to:

AnalogMan. He made splitNSP.py, figured the needed block size for Horizon format splitted nsps (wich differs from the splitted xci block size) and the need to archive the folders)
https://github.com/AnalogMan151/splitNSP/releases

Thx to MadScript77 his great suggestions,specially the idea of profiles for the batch.

Thx to 0mn0 and the old SH crew for always being helpful.

Thx to evOLved, Cinnabar and a certain dragon for their help and good suggestions.

Also thanks to all members from gbatemp, elotrolado.net and my friends at discord ;)
