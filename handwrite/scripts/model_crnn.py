import paddle
import paddle.nn as nn
import paddle.nn.functional as F


class CRNNCTC(nn.Layer):
    def __init__(self, num_classes: int):
        super().__init__()
        # simple conv backbone for 48x512 input
        self.conv = nn.Sequential(
            nn.Conv2D(3, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2D((2, 2)),  # 24x256
            nn.Conv2D(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2D((2, 2)), # 12x128
            nn.Conv2D(64, 128, 3, padding=1), nn.ReLU(), nn.MaxPool2D((2, 2)),# 6x64
            nn.Conv2D(128, 256, 3, padding=1), nn.ReLU(),
        )
        self.proj = nn.Conv2D(256, 256, 3, padding=1)
        self.bi_lstm = nn.LSTM(256*6, 256, num_layers=2, direction='bidirect')
        self.fc = nn.Linear(512, num_classes)  # bidirectional hidden size*2

    def forward(self, x):
        # x: (N, C, H=48, W=512)
        x = self.conv(x)  # (N, 256, 6, 64)
        x = self.proj(x)  # (N, 256, 6, 64)
        n, c, h, w = x.shape
        x = x.transpose([0, 3, 1, 2])  # (N, W, C, H)
        x = x.reshape([n, w, c*h])     # (N, T=W, D)
        x, _ = self.bi_lstm(x)         # (N, T, 512)
        x = self.fc(x)                 # (N, T, num_classes)
        x = x.transpose([1, 0, 2])     # (T, N, num_classes) for CTC
        return x

