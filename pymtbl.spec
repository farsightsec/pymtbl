# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python-pymtbl
Version:        0.4.1
Release:        1%{?dist}
Summary:        immutable sorted string table library (Python bindings)

License:        Apache-2.0
URL:            https://github.com/farsightsec/pymtbl
Source0:        https://dl.farsightsecurity.com/dist/pymtbl/pymtbl-%{version}.tar.gz

#BuildArch:
BuildRequires:  python-devel mtbl-devel Cython
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


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT


%files
%doc
# For arch-specific packages: sitearch
%{python_sitearch}/*


%changelog
