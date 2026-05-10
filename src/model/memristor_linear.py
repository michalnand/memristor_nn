import torch
import torch.nn as nn
import torch.nn.functional as F


class MemristorLinear(nn.Module):

    def __init__(
        self,
        in_features, out_features, bias=True, g_min=0.01, g_max=1.0, weight_bits=4, sigma=0.02, init_gain = 1.0):
        super().__init__()

        self.g_min = g_min
        self.g_max = g_max
        self.weight_bits = weight_bits
        self.sigma = sigma

        # latent float parameters   
        self.p_pos = nn.Parameter(torch.randn(out_features, in_features) * init_gain)
        self.p_neg = nn.Parameter(torch.randn(out_features, in_features) * init_gain)

        if bias:
            self.bias = nn.Parameter(torch.zeros(out_features))
        else:
            self.register_parameter("bias", None)

    def to_conductance(self, p):
        s = torch.sigmoid(p)

        return self.g_min + (self.g_max - self.g_min) * s


    def quantize_conductance(self, g):
        levels = 2 ** self.weight_bits

        scale = (self.g_max - self.g_min) / (levels - 1)

        q = torch.round((g - self.g_min) / scale)

        g_q = q * scale + self.g_min

        return g + (g_q - g).detach()

    def apply_device_variation(self, g):
        #Device-to-device / read variability.
        if self.training and self.sigma > 0:

            noise = torch.randn_like(g) * self.sigma

            g = g * (1.0 + noise)

        return g

    def forward(self, x):        
        g_pos, g_neg = self.get_quantized()

        # device variability
        g_pos = self.apply_device_variation(g_pos)
        g_neg = self.apply_device_variation(g_neg)
        
        # physical  computation
        y = 0.0

        if self.bias is not None:
            y = y + self.bias

        y = y + (x @ g_pos.T)
        y = y - (x @ g_neg.T)

        return y
    

    def get_quantized(self):
        # map latent params to physical conductances
        g_pos = self.to_conductance(self.p_pos)
        g_neg = self.to_conductance(self.p_neg)

        # quantized states
        g_pos = self.quantize_conductance(g_pos)
        g_neg = self.quantize_conductance(g_neg)

        return g_pos, g_neg