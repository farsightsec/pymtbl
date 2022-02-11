Name:           python3-pymtbl
Version:        0.5.1
Release:        1%{?dist}
Summary:        immutable sorted string table library (Python3 bindings)

License:        Apache-2.0
URL:            https://github.com/farsightsec/pymtbl
Source0:        https://dl.farsightsecurity.com/dist/pymtbl/pymtbl-%{version}.tar.gz

#BuildArch:
BuildRequires:  mtbl-devel
BuildRequires:	python3-devel python36-Cython
Requires:	mtbl

%description
mtbl is a immutable sorted string table library.

This package contains the Python 3 wrapper for libmtbl's reader, writer,
sorter, and merger interfaces

%prep
%setup -q -n pymtbl-%{version}


%build
%py3_build


%install
rm -rf $RPM_BUILD_ROOT
%py3_install


%files
%doc
# For arch-specific packages: sitearch
%{python3_sitearch}/*


%changelog
