# Install programs
sudo apt-get install git
sudo apt-get install bzip2
sudo apt-get install byobu
sudo apt-get install openslide-tools
sudo apt-get install gcc
sudo apt-get install python3-dev
sudo apt-get install python3-openslide


# Install anaconda
wget https://repo.anaconda.com/archive/Anaconda3-2018.12-Linux-x86_64.sh
/bin/bash Anaconda3-2018.12-Linux-x86_64.sh
rm Anaconda3-2019.03-Linux-x86_64.sh


# Install libraries
pip install openslide-python
conda install nodejs

# TF and Keras for GPU
# conda install tensorflow-gpu 
# conda install -c anaconda keras-gpu 

# TF and Keras
conda install tensorflow
conda install keras

pip install tensorboard


pip install ipywidgets 
jupyter nbextension enable --py widgetsnbextension
jupyter labextension install @jupyter-widgets/jupyterlab-manager