from torch.nn import ZeroPad2d
from torch.utils.data import DataLoader, Dataset
import torch.optim as optim
import torch
from args import args
from cvt import *
from utils import *


class CryptoDataset(Dataset):
    def __init__(self, dataset, data_type="train"):
        df_btc = get_btc(args)
        if dataset == 'btc':
            df_train = df_btc
        elif dataset == 'btc_trend':
            df_trend = get_trend(args)
            df_train = df_btc.join(df_trend).dropna()
        elif dataset == 'btc_wiki':
            df_wiki = get_wiki()
            df_train = df_btc.join(df_wiki).dropna()
        elif dataset == 'btc_trend_wiki':
            df_wiki = get_wiki()
            df_trend = get_trend(args)
            df_train = df_btc.join(df_wiki).join(df_trend).dropna()

        #(2348, 30, 5) (2348, 3)
        self.X_train, self.y_train, self.X_test, self.y_test, self.dates_train, self.dates_test = create_train_test(df_train, args)
        #(2348, 5, 30)
        self.X_train = np.expand_dims(np.transpose(self.X_train, (0, 2, 1)), axis=1)
        self.X_train = torch.from_numpy(self.X_train).float()
        self.X_test = np.expand_dims(np.transpose(self.X_test, (0, 2, 1)), axis=1)
        self.X_test = torch.from_numpy(self.X_test).float()
        if data_type == "train":
            self.X = self.X_train
            self.Y = self.y_train
        elif data_type == "test":
            self.X = self.X_test
            self.Y = self.y_test

    def set_data_type(self, data_type):
        if data_type == "train":
            self.X = self.X_train
            self.Y = self.y_train
        elif data_type == "test":
            self.X = self.X_test
            self.Y = self.y_test

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.Y[idx]


if __name__ == '__main__':
    dev = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    
    train_dataset = CryptoDataset(args.dataset)
    train_dataloader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    n_features = train_dataset[0][0].shape[1] 
    print(n_features, args.window_size, 1, len(class_names))
    # 5 30 1 3
    model = CvT(n_features, args.window_size, 1, len(class_names))
    model.to(dev)
    
    parameters = filter(lambda p: p.requires_grad, model.parameters())
    parameters = sum([np.prod(p.size()) for p in parameters]) / 1_000_000
    print('Trainable Parameters: %.3fM' % parameters)

    criterion = nn.CrossEntropyLoss()
    #optimizer = optim.SGD(model.parameters(), lr=args.learning_rate, momentum=0.9)
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)

    for epoch in range(args.epochs):  # loop over the dataset multiple times
    
        running_loss = 0.0
        for i, data in enumerate(train_dataloader, 0):
            # get the inputs; data is a list of [inputs, labels]
            inputs, labels = data
    
            # zero the parameter gradients
            optimizer.zero_grad()
    
            # forward + backward + optimize
            outputs = model(inputs.to(dev))
            labels = torch.argmax(labels, dim=1)
            loss = criterion(outputs, labels.to(dev))
            loss.backward()
            optimizer.step()
    
            # print statistics
            running_loss += loss.item()
            if i % 10 == 0:    # print every 2000 mini-batches
                print('[%d, %5d] loss: %.3f' %
                      (epoch + 1, i + 1, running_loss / 10))
                running_loss = 0.0
    
    print('Finished Training')

    torch.save(model.state_dict(), "test.h5")
    test_dataset = train_dataset
    test_dataset.set_data_type("test")
    test_dataloader = DataLoader(test_dataset, batch_size=1, shuffle=False)
    for (x, y) in test_dataloader:
        pred = model(x.to(dev))
        print(torch.argmax(pred, dim=1), torch.argmax(y, dim=1))
