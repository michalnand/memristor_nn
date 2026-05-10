import torchvision
import torch
import numpy

class DatasetMnist:
    def __init__(self, root_path = "./data/", train = True):
        self.dataset = torchvision.datasets.MNIST(root_path, train = train, download=True)

        self.input_shape  = (1, 28, 28)
        self.output_shape = (10, )

    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, index):
        return self.get(index)

    def get(self, index):
        x, y = self.dataset[index]

        x = numpy.array(x)/255.0
        y = numpy.array(y)

        x = torch.from_numpy(x).float().unsqueeze(0)
        y = torch.from_numpy(y).long()

        return x, y
    

    def get_batch(self, batch_size):
        x_batch = []
        y_batch = []

        for n in range(batch_size):
            idx = numpy.random.randint(0, len(self.dataset))
            x, y = self.get(idx)
            x_batch.append(x)
            y_batch.append(y)

        x_batch = torch.stack(x_batch)
        y_batch = torch.stack(y_batch)

        return x_batch, y_batch