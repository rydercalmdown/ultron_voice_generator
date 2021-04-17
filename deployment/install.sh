#!/bin/bash
# install.sh

cd ../

if [ -d "src/encoder/saved_models" ] 
then
    echo "Models already downloaded" 
else
    echo "Downloading and extracting pretrained models"
    wget https://github.com/blue-fish/Real-Time-Voice-Cloning/releases/download/v1.0/pretrained.zip
    unzip pretrained.zip
    rm pretrained.zip
    mv encoder/saved_models src/encoder/saved_models
    mv synthesizer/saved_models src/synthesizer/saved_models
    mv vocoder/saved_models src/vocoder/saved_models
    rm -rf encoder
    rm -rf synthesizer
    rm -rf vocoder
    rm -rf pretrained.zip*
fi

docker build -t $IMAGE_NAME .
