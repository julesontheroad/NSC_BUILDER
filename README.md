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
d.) nstool: Program with similar functions as hactool but with more file options
nstool was made by jakcron
https://github.com/jakcron/NNTools/tree/master/programs/nstool
e.) 7zip: Program meant to compress and extract files in several formats
7zip was made by Igor Pavlov
https://www.7-zip.org/

