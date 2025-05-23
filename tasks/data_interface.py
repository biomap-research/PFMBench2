from torch.utils.data import DataLoader
import torch
from torch.utils.data import DataLoader, DistributedSampler
from src.interface.data_interface import DInterface_base
from src.data.protein_dataset import ProteinDataset
from src.model.pretrain_model_interface import PretrainModelInterface

class DInterface(DInterface_base):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        self.save_hyperparameters()

    def setup(self, stage=None):
        pass
    
    def data_setup(self, target="all"):
        pretrain_model_interface = None
        if self.finetune_type == "adapter":
            pretrain_model_interface = PretrainModelInterface(self.hparams.pretrain_model_name, batch_size=self.hparams.pretrain_batch_size, max_length=self.hparams.seq_len, sequence_only=self.hparams.sequence_only, task_type=self.hparams.task_type)
        if target == "all":
            self.train_set = ProteinDataset(self.hparams.train_data_path, self.hparams.pretrain_model_name, self.hparams.seq_len, pretrain_model_interface=pretrain_model_interface, task_name=self.task_name, task_type=self.hparams.task_type, num_classes=self.hparams.num_classes)
            self.val_set = ProteinDataset(self.hparams.val_data_path, self.hparams.pretrain_model_name, self.hparams.seq_len, pretrain_model_interface=pretrain_model_interface, task_name=self.task_name, task_type=self.hparams.task_type, num_classes=self.hparams.num_classes)
            self.test_set = ProteinDataset(self.hparams.test_data_path, self.hparams.pretrain_model_name, self.hparams.seq_len, pretrain_model_interface=pretrain_model_interface, task_name=self.task_name, task_type=self.hparams.task_type, num_classes=self.hparams.num_classes)
        elif target == "test":
            self.test_set = ProteinDataset(self.hparams.test_data_path, self.hparams.pretrain_model_name, self.hparams.seq_len, pretrain_model_interface=pretrain_model_interface, task_name=self.task_name, task_type=self.hparams.task_type, num_classes=self.hparams.num_classes)
    

    def train_dataloader(self):
        return DataLoader(self.train_set, batch_size=self.hparams.batch_size, shuffle=True, num_workers=self.hparams.num_workers, pin_memory=True, collate_fn=self.data_process_fn)

    def val_dataloader(self):
        return DataLoader(self.val_set, batch_size=self.hparams.batch_size, shuffle=False, num_workers=self.hparams.num_workers, pin_memory=True, collate_fn=self.data_process_fn)

    def test_dataloader(self):
        return DataLoader(self.test_set, batch_size=self.hparams.batch_size, shuffle=False, num_workers=self.hparams.num_workers, pin_memory=True, collate_fn=self.data_process_fn)

    def data_process_fn(self, data_list):
        if self.hparams.finetune_type == 'adapter':
            name_list = []
            mask_list = []
            label_list = []
            embedding_list = []
            smiles = []
            for data in data_list:
                name_list.append(data['name'])
                mask_list.append(data['attention_mask'])
                label_list.append(data['label'])
                embedding_list.append(data['embedding'])
                if data.get('smiles') is not None:
                    smiles.append(data['smiles'])
            return {'name': name_list,
                    'attention_mask': torch.stack(mask_list, dim=0),
                    'label': torch.stack(label_list, dim=0),
                    'embedding': torch.stack(embedding_list, dim=0),
                    'smiles': torch.stack(smiles, dim=0) if len(smiles) > 0 else None,
                    }
        else:
            return data_list
