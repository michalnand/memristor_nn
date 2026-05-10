import torch

from .memristor_linear import *

class MemristorMLP(torch.nn.Module):
    def __init__(self, input_shape, ouput_shape):
        super(MemristorMLP, self).__init__()

        n_inputs = input_shape[0]*input_shape[1]*input_shape[2]

        self.lin_0  = MemristorLinear(n_inputs, 256, init_gain=0.5)
        self.act_0  = torch.nn.ReLU()

        self.lin_1  = MemristorLinear(256, 128, init_gain=0.5)
        self.act_1  = torch.nn.ReLU()

        self.lin_2  = MemristorLinear(128, ouput_shape[0], init_gain=0.01)

        
    def forward(self, x):
        x = torch.flatten(x, 1)

        x = self.lin_0(x)
        x = self.act_0(x)

        x = self.lin_1(x)
        x = self.act_1(x)

        x = self.lin_2(x)
        
        return x
    

    def get_weights(self):
        result = []
        p, n = self.lin_0.get_quantized()
        result.append(torch.concatenate([p, n]))    

        p, n = self.lin_1.get_quantized()
        result.append(torch.concatenate([p, n]))

        p, n = self.lin_2.get_quantized()
        result.append(torch.concatenate([p, n]))

        return result
        