import timm
import torch
import torch.nn as nn
import torch.nn.functional as F

class Network(nn.Module):
    def __init__(self):
        super(Network, self).__init__()
        self.backbone = timm.create_model('efficientnet_b0')
        self.fc1 = nn.Linear(1000, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        x = self.backbone(x)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x)


def extract_result(net_out):
    return (torch.max(net_out.data, 1)[1]).numpy()

