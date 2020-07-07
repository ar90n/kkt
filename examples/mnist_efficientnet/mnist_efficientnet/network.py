import timm
import torch
import torch.nn as nn

class Network(nn.Module):
    def __init__(self):
        super(Network, self).__init__()
        self.net = timm.create_model('efficientnet_b0', num_classes=10)

    def forward(self, x):
        return self.net(x)


def extract_result(net_out):
    return (torch.max(net_out.data, 1)[1]).numpy()

