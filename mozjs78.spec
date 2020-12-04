#
# Conditional build:
%bcond_without	tests	# tests build

Summary:	SpiderMonkey 78 - JavaScript implementation
Summary(pl.UTF-8):	SpiderMonkey 78 - implementacja języka JavaScript
Name:		mozjs78
Version:	78.2.0
Release:	2
License:	MPL v2.0
Group:		Libraries
#Source0:	http://ftp.gnome.org/pub/gnome/teams/releng/tarballs-needing-help/mozjs/mozjs-%{version}.tar.bz2
Source0:	http://ftp.mozilla.org/pub/firefox/releases/%{version}esr/source/firefox-%{version}esr.source.tar.xz
# Source0-md5:	e071f6c9bea8344d4556323f02bf6125
Patch0:		copy-headers.patch
Patch1:		system-virtualenv.patch
Patch2:		include-configure-script.patch
Patch3:		x32.patch
Patch4:		%{name}-x32-rust.patch
Patch5:		arm.patch
URL:		https://developer.mozilla.org/en-US/docs/Mozilla/Projects/SpiderMonkey
BuildRequires:	autoconf2_13 >= 2.13
BuildRequires:	cargo
# "TestWrappingOperations.cpp:27:1: error: non-constant condition for static assertion" with -fwrapv on gcc 6 and 7
%{?with_tests:BuildRequires:	gcc-c++ >= 6:8}
BuildRequires:	libicu-devel >= 67.1
BuildRequires:	libstdc++-devel >= 6:4.4
BuildRequires:	nspr-devel >= 4.25
BuildRequires:	perl-base >= 1:5.6
BuildRequires:	pkgconfig
BuildRequires:	python3 >= 1:3.8.5-3
BuildRequires:	python3-virtualenv >= 1.9.1-4
BuildRequires:	readline-devel
BuildRequires:	rpm-perlprov
BuildRequires:	rpmbuild(macros) >= 1.294
BuildRequires:	rust >= 1.41.0
BuildRequires:	zlib-devel >= 1.2.3
Requires:	nspr >= 4.25
Requires:	zlib >= 1.2.3
ExclusiveArch:	%{x8664} %{ix86} x32 aarch64 armv6hl armv7hl armv7hnl
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
JavaScript Reference Implementation (codename SpiderMonkey). The
package contains JavaScript runtime (compiler, interpreter,
decompiler, garbage collector, atom manager, standard classes) and
small "shell" program that can be used interactively and with .js
files to run scripts.

%description -l pl.UTF-8
Wzorcowa implementacja JavaScriptu (o nazwie kodowej SpiderMonkey).
Pakiet zawiera środowisko uruchomieniowe (kompilator, interpreter,
dekompilator, odśmiecacz, standardowe klasy) i niewielką powłokę,
która może być używana interaktywnie lub z plikami .js do uruchamiania
skryptów.

%package devel
Summary:	Header files for JavaScript reference library
Summary(pl.UTF-8):	Pliki nagłówkowe do biblioteki JavaScript
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	libstdc++-devel
Requires:	nspr-devel >= 4.25

%description devel
Header files for JavaScript reference library.

%description devel -l pl.UTF-8
Pliki nagłówkowe do biblioteki JavaScript.

%prep
%setup -q -n firefox-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%ifarch x32
%patch4 -p1
%endif
%patch5 -p1

%build
export PYTHON="%{__python}"
export AUTOCONF="%{_bindir}/autoconf2_13"
export SHELL="/bin/sh"
cd js/src
mkdir -p obj
cd obj

%define configuredir ".."
%configure2_13 \
	--enable-gcgenerational \
	--disable-jemalloc \
	--enable-readline \
	--enable-shared-js \
	%{!?with_tests:--disable-tests} \
	--enable-threadsafe \
	--with-intl-api \
	--with-system-icu \
	--with-system-nspr \
	--with-system-zlib

%{__make} \
	HOST_OPTIMIZE_FLAGS= \
	MODULE_OPTIMIZE_FLAGS= \
	MOZ_OPTIMIZE_FLAGS="-freorder-blocks" \
	MOZ_PGO_OPTIMIZE_FLAGS= \
	MOZILLA_VERSION=%{version}

%install
rm -rf $RPM_BUILD_ROOT

cd js/src/obj

%{__make} -C js/src install \
	DESTDIR=$RPM_BUILD_ROOT \
	MOZILLA_VERSION=%{version}

%{__rm} $RPM_BUILD_ROOT%{_libdir}/*.ajs

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc js/src/README.html
%attr(755,root,root) %{_bindir}/js78
%attr(755,root,root) %{_libdir}/libmozjs-78.so

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/js78-config
%{_includedir}/mozjs-78
%{_pkgconfigdir}/mozjs-78.pc
