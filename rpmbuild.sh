#!/bin/bash

#Check code by pylint
REPORT_PATH='/tmp/blik-ri.report'
BASE_SEARCH='./'
EXCLUDE_DIRS=('blik/inventory/web_site/BlikRI/media' 'blik/inventory/web_site/BlikRI/templates')

exclude=''
for i in "${EXCLUDE_DIRS[@]}"
do
    if [ -n "$exclude" ]; then exclude=$exclude" -o "; fi
    exclude=$exclude"-path $BASE_SEARCH$i -prune"
done

for file in $(/bin/find $BASE_SEARCH $exclude -o -type d -o -print)
do
    if [[ ("$file" == *".py") || (`grep -Hr -E '^#!.*python' $file | cut -d: -f1`) ]]
    then 
        FIND_FILES=("${FIND_FILES[@]}" $file)
    fi
done

echo " --> Pylint processing started"
pylint --rcfile=./pylint.rc ${FIND_FILES[@]} > $REPORT_PATH
echo " --> Pylint processing finished. See report at $REPORT_PATH"

VERS=`echo $1 | cut -d'-' -f1`
RELEASE=`echo $1 | cut -d'-' -f2- | sed -e "s/-/_/g"`
if [ $VERS = $RELEASE ]
then
    RELEASE='0'
fi

SPECFILE="blik-ri.spec"
NAME=`cat $SPECFILE | grep '%define name' | awk '{print $3}'`

rpmTopDir=/tmp/build/rpm

rm -rf $rpmTopDir
set -x
mkdir -p $rpmTopDir/{SOURCES,SRPMS,BUILD,SPECS,RPMS}

#Copy files to build directory
cp -r blik $rpmTopDir/BUILD
cp -r __init__.py $rpmTopDir/BUILD

#Define version and release in spec-file
sed -e "s/vNNN/${VERS}/g" -e "s/rNNN/${RELEASE}/g" < ./$SPECFILE >  ${rpmTopDir}/SPECS/$SPECFILE

cd ${rpmTopDir}

rpmbuild  -bb  --clean ${rpmTopDir}/SPECS/$SPECFILE
if [ $? -ne 0 ] ; then
    echo "$0: rpm build failed."
    exit 2
fi

if [ -z $2 ]
then
    echo "Output directory is not passed! Set default value ./dist"
    DIST=$OLDPWD"/dist"
else
    DIST=$2
fi

if [ ! -d "$DIST" ]; then
  mkdir -p $DIST
fi

cp ${rpmTopDir}/RPMS/noarch/${NAME}*.rpm $DIST
if [ $? -ne 0 ] ; then
    echo "$0: rpm copy failed."
    exit 2
fi