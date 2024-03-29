import matplotlib.pylab as plt
import numpy as np
import torch
import torchvision
from PIL import Image

def get_devices():
    device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
    fft_device = 'cuda' if torch.cuda.is_available() else 'cpu'
    return device, fft_device

class TestImage:
    def __init__(self, image_path, size=None, grayscale=True, crop=True):
        self.image_path = image_path
        self.grayscale = grayscale
        self.crop = crop
        self.size = size
        self.device, _ = get_devices()
        self.image = self.load()
    
    def load(self):
        image = np.float32(plt.imread(self.image_path))
        if np.max(image) > 1:
            image /= 255
        if len(image.shape) == 3:
            if self.grayscale:
                image = np.expand_dims(np.dot(image[...,:3],[0.299, 0.587, 0.144]), axis=2)
            x = torch.tensor(image).permute(2,0,1)
        else:
            if not self.grayscale:
                x = torch.tensor(np.repeat(image.reshape(1, image.shape[0], image.shape[1]), 3, axis=0))
            else:
                x = torch.tensor(image.reshape(1, image.shape[0], image.shape[1]))
        
        if self.size:
            x = torchvision.transforms.Resize(self.size, antialias=True)(x)
        
        if self.crop:
            x = torchvision.transforms.CenterCrop(min(x.shape[1], x.shape[2]))(x)

        return x.type(torch.float32).to(self.device)

def plot_images(images, titles, save_path):
    
    plt.figure(figsize=(4*len(images), 4))
    assert len(images) == len(titles)

    for i in range(len(images)):
        plt.subplot(1, len(images), i+1)
        plt.imshow(images[i].detach().cpu().numpy(), cmap='gray')
        plt.title(titles[i])
    
    plt.savefig(save_path)

    print(f"Figure saved at {save_path}")

def save_gif(images, save_path, sample_rate=5):
    images = [Image.fromarray(img.squeeze().detach().cpu().numpy()*255) for img in images]
    images = images[:len(images):sample_rate]
    images[0].save(save_path, save_all=True, append_images=images[1:], duration=10, loop=0)
        