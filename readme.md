# Installation
```
conda create --name edgs python=3.10
conda activate edgs
# for doubao
pip install volcengine-python-sdk[ark] 
# for awake
cd edgs/external
sudo apt update
sudo apt install swig
sudo apt install libblas-dev liblapack-dev
sudo apt install libatlas-base-dev
cd snowboy/swig/Python3
make
# for understanding module
sudo apt-get install portaudio19-dev
# for curobo
cd edgs/external/curobo
pip install -r requirements.txt
pip install -e .
```

## 设置dinox
在<a hraf="https://cloud.deepdataspace.com/">dino-x开放平台</a>注册帐号后会有20元的额度，可用于购买dino-x的服务。

点击控制台-Token密钥，创建项目后即可获得token。然后在路径`edgs/dexterous_grasp/config/vision_module_variant.py`中填入token。

## 设置doubao
在<a hraf="https://console.volcengine.com/ark/region:ark+cn-beijing/model/detail?Id=doubao-pro-32k&projectName=undefined">火山引擎官网</a>获取doubao的api_key。
在路径`edgs/dexterous_grasp/config/understanding_module_varant.py`中填入api_key。


# Run
```
cd edgs
python main.py
```

