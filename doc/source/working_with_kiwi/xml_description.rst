The Image Description
=====================

An image description is a XML file that defines properties of the appliance
that will be build by KIWI, for example:

- image type (e.g. QEMU disk image, PXE bootable image, Vagrant box, etc.)
- partition layout
- packages to be installed on the system
- users to be added

The following sections will walk you through the major elements and
attributes of the RELAX NG schema [#f1]_. A complete description of the
schema can be found in :ref:`schema-docs`.


The `image` Element
-------------------

The image description consists of the root element `image` and its
children, for example:

.. code-block:: xml

   <?xml version="1.0" encoding="utf-8"?>

   <image schemaversion="6.9" name="LimeJeOS-Leap-15.0">
       <!-- all setting belong here -->
   </image>

The `image` element requires the following two attributes (as shown in the
above example):

- `name`: A name for this image that must not contain spaces or `/`.

- `schemaversion`: The used version of the [KIWI] RNG schema. KIWI will
  automatically convert your image description from an older schema
  version to the most recent one (it will perform this only internally and
  won't modify your :file:`config.xml`).

The `name` attribute will be used to create the bootloader entry, however
it can be inconvenient to use as it must be POSIX-safe. You can therefore
provide an alternative name that will be displayed in the bootloader via
the attribute `displayName`, which doesn't have the same strict rules as
`name`:

.. code-block:: xml

   <?xml version="1.0" encoding="utf-8"?>

   <image schemaversion="6.9" name="LimeJeOS-Leap-15.0" displayName="LimeJeOS Leap 15.0">
       <!-- all setting belong here -->
   </image>


The `description` Element
-------------------------

The `description` element, contains some high level information about your
image:

.. code-block:: xml

   <image schemaversion="6.9" name="LimeJeOS-Leap-15.0">

     <description type="system">
       <author>Jane Doe</author>
       <contact>jane@myemaildomain.xyz</contact>
       <specification>
         Leap 15.0 JeOS, a small image, that is just enough of an OS
       </specification>
       <license>GPLv3</license>
     </description>

     <!-- snip -->
   </image>


The `description` element must always contain a `type` attribute. This
attribute accepts the values `system` or `boot`. The value `boot` is used
by the KIWI developers and is not relevant for the end user, thus `type`
should be always set to `system`.

`description` allows the following optional children:

- `author`: The name of the author of this image.

- `contact`: Some means how to contact the author of the image (e.g. an
  email address, an IM nickname and network, etc.)

- `specification`: A detailed description of this image, e.g. its use case.

- `license`: If applicable, you can specify a license for the image.


The `preferences` Element
-------------------------

The mandatory `preferences` element contains the definition of the various
enabled image types (so-called build types). Each of these build types can
be supplied with attributes specific to that image type, which we described
in section :ref:`xml-description-build-types`.

The elements that are not image type specific are presented afterwards in
section :ref:`xml-description-preferences-common-elements`.


.. _xml-description-build-types:

Build Types
^^^^^^^^^^^

A build type defines the type of an appliance that is produced by KIWI, for
instance, a live ISO image or a virtual machine disk.

For example, a live ISO image is specified as follows:

.. code-block:: xml

   <image schemaversion="6.9" name="LimeJeOS-Leap-15.0">
     <preferences>
       <type image="iso" primary="true" flags="overlay" hybridpersistent_filesystem="ext4" hybridpersistent="true"/>
       <!-- additional preferences -->
     </preferences>

     <!-- additional image settings -->
   </image>


A build type is defined via a single `type` element whose only required
attribute is `image`, that defines which image type is created. All other
attributes are optional and can be used to customize an image further. In
the above example we created an ISO image, with the an ext4 filesystem
[#f2]_.

It is possible to provide **multiple** `type` elements with different
`image` attributes inside the preferences section. For instance, the
following XML snippet can be used to create a live image, an OEM
installation image, and a virtual machine disk of the same appliance:

.. code-block:: xml

   <image schemaversion="6.9" name="LimeJeOS-Leap-15.0">
     <preferences>
       <!-- Live ISO -->
       <type image="iso" primary="true" flags="overlay" hybridpersistent_filesystem="ext4" hybridpersistent="true"/>

       <!-- Virtual machine -->
       <type image="vmx" filesystem="ext4" bootloader="grub2" kernelcmdline="splash" firmware="efi"/>

       <!-- OEM installation image -->
       <type image="oem" filesystem="ext4" initrd_system="dracut" installiso="true" bootloader="grub2" kernelcmdline="splash" firmware="efi">
         <oemconfig>
           <oem-systemsize>2048</oem-systemsize>
           <oem-swap>true</oem-swap>
           <oem-device-filter>/dev/ram</oem-device-filter>
           <oem-multipath-scan>false</oem-multipath-scan>
         </oemconfig>
         <machine memory="512" guestOS="suse" HWversion="4"/>
       </type>
       <!-- additional preferences -->
     </preferences>

     <!-- additional image settings -->
   </image>

Note the additional attribute `primary` in the Live ISO image build
type. KIWI will by default build the image which attribute `primary` is set
to `true`.

KIWI supports the following values for the `image` attribute (further
attributes of the `type` element are documented inside the referenced
sections):

- `iso`: a live ISO image, see :ref:`hybrid_iso`
- `vmx`: build a virtual machine image, see: :ref:`vmx`
- `oem`: results in an expandable image that can be deployed via a bootable
  installation medium, e.g. a USB drive or a CD. See :ref:`oem`
- `pxe`: creates an image that can be booted via PXE (network boot), see
  :ref:`build_pxe`

- `docker`, `oci`: container images, see :ref:`building-docker-build`

- `btrfs`, `ext2`, `ext3`, `ext4`, `xfs`: KIWI will convert the
  image into a mountable filesystem of the specified type.

- `squashfs`, `clicfs`: creates the image as a filesystem that can be used
  in live systems

- `tbz`, `cpio`: the unpacked source tree will be compressed into a `XZ
  <https://en.wikipedia.org/wiki/Xz>`_ or `CPIO
  <https://en.wikipedia.org/wiki/Cpio>`_ archive.


The `type` element furthermore supports the following subelements (as shown
above, `oemconfig` is a subelement of `<type image="oem" ...>`):

- `containerconfig`: contains settings specific for the creation of
  container images, see :ref:`building-docker-build`

- `oemconfig`: configurations relevant for building OEM images, see:
  :ref:`oem`

- `pxedeploy`: settings for PXE booting, see :ref:`build_pxe`

- `vagrantconfig`: instructs KIWI to build a Vagrant box instead of a
  standard virtual machine image, see :ref:`setup_vagrant`

Please consult the :ref:`schema-docs` for concerning the documentation of
the remaining child-elements: `machine`, `size` and `systemdisk`.


.. _xml-description-preferences-common-elements:

Common Elements
^^^^^^^^^^^^^^^

Now that we have covered the `type` element, we shall return to the
remaining child-elements of `preferences`:

- `version`: A version number of this image. We recommend to use the
  following format: **Major.Minor.Release**, however other versions are
  possible, e.g. one can use the version of the underlying operating
  system.

- `packagemanager`: Specify the package manager that will be used to
  download and install the packages for your appliance. Currently the
  following package managers are supported: apt-get, zypper and dnf. Note
  that the package manager must be installed on the system **calling**
  KIWI, it is **not** sufficient to install it inside the appliance.

- `locale`: Specify the locale that the resulting appliance will use.

- `timezone`: Override the default timezone of the image to a more suitable
  value, e.g. the timezone in which the image's users reside.

- `rpm-check-signatures`: Boolean value that defines whether the signatures
  of the downloaded RPM packages will be verified before installation.
  Note that when building appliances for a different distribution you will
  have to either import the other distribution's signing-key or set this to
  `false` (RPM will otherwise fail to verify the package signatures, as it
  does will not trust the signature key of other distributions or even
  other versions of the same distribution).

- `rpm-excludedocs`: Boolean value that instructs RPM whether to install
  documentation with packages or not (currently this setting has only an
  effect for zypper). Please bear in mind that enabling this can have quite
  a negative impact on user-experience and should thus be used with care.

- `bootloader-theme` and `bootsplash-theme`: themes for the bootloader and
  the bootsplash-screen. These themes have to be either built-in to the
  bootloader or installed via the `packages` section.


An example excerpt from a image description using these child-elements of
`preferences`, results in the following:

.. code-block:: xml

   <image schemaversion="6.9" name="OpenSUSE-Leap-15.0">
     <!-- snip -->
     <preferences>
       <version>15.0</version>
       <packagemanager>zypper</packagemanager>
       <locale>en_US</locale>
       <keytable>us</keytable>
       <timezone>Europe/Berlin</timezone>
       <rpm-excludedocs>true</rpm-excludedocs>
       <rpm-check-signatures>false</rpm-check-signatures>
       <bootsplash-theme>openSUSE</bootsplash-theme>
       <bootloader-theme>openSUSE</bootloader-theme>
       <type image="vmx" filesystem="ext4" format="qcow2" boottimeout="0" bootloader="grub2">
    </preferences>
    <!-- snip -->
  </image>


.. _xml-description-image-profiles:

Image Profiles
--------------

In the previous section we have covered build types, that are represented
in the image description as the `type` element. We have also shown how it
is possible to include multiple build types in the same
appliance. Unfortunately that approach has one significant limitation: one
can only include multiple build types with **different** settings for
`image`.

In certain cases this is undesirable, for instance when building multiple
very similar virtual machine disks. Then one would have to duplicate the
whole :file:`config.xml` for each virtual machine. KIWI supports profiles
to work around this issue.

A profile is a namespace for additional settings that can be applied by
KIWI on top of the default settings (or other profiles), thereby allowing
to build multiple appliances with the same build type but with different
configurations.

In the following example, we create two virtual machine images: one for
QEMU (using the `qcow2` format) and one for VMWare (using the `vmdk`
format).

.. code-block:: xml

   <image schemaversion="6.9" name="OpenSUSE-Leap-15.0">
     <!-- snip -->
     <profiles>
       <profile name="QEMU" description="virtual machine for QEMU"/>
       <profile name="VMWare" description="virtual machine for VMWare"/>
     </profiles>
     <preferences>
       <version>15.0</version>
       <packagemanager>zypper</packagemanager>
     </preferences>
     <preferences profiles="QEMU">
       <type image="vmx" format="qcow2" filesystem="ext4" bootloader="grub2">
     </preferences>
     <preferences profiles="VMWare">
       <type image="vmx" format="vmdk" filesystem="ext4" bootloader="grub2">
     </preferences>
     <!-- snip -->
   </image>


Each profile is declared via the element `profile`, which itself must be a
child of `profiles` and must contain the `name` and `description`
attributes. The `description` is only present for documentation purposes,
`name` on the other hand is used to instruct KIWI which profile to build
via the command line. Additionally one can provide the boolean attribute
`import`, which defines whether this profile should be used by default when
KIWI is invoked via the command line.

A profile inherits the default settings which do not belong to any
profile. It applies only to elements that contain the profile in their
`profiles` attribute. The attribute `profiles` expects a comma separated
list of profiles for which the settings of this element apply. The
attribute is present in the following elements only:

- `preferences`
- `drivers`
- `repository` and `packages` (see
  :ref:`xml-description-repositories-and-packages`)
- `users`

Profiles can furthermore inherit settings from another profile via the
`requires` sub-element:

.. code-block:: xml

   <profiles>
     <profile name="VM" description="virtual machine"/>
     <profile name="QEMU" description="virtual machine for QEMU">
       <requires>VM</requires>
     </profile>
   </profiles>

The profile `QEMU` would inherit the settings from `VM` in the above
example.

.. FIXME: link to build_with_profiles.rst

.. _xml-description-adding-users:

Adding Users
------------

User accounts can be added or modified via the `users` element, which
supports a list of multiple `user` child elements:

.. code-block:: xml

   <image schemaversion="6.9" name="JeOS-Tumbleweed">
     <users>
       <user password="this_is_soo_secure" home="/home/me" name="me" groups="users" pwdformat="plain" />
       <user password="$1$wYJUgpM5$RXMMeASDc035eX.NbYWFl0" home="/root" name="root" groups="root"/>
     </users>
   </image>

Each `user` element represents a specific user that is added or
modified. The following attributes are mandatory:

- `name`: the UNIX username

- `home`: the path to the user's home directory

Additionally, the following optional attributes can be specified:

- `groups`: A comma separated list of UNIX groups. The first element of the
  list is used as the user's primary group. The remaining elements are
  appended to the user's supplementary groups. When no groups are assigned
  then the system's default primary group will be used [#f3]_.

- `id`: The user id of this account.

- `pwdformat`: The format in which `password` is provided, either `plain`
  or `encrypted` (the latter is the default).

- `password`: The password for this user account. It can be provided either
  in cleartext form (`pwdformat="plain"`) or in `crypt`'ed form
  (`pwdformat="encrypted"`). Plain passwords are discouraged, as everyone
  with access to the image description would know the password. Thus
  generate a hash of your password, e.g. with the `mkpasswd` tool
  (available in most Linux distributions via the `whois` package):

  .. code:: bash

     $ mkpasswd -m sha-512 -S $(date +%N) -s <<< INSERT_YOUR_PASSWORD_HERE


The `users` element furthermore accepts a list of profiles (see
:ref:`xml-description-image-profiles`) to which it applies via the
`profiles` attribute, as shown in the following example:

.. code-block:: xml

   <image schemaversion="6.9" name="JeOS-Tumbleweed">
     <profiles>
       <profile name="VM" description="standard virtual machine"/>
       <profile name="shared_VM" description="virtual machine shared by everyone"/>
     </profiles>
     <!-- snip -->
     <users>
       <user password="$1$wYJUgpM5$RXMMeASDc035eX.NbYWFl0" home="/root" name="root" groups="root"/>
     </users>
     <users profiles="VM">
       <user password="$1$blablabl$FRTFJZxMPfM6LA1g0EZ5h1" home="/home/devel" name="devel"/>
     </users>
     <users profiles="shared_VM">
       <user password="super_secr4t" home="/share/devel" name="devel" groups="users,devel" pwdformat="plain"/>
     </users>
   </image>

Here the settings for the root user are shared among all appliances. The
configuration of the `devel` user on the other hand depends on the
profile.


.. _xml-description-repositories-and-packages:

Defining Repositories and Adding or Removing Packages
-----------------------------------------------------

A crucial part of each appliance


Stripping files from the appliance
----------------------------------

.. [#f1] `RELAX NG <https://en.wikipedia.org/wiki/RELAX_NG>`_ is a
         so-called schema language: it describes the structure of a XML
         document.

.. [#f2] A hybrid persistent filesystem contains a copy-on-write file to
         keep data persistent over a reboot.

.. FIXME: @schaefi: is this correct?
.. [#f3] Note that the default primary group is taken from the system on
         which KIWI is run, not from the system that KIWI is building.
