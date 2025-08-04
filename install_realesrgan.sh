#!/bin/bash
pip install torch numpy opencv-python
git clone https://github.com/xinntao/Real-ESRGAN
cd Real-ESRGAN
pip install -r requirements.txt
python setup.py develop