# wzy
import os
import torch
import torchvision
from torch import nn, optim
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torch.utils.tensorboard import SummaryWriter
from torchvision import transforms

# device
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


# dataset
class MyData(Dataset):
    def __init__(self, image_dir, label_dir, transform=None):
        self.image_dir = image_dir
        self.label_dir = label_dir
        self.transform = transform
        self.file_names = os.listdir(self.image_dir)

    def __len__(self):
        return len(self.file_names)

    def __getitem__(self, idx):
        img_name = self.file_names[idx]
        img_path = os.path.join(self.image_dir, img_name)
        image = Image.open(img_path)
        image = image.convert('RGB')
        label_name = img_name.replace(".png", ".txt")
        label_path = os.path.join(self.label_dir, label_name)
        with open(label_path, 'r') as f:
            label = int(f.read().strip())

        if self.transform:
            image = self.transform(image)
            label = torch.tensor(label)

        return image, label


# 文件夹
save_folder_base = "C:/Users/wzy/Desktop/频谱图/data_Z_process_3"
train_folder = os.path.join(save_folder_base, "train")
val_folder = os.path.join(save_folder_base, "val")

train_image_dir = os.path.join(train_folder, "image")
train_label_dir = os.path.join(train_folder, "label")
val_image_dir = os.path.join(val_folder, "image")
val_label_dir = os.path.join(val_folder, "label")

transform = transforms.Compose([
    torchvision.transforms.Resize((600, 1000)),
    transforms.ToTensor(),

])

# data load
train_data = MyData(train_image_dir, train_label_dir, transform)
val_data = MyData(val_image_dir, val_label_dir, transform)
train_data_size = len(train_data)
test_data_size = len(val_data)
print("训练数据集的长度为：{}".format(train_data_size))
print("测试数据集的长度为：{}".format(test_data_size))
train_dataloader = DataLoader(train_data, batch_size=8, shuffle=False)
test_dataloader = DataLoader(val_data, batch_size=7, shuffle=False)


# network
class WZY(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d(3, 6, 20, 20, 0),
            nn.Sigmoid(),
            nn.MaxPool2d(2),
            nn.Conv2d(6, 3, 5, 5, 0),
            nn.Sigmoid(),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(6, 6),
            # nn.Dropout(p=0.5),  # p是丢弃概率
            nn.Linear(6, 3),
        )

    def forward(self, x):
        x = self.model(x)
        return x


wzy = WZY()
wzy = wzy.to(device)

# loss
loss_fn = nn.CrossEntropyLoss()
loss_fn = loss_fn.to(device)

# optim
learning_rate = 3e-2
optimizer = optim.SGD(wzy.parameters(), lr=learning_rate, weight_decay=1e-5)

# setting
total_train_step = 0
total_test_step = 0
epoch = 500

# tensorboard
writer = SummaryWriter('logs_train')

for i in range(epoch):
    print("--------第 {} 轮训练开始--------".format(i + 1))

    # train
    wzy.train()
    for data in train_dataloader:
        imgs, targets = data
        imgs = imgs.to(device)
        targets = targets.to(device)
        outputs = wzy(imgs)
        loss = loss_fn(outputs, targets)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_train_step += 1
        if total_train_step % 56 == 0:
            print("训练次数：{}, Loss: {}".format(total_train_step, loss.item()))
            writer.add_scalar('train_loss', loss.item(), total_train_step)

    # test
    wzy.eval()
    total_test_loss = 0
    total_accuracy = 0
    with torch.no_grad():
        for data in test_dataloader:
            imgs, targets = data
            imgs = imgs.to(device)
            targets = targets.to(device)
            outputs = wzy(imgs)
            loss = loss_fn(outputs, targets)
            total_test_loss += loss.item()
            accuracy = (outputs.argmax(1) == targets).sum()
            total_accuracy += accuracy.item()

    print("整体测试集上的Loss: {}".format(total_test_loss))
    print("整体数据集上的准确率Accuracy: {}".format(total_accuracy / test_data_size))
    writer.add_scalar('test_loss', total_test_loss, total_test_step)
    writer.add_scalar('test_accuracy', total_accuracy / test_data_size, total_test_step)
    total_test_step += 1

torch.save(wzy, "wzy_3.pth")
print("模型已保存")

writer.close()
