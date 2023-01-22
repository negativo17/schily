%global version_schily 2023-01-12

%global perms_cdda2wav %caps(cap_dac_override,cap_sys_admin,cap_sys_nice,cap_net_bind_service,cap_sys_rawio+ep)
%global perms_cdrecord %caps(cap_sys_resource,cap_dac_override,cap_sys_admin,cap_sys_nice,cap_net_bind_service,cap_ipc_lock,cap_sys_rawio+ep)
%global perms_readcd %caps(cap_dac_override,cap_sys_admin,cap_net_bind_service,cap_sys_rawio+ep)

# Todo:
# Figure out what to do with /usr/xpg4/bin/ Posix variation binaries
# Fix ved online help in /usr/share/man/help/ved.help
# Further split out components
# Check if it's possible to move /usr/share/lib/*make files
# Add patch to fix sccspatch link
# More subpackages / different versions for subpackages?

Name:           schily
Version:        %(echo %version_schily | tr '-' '.')
Release:        2%{?dist}
Epoch:          10
Summary:        The "Schily" Tool Box
License:        CDDL-1.0 and GPLv2 and BSD
URL:            http://schilytools.sourceforge.net/

Source0:        https://codeberg.org/schilytools/schilytools/archive/%{version_schily}.tar.gz#/schily-%{version_schily}.tar.gz
Patch0:         %{name}-cdrecord-default.patch

%if 0%{?rhel} == 7
BuildRequires:  devtoolset-9-gcc-c++
%else
BuildRequires:  gcc-c++
%endif

BuildRequires:  gettext-devel
BuildRequires:  libcap-devel

%description
The "Schily" Tool Box is a set of tools written or managed by Jörg Schilling.

%package -n sccs
Summary:        Source Code Control System
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description -n sccs
Source Code Control System (SCCS) is a version control system for
tracking changes in source code and other text files during the
development of a piece of software. This allows the user to retrieve
any of the previous versions of the original source code and the
changes which are stored.

%package -n cdrecord
Summary:        Creates an image of an ISO9660 file system
Obsoletes:      wodim < %{epoch}:
Provides:       wodim = %{epoch}:

%description -n cdrecord
A set of command line programs that allows to record and read CD/DVD/BluRay
media.

%package -n mkisofs
Summary:        Creates an image of an ISO9660 file system
Obsoletes:      genisoimage < %{epoch}:
Provides:       genisoimage = %{epoch}:

%description -n mkisofs
Programs to create and manipulate hybrid ISO9660/JOLIET/HFS file systems with
Rock Ridge attributes.

%package -n cdda2wav
Summary:        A CD-Audio Grabbing tool
Obsoletes:      icedax < %{epoch}: 
Provides:       icedax = %{epoch}:

%description -n cdda2wav
The most evolved CD-audio extraction program with paranoia support.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}-libs%{?_isa} = %{epoch}:%{version}-%{release}

%description devel
This package provides the development files of the %{name} package.

%package libs
Summary:        Libraries for %{name}
Provides:       cdrtools-libs = %{epoch}:%{version}-%{release}
Obsoletes:      cdrtools-libs <= %{epoch}:3.02
Requires(post): ldconfig

%description libs
This package provides the shared libraries for %{name}.

%prep
%autosetup -p1 -n schilytools

# Convert files to utf8 for german letters
for i in \
    $(find . -name "*.1") \
    $(find . -name "*.5") \
    $(find . -name "README*") \
    $(find . -name "THANKS*"); do
    iconv -f iso-8859-1 $i -t utf-8 -o $i.new && mv -f $i.new $i
done

%build
%if 0%{?rhel} == 7
. /opt/rh/devtoolset-9/enable
%endif

make \
    GMAKE_NOWARN=true \
    LINKMODE="dynamic" \
    RUNPATH= \
    SCCS_BIN_PRE="%{_lib}/ccs/" \
    SCCS_HELP_PRE="%{_lib}/ccs/" \
    CPPOPTX="$RPM_OPT_FLAGS" \
    COPTX="$RPM_OPT_FLAGS"

%install
make \
    GMAKE_NOWARN=true \
    LINKMODE="dynamic" \
    RUNPATH= \
    SCCS_BIN_PRE="%{_lib}/ccs/" \
    SCCS_HELP_PRE="%{_lib}/ccs/" \
    INS_BASE=%{_prefix} \
    INS_RBASE=/ \
    DESTDIR=%{buildroot} \
    install

# Remove unused libraries
rm -frv %{buildroot}%{_prefix}/lib/profiled
find %{buildroot} -name "*.a" -delete

# Fix sccpatch & svr4.make
rm -frv %{buildroot}%{_prefix}/ccs
ln -sf ../../../../bin/spatch %{buildroot}%{_libdir}/ccs/bin/sccspatch
rm -fr %{buildroot}%{_prefix}/lib/svr4.make

# Remove unused binaries
find %{buildroot} -name "btcflash*" -delete
find %{buildroot} -name "pxupgrade*" -delete

# Remove overlapping K&R cpp
rm -fv %{buildroot}%{_prefix}/lib/cpp

# Remove Bourne Shell replacement for /bin/sh
rm -fv %{buildroot}%{_bindir}/{sh,bosh,jsh,pfsh}
rm -fv %{buildroot}%{_mandir}/man1/sh.*

# libsiconv tries to use libc's iconv first before trying its own tables
rm -frv %{buildroot}%{_datadir}/lib/siconv

# Remove various manpages
rm -frv %{buildroot}%{_mandir}/de

# Install documents directly from the files section
rm -frv %{buildroot}%{_docdir}

# Move libraries to the appropriate place on 64 bit arches
if [ %{_libdir} != %{_prefix}/lib ]; then 
    mkdir -p %{buildroot}%{_libdir}
    mv %{buildroot}%{_prefix}/lib/lib*.so* %{buildroot}%{_libdir}
fi

# Make binaries executable
chmod 755 %{buildroot}%{_libdir}/lib*.so* %{buildroot}%{_bindir}/*

# Config files
mv %{buildroot}%{_prefix}%{_sysconfdir}/termcap %{buildroot}%{_sysconfdir}/
rm -fr %{buildroot}%{_prefix}%{_sysconfdir}

# TBD - Posix variations
rm -frv %{buildroot}%{_prefix}/xpg4
# TBD - Ved online help
rm -frv %{buildroot}%{_mandir}/help

%ldconfig_scriptlets libs

%files
%doc star/README.* star/STARvsGNUTAR
%config(noreplace) %{_sysconfdir}/default/rmt
%config(noreplace) %{_sysconfdir}/default/star
%config(noreplace) %{_sysconfdir}/sformat.dat
%{_bindir}/Cstyle
#{_bindir}/bosh
%{_bindir}/bsh
%{_bindir}/cal
%{_bindir}/calc
%{_bindir}/calltree
%{_bindir}/change
%{_bindir}/compare
%{_bindir}/copy
%{_bindir}/count
%{_bindir}/cstyle.js
%{_bindir}/ctags
%{_bindir}/dmake
%{_bindir}/fdiff
%{_bindir}/fifo
%{_bindir}/fsdiff
%{_bindir}/gnutar
%{_bindir}/hdump
#{_bindir}/jsh
%{_bindir}/krcpp
%{_bindir}/label
%{_bindir}/lndir
%{_bindir}/make
#{_prefix}/xpg4/bin/make
%{_bindir}/match
%{_bindir}/mdigest
%{_bindir}/mt
%{_bindir}/obosh
%{_bindir}/od
%{_bindir}/opatch
%{_bindir}/p
%{_bindir}/pbosh
%{_bindir}/pfbsh
#{_bindir}/pfsh
%{_bindir}/printf
%{_bindir}/scpio
%{_bindir}/scut
%{_bindir}/sdd
%{_bindir}/sfind
%{_bindir}/sformat
%{_bindir}/sgrow
#{_bindir}/sh
#{_prefix}/xpg4/bin/sh
%{_bindir}/smake
%{_bindir}/smt
%{_bindir}/spaste
%{_bindir}/spatch
%{_bindir}/spax
%{_bindir}/star
%{_bindir}/star_sym
%{_bindir}/strar
%{_bindir}/suntar
%{_bindir}/svr4.make
%{_bindir}/tar
%{_bindir}/tartest
%{_bindir}/termcap
%{_bindir}/translit
%{_bindir}/udiff
%{_bindir}/ustar
%{_bindir}/vctags
%{_bindir}/ved
%{_bindir}/ved-e
%{_bindir}/ved-w
%{_datadir}/lib
%{_sbindir}/mountcd
%{_sbindir}/rmt
%{_mandir}/man1/bosh.*
%{_mandir}/man1/bsh.*
%{_mandir}/man1/cal.*
%{_mandir}/man1/calc.*
%{_mandir}/man1/calltree.*
%{_mandir}/man1/change.*
%{_mandir}/man1/compare.*
%{_mandir}/man1/copy.*
%{_mandir}/man1/count.*
%{_mandir}/man1/cstyle.*
%{_mandir}/man1/dmake.*
%{_mandir}/man1/fdiff.*
%{_mandir}/man1/fifo.*
%{_mandir}/man1/fsdiff.*
%{_mandir}/man1/gnutar.*
%{_mandir}/man1/hdump.*
%{_mandir}/man1/jsh.*
%{_mandir}/man1/krcpp.*
%{_mandir}/man1/label.*
%{_mandir}/man1/lndir.*
%{_mandir}/man1/make.*
%{_mandir}/man1/match.*
%{_mandir}/man1/mdigest.*
%{_mandir}/man1/mountcd.*
%{_mandir}/man1/mt.*
%{_mandir}/man1/obosh.*
%{_mandir}/man1/od.*
%{_mandir}/man1/opatch.*
%{_mandir}/man1/p.*
%{_mandir}/man1/patch.*
%{_mandir}/man1/pbosh.*
%{_mandir}/man1/pfbsh.*
%{_mandir}/man1/pfsh.*
%{_mandir}/man1/printf.*
%{_mandir}/man1/rmt.*
%{_mandir}/man1/scpio.*
%{_mandir}/man1/scut.*
%{_mandir}/man1/sdd.*
%{_mandir}/man1/sfind.*
%{_mandir}/man1/sgrow.*
#{_mandir}/man1/sh.*
%{_mandir}/man1/smake.*
%{_mandir}/man1/smt.*
%{_mandir}/man1/spaste.*
%{_mandir}/man1/spatch.*
%{_mandir}/man1/spax.*
%{_mandir}/man1/star.*
%{_mandir}/man1/star_sym.*
%{_mandir}/man1/strar.*
%{_mandir}/man1/suntar.*
%{_mandir}/man1/sysV-make.*
%{_mandir}/man1/tartest.*
%{_mandir}/man1/termcap.*
%{_mandir}/man1/translit.*
%{_mandir}/man1/udiff.*
%{_mandir}/man1/ustar.*
%{_mandir}/man1/vctags.*
%{_mandir}/man1/ved-e.*
%{_mandir}/man1/ved-w.*
%{_mandir}/man1/ved.*
%{_mandir}/man1/prs.*
%{_mandir}/man1/prt.*
%{_mandir}/man5/makefiles.*
%{_mandir}/man5/makerules.*
%{_mandir}/man5/star.*
%{_mandir}/man5/streamarchive.*
%{_sysconfdir}/termcap

%files -n sccs
%{_bindir}/sccs
#{_prefix}/xpg4/bin/sccs
%{_libdir}/ccs/bin/admin
%{_libdir}/ccs/bin/bdiff
%{_libdir}/ccs/bin/cdc
%{_libdir}/ccs/bin/comb
%{_libdir}/ccs/bin/delta
%{_libdir}/ccs/bin/diff
%{_libdir}/ccs/bin/fsdiff
%{_libdir}/ccs/bin/get
#{_prefix}/xpg4/bin/get
%{_libdir}/ccs/bin/help
%{_libdir}/ccs/bin/prs
%{_libdir}/ccs/bin/prt
%{_libdir}/ccs/bin/rcs2sccs
%{_libdir}/ccs/bin/rmchg
%{_libdir}/ccs/bin/rmdel
%{_libdir}/ccs/bin/sact
%{_libdir}/ccs/bin/sccs
%{_libdir}/ccs/bin/sccscvt
%{_libdir}/ccs/bin/sccsdiff
%{_libdir}/ccs/bin/sccslog
%{_libdir}/ccs/bin/sccspatch
%{_libdir}/ccs/bin/unget
%{_libdir}/ccs/bin/val
%{_libdir}/ccs/bin/vc
%{_libdir}/ccs/bin/what
%{_libdir}/ccs/lib
%{_mandir}/man1/sccs-add.*
%{_mandir}/man1/sccs-admin.*
%{_mandir}/man1/sccs-branch.*
%{_mandir}/man1/sccs-cdc.*
%{_mandir}/man1/sccs-check.*
%{_mandir}/man1/sccs-clean.*
%{_mandir}/man1/sccs-comb.*
%{_mandir}/man1/sccs-commit.*
%{_mandir}/man1/sccs-create.*
%{_mandir}/man1/sccs-cvt.*
%{_mandir}/man1/sccs-deledit.*
%{_mandir}/man1/sccs-delget.*
%{_mandir}/man1/sccs-delta.*
%{_mandir}/man1/sccs-edit.*
%{_mandir}/man1/sccs-diffs.*
%{_mandir}/man1/sccs-editor.*
%{_mandir}/man1/sccs-enter.*
%{_mandir}/man1/sccs-fix.*
%{_mandir}/man1/sccs-get.*
%{_mandir}/man1/sccs-help.*
%{_mandir}/man1/sccs-histfile.*
%{_mandir}/man1/sccs-info.*
%{_mandir}/man1/sccs-init.*
%{_mandir}/man1/sccs-istext.*
%{_mandir}/man1/sccs-ldiffs.*
%{_mandir}/man1/sccs-log.*
%{_mandir}/man1/sccs-print.*
%{_mandir}/man1/sccs-prs.*
%{_mandir}/man1/sccs-prt.*
%{_mandir}/man1/sccs-rcs2sccs.*
%{_mandir}/man1/sccs-remove.*
%{_mandir}/man1/sccs-rename.*
%{_mandir}/man1/sccs-rmdel.*
%{_mandir}/man1/sccs-root.*
%{_mandir}/man1/sccs-sact.*
%{_mandir}/man1/sccs-sccsdiff.*
%{_mandir}/man1/sccs-status.*
%{_mandir}/man1/sccs-tell.*
%{_mandir}/man1/sccs-unedit.*
%{_mandir}/man1/sccs-unget.*
%{_mandir}/man1/sccs-val.*
%{_mandir}/man1/sccs.*
%{_mandir}/man1/sccscvt.*
%{_mandir}/man1/sccsdiff.*
%{_mandir}/man1/sccslog.*
%{_mandir}/man1/sccspatch.*
%{_mandir}/man1/admin.*
%{_mandir}/man1/bdiff.*
%{_mandir}/man1/cdc.*
%{_mandir}/man1/comb.*
%{_mandir}/man1/delta.*
%{_mandir}/man1/diff.*
%{_mandir}/man1/get.*
%{_mandir}/man1/help.*
%{_mandir}/man1/rcs2sccs.*
%{_mandir}/man1/rmdel.*
%{_mandir}/man1/sact.*
%{_mandir}/man1/unget.*
%{_mandir}/man1/val.*
%{_mandir}/man1/vc.*
%{_mandir}/man1/what.*
%{_mandir}/man5/changeset.5*
%{_mandir}/man5/sccschangeset.5*
%{_mandir}/man5/sccsfile.5*

%files -n cdrecord
%doc cdrecord/README*
%config(noreplace) %{_sysconfdir}/default/cdrecord
%config(noreplace) %{_sysconfdir}/default/rscsi
%{perms_cdrecord} %{_bindir}/cdrecord
%{_bindir}/scgcheck
%{_bindir}/scgskeleton
%{perms_readcd} %{_bindir}/readcd
%{_sbindir}/rscsi
%{_mandir}/man1/cdrecord.*
%{_mandir}/man1/readcd.*
%{_mandir}/man1/scgcheck.*
%{_mandir}/man1/rscsi.*
%{_mandir}/man1/scgskeleton.*

%files -n mkisofs
%license mkisofs/COPYING
%doc mkisofs/README*
%{_bindir}/mkisofs
%{_bindir}/mkhybrid
%{_bindir}/isoinfo
%{_bindir}/devdump
%{_bindir}/isodump
%{_bindir}/isovfy
%{_bindir}/isodebug
%{_mandir}/man8/*

%files -n cdda2wav
%doc cdda2wav/FAQ cdda2wav/HOWTOUSE cdda2wav/NEEDED cdda2wav/THANKS cdda2wav/README
%{_bindir}/cdda2mp3
%{_bindir}/cdda2ogg
%{perms_cdda2wav} %{_bindir}/cdda2wav
%{_mandir}/man1/cdda2wav.*
%{_mandir}/man1/cdda2mp3.*
%{_mandir}/man1/cdda2ogg.*

%files libs
%license COPYING GPL-2.0.txt LGPL-2.1.txt CDDL.Schily.txt
%{_libdir}/lib*.so.*

%files devel
%{_includedir}/*
%{_libdir}/lib*.so
%{_mandir}/man3/*

%changelog
* Fri Jan 20 2023 Simone Caronni <negativo17@gmail.com> - 10:2023.01.12-2
- Update to 2023-01-12.

* Sun Oct 30 2022 Simone Caronni <negativo17@gmail.com> - 10:2022.10.16-1
- Update to 2022-10-16.

* Tue Sep 20 2022 Simone Caronni <negativo17@gmail.com> - 10:2022.09.18-2
- Update to 2022-09-18.

* Mon Sep 12 2022 Simone Caronni <negativo17@gmail.com> - 10:2022.08.18.beta-1
- Update to new maintained fork at Codeberg:
  https://codeberg.org/schilytools/schilytools

* Sun Sep 12 2021 Simone Caronni <negativo17@gmail.com> - 10:2021.09.01-2
- Update to 2021-09-01.

* Mon Aug 09 2021 Simone Caronni <negativo17@gmail.com> - 10:2021.07.29-1
- Update to 2021-09-27 release.

* Tue May 04 2021 Simone Caronni <negativo17@gmail.com> - 10:2021.04.21-1
- Update to 2021-04-21.

* Sat Feb 06 2021 Simone Caronni <negativo17@gmail.com> - 10:2021.01.05-1
- Update to 2021-01-05.

* Sun Nov 01 2020 Simone Caronni <negativo17@gmail.com> - 10:2020.10.09-1
- Update to 2020-10-09.

* Thu Jul 09 2020 Simone Caronni <negativo17@gmail.com> - 10:2020.07.01-1
- Update to 2020-07-01.

* Mon May 25 2020 Simone Caronni <negativo17@gmail.com> - 10:2020.05.11-1
- Update to 2020-05-11.

* Sun Apr 26 2020 Simone Caronni <negativo17@gmail.com> - 10:2020.04.18-1
- Build Schily tools from the same SPEC file and keep cdrtools separate in
  subpackages.

* Sat Oct 27 2018 Simone Caronni <negativo17@gmail.com> - 10:3.02-a09.2
- Add C++ compiler build requirement.

* Wed Feb 14 2018 Simone Caronni <negativo17@gmail.com> - 10:3.02-a09.1
- Update to 3.02a09.

* Mon Feb 27 2017 Simone Caronni <negativo17@gmail.com> - 10:3.02-a07.2
- Remove support for RHEL 5
- Implement license macro.

* Fri Dec 16 2016 Simone Caronni <negativo17@gmail.com> - 10:3.02-a07.1
- Update to 3.02a07.

* Fri Mar 25 2016 Simone Caronni <negativo17@gmail.com> - 10:3.02-a05.1
- Update to 3.02a06.

* Thu Jan 28 2016 Simone Caronni <negativo17@gmail.com> - 10:3.02-a05.1
- Update to 3.02a05.

* Mon Dec 21 2015 Simone Caronni <negativo17@gmail.com> - 10:3.02-a04.1
- Update to 3.02a04.

* Sun Dec 06 2015 Simone Caronni <negativo17@gmail.com> - 10:3.02-a03.1
- Update to 3.02a03.

* Fri Nov 20 2015 Simone Caronni <negativo17@gmail.com> - 10:3.02-a02.1
- Updated to 3.02a02.

* Tue Nov 10 2015 Simone Caronni <negativo17@gmail.com> - 10:3.02-a01.1
- Updated to 3.02a01.

* Tue Sep 08 2015 Simone Caronni <negativo17@gmail.com> - 10:3.01-a31.2
- Fix isaed requirements.

* Tue Aug 04 2015 Simone Caronni <negativo17@gmail.com> - 10:3.01-a31.1
- Update to 3.01a31.

* Wed Jul 08 2015 Simone Caronni <negativo17@gmail.com> - 10:3.01-a30.1
- Updated to 3.01a30, rc for 3.01 final.
- Add libschily manpages to devel subpackage, adjust docs for each subpackage
  and charset conversion accordingly.
- Update URL.
- Update permissions on executables.
- Use RUNPATH= also on install section, required for libschily.

* Wed Jun 10 2015 Simone Caronni <negativo17@gmail.com> - 10:3.01-a29.1
- Update to 3.01a29.

* Wed Mar 25 2015 Simone Caronni <negativo17@gmail.com> - 10:3.01-a28.1
- Update to 3.01a28.
- Switched to Sourceforge URL.

* Sat Jan 31 2015 Simone Caronni <negativo17@gmail.com> - 10:3.01-a27.1
- Update to 3.01a27.

* Wed Jan 07 2015 Simone Caronni <negativo17@gmail.com> - 10:3.01-a26.1
- Update to 3.01a26.

* Tue Oct 07 2014 Simone Caronni <negativo17@gmail.com> - 10:3.01-a25.1
- Updated to 3.01a25.

* Mon May 19 2014 Simone Caronni <negativo17@gmail.com> - 10:3.01-a24.1
- Updated to 3.01a24.

* Wed Mar 05 2014 Simone Caronni <negativo17@gmail.com> - 10:3.01-a23.1
- Updated to 3.01a23.

* Tue Jan 21 2014 Simone Caronni <negativo17@gmail.com> - 10:3.01-a22.1
- Updated to 3.01a22.

* Sat Jan 04 2014 Simone Caronni <negativo17@gmail.com> - 10:3.01-a21.1
- Updated to 3.01a21.

* Thu Jan 02 2014 Simone Caronni <negativo17@gmail.com> - 10:3.01-a20.2
- Add patch for mkisofs -help bug. Thanks Frederik.

* Mon Dec 30 2013 Simone Caronni <negativo17@gmail.com> - 10:3.01-a20.1
- Update to 3.01a20.
- Removed upstreamed patch.

* Mon Nov 25 2013 Simone Caronni <negativo17@gmail.com> - 10:3.01-a19.1
- Update to 3.01a19.

* Mon Oct 14 2013 Simone Caronni <negativo17@gmail.com> - 10:3.01-a18.2
- Add explicit dependency on versioned library packages.

* Mon Oct 14 2013 Simone Caronni <negativo17@gmail.com> - 10:3.01-a18.1
- Update to 3.01a18.

* Mon Oct 07 2013 Simone Caronni <negativo17@gmail.com> - 10:3.01-a17.2
- Enable dynamic linking and shared objects with LINKMODE; added libraries and
  devel subpackage.
- Try supporting linux file flags.
- Fix capabilities support packaging error introduced in 3.01-a17.2.

* Mon Aug 05 2013 Simone Caronni <negativo17@gmail.com> - 10:3.01-a17.1
- Updated to 3.01a17.
- Added patch to enable additional platforms (ppc/el5, ppc64/el6, armv7hl/f20).

* Mon Jul 15 2013 Simone Caronni <negativo17@gmail.com> - 10:3.01-a16.1
- Updated.

* Mon Jun 03 2013 Simone Caronni <negativo17@gmail.com> - 10:3.01-a15.1
- Updated.

* Wed Apr 24 2013 Simone Caronni <negativo17@gmail.com> - 10:3.01-a14.1
- Updated.
- Added file capabilities for RHEL 6+ and Fedora.
- Moved around %%caps enabled files as in:
  https://bugzilla.redhat.com/show_bug.cgi?id=956190
  https://bugzilla.redhat.com/show_bug.cgi?id=904818

* Tue Mar 05 2013 Simone Caronni <negativo17@gmail.com> - 10:3.01-a13.1
- Updated.

* Wed Feb 13 2013 Simone Caronni <negativo17@gmail.com> - 10:3.01-a12.1
- Updated.

* Thu Jan 10 2013 Simone Caronni <negativo17@gmail.com> - 10:3.01-a11.1
- Updated.

* Mon Dec 17 2012 Simone Caronni <negativo17@gmail.com> - 10:3.01-a10.1
- Updated.

* Tue Dec 11 2012 Simone Caronni <negativo17@gmail.com> - 10:3.01-a09.1
- Updated.

* Thu Aug 16 2012 Simone Caronni <negativo17@gmail.com> - 10:3.01-a08.1
- Updated.

* Mon May 21 2012 Simone Caronni <negativo17@gmail.com> - 10:3.01-a07.3
- Added ?_isa.
- Added license files everywhere.
- Removed devel and btcflash subpackage.
- Changed man pages packaging.

* Wed May 16 2012 Simone Caronni <negativo17@gmail.com> - 10:3.01-a07.2
- Changed default device to sr0 as the cdrom symlink changes over time.

* Mon Mar 05 2012 Simone Caronni <negativo17@gmail.com> - 10:3.01-a07.1
- Updated.

* Thu Oct 27 2011 Simone Caronni <negativo17@gmail.com> - 10:3.01-a06.1
- Updated.

* Fri Sep 16 2011 Simone Caronni <negativo17@gmail.com> - 10:3.01-a05.2
- rpmlint fixes.

* Mon Jun 06 2011 Simone Caronni <negativo17@gmail.com> - 10:3.01-a05.1
- Updated.

* Mon May 09 2011 Simone Caronni <negativo17@gmail.com> - 10:3.01-a04.1
- Updated.

* Tue Mar 15 2011 Simone Caronni <negativo17@gmail.com> - 10:3.01-a03.1
- Updated.

* Tue Feb 08 2011 Simone Caronni <negativo17@gmail.com> - 10:3.01-a02.1
- Updated.

* Fri Dec 10 2010 Simone Caronni <negativo17@gmail.com> - 10:3.01-a01.2
- Fixed rpmlint errors.

* Tue Dec 07 2010 Simone Caronni <negativo17@gmail.com> - 3.01-a01.1
- Updated to 3.01a01.

* Mon Nov 29 2010 Simone Caronni <negativo17@gmail.com> - 3.00-4
- Remove linker paths.
- setuid for cdda2wav, readcd and rscsi.

* Fri Nov 26 2010 Roman Rakus <rrakus@redhat.com> - 3.00-2
- Fixed some rpmlint errors and warnings

* Thu Nov 25 2010 Simone Caronni <negativo17@gmail.com> - 3.00-1
- First build:
    +Patch default device to match standard Fedora behaviour, the first
     cdrom device setup by udev can be used without parameters.
    +Fix german letters in copyright.
    +Obsoletes cdrkit but provides its components for Anaconda, etc.
    +Epoch set to 10 to avoid loop problems with yum.
