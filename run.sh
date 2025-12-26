#!/bin/bash
export JAVA_HOME=~/Downloads/jdk-17.0.2.jdk/Contents/Home
export PATH=$JAVA_HOME/bin:$PATH
export PATH=~/Downloads/gradle-8.6/bin:$PATH

gradle :applications:provenance-server:build -x test && \
java -Djavax.net.ssl.trustStore=/dev/null \
     -Djavax.net.ssl.trustStoreType=KeychainStore \
     -jar applications/provenance-server/build/libs/provenance-server-1.0-SNAPSHOT.jar
