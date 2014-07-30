#!/bin/bash

if [[ $(uname) == Darwin ]]
then
    EXT=dylib
else
    EXT=so
fi

SITECFG=lib/iris/etc/site.cfg
echo "[System]" > $SITECFG
echo "udunits2_path = $PREFIX/lib/libudunits2.${EXT}" >> $SITECFG

$PYTHON setup.py --with-unpack build_ext --inplace --include-dirs=${PREFIX}/include --library-dirs=${PREFIX}/lib --rpath=${PREFIX}/lib install --prefix=$PREFIX
