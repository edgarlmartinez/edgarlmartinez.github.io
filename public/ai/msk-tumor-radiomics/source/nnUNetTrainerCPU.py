import torch
from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer

class nnUNetTrainerCPU(nnUNetTrainer):
    """Short schedule so the default nnU-Net recipe can be trained on a 4-core CPU.
    Same architecture family, losses (Dice+CE, deep supervision), augmentation and
    sliding-window inference as nnUNetTrainer; only the training length differs."""
    def __init__(self, plans, configuration, fold, dataset_json, device=torch.device('cpu')):
        super().__init__(plans, configuration, fold, dataset_json, device)
        self.num_epochs = 40
        self.num_iterations_per_epoch = 100
        self.num_val_iterations_per_epoch = 15


class nnUNetTrainerCPU30(nnUNetTrainerCPU):
    def __init__(self, plans, configuration, fold, dataset_json, device=torch.device('cpu')):
        super().__init__(plans, configuration, fold, dataset_json, device)
        self.num_epochs = 30
