%global version_schily 2024-03-21

%global perms_cdda2wav %caps(cap_dac_override,cap_sys_admin,cap_sys_nice,cap_net_bind_service,cap_sys_rawio+ep)
%global perms_cdrecord %caps(cap_sys_resource,cap_dac_override,cap_sys_admin,cap_sys_nice,cap_net_bind_service,cap_ipc_lock,cap_sys_rawio+ep)
%global perms_readcd %caps(cap_dac_override,cap_sys_admin,cap_net_bind_service,cap_sys_rawio+ep)

# Use a specific order for building as libraries are linked to each other:
%global components libschily libscg libscgcmd librscg libparanoia libdeflt libcdrdeflt libmdigest libedc libhfs_iso libfile libsiconv libfind cdda2wav cdrecord  mkisofs mkisofs/diag readcd

Name:           schily
Version:        %(echo %version_schily | tr '-' '.')
Release:        2%{?dist}
Epoch:          10
Summary:        The "Schily" Tool Box
License:        CDDL-1.0 and GPLv2 and LGPL-2.1 and BSD-2-Clause and BSD-3-Clause
URL:            https://codeberg.org/schilytools/schilytools

Source0:        %{url}/archive/%{version_schily}.tar.gz#/schily-%{version_schily}.tar.gz
Patch0:         %{name}-cdrecord-default.patch

BuildRequires:  gcc-c++
BuildRequires:  gettext-devel
BuildRequires:  libcap-devel
BuildRequires:  make

%description
The "Schily" Tool Box is a collection of tools originally written or managed by
Jörg Schilling.

%package -n cdrecord
Summary:        Creates an image of an ISO9660 file system
Obsoletes:      wodim < %{epoch}:%{version}-%{release}
Provides:       wodim = %{epoch}:%{version}-%{release}

%description -n cdrecord
A set of command line programs that allows to record and read CD/DVD/BluRay
media.

%package -n mkisofs
Summary:        Creates an image of an ISO9660 file system
Obsoletes:      genisoimage < %{epoch}:%{version}-%{release}
Provides:       genisoimage = %{epoch}:%{version}-%{release}

%description -n mkisofs
Programs to create and manipulate hybrid ISO9660/JOLIET/HFS file systems with
Rock Ridge attributes.

%package -n cdda2wav
Summary:        A CD-Audio Grabbing tool
Obsoletes:      icedax < %{epoch}:%{version}-%{release}
Provides:       icedax = %{epoch}:%{version}-%{release}

%description -n cdda2wav
The most evolved CD-audio extraction program with paranoia support.

%package libs
Summary:        Libraries for %{name}
Provides:       cdrtools-libs = %{epoch}:%{version}-%{release}
Obsoletes:      cdrtools-libs <= %{epoch}:3.02

%description libs
This package provides the shared libraries for the Sch.

%prep
%autosetup -p1 -n schilytools

# Convert files to utf8 for german letters:
for i in \
    $(find . -name "*.1") \
    $(find . -name "*.8") \
    $(find . -name "README*") \
    $(find . -name "THANKS*"); do
    iconv -f iso-8859-1 $i -t utf-8 -o $i.new && mv -f $i.new $i
done

%build
make_command() {
  cd $i
  make -f Makefile \
      CPPOPTX="%{build_cxxflags} -Wno-incompatible-pointer-types -Wno-old-style-definition" \
      COPTX="%{build_cflags} -Wno-incompatible-pointer-types -Wno-old-style-definition" \
      GMAKE_NOWARN=true \
      LDOPTX="%{build_ldflags}" \
      LINKMODE="dynamic" \
      NOECHO= \
      RUNPATH= \
      $*
   cd -
}

for i in %{components}; do
  make_command config
  make_command all
done

%install
for i in %{components}; do
  cd $i
  make -f Makefile \
      DESTDIR=%{buildroot} \
      GMAKE_NOWARN=true \
      INS_BASE=%{_prefix} \
      INS_RBASE=/ \
      LINKMODE="dynamic" \
      NOECHO= \
      RUNPATH= \
      install
  cd -
done

# Move libraries to the appropriate place on 64 bit arches
if [ %{_libdir} != %{_prefix}/lib ]; then
    mkdir -p %{buildroot}%{_libdir}
    mv %{buildroot}%{_prefix}/lib/lib*.so.* %{buildroot}%{_libdir}
fi

# Remove unused stuff:
rm -fr \
  %{buildroot}%{_libdir}/*.so \
  %{buildroot}%{_mandir}/man3 \
  %{buildroot}%{_prefix}/lib

# Install documents directly in the files section:
rm -frv %{buildroot}%{_docdir}
  
%check
for i in %{components}; do
  cd $i
  make -f Makefile \
      GMAKE_NOWARN=true \
      LINKMODE="dynamic" \
      NOECHO= \
      RUNPATH= \
      tests
  cd -
done

%files -n cdrecord
%doc cdrecord/README
%doc cdrecord/README.ATAPI
%doc cdrecord/README.audio
%doc cdrecord/README.cdplus
%doc cdrecord/README.cdrw
%doc cdrecord/README.cdtext
%doc cdrecord/README.clone
%doc cdrecord/README.copy
%doc cdrecord/README.DiskT@2
%doc cdrecord/README.multi
%doc cdrecord/README.parallel
%doc cdrecord/README.raw
%doc cdrecord/README.sony
%doc cdrecord/README.verify
%doc cdrecord/README.WORM
%config(noreplace) %{_sysconfdir}/default/cdrecord
%{perms_cdrecord} %{_bindir}/cdrecord
%{perms_readcd} %{_bindir}/readcd
%{_mandir}/man1/cdrecord.1*
%{_mandir}/man1/readcd.1*

%files -n mkisofs
%license mkisofs/COPYING
%doc mkisofs/README*
%{_bindir}/devdump
%{_bindir}/isodebug
%{_bindir}/isodump
%{_bindir}/isoinfo
%{_bindir}/isovfy
%{_bindir}/mkisofs
%{_bindir}/mkhybrid
%{_mandir}/man8/devdump.8*
%{_mandir}/man8/isodebug.8*
%{_mandir}/man8/isodump.8*
%{_mandir}/man8/isoinfo.8*
%{_mandir}/man8/isovfy.8*
%{_mandir}/man8/mkisofs.8*
%{_mandir}/man8/mkhybrid.8*

%files -n cdda2wav
%doc cdda2wav/FAQ
%doc cdda2wav/HOWTOUSE
%doc cdda2wav/README
%doc cdda2wav/THANKS
%{_bindir}/cdda2mp3
%{_bindir}/cdda2ogg
%{perms_cdda2wav} %{_bindir}/cdda2wav
%{_mandir}/man1/cdda2wav.1*
%{_mandir}/man1/cdda2mp3.1*
%{_mandir}/man1/cdda2ogg.1*

%files libs
%license COPYING GPL-2.0.txt LGPL-2.1.txt CDDL.Schily.txt AN-2024-03-21 CONTRIBUTORS
%doc README
%{_libdir}/libcdrdeflt.so.1.0
%{_libdir}/libdeflt.so.1.0
%{_libdir}/libedc_ecc.so.1.0
%{_libdir}/libedc_ecc_dec.so.1.0
%{_libdir}/libfile.so.1.0
%{_libdir}/libfind.so.4.0
%{_libdir}/libhfs.so.1.0
%{_libdir}/libmdigest.so.1.0
%{_libdir}/libparanoia.so.1.0
%{_libdir}/librscg.so.1.0
%{_libdir}/libscg.so.1.0
%{_libdir}/libscgcmd.so.1.0
%{_libdir}/libschily.so.2.0
%{_libdir}/libsiconv.so.1.0

%changelog
* Fri Apr 11 2025 Simone Caronni <negativo17@gmail.com> - 10:2024.03.21-2
- Build only cdrtools related components and drop the rest.
- Remove some warnings during build.
- Trim changelog.
- Clean up SPEC file.
- Add test section.

* Fri May 24 2024 Simone Caronni <negativo17@gmail.com> - 10:2024.03.21-1
- Update to release 2024-03-21.

* Fri Sep 29 2023 Simone Caronni <negativo17@gmail.com> - 10:2023.09.28-1
- Update to 2023-09-28 release.

* Fri Jan 20 2023 Simone Caronni <negativo17@gmail.com> - 10:2023.01.12-2
- Update to 2023-01-12.

* Sun Oct 30 2022 Simone Caronni <negativo17@gmail.com> - 10:2022.10.16-1
- Update to 2022-10-16.

* Tue Sep 20 2022 Simone Caronni <negativo17@gmail.com> - 10:2022.09.18-2
- Update to 2022-09-18.

* Mon Sep 12 2022 Simone Caronni <negativo17@gmail.com> - 10:2022.08.18.beta-1
- Update to new maintained fork at Codeberg:
  https://codeberg.org/schilytools/schilytools
