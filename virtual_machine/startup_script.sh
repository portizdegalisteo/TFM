sudo -su jupyter bash
cd
# wget https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh
wget https://repo.anaconda.com/archive/Anaconda2-2018.12-Linux-x86_64.sh

/bin/bash Anaconda3-2019.03-Linux-x86_64.sh -b
rm Anaconda3-2019.03-Linux-x86_64.sh


conda install ipykernel
ipython kernel install --name base --user



pip install ipywidgets 

jupyter nbextension enable --py widgetsnbextension
jupyter labextension install @jupyter-widgets/jupyterlab-manager


apt-get install openslide-tools	
apt-get install python3-openslide
pip install openslide-python
pip install numpy==1.15.4 
pip install pandas==0.23.4


conda install tensorflow-gpu 
conda install keras-gpu 
conda install -c anaconda keras-gpu 

# gcloud auth login
