FROM ubuntu:14.04
MAINTAINER Stuti Agrawal <stutia@uchicago.edu>
USER root
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --force-yes \
    curl \
    g++ \
    make \
    python \
    libboost-dev \
    libboost-thread-dev \
    libboost-system-dev \
    zlib1g-dev \
    ncurses-dev \
    unzip \
    gzip \
    bzip2 \
    libxml2-dev \
    libxslt-dev \
    python-pip \
    python-dev \
    git \
    s3cmd \
    time \
    wget \
    python-virtualenv \
    default-jre \
    default-jdk

RUN adduser --disabled-password --gecos '' ubuntu && adduser ubuntu sudo && echo "ubuntu    ALL=(ALL)   NOPASSWD:ALL" >> /etc/sudoers.d/ubuntu
ENV HOME /home/ubuntu
USER ubuntu
RUN mkdir ${HOME}/bin
WORKDIR ${HOME}/bin

#install STAR 
RUN wget https://github.com/alexdobin/STAR/archive/STAR_2.4.0f1.tar.gz && tar xzvf STAR_2.4.0f1.tar.gz 

#download Samtools
RUN wget http://sourceforge.net/projects/samtools/files/samtools/1.1/samtools-1.1.tar.bz2 && tar xf samtools-1.1.tar.bz2 && mv samtools-1.1 samtools
WORKDIR ${HOME}/bin/samtools/
RUN make
WORKDIR ${HOME}/bin

#install cufflinks
RUN wget http://cole-trapnell-lab.github.io/cufflinks/assets/downloads/cufflinks-2.2.1.Linux_x86_64.tar.gz && tar -xzvf cufflinks-2.2.1.Linux_x86_64.tar.gz 

#install FastQC 0.11.3
RUN wget http://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.3.zip && unzip fastqc_v0.11.3.zip && chmod +x FastQC/fastqc 

#download Picard
RUN wget https://github.com/broadinstitute/picard/releases/download/1.136/picard-tools-1.136.zip && unzip picard-tools-1.136.zip

#download Biobambam
RUN wget https://github.com/gt1/biobambam2/releases/download/2.0.8-release-20150427235350/biobambam2-2.0.8-release-20150427235350-x86_64-etch-linux-gnu.tar.gz && tar xf biobambam2-2.0.8-release-20150427235350-x86_64-etch-linux-gnu.tar.gz && mv biobambam2-2.0.8-release-20150427235350-x86_64-etch-linux-gnu biobambam


#remove the compressed files
RUN rm *.gz *.zip

USER ubuntu

ENV PATH ${PATH}:${HOME}/bin/FastQC:${HOME}/bin/STAR-STAR_2.4.0f1/bin/Linux_x86_64:${HOME}/bin/biobambam/bin:${HOME}/bin/samtools/:${HOME}/bin/cufflinks-2.2.1.Linux_x86_64/
USER root

RUN pip install lxml
RUN pip install s3cmd --user
ENV rna_seq_star_cuff 1.8
WORKDIR ${HOME}
RUN git clone https://github.com/stutiagrawal/expression/
WORKDIR ${HOME}/bin

