                 __       __          __       __             __                          
    ____  __  __/ /_     / /_  ____ _/ /______/ /_      _____/ /__  ____ _____  ___  _____
   / __ \/ / / / __/    / __ \/ __ `/ __/ ___/ __ \    / ___/ / _ \/ __ `/ __ \/ _ \/ ___/
  / / / / /_/ / /_     / /_/ / /_/ / /_/ /__/ / / /   / /__/ /  __/ /_/ / / / /  __/ /    
 /_/ /_/\__,_/\__/____/_.___/\__,_/\__/\___/_/ /_/____\___/_/\___/\__,_/_/ /_/\___/_/     
                /_____/                         /_____/       
-------------------------------------------------------------------------------------
=============================     BY JULESONTHEROAD     =============================
-------------------------------------------------------------------------------------
"                              POWERED WITH NUT BY BLAWAR                           "
                                     Version 0.21
------------------------------------------------------------------------------------------
MORE AT: https://github.com/julesontheroad/NUT_BATCH_CLEANER                   
also check xci_batch_builder at: https://github.com/julesontheroad/-XCI-Batch-Builder-
and check blawar's NUT at:  https://github.com/blawar/nut 
and also check blawar's awesome installer in the works at https://github.com/blawar/sysnut
------------------------------------------------------------------------------------------
---------------
0. Changelog
---------------
v0.40- While I finish NX_Builder I solved couple of naming issues.
       1.- Now you don't need [titleid] in filename.
       2.- Solved issues with special characters like !,+,&,$... Added correction for
       a bunch of them if you need to add more edit ztools/safename.bat
       Example: If you want to replace @ for a input:
       set fileinput=%fileinput:@=a%
       Or to delete it:
       set fileinput=%fileinput:@=%
       You'll probably see the first version for NX_Builder either trough the weekend
       or at the beginning of next week.
       NOTE: This version is using a function of my modified NUT libraries for NX_Builder
       so don't change the config to use the whole NUT.
v0.30- Added new options in zconfig.
       > Option 4: Way the items are organized.
         * line: scattered in output folder
         * folder: in folders according to game name
       > Option 5 and option 6: Output folders for xci and nsp. As default using
         a common folder for both.
       > Option 7: Preserve stripped files from the nsp as a .zip file for future
         restore function. (True by default)
       > Option 8: Replace original file with clean/converted files.As default false.
         TAKE CARE WITH THIS ONE. BETTER CHECK ALL WORKS FINE BEFORE ACTIVATING IT.
       Added option to erase list.txt in manual mode.
v0.21- Fixed issue with manual mode not detecting the user repacking input correctly
       Added better check for dlcs and updates, according to id
       Added another config parameter to "nsp_cleaner_options.cmd" (xnsp_ifnotgame)
       > This parameter serves to repack dlcs and updates as nsp if processing list as xci only.
         Options are:
         * true: repack dlcs and updates as nsp
         * false: skip dlc and update repacking when exporting as xci.
v0.2 - Added xci repacking. You can now repack as:
       *xci
       *nsp
       *both formats
     - Added nsp_cleaner_options.cmd at zconfig. It'll let you configure the repack
       option for auto-mode as (xci,nsp,both)
     - If xci repacking filenames with [UPD] tag are skipped
     - If with xci repacking an error is logged it activates a fallback and an
       xci + [lc].nsp are build.
     - Now we support subfolders, thanks to MadScript77 for the advice on how to 
       set it as in the other great advices he gave about the code.
     - For manual mode you can allways choose what format to build from the current
       list.
     - More changes coming soon.
v0.1 - First official release

NOTE: STILL DIDN'T HAVE TIME TO FIX THE WEIRD CHARACTERS ERROR
      also repacking a batch to get python libraries dependencies. I believe they're
      only "urllib3" and unidecode but added commented the other ones from nut if
      you want to install them take off the "::"  
---------------
1. Description
---------------
Nut_batch_cleaner uses the awesome function "REMOVE_TITLE_RIGHTS" from nut by blawar
this function let's you erase the titlerights encryption from nsp files.
Tinfoil and SX installer will install the ticket either way so for it to not stay in 
your system you need to erase the ticket and cert from the nsp, this batch will take
care of that.

This batch automates a process you can do yourself with nut and let's make clean nsp
files that you can also pass for XCI-Batch-Builder to generate xci files that don't
need a ticket.

This batch fetures numerous new options that will be implemented in the future version
of XCI-Batch-Builder.

The batch has 2 modes:

- auto mode: you drag nsp files individually or folders with severall nsp files and
you get clean nsp files in "o_clean_nsp" folder
Note: auto mode won't process subfolders yet.
- manual mode: you double click the batch and uou can build a list of nsp files to
clean, you can even erase items via batch or directly in the list before starting.
You can resume the list if you close the window before compleating all the cleanings.
It also fetures a check that will stop the cleaning for a file if the titlerights
can't be stripped from it. In this case it will generate a log.txt with the file name.
If an error is found that file is skipped an the batch continues processing the queue.
---------------
2. Important
---------------
The program incorporates a build of nut.py with only the "REMOVE_TITLE_RIGHTS" function
and required libraries, the reason is to remove the python libraries requirements for
normal nut to facilitate the life of most users and to eliminate the CDNSP functions
so it can be shared in places CDNSP isn't allowed.
You can make it to work with normal nut by changing nut location for your NUT location
in nsp_cleaner_options.txt inside zconfig.
The other options are not enabled yet (sorry about that).
---------------
2. Requirements
---------------
- You'll need to have Python installed for the program to work correctly
- You need to fill the keys.txt file inside the ztools folder.
------------------------
3. Thanks and credits to 
------------------------
Nut_batch_cleaner is based on

a.) Nut: Without the work of "blawar" one of the most talented Switch sceners nothing of this would
be possible at this point. Check his awesome projects:
https://github.com/blawar/nut
https://github.com/blawar/sysnut

b.) hactool: Program which function is give information, decrypt and extract a lot of different kind of files us by the NX System.
Hactool was made by SciresM
https://github.com/SciresM/hactool
c.) nspBuild: Program meant to create nsp files from nca files. 
nspBuild was made by CVFireDragon
https://github.com/CVFireDragon/nspBuild
Thx to MadScript77 and BigJokker for their great suggestions.
Also thanks to all members from gbatemp, elotrolado.net and my friends at discord ;)
