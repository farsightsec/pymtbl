Name:           python-pymtbl
Version:        0.5.0
Release:        1%{?dist}
Summary:        immutable sorted string table library (Python bindings)

License:        Apache-2.0
URL:            https://github.com/farsightsec/pymtbl
Source0:        https://dl.farsightsecurity.com/dist/pymtbl/pymtbl-%{version}.tar.gz

#BuildArch:
BuildRequires:  python-devel mtbl-devel Cython >= 0.25.2
BuildRequires:	python3-devel python36-Cython
Requires:	mtbl

%description
mtbl is a immutable sorted string table library.

This package contains the Python wrapper for libmtbl's reader, writer,
sorter, and merger interfaces

%prep
%setup -q -n pymtbl-%{version}


%build
# Remove CFLAGS=... for noarch packages (unneeded)
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build
%py3_build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
%py3_install


%files
%doc
# For arch-specific packages: sitearch
%{python_sitearch}/*

%package -n python3-pymtbl
Summary:	immutable sorted string table library (Python3 bindings)

%description -n python3-pymtbl
mtbl is a immutable sorted string table library.

This package contains the Python 3 wrapper for libmtbl's reader, writer,
sorter, and merger interfaces

%files -n python3-pymtbl
%doc
%{python3_sitearch}/*


%changelog
