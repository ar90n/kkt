from pathlib import Path

import torch
import torch.nn as nn
from torch.autograd import Variable

from mnist_efficientnet import io
from mnist_efficientnet.network import Network, extract_result


root = Path("../input/digit-recognizer")
train_x, train_y = io.load_train_data(root)
test = io.load_test_data(root)

net = Network()
optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
loss_func = nn.CrossEntropyLoss()
epochs = 10
batch_size = 50

loss_log = []
for e in range(epochs):
    loss = None
    for i in range(0, train_x.shape[0], batch_size):
        x_mini = train_x[i : i + batch_size]
        y_mini = train_y[i : i + batch_size]

        optimizer.zero_grad()
        net_out = net(Variable(x_mini))

        loss = loss_func(net_out, Variable(y_mini))
        loss.backward()
        optimizer.step()
    if loss is not None:
        print(f"Epoch: {e+1} - Loss: {loss.item():.6f}")

with torch.no_grad():
    net_out = net(test)
result = extract_result(net_out)
io.save_result(result)
