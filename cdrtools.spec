# Put to Alpha version if you need alpha releases
%global alpha_version a06

# Expand version and url
%if 0%{?alpha_version:1}
%define alpha_url /alpha
%endif

%if 0%{?rhel} == 5
%global perms_cdda2wav %attr(4755, root, root)
%global perms_cdrecord %attr(4755, root, root)
%global perms_readcd %attr(4755, root, root)
%else
%global perms_cdda2wav %caps(cap_dac_override,cap_sys_admin,cap_sys_nice,cap_net_bind_service,cap_sys_rawio+ep)
%global perms_cdrecord %caps(cap_sys_resource,cap_dac_override,cap_sys_admin,cap_sys_nice,cap_net_bind_service,cap_ipc_lock,cap_sys_rawio+ep)
%global perms_readcd %caps(cap_dac_override,cap_sys_admin,cap_net_bind_service,cap_sys_rawio+ep)
%endif

Name:           cdrtools
Version:        3.02
Release:        %{?alpha_version}.1%{?dist}
Epoch:          10
Summary:        CD/DVD/BluRay command line recording software

Group:          Applications/Archiving
License:        CDDL and GPLv2 and BSD
URL:            http://cdrtools.sourceforge.net/private/cdrecord.html
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Source0:        http://downloads.sourceforge.net/%{name}%{?alpha_url}/%{name}-%{version}%{?alpha_version}.tar.bz2
Patch0:         %{name}-%{version}-cdrecord-default.patch

BuildRequires:  gettext-devel
%if 0%{?fedora} || 0%{?rhel} >= 6
BuildRequires:  libcap-devel
%endif

%description
A set of command line programs that allows to record CD/DVD/BluRay media.

%package -n cdrecord
Summary:        Creates an image of an ISO9660 file system
Group:          Applications/Archiving
Requires:       %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Obsoletes:      wodim < %{epoch}:
Provides:       wodim = %{epoch}:

%description -n cdrecord
A set of command line programs that allows to record and read CD/DVD/BluRay
media.

%package -n mkisofs
Summary:        Creates an image of an ISO9660 file system
Group:          Applications/Archiving
Requires:       %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Obsoletes:      genisoimage < %{epoch}:
Provides:       genisoimage = %{epoch}:

%description -n mkisofs
Programs to create and manipulate hybrid ISO9660/JOLIET/HFS file systems with
Rock Ridge attributes.

%package -n cdda2wav
Summary:        A CD-Audio Grabbing tool
Group:          Applications/Multimedia
Requires:       %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Obsoletes:      icedax < %{epoch}: 
Provides:       icedax = %{epoch}:

%description -n cdda2wav
The most evolved CD-audio extraction program with paranoia support.

%package devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}

%description devel
This package provides the development files of the %{name} package.

%package libs
Summary:        Libraries for %{name}
Group:          System Environment/Libraries
Requires(post): ldconfig

%description libs
This package provides the shared libraries for %{name}.

%prep
%setup -q
%patch0 -p0
rm -fr btcflash

# Convert files to utf8 for german letters
for i in \
    $(find . -name "*.c") \
    $(find . -name "*.1") \
    $(find . -name "*.3") \
    $(find . -name "*.8") \
    $(find . -name "README*") \
    $(find . -name "THANKS*"); do
    iconv -f iso-8859-1 $i -t utf-8 -o $i.new && mv -f $i.new $i
done

%build
make GMAKE_NOWARN=true LINKMODE="dynamic" RUNPATH= \
    CPPOPTX="$RPM_OPT_FLAGS" COPTX="$RPM_OPT_FLAGS -DTRY_EXT2_FS"

%install
rm -rf %{buildroot}
make GMAKE_NOWARN=true LINKMODE="dynamic" RUNPATH= \
    INS_BASE=%{_prefix} INS_RBASE=/ DESTDIR=%{buildroot} \
    install

# Remove unused libraries
rm -fr %{buildroot}%{_prefix}/lib/profiled
rm -f %{buildroot}%{_prefix}/lib/lib*.a
# Remove makefiles and makerules manpages
rm -fr %{buildroot}%{_mandir}/man5
# Install documents directly from the files section
rm -fr %{buildroot}%{_docdir}

# Move libraries to the appropriate place on 64 bit arches
if [ %{_libdir} != %{_prefix}/lib ]; then 
    mkdir -p %{buildroot}%{_libdir}
    mv %{buildroot}%{_prefix}/lib/lib*.so* %{buildroot}%{_libdir}
fi

chmod 755 %{buildroot}%{_libdir}/lib*.so* \
    %{buildroot}%{_bindir}/* %{buildroot}%{_sbindir}/*

%clean
rm -rf %{buildroot}

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files -n cdrecord
%defattr(-,root,root,-)
%doc cdrecord/README*
%config(noreplace) /etc/default/cdrecord
%config(noreplace) /etc/default/rscsi
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
%defattr(-,root,root,-)
%doc mkisofs/COPYING mkisofs/RELEASE mkisofs/TODO mkisofs/README*
%{_bindir}/mkisofs
%{_bindir}/mkhybrid
%{_bindir}/isoinfo
%{_bindir}/devdump
%{_bindir}/isodump
%{_bindir}/isovfy
%{_bindir}/isodebug
%{_mandir}/man8/*
%{_prefix}/lib/siconv/*

%files -n cdda2wav
%defattr(-,root,root,-)
%doc cdda2wav/FAQ cdda2wav/HOWTOUSE cdda2wav/NEEDED cdda2wav/TODO cdda2wav/THANKS cdda2wav/README
%{_bindir}/cdda2mp3
%{_bindir}/cdda2ogg
%{perms_cdda2wav} %{_bindir}/cdda2wav
%{_mandir}/man1/cdda2wav.*
%{_mandir}/man1/cdda2mp3.*
%{_mandir}/man1/cdda2ogg.*

%files libs
%defattr(-,root,root,-)
%doc COPYING GPL-2.0.txt LGPL-2.1.txt CDDL.Schily.txt
%{_libdir}/lib*.so.*

%files devel
%defattr(-,root,root,-)
%{_includedir}/*
%{_libdir}/lib*.so
%{_mandir}/man3/*

%changelog
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
