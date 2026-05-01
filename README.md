# DM-GRD

**💡 This is the official implementation of the paper "Dual Memory Networks Guided Reverse Distillation for Unsupervised Anomaly Detection (ACCV 2024)"**  

## 🔧 Installation
```
### Using conda
#### Using environment.yml
```bash
conda env create -f envs/environment.yml
conda activate anomaly
pip install -e .
```

#### Using requirements.txt
```bash
conda create --name anomaly python=3.10.12
conda activate anomaly
pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu117
pip install -r envs/requirements.txt
pip install -e .
```

### Using uv
```bash
uv venv anomaly --python=3.10.12
source anomaly/bin/activate
uv pip install -e .
```

## 🏆 Dataset preparation
For the MVTec dataset, please download it from this [link](https://www.mvtec.com/company/research/datasets/mvtec-ad).

For the BTAD dataset, please download it from this [repository](https://github.com/pankajmishra000/VT-ADL).

For the VisA dataset, please download it from this [repository](https://github.com/amazon-science/spot-diff).

For the DTD dataset, please download it from this [link](https://www.robots.ox.ac.uk/~vgg/data/dtd/).

## 🚀 Experiments
### 🌞 Training and testing DM-GRD on the MVTec dataset
```shell
bash scripts/train_mvtec.sh
bash scripts/test_mvtec.sh
```

### 🌞 Training and testing DM-GRD on the BTAD dataset
```shell
bash scripts/train_btad.sh
bash scripts/test_btad.sh
```

### 🌞 Training and testing DM-GRD on the VisA dataset
```shell
bash scripts/train_visa.sh
bash scripts/test_visa.sh
```

## 🔗 Citation
If you find our work useful, please cite the following:
```
@inproceedings{tran2024dual,
  title={Dual Memory Networks Guided Reverse Distillation for Unsupervised Anomaly Detection},
  author={Tran, Chi Dai and Pham, Long Hoang and Tran, Duong Nguyen-Ngoc and Ho, Quoc Pham-Nam and Jeon, Jae Wook},
  booktitle={Proceedings of the Asian Conference on Computer Vision},
  pages={2650--2666},
  year={2024}
}
```

## ☎️ Contact
If you have any questions, feel free to contact `Chi D. Tran` ([ctran743@gmail.com](ctran743@gmail.com) or [tdc2000@skku.edu](tdc2000@skku.edu)).

## 🙏 Acknowledgement
Our framework is built using multiple open source, thanks for their great contributions.
<!--ts-->
* [hq-deng/RD4AD](https://github.com/hq-deng/RD4AD)
* [tientrandinh/Revisiting-Reverse-Distillation](https://github.com/tientrandinh/Revisiting-Reverse-Distillation)
<!--te-->