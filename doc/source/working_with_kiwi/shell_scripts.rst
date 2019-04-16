User defined scripts
====================

.. hint:: **Abstract**

   This chapter describes the usage of the user defined scripts
   :file:`config.sh` and :file:`image.sh`, which can be used to further
   customize an image in ways that are not possible via the image
   description alone.


KIWI supports up to two user defined scripts that it runs in the chroot
containing your new appliance:

1. :file:`config.sh` runs the end of the :ref:`prepare step <prepare-step>`
   if present. It can be used to fine tune the unpacked image.

2. :file:`images.sh` is executed at the beginning of the image creation
   process. It is run on the top level of the target root tree. The script
   is usually used to remove files that are no needed in the final
   image. For example, if an appliance is being built for a specific
   hardware, unnecessary kernel drivers can be removed using this script.

.. _image-customization-config-sh:

Image Customization via the ``config.sh`` shell script
------------------------------------------------------

The KIWI image description allows to have an optional :file:`config.sh`
bash script in place. It can be used for changes appropriate for all images
to be created from a given unpacked image (since :file:`config.sh` runs
prior to the create step).

Basically the script should be designed to take over control of adding the
image operating system configuration. Configuration in that sense means all
tasks which runs once in an OS installation process like activating
services, creating configuration files, prepare an environment for a
firstboot workflow, etc. The :file:`config.sh` script is called at the end
of the :ref:`prepare step <prepare-step>` (after users have been set and
the *overlay tree directory* has been applied). If :file:`config.sh` exits
with an exit code != 0 the kiwi process will exit with an error too.

See below a common template for `config.sh` script:

.. code:: bash

   #======================================
   # Functions...
   #--------------------------------------
   test -f /.kconfig && . /.kconfig
   test -f /.profile && . /.profile

   #======================================
   # Greeting...
   #--------------------------------------
   echo "Configure image: [$kiwi_iname]..."

   #======================================
   # Mount system filesystems
   #--------------------------------------
   baseMount

   #======================================
   # Call configuration code/functions
   #--------------------------------------
   ...

   #======================================
   # Umount kernel filesystems
   #--------------------------------------
   baseCleanMount

   #======================================
   # Exit safely
   #--------------------------------------
   exit 0

Common Functions
^^^^^^^^^^^^^^^^

The :file:`.kconfig` file allows to make use of a common set of functions.
Functions specific to SUSE Linux specific begin with the name suse.
Functions applicable to all linux systems starts with the name base.
The following list describes the functions available inside the
:file:`config.sh` script.

``baseCleanMount``
  Umount the system filesystems :file:`/proc`, :file:`/dev/pts`, and
  :file:`/sys`.

``baseDisableCtrlAltDel``
  Disable the Ctrl–Alt–Del key sequence setting in :file:`/etc/inittab`.

``baseGetPackagesForDeletion``
  Return the name(s) of packages which will be deleted.

``baseGetProfilesUsed``
  Return the name(s) of profiles used to build this image.

``baseSetRunlevel {value}``
  Set the default run level.

``baseSetupBoot``
  Set up the linuxrc as init.

``baseSetupBusyBox {-f}``
  Activates busybox if installed for all links from the
  :file:`busybox/busybox.links` file—you can choose custom apps to be forced
  into busybox with the -f option as first parameter, for example:

  .. code:: bash

     baseSetupBusyBox -f /bin/zcat /bin/vi

``baseSetupInPlaceGITRepository``
  Create an in place git repository of the root directory. This process
  may take some time and you may expect problems with binary data handling.

``baseSetupInPlaceSVNRepository {path_list}``
  Create an in place subversion repository for the specified directories.
  A standard call could look like this baseSetupInPlaceSVNRepository
  :file:`/etc`, :file:`/srv`, and :file:`/var/log`.

``baseSetupPlainTextGITRepository``
  Create an in place git repository of the root directory containing all
  plain/text files.

``baseSetupUserPermissions``
  Search all home directories of all users listed in :file:`/etc/passwd` and
  change the ownership of all files to belong to the correct user and group.

``baseStripAndKeep {list of info-files to keep}``
  Helper function for strip* functions read stdin lines of files to check
  for removing params: files which should be keep.

``baseStripDocs {list of docu names to keep``
  Remove all documentation, except one given as parameter.

``baseStripInfos {list of info-files to keep}``
  Remove all info files, except one given as parameter.

``baseStripLocales {list of locales}``
  Remove all locales, except one given as parameter.

``baseStripMans {list of manpages to keep}``
  Remove all manual pages, except one given as parameter
  example:

  .. code:: bash

     baseStripMans more less

``baseStripRPM``
  Remove rpms defined in :file:`config.xml` in the packages `type=delete`
  section.

``suseRemovePackagesMarkedForDeletion``
  Remove rpms defined in :file:`config.xml` in the packages `type=delete`
  section. The difference compared to `baseStripRPM` is that the suse
  variant checks if the package is really installed prior to passing it
  to rpm to uninstall it. The suse rpm exits with an error exit code
  while there are other rpm version which just ignore if an uninstall
  request was set on a package which is not installed.

``baseStripTools {list of toolpath} {list of tools}``
  Helper function for suseStripInitrd function params: toolpath, tools.

``baseStripUnusedLibs``
  Remove libraries which are not directly linked against applications
  in the bin directories.

``baseUpdateSysConfig {filename} {variable} {value}``
  Update sysconfig variable contents.

``Debug {message}``
  Helper function to print a message if the variable DEBUG is set to 1.

``Echo {echo commandline}``
  Helper function to print a message to the controlling terminal.

``Rm {list of files}``
  Helper function to delete files and announce it to log.

``Rpm {rpm commandline}``
  Helper function to the RPM function and announce it to log.

``suseConfig``
  Setup keytable language, timezone and hwclock if specified in
  :file:`config.xml` and call SuSEconfig afterwards SuSEconfig is only
  called on systems which still support it.

``suseInsertService {servicename}``
  This function calls baseInsertService and exists only for
  compatibility reasons.

``suseRemoveService {servicename}``
  This function calls baseRemoveService and exists only for
  compatibility reasons.

``baseInsertService {servicename}``
  Activate the given service by using the :command:`chkconfig`
  or :command:`systemctl` program. Which init system is in use
  is auto detected.

``baseRemoveService {servicename}``
  Deactivate the given service by using the :command:`chkconfig`
  or :command:`systemctl` program. Which init system is in
  use is auto detected.

``baseService {servicename} {on|off}``
  Activate/Deactivate a service by using the :command:`chkconfig`
  or :command:`systemctl` program. The function requires the service
  name and the value on or off as parameters. Which init system is in
  use is auto detected.

``suseActivateDefaultServices``
  Activates the following sysVInit services to be on by default using
  the :command:`chkconfig` program: boot.rootfsck, boot.cleanup,
  boot.localfs, boot.localnet, boot.clock, policykitd, dbus, consolekit,
  haldaemon, network, atd, syslog, cron, kbd. And the following for
  systemd systems: network, cron.

``suseSetupProduct``
  This function creates the baseproduct link in :file:`/etc/products.d`
  pointing to the installed product.

``suseSetupProductInformation``
  This function will use zypper to search for the installed product
  and install all product specific packages. This function only
  makes sense if zypper is used as package manager.

``suseStripPackager {-a}``
  Remove smart or zypper packages and db files Also remove rpm
  package and db if -a given.

Profile Environment Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :file:`.profile` environment file contains a specific set of
variables which are listed below. Some of the functions above
use the variables.

``$kiwi_compressed``
  The value of the compressed attribute set in the type element
  in :file:`config.xml`.

``$kiwi_delete``
  A list of all packages which are part of the packages section
  with `type="delete"` in :file:`config.xml`.

``$kiwi_drivers``
  A comma separated list of the driver entries as listed in the
  drivers section of the :file:`config.xml`.

``$kiwi_iname``
  The name of the image as listed in :file:`config.xml`.

``$kiwi_iversion``
  The image version string major.minor.release.

``$kiwi_keytable``
  The contents of the keytable setup as done in :file:`config.xml`.

``$kiwi_language``
  The contents of the locale setup as done in :file:`config.xml`.

``$kiwi_profiles``
  A list of profiles used to build this image.

``$kiwi_size``
  The predefined size value for this image. This is not the
  computed size but only the optional size value of the preferences
  section in :file:`config.xml`.

``$kiwi_timezone``
  The contents of the timezone setup as done in :file:`config.xml`.

``$kiwi_type``
  The basic image type.


Configuration Tips
^^^^^^^^^^^^^^^^^^

In this section some ideas of how :file:`config.sh` file could be used to
fine tune the resulting unpacked image are quickly described:

#. **Stateless systemd UUIDs:**

  During the image packages installation when *systemd* and/or
  *dbus* are installed machine ID files are created and set
  (:file:`/etc/machine-id`, :file:`/var/lib/dbus/machine-id`). Those
  UUIDs are meant to be unique and set only once in each deployment.
  KIWI follows the `systemd recommandations
  <https://www.freedesktop.org/software/systemd/man/machine-id.html>`_ and
  whipes any :file:`/etc/machine-id` content, leaving it as an empty file.
  Note this is only applied for images based on dracut initrd, on container
  images, for instance, this setting is not applied.

  In case this setting is required also for a non dracut based image
  this could be also achieved by clearing :file:`/etc/machine-id`
  in :file:`config.sh`.

  .. note:: Avoid interactive boot

     It is important to remark that the file :file:`/etc/machine-id`
     is set to an empty file instead of deleting it. Systemd may trigger
     :command:`systemd-firstboot` service if this file is not present,
     which leads to an interactive firstboot where the user is
     asked to provide some data.

  .. note:: Avoid inconsistent :file:`var/lib/dbus/machine-id`

     It is important to remark that :file:`/etc/machine-id` and
     :file:`/var/lib/dbus/machine-id` should contain the same unique ID. In
     modern systems :file:`/var/lib/dbus/machine-id` is already a symlink
     to :file:`/etc/machine-id`. However in older systems those might be two
     different files. This is the case for SLE-12 based images, so
     in those cases it is recommended to add into the :file:`config.sh`
     the symlink creation:

     .. code:: bash

        #======================================
        # Make machine-id consistent with dbus
        #--------------------------------------
        if [ -e /var/lib/dbus/machine-id ]; then
            rm /var/lib/dbus/machine-id
        fi
        ln -s /etc/machine-id /var/lib/dbus/machine-id


.. _image-customization-images-sh:

Image Customization via the ``images.sh`` shell script
------------------------------------------------------

The KIWI image description allows to have an optional :file:`images.sh`
bash script in place. It can be used for changes appropriate for
certain images/image types on case-by-case basis (since it runs at
beginning of :ref:`create step <create-step>`). Basically the script
should be designed to take over control of handling image type specific
tasks. For example if building the oem type requires some additional
package or config it can be handled in :file:`images.sh`. Please keep in
mind there is only one unpacked root tree the script operates in. This
means all changes are permanent and will not be automatically restored.
It is also the script authors tasks to check if changes done before do not
interfere in a negative way if another image type is created from the
same unpacked image root tree. If :file:`images.sh` exits with an exit
code != 0 the kiwi process will exit with an error too.

See below a common template for :file:`images.sh` script:

.. code:: bash

   #======================================
   # Functions...
   #--------------------------------------
   test -f /.kconfig && . /.kconfig
   test -f /.profile && . /.profile

   #======================================
   # Greeting...
   #--------------------------------------
   echo "Configure image: [$kiwi_iname]..."

   #======================================
   # Call configuration code/functions
   #--------------------------------------
   ...

   #======================================
   # Exit safely
   #--------------------------------------
   exit

Common Functions
^^^^^^^^^^^^^^^^

The :file:`.kconfig` file allows to make use of a common set of functions.
Functions specific to SUSE Linux specific begin with the name *suse*.
Functions applicable to all linux systems starts with the name *base*.
The following list describes the functions available inside the
:file:`images.sh` script.

``baseCleanMount``
  Umount the system file systems :file:`/proc`, :file:`/dev/pts`,
  and :file:`/sys`.

``baseGetProfilesUsed``
  Return the name(s) of profiles used to build this image.

``baseGetPackagesForDeletion``
  Return the list of packages setup in the packages *type="delete"*
  section of the :file:`config.xml` used to build this image.

``suseGFXBoot {theme} {loadertype}``
  This function requires the gfxboot and at least one *bootsplash-theme-**
  package to be installed to work correctly. The function creates from
  this package data a graphics boot screen for the isolinux and grub boot
  loaders. Additionally it creates the bootsplash files for the
  resolutions 800x600, 1024x768, and 1280x1024.

``suseStripKernel``
  This function removes all kernel drivers which are not listed in the
  drivers sections of the :file:`config.xml` file.

``suseStripInitrd``
  This function removes a whole bunch of tools binaries and libraries
  which are not required to boot a suse system with KIWI.

``Rm {list of files}``
  Helper function to delete files and announce it to log.

``Rpm {rpm commandline}``
  Helper function to the rpm function and announce it to log.

``Echo {echo commandline}``
  Helper function to print a message to the controlling terminal.

``Debug {message}``
  Helper function to print a message if the variable *DEBUG* is set to 1.

Profile environment variables
'''''''''''''''''''''''''''''

The :file:`.profile` environment file contains a specific set of
variables which are listed below. Some of the functions above use the
variables.

``$kiwi_iname``
  The name of the image as listed in :file:`config.xml`.

``$kiwi_iversion``
  The image version string major.minor.release.

``$kiwi_keytable``
  The contents of the keytable setup as done in :file:`config.xml`.

``$kiwi_language``
  The contents of the locale setup as done in :file:`config.xml`.

``$kiwi_timezone``
  The contents of the timezone setup as done in :file:`config.xml`.

``$kiwi_delete``
  A list of all packages which are part of the packages section with
  *type="delete"* in :file:`config.xml`.

``$kiwi_profiles``
  A list of profiles used to build this image.

``$kiwi_drivers``
  A comma separated list of the driver entries as listed in the drivers
  section of the :file:`config.xml`.

``$kiwi_size``
  The predefined size value for this image. This is not the computed size
  but only the optional size value of the preferences section in
  :file:`config.xml`.

``$kiwi_compressed``
  The value of the compressed attribute set in the type element in
  :file:`config.xml`.

``$kiwi_type``
  The basic image type.
