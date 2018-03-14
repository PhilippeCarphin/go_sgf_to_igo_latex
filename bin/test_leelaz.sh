pushd $(dirname $0) >/dev/null
basepath=$(pwd)
popd > /dev/null

echo "basepath = $basepath"

leela="echo invalid uname"
if [ $(uname) = Darwin ] ; then
	leela=./leelaz_osx_x64_opencl
elif [ $(uname) = Linux ] ; then
	leela=./leelaz_linux_x64 -w 
fi

$leela -w leelaz-model-5309030-128000.txt $1 $2
