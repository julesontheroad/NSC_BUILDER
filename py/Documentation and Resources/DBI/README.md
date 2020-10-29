# DBI from DuckBill
NSCB MTP support was tested from DBI version 125-175. 
You can  find the latest recommended DBI version on the dbi repository by Rashevskyv
https://github.com/rashevskyv/dbi/releases

## 1. What's DBI?

DBI is a installer in a similar fashion as old tinfoil by Adubbz with extended functions and a MTP responder mode that allows access to the Nintendo Switch via the MTP protocol to transfer files between Switch and pc and to get several information from the switch like installed games, storage used, firmware on the Switch, etc...

DBI was created and maintained by the rusian developper Duckbill.

Each folder represent a DBI version, included is the DBI .nro and a nsp that includes the full romfs (not a redirector), use what you prefer but the nsp allows going home without closing the install, is safer to the filesystem and can be overclocked with sys-clk to improve performance.

## 2. Why do you include this on your github?

Since NSC_Builder v0.99, NSCB features a new "m" mode which is a mtp manager meant mainly for DBI though a couple of functions work with blawar's tinfoil.

## 3. Why make a mtp installer?

While mtp means you can install directly from the windows manager that has several caveats. For example the mtp protocol means that a transfer bigger than 4GB needs to be transfered without a specific size which makes the windows explorer error on timeout though the transfer is actually completed.

By keeping track of the stream NSCB can close the transfers when actually completed.
Other interesting function that NSCB makes use of is to search for new updates on games installed and autoupdate the console via SD, keep track of the used space while installing, reclaim space by deleting new updates, etc... **It also supports direct installation from remote locations via USB like google drive and 1fichier.**

## 4. NSCB_MTP Full list of features

#### I.- Installer

##### a) Local files installer

  * Installation via queue for **nsp, nsz (directly)** and **xci (preconversion)**
  * Select installation medium **(SD\EMMC)**
  * **Pre-verification of files** (disabled,level2,hash verification)
  * **Check space on device before installing** each file and optionally **change installation medium** (SD\EMMC) if the other has space left and the targetted one runs off space.
  * **Check keygeneration required by files** vs fw reported from console, skip installation if the keygeneration required is bigger than the available. Optionally patch the file pre-installation.
  * Optionally **check if game is already installed and skip installation** if that's the case.
  * Optionally check if the same update id is installed, check version installed and if the installed version is bigger skip installation while if it's smaller predelete the old update to reclaim space and procede to the installation.
  * Optionally **install prepatched nsps when attempting to install a nsp that requires a higher keygeneration.**
  * Preconvert xci\xcz to install on the system.

##### b) Remote location installer

  * Install nsp and nsz directly from google drive and 1fichier

#### II.- File transfer

  * Transfer any file from local or remote locations.

  * DBI allows transfers of more than 4GB via mtp autoarchiving in Nintendo format, that means the transfer mode can transfer with ease xcis or movies to the setup locations on the SD.

#### III.- Auto-updater.

  * Take a local library or google drive library and check if it has new updates or dlcs for the installed games, if it does autoupdate the console.
  * You can let the program applied updates automatically or select between the ones detected.
  * Note: If you installed games previously on this mtp sesion disconnect the mtp responder first and reconnect again to get accurate information since installed games data is parsed once per session.

#### IV.- Uninstaller.

  * Identifies installed games,updates and dlcs and allows them to be removed via a selector.

#### VI.- Content dumper.

  * Allows to dump games, updates and dlcs to the setup libraries.

#### VI.- Archived games cleaner.

  * Identifies archived games and allows to clean them up.

#### VIII.- Information

  * Device information
  * Check installed and archived games
  * Search new updates and dlcs for the installed games and xcis on the SD versus nutdb
  * Search new updates and dlcs for the  archived games versus nutdb

#### IX.- Savegames

  * Detect empty registries and clean them up
  * Dump savegames in JKSV zip format
  * Adds the date of the dump to the name of the file so several dumps don't collide.
  * Optionally add **[titleid]** and **[version]** to the name of the Files
  * Optionally store the files in folders per game or inline

#### X.- Generate SX autoloader files

  * Can generate sx autoloader cache files for any path on the SD if titleid is listed. That includes non scanned paths.
  * Can generate sx autoloader cache files for any path on a HDD if connected and send them to the appropiate folder on the SD.
  * Can ensure autoloader files won't collide between the SD and the HDD.
  * Note: While the autoloader works on archived files and installed placeholders the placeholder takes priority so the xcis are loaded after an error, that's the reason the placeholder won't be created automatically.
  * Note 2: As an alternative NSCB can create xci placeholders, which will load a gamecard placeholder which is appropiate for the autoloader. This xcis will be loaded to a path scanned by rommenu and can be deleted after.
  * Note 3: Alternatively you can make the first xci mounting from sx installer file browser.

## 5. How to setup each library type

* To get full support for every function on NSCB mtp mode you'll need to setup several library files, examples for this files can be found in zconfig. You'll have to edit the example and delete the example tag in the file name. Specifically mtp mode makes use of the files depicted in this section. Bellow you can find the meaning of each file and how to set it up.

  * **mtp_download_libraries_example.txt > mtp_download_libraries.txt**

    > Libraries to setup the dumps and savegames and in general files the pc receives from the Switch.

    Setup: **library_name|path**

    Example: **Dumps|C:\Dumps**

  * **mtp_SD_libraries_example.txt > mtp_SD_libraries.txt**    

    > Libraries to setup the folders in which the switch will receive files pushed with the transfer function.

    Setup: **library_name|path**

    Example: **SD_XCI|1: External SD Card\sxos\xci**

   As you can see the SD locations starts with **1: External SD Card\** this is the name of the SD mount DBI makes on your pc, start your locations on the sd with that string.

  * **mtp_source_libraries_example.txt > mtp_source_libraries.txt**    

    > Libraries to setup the local folders from your pc that will be used by the autoupdate function to search for new files, when used in local mode.

    Setup: **library_name|path|Update**

    Example: **BASE|C:\NSP\BASE|FALSE** or **UPDATES|C:\NSP\UPDATES|TRUE**

   As you can see a **Update** parameter is added, this sets up what folders are scanned in the autoupdate function. If **TRUE** the folder is scanned if **FALSE** it won't get scanned. The non scanned libraries will get used by the installer and transfer mode in the future.

  * **remote_libraries_example.txt > remote_libraries.txt**    

    > Libraries to setup the google drive folders that will be used by the remote installer, remote autoupdater and remote transfer functions.

    > It will also be used in the NSCB Drive Mode and in the library function from NSCB Web Interface.

    Setup: **library_name|path|TD_name|Update**

    Example: **BASE|drive:/base|TD_Name|FALSE** or **UPD|drive:/updates|None|TRUE**

  The **Update** parameter sets up what folders are scanned in the autoupdate function. If **TRUE** the folder is scanned if **FALSE** it won't get scanned. The non scanned libraries are used by the remote installer and remote transfer functions.

  The **TD** parameter is used when your files or folders are in a TeamDrive or Shared Drives as are called currently. If your files aren't in a TD input **None** there or **||**. With double bar it'll look as  **UPD|drive:/updates||TRUE**

  Remember that **drive** is your token name.

  * **remote_cache_location_example.txt > remote_cache_location.txt**    

    > Folder in your google drive account where public files are stored to avoid quota and get a better support on the google drive API. Is recommended for the Interface and required for the mtp mode when using public links.

    Setup: **library_name|path|TD_name**

    Example: **cache|token:/cache|** or **cache|drive:/cache|TDName**

    As you can see if you don't have a TD just add a **|** at the end, you can also add **None** if you have a TD add your TeamDrive name.

## 6. How to setup auth for google drive
To enable the google drive api you need to go here https://developers.google.com/drive/api/v3/quickstart/python and press on **Enable the drive api**, select **Desktop App**, press **Create** and the press **Download Client Configuration**, you'll get a credentials json.

You can use that file to generate tokens for any account, but you'll get a message of not verified app if you use it with a different account. **This is unrelated to NSCB since you're using your own app, setup with that credentials file**

Once a token is generated you can delete the credentials file though you can also have several files renamed as **token_name.json** Token name is the name of the token you plan to setup on the next step.

**To setup the token, open NSCB go to configuration and google drive configuration**, then press 1 to register an account, it'll ask you the name of the token, once you input that a browser will be open and you'll log into the account you mean to setup.

**The token name is important** NSCB uses your token as if it was a path letter, so a token called **mydrive** will be able to setup locations such as **mydrive:/Switch/nsp**

## 7. How to setup auth for 1fichier

For 1fichier auth you need to store the 1fichier token in zconfig/credentials with the name **_1fichier_token.tk**

To get the token you need a 1fichier account, then in this page https://1fichier.com/console/params.pl you'll find a section called *API Key*, press in Enable API usage, get the key and paste it in an empty txt file, then rename the file to **_1fichier_token.tk**

## 8. Does it support tinfoil?

During the initial testings I couldn't get tinfoil to be recognize by the api, unlike nx-mtp and DBI installer. This changed by using the driver present in this nut released:
https://github.com/blawar/nut/releases/tag/v2.7

Either way even with the driver I had issues in several functions, and my installer just makes tinfoil hang up so the support is limited to the info functions, which will tell you the new updates for the device if using tinfoil.

Future versions may support tinfoil with a mixed approach by using the usb installation protocol to install and the mtp api to get console information.

## 9. Limitations

Currently NSCB can't make installations from patched streams, this means installing xci files or keygeneration patched files. This is something that will be worked on future versions.

Direct remote installation from 1fichier and google drive doesn't support pre-verification this will be solved soon. The reason being I didn't finish porting verification to the NSCB google drive API.
