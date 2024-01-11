%{!?_pkgdocdir:%global _pkgdocdir %{_docdir}/%{name}-%{version}}

%global so_ver      4
%global reldate     20180305

# Uncomment when building a bootstrap for a bumped so-name.
# You also need to adjust the parameters below.
%global bootstrap   0

%if 0%{?bootstrap}
%global reldate_old 20171207
%global version_old 0.13
%global so_ver_old  3
%endif


Name:           json-c
Version:        0.13.1
Release:        3%{?dist}
Summary:        JSON implementation in C

License:        MIT
URL:            https://github.com/%{name}/%{name}
Source0:        %{url}/archive/%{name}-%{version}-%{reldate}.tar.gz
%if 0%{?bootstrap}
Source1:        %{url}/archive/%{name}-%{version_old}-%{reldate_old}.tar.gz
%endif
# CVE-2020-12762 json-c: integer overflow and out-of-bounds write via a large JSON file
# rhbz#1835626
Patch0:		json-c-int-overflow.patch
# patch for support of versioned symbols
# rhbz#2001063
Patch1:		json-c-versioned-symbols.patch

BuildRequires:  libtool

%description
JSON-C implements a reference counting object model that allows you
to easily construct JSON objects in C, output them as JSON formatted
strings and parse JSON formatted strings back into the C representation
of JSON objects.  It aims to conform to RFC 7159.


%package        devel
Summary:        Development files for %{name}

Requires:       %{name}%{?_isa} == %{version}-%{release}

%description    devel
This package contains libraries and header files for
developing applications that use %{name}.


%package        doc
Summary:        Reference manual for json-c

BuildArch:      noarch

BuildRequires:  doxygen
BuildRequires:  hardlink

%description    doc
This package contains the reference manual for %{name}.


%prep
%autosetup -Tb 0 -n %{name}-%{name}-%{version}-%{reldate} -p 1

for doc in ChangeLog; do
  %{_bindir}/iconv -f iso-8859-1 -t utf8 ${doc} > ${doc}.new
  /bin/touch -r ${doc} ${doc}.new
  %{__mv} -f ${doc}.new ${doc}
done

%{__sed} -i -e 's!#ACLOCAL_AMFLAGS!ACLOCAL_AMFLAGS!g' Makefile.am
%{_bindir}/autoreconf -fiv

%if 0%{?bootstrap}
%{__mkdir} -p bootstrap_ver
pushd bootstrap_ver
%{__tar} --strip-components=1 -xf %{SOURCE1}

%{__sed} -i -e 's!#ACLOCAL_AMFLAGS!ACLOCAL_AMFLAGS!g' Makefile.am
%{_bindir}/autoreconf -fiv
popd
%endif


%build
# it is easier and more efficient to add version script flag
# here instead of having to rebuild the configure script
LDFLAGS="%{build_ldflags} -Wl,--version-script,${PWD}/json-c.sym"
%configure               \
  --disable-silent-rules \
  --disable-static       \
  --enable-shared        \
  --enable-threading

%make_build

%{_bindir}/doxygen Doxyfile

%if 0%{?bootstrap}
pushd bootstrap_ver
%configure               \
  --disable-silent-rules \
  --disable-static       \
  --enable-shared        \
  --enable-threading

%make_build
popd
%endif


%install
%if 0%{?bootstrap}
%make_install -C bootstrap_ver
%{__rm} -fr %{buildroot}%{_includedir}/%{name}   \
            %{buildroot}%{_libdir}/lib%{name}.so \
            %{buildroot}%{_libdir}/pkgconfig
%endif

%make_install

%{_bindir}/find %{buildroot} -name '*.a' -delete -print
%{_bindir}/find %{buildroot} -name '*.la' -delete -print

%{__mkdir} -p %{buildroot}%{_pkgdocdir}
%{__cp} -pr doc/html ChangeLog README README.* %{buildroot}%{_pkgdocdir}
%{_sbindir}/hardlink -cvf %{buildroot}%{_pkgdocdir}


%check
%make_build check

%if 0%{?bootstrap}
%make_build -C bootstrap_ver check
%endif


%pretrans devel -p <lua>
path = "%{_includedir}/%{name}"
st = posix.stat(path)
if st and st.type == "link" then
  os.remove(path)
end


%ldconfig_scriptlets


%files
%license AUTHORS
%license COPYING
%{_libdir}/lib%{name}.so.%{so_ver}*
%if 0%{?bootstrap}
%{_libdir}/lib%{name}.so.%{so_ver_old}*
%endif


%files devel
%doc %{_pkgdocdir}/ChangeLog
%doc %{_pkgdocdir}/README*
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc


%files doc
%if 0%{?fedora} || 0%{?rhel} >= 7
%license %{_datadir}/licenses/%{name}*
%endif # 0%%{?fedora} || 0%%{?rhel} >= 7
%doc %{_pkgdocdir}


%changelog
* Tue Sep 14 2021 Tomas Korbar <tkorbar@redhat.com> - 0.13.1-3
- Start versioning symbols when building library
- Resolves: rhbz#2001063

* Thu May 20 2021 Joe Orton <jorton@redhat.com> - 0.13.1-2
- rebuild (#1954436)

* Thu Apr 15 2021 Tomas Korbar <tkorbar@redhat.com> - 0.13.1-1
- Fix CVE-2020-12762 out-of-bounds write via a large JSON file
- Resolves: rhbz#1835626

* Wed Feb 03 2021 Petr Menšík <pemensik@redhat.com> - 0.13.1-0.4
- Move json-c-devel to AppStream

* Fri Sep 18 2020 Anna Khaitovich <akhaitov@redhat.com> - 0.13.1-0.3
- Don't package empty /usr/share/doc/json-c
- Resolves: rhbz#1741076
- Do not use --enable-rdrand
- Resolves: rhbz#1806532

* Fri Aug 03 2018 Radovan Sroka <rsroka@redhat.com> - 0.13.1-0.2
- disable bootstrap for RHEL8

* Tue Mar 06 2018 Björn Esser <besser82@fedoraproject.org> - 0.13.1-0.1
- Bootstrapping for so-name bump

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.13-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Feb 02 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.13-6
- Switch to %%ldconfig_scriptlets

* Thu Dec 14 2017 Björn Esser <besser82@fedoraproject.org> - 0.13-5
- Update patch fixing a segfault caused by possible invalid frees

* Wed Dec 13 2017 Björn Esser <besser82@fedoraproject.org> - 0.13-4
- Add upstream patch fixing invalid free in some cases

* Wed Dec 13 2017 Björn Esser <besser82@fedoraproject.org> - 0.13-3
- Add upstream patch for adding size_t json_c_object_sizeof()
- Enable partial multi-threaded support

* Mon Dec 11 2017 Björn Esser <besser82@fedoraproject.org> - 0.13-2
- Drop json_object_private.h

* Mon Dec 11 2017 Björn Esser <besser82@fedoraproject.org> - 0.13-1
- New upstream release (rhbz#1524155)

* Sun Dec 10 2017 Björn Esser <besser82@fedoraproject.org> - 0.13-0.1
- Bootstrapping for so-name bump
- Keep json_object_private.h

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.12.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.12.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 03 2017 Björn Esser <besser82@fedoraproject.org> - 0.12.1-2
- Add patch to replace obsolete autotools macro

* Thu Apr 27 2017 Björn Esser <besser82@fedoraproject.org> - 0.12.1-1
- Update to new upstream release
- Introduces SONAME bump, that should have been in 0.12 already
- Unify %%doc
- General spec-file cleanup

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.12-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.12-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.12-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.12-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jul 29 2014 Christopher Meng <rpm@cicku.me> - 0.12-4
- SONAME bump postponed.

* Mon Jul 28 2014 Christopher Meng <rpm@cicku.me> - 0.12-3
- SONAME bump, see bug 1123785

* Fri Jul 25 2014 Christopher Meng <rpm@cicku.me> - 0.12-2
- NVR bump

* Thu Jul 24 2014 Christopher Meng <rpm@cicku.me> - 0.12-1
- Update to 0.12

* Sat Jul 12 2014 Tom Callaway <spot@fedoraproject.org> - 0.11-8
- fix license handling

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Apr 09 2014 Susi Lehtola <jussilehtola@fedoraproject.org> - 0.11-7
- Address CVE-2013-6371 and CVE-2013-6370 (BZ #1085676 and #1085677).
- Enabled rdrand support.

* Mon Feb 10 2014 Susi Lehtola <jussilehtola@fedoraproject.org> - 0.11-6
- Bump spec.

* Sat Dec 21 2013 Ville Skyttä <ville.skytta@iki.fi> - 0.11-5
- Run test suite during build.
- Drop empty NEWS from docs.

* Tue Sep 10 2013 Susi Lehtola <jussilehtola@fedoraproject.org> - 0.11-4
- Remove default warning flags so that package builds on EPEL as well.

* Sat Aug 24 2013 Remi Collet <remi@fedoraproject.org> - 0.11-3
- increase parser strictness for php

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Apr 29 2013 Remi Collet <remi@fedoraproject.org> - 0.11-1
- update to 0.11
- fix source0
- enable both json and json-c libraries

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Nov 24 2012 Jussi Lehtola <jussilehtola@fedoraproject.org> - 0.10-2
- Compile and install json_object_iterator using Remi Collet's fix (BZ #879771).

* Sat Nov 24 2012 Jussi Lehtola <jussilehtola@fedoraproject.org> - 0.10-1
- Update to 0.10 (BZ #879771).

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jan 23 2012 Jiri Pirko <jpirko@redhat.com> - 0.9-4
- add json_tokener_parse_verbose, and return NULL on parser errors

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Apr 06 2010 Jussi Lehtola <jussilehtola@fedoraproject.org> - 0.9-1
- First release.
