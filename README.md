# Byte Foods Data Analytic

This is a analysis performed on transactions of Byte Food's Kiosk in the past year. Data exploration, analysis, and pipeline explanation are detailed in the Jupyter Notebook file (data_exploration.ipynb). 

## Prerequisites
The data analysis and pipeline were built with Python 3. A Python pip requirement.txt is included in this repo to reproduce the analytics as well as run the pipeline. Virtualenv or Anaconda are recommended to manage the environment.

Data are not included in the repo due to Github's size limitation, so users will have to manually drop the data file with the name **items_purchased.csv** into the **data** folder.


```
pip3 install -r requirements.txt
```

## Usage
Run the anomaly_detection Python script in command prompt or terminal. And then follow the prompts to find anomaly events in Kiosks and Products.

```
python anomaly_detection.py
```