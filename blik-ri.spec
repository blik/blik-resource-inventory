%define name blik-ri
%define version vNNN
%define release rNNN
%define _topdir /tmp/build/rpm
%define _tmppath /tmp
%define blikridir /opt/blik/inventory

Summary: Blik Resource Inventory
Name: %{name}
Version: %{version}
Release: %{release}
License: GPLv3
Group: Development/Application
BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot
BuildArch: noarch
Vendor: Blik software

Requires: python >= 2.6
Requires: mongo-10gen, mongo-10gen-server, pymongo
Requires: libyaml, PyYAML
Requires: Django14
Requires: python-cherrypy


%description
This is lightweight inventory system for storing and managing any types of resources.
Blik Resource Inventory allows you to create your specific structure of resources and
implement custom login for this resources.

Blik Resource Inventory store their objects in NoSQL database.

%prep

%build
mkdir -p $RPM_BUILD_ROOT%{blikridir}
cp -r ./blik/inventory/* $RPM_BUILD_ROOT%{blikridir}

mkdir -p $RPM_BUILD_ROOT/var/log/blik/inventory/
mkdir -p $RPM_BUILD_ROOT/etc/init.d/

cp ./blik/inventory/service/blikri $RPM_BUILD_ROOT/etc/init.d/

%pre

%install
echo "package installed"

%post
#!/bin/bash
#TODO: Create service to simple work with BlikRI
#chkconfig --add blikri
#chkconfig --levels 345 blikri on

if [ ! -e %{blikridir}/conf/blik-ri-conf.yaml ]; then
    echo
    echo "-----------------------------------------------------------------------------------------------------------------------------"
    echo "NOTICE: Configuration of Blik Resource Inventory should be saved into /opt/blik/inventory/conf/blik-ri-conf.yaml"
    echo "        See configuration sample in /opt/blik/inventory/conf/blik-ri-conf.yaml.example file"
    echo "-----------------------------------------------------------------------------------------------------------------------------"
fi

if [ ! -e %{blikridir}/conf/cherrypy.conf ]; then
    echo
    echo "-----------------------------------------------------------------------------------------------------------------------------"
    echo "NOTICE: Configuration of CherryPy WebServer should be saved into /opt/blik/inventory/conf/cherrypy.conf"
    echo "        See configuration sample in /opt/blik/inventory/conf/cherrypy.conf.example file"
    echo "-----------------------------------------------------------------------------------------------------------------------------"
fi



%preun
%postun

%clean
if [ $RPM_BUILD_ROOT != '/' ]; then rm -rf $RPM_BUILD_ROOT; fi

%files
%defattr(-,root,root)
%attr(775,root,root) %{blikridir}/*
%attr(775,root,root) /var/log/blik/inventory
%attr(755,root,root) /etc/init.d/blikri
