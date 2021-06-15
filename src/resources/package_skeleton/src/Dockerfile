FROM arm64v8/ubuntu

#Download python3 and numpy
RUN apt-get update \
&& apt-get install -y software-properties-common \
&& add-apt-repository ppa:deadsnakes/ppa \
&& apt-get install -y python3-pip python3.7-dev libkeyutils-dev \
&& cd /usr/local/bin \
&& ln -s /usr/bin/python3 python \
&& apt-get clean \
&& pip3 install --upgrade pip \
&& pip3 install numpy==1.18.2

#Required so we can mount these locations from a read-only sqfs
RUN mkdir -p /Panorama/usr/local
RUN mkdir -p /Panorama/usr/lib
RUN mkdir -p /data/containerLogs

#Temporary group required in the container. 
RUN groupadd panoramaCommon