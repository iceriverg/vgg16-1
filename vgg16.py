import chainer
import chainer.functions as F
import chainer.links as L


class VGG16(chainer.Chain):

    def __init__(self):
        super(VGG16, self).__init__(
            conv1_1=L.Convolution2D(3, 64, 3, stride=1, pad=1),
            bn1_1=L.BatchNormalization(64),
            conv1_2=L.Convolution2D(64, 64, 3, stride=1, pad=1),
            bn1_2=L.BatchNormalization(64),

            conv2_1=L.Convolution2D(64, 128, 3, stride=1, pad=1),
            bn2_1=L.BatchNormalization(128),
            conv2_2=L.Convolution2D(128, 128, 3, stride=1, pad=1),
            bn2_2=L.BatchNormalization(128),

            conv3_1=L.Convolution2D(128, 256, 3, stride=1, pad=1),
            bn3_1=L.BatchNormalization(256),
            conv3_2=L.Convolution2D(256, 256, 3, stride=1, pad=1),
            bn3_2=L.BatchNormalization(256),
            conv3_3=L.Convolution2D(256, 256, 3, stride=1, pad=1),
            bn3_3=L.BatchNormalization(256),

            conv4_1=L.Convolution2D(256, 512, 3, stride=1, pad=1),
            bn4_1=L.BatchNormalization(512),
            conv4_2=L.Convolution2D(512, 512, 3, stride=1, pad=1),
            bn4_2=L.BatchNormalization(512),
            conv4_3=L.Convolution2D(512, 512, 3, stride=1, pad=1),
            bn4_3=L.BatchNormalization(512),

            conv5_1=L.Convolution2D(512, 512, 3, stride=1, pad=1),
            bn5_1=L.BatchNormalization(512),
            conv5_2=L.Convolution2D(512, 512, 3, stride=1, pad=1),
            bn5_2=L.BatchNormalization(512),
            conv5_3=L.Convolution2D(512, 512, 3, stride=1, pad=1),
            bn5_3=L.BatchNormalization(512),

            fc6=L.Linear(25088, 4096),
            fc7=L.Linear(4096, 4096),
            fc8=L.Linear(4096, 1000)
        )
        self.train = False

    def __call__(self, x, t=None):
        h = F.relu(self.bn1_1(self.conv1_1(x), test=not self.train))
        h = F.relu(self.bn1_2(self.conv1_2(h), test=not self.train))
        h = F.max_pooling_2d(h, 2, stride=2)

        h = F.relu(self.bn2_1(self.conv2_1(h), test=not self.train))
        h = F.relu(self.bn2_2(self.conv2_2(h), test=not self.train))
        h = F.max_pooling_2d(h, 2, stride=2)

        h = F.relu(self.bn3_1(self.conv3_1(h), test=not self.train))
        h = F.relu(self.bn3_2(self.conv3_2(h), test=not self.train))
        h = F.relu(self.bn3_3(self.conv3_3(h), test=not self.train))
        h = F.max_pooling_2d(h, 2, stride=2)

        h = F.relu(self.bn4_1(self.conv4_1(h), test=not self.train))
        h = F.relu(self.bn4_2(self.conv4_2(h), test=not self.train))
        h = F.relu(self.bn4_3(self.conv4_3(h), test=not self.train))
        h = F.max_pooling_2d(h, 2, stride=2)

        h = F.relu(self.bn5_1(self.conv5_1(h), test=not self.train))
        h = F.relu(self.bn5_2(self.conv5_2(h), test=not self.train))
        h = F.relu(self.bn5_3(self.conv5_3(h), test=not self.train))
        h = F.max_pooling_2d(h, 2, stride=2)

        h = F.dropout(F.relu(self.fc6(h)), train=self.train, ratio=0.5)
        h = F.dropout(F.relu(self.fc7(h)), train=self.train, ratio=0.5)
        h = self.fc8(h)
        fc8 = h

        self.pred = F.softmax(h)

        if t is None:
            assert not self.train
            return

        self.loss = F.softmax_cross_entropy(fc8, t)
        self.acc = F.accuracy(self.pred, t)

        if self.train:
            return self.loss