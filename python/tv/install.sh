#!/bin/bash
# Frank Zhao, July 2015
echo "Download prerequisites... [1 of 4]"
curl -O http://www.ist-inc.com/motif/download/motif_files/openmotif-compat-2.1.32_IST.macosx10.5.dmg
curl -O ftp://ftp.freetds.org/pub/freetds/stable/freetds-patched.tar.gz
curl -O http://xquartz.macosforge.org/downloads/SL/XQuartz-2.7.7.dmg
curl -O http://www.mdsplus.org/dist/macosx/stable/MDSplus-7-0-103-osx.pkg

echo "Installing OpenMotif... [1 of 4]"
hdiutil attach openmotif-compat-2.1.32_IST.macosx10.5.dmg
installer -pkg /Volumes/openmotif/OpenMotif-compat-2.1.32.pkg -target /

echo "Installing Xquartz... [2 of 4]"
hdiutil attach XQuartz-2.7.7.dmg
installer -pkg /Volumes/XQuartz-2.7.7/XQuartz.pkg -target /

echo "Installing FreeTDS... [3 of 4]"
tar -xvf freetds-patched.tar.gz

echo "Installing MDSplus... [4 of 4]"
installer -pkg MDSplus-7-0-103-osx.pkg -target /

cd freetds-0.95.18 && ./configure
make -j4
make install
cd ..

# Configure this to your tree_path
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/usr/local/mdsplus/lib

# Configure MATLAB
source /usr/local/mdsplus/setup.sh
sed -i '' '1i\'$'\n''/usr/local/mdsplus/java/classes/mdsobjects.jar'$'\n' /Applications/MATLAB_R2014b.app/toolbox/local/classpath.txt
echo /usr/local/mdsplus/lib/ >> /Applications/MATLAB_R2014b.app/toolbox/local/librarypath.txt
echo /usr/local/mdsplus/java/classes/mdsobjects.jar > ~/.matlab/R2014b/javalibrarypath.txt
sh -c '/usr/local/mdsplus/bin/mdsplus_launchconfig >> /etc/launchd.conf'

# Install Python library
pip install numpy
pip install mdsplus

echo "Cleaning up..."
hdiutil eject `df | grep XQuartz | cut -d " " -f 1`
hdiutil eject `df | grep openmotif | cut -d " " -f 1`
rm -rf freetds-0.95.18
rm -rf MDSplus-7-0-103-osx.pkg

echo "Done!"