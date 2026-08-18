Name:           python3-pymtbl
Version:        0.6.1
Release:        1%{?dist}
Summary:        immutable sorted string table library (Python3 bindings)

License:        Apache-2.0
URL:            https://github.com/farsightsec/pymtbl
Source0:        pymtbl-%{version}.tar.gz

BuildRequires:  mtbl-devel
BuildRequires:  python3-devel
BuildRequires:  python3-Cython
BuildRequires:  python3-setuptools
BuildRequires:  pkg-config
Requires:       mtbl

%description
mtbl is an immutable sorted string table library.

This package contains the Python 3 wrapper for libmtbl's reader, writer,
sorter, and merger interfaces.

%prep
%setup -q -n pymtbl-%{version}

%build
%py3_build

%install
%py3_install

%files
%license COPYRIGHT LICENSE
%doc README.md
%{python3_sitearch}/mtbl*.so
%{python3_sitearch}/pymtbl-%{version}-*.egg-info

%changelog
* Mon Aug 18 2026 Allan LeSage <alesage@domaintools.com> - 0.6.1-1
- Fix build with Cython 3.X
- Modernize packaging: add pyproject.toml, clean up spec
