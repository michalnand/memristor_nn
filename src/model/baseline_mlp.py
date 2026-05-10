import torch

class BaselineMLP(torch.nn.Module):

    def __init__(self, input_shape, ouput_shape):
        super(BaselineMLP, self).__init__()

        n_inputs = input_shape[0]*input_shape[1]*input_shape[2]

        self.lin_0  = torch.nn.Linear(n_inputs, 256)
        self.act_0  = torch.nn.ReLU()

        self.lin_1  = torch.nn.Linear(256, 128)
        self.act_1  = torch.nn.ReLU()

        self.lin_2  = torch.nn.Linear(128, ouput_shape[0])

        torch.nn.init.orthogonal_(self.lin_0.weight, 0.5)
        torch.nn.init.orthogonal_(self.lin_1.weight, 0.5)
        torch.nn.init.orthogonal_(self.lin_2.weight, 0.01)

        torch.nn.init.zeros_(self.lin_0.bias)
        torch.nn.init.zeros_(self.lin_1.bias)
        torch.nn.init.zeros_(self.lin_2.bias)


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
        result.append(self.lin_0.weight)
        result.append(self.lin_1.weight)
        result.append(self.lin_2.weight)

      
        return result
        