# NSC_Builder v0.99 - Changelog

![DeviceTag](https://img.shields.io/badge/Device-SWITCH-e60012.svg)  ![LanguageTag](https://img.shields.io/badge/languages-python_batch_html5_javascript-blue.svg)

## *Introducing MTP Mode a mtp manager for DBI Installer*

**DBI is a installer made by Rashevsky and the Keffir** Team in a similar fashion as old tinfoil by Adubbz with extended functions and a MTP responder mode that allows access to the Nintendo Switch via the MTP protocol to transfer files between Switch and pc and to get several information from the switch like installed games, storage used, firmware on the Switch, etc...

When you open the nro or installed DBI program on your switch and run the **MTP responder** option you'll be able to connect your switch via usb to your pc, allowing NSC_Builder v0.99 to work together with DBI an access your Switch providing a whole lot of functions.

The tested version of DBI is 1.25, which can be downloaded as part of the following keffir release:

https://github.com/rashevskyv/switch/releases/tag/456

It can also be downloaded individually as nro or nsp here:

[DBI_1.25.nsp](../DBI/1.25/DBI_0591703820420000.nsp)
[DBI_1.25.nro](../DBI/1.25/DBI.nro)

More information about DBI here:

[DBI and mtp Readme](../DBI/README.md)

## *Changelog*

### 1. New Mode "M" - mtp a MTP manager for DBI

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

## 3. New things added to the File Info Web Interface

* Support to read xc0 and ns0 files (missning nmpdm reader and verification)
* Support to read files from google driver
* Direct link reader support for interface meant to use with public google drive links
* Ability to avoid quota in public drive links by setting a remote cache library, which will clone to that folder on google drive the link before reading it's information.
* Ability to setup libraries to search and load information from them.
* Ability to open the selected picture in the gallery in a new window to zoom it
* Ability to detach the gui from the console with the "noconsole" parameter which will load the console information in a new side tab on the Interface.
* Ability to open several interface windows at the same time by opening different ports per Interface.
* Ability to setup host and fixed port for the interface.

## 4. Test server concept

* The new Server.bat can load a new server concept with the functions from the gui. This server will not open a windows but it'll generate the webpage every time you open the specified port and host.
* The server allows to setup ssl connections by adding a valid key.pem and certificate.pem in zconfig and changing it's ssl parameter. That will connect to it using https: instead of http and secure sockets.
* The server can load files using the library functions or if open locally the normal window selector. The selector will be hidden if you open NSCB.html but will be visible with main.html
* The server can be ran with a hidden console too.
* It being a proof of concept the interface isn't fully adapted to widescreen yet since and it doesn't have any kind of account validation so secure it if you plan access trough the internet.

## 5. Bugfixes

* Added data for new firmware.
* Fixed ticket class issue related to #132
* Fixed issue where the nacp reader wasn't showing the proper information on certain parameters on gui and cmnd. Only the reader, patching functions or other nacp based functions were setup correctly.
* Added support to new sig1 key thanks to 0Liam.
* Several other stuff I don't remember since a lot of fixes and modifications were done to the beta branch since 0.98

## 6. How to setup each library type

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

    > Libraries to setup the local folders from your pc that will be used by the autoupdate function to search for new files, as well as with the install and transfer functions.

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

  * **local_libraries_example.txt > local_libraries.txt**    

    > Folder where your local library is stored. This is used currently by the HTML interface local libraries

      Setup: **library_name|path**

      Example: **Folder1|C:\Nintendo**

  * **download_libraries_example.txt > download_libraries.txt**    

    > This is used on the Drive mode to setup folder where the program will download or generate files

    Setup: **library_name|path**

    Example: **Folder1|C:\Downloads**

## 7. How to setup auth for google drive
To enable the google drive api you need to go here https://developers.google.com/drive/api/v3/quickstart/python and press on **Enable the drive api**, select **Desktop App**, press **Create** and the press **Download Client Configuration**, you'll get a credentials json.

You can use that file to generate tokens for any account, but you'll get a message of not verified app if you use it with a different account. **This is unrelated to NSCB since you're using your own app, setup with that credentials file**

Once a token is generated you can delete the credentials file though you can also have several files renamed as **token_name.json** Token name is the name of the token you plan to setup on the next step.

**To setup the token, open NSCB go to configuration and google drive configuration**, then press 1 to register an account, it'll ask you the name of the token, once you input that a browser will be open and you'll log into the account you mean to setup.

**The token name is important** NSCB uses your token as if it was a path letter, so a token called **mydrive** will be able to setup locations such as **mydrive:/Switch/nsp**

## 8. How to setup auth for 1fichier

For 1fichier auth you need to store the 1fichier token in zconfig/credentials with the name **_1fichier_token.tk**

To get the token you need a 1fichier account, then in this page https://1fichier.com/console/params.pl you'll find a section called *API Key*, press in Enable API usage, get the key and paste it in an empty txt file, then rename the file to **_1fichier_token.tk**
