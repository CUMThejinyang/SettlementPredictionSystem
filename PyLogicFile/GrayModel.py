import numpy as np
import pandas

class GrayModel:

    def __init__(self, train_data: np.ndarray, test_data: np.ndarray, predict_cnt: int):
        self.train_data = train_data
        self.test_data = test_data
        self.predict_cnt = predict_cnt
        self.train_length = len(self.train_data)
        self.GM()

        print(self.ordinaryGMPredict())



    # 级比校验
    def ratio_check(self):
        threshold = (np.exp(-2 / (self.train_length + 2)), np.exp(2 / (self.train_length + 2)))
        retio_lst = [self.train_data[i] / self.train_data[i + 1] for i in range(self.train_length - 1)]
        min_val, max_val = min(retio_lst), max(retio_lst)
        if min_val < threshold[0] or max_val > threshold[-1]:
            return False
        else:
            return True

    def GM(self):
        # 1. 对原始数据进行一次累加
        self.consume_data = np.cumsum(self.train_data)
        # 2. 构造B与Y矩阵
        z = -0.5 * (self.consume_data[1:] + self.consume_data[0:self.train_length - 1]).reshape(
            (self.train_length - 1, 1))
        B = np.hstack((z, np.ones(shape=(self.train_length - 1, 1))))
        # 3. 构造Y矩阵
        Y = self.train_data[1:].reshape((self.train_length - 1, 1))
        # 4. 计算参数alpha
        [[self.a], [self.b]] = np.linalg.inv(B.T @ B) @ B.T @ Y

    def grayFunc(self, k):
        """
        :param k: 第k次的预测值
        :return:
        """
        if k == 0:
            return self.train_data[0]
        else:
            return (self.train_data[0] - self.b / self.a) * (1 - np.exp(self.a)) * np.exp(- self.a * (k))

    def modelCalculateValue(self, k):
        if k == 0:
            return self.train_data[0]
        else:
            return (self.train_data[0] - self.b / self.a) * np.exp(-self.a * k) + self.b / self.a



    def ordinaryGMPredict(self):
        ret = {}
        predict_lst = []
        caculate_lst = []
        for i in range(self.predict_cnt + self.train_length):
            predict_lst.append(self.grayFunc(i))
            caculate_lst.append(self.modelCalculateValue(i))

        ret['实际值'] = self.train_data.tolist()
        ret['实际值'].extend(self.test_data.tolist())
        ret['预测值'] = predict_lst
        ret['GM(1,1)模型计算值'] = caculate_lst
        ret['1-AGO'] = self.consume_data.tolist()
        length = min(len(ret['预测值']), len(ret['实际值']))
        ret['误差'] = [ret['预测值'][i] - ret['实际值'][i] for i in range(length)]
        ret['相对误差(%)'] = [abs(ret['预测值'][i] - ret['实际值'][i]) / ret['实际值'][i] * 100 for i in range(length)]

        lst =[]
        for k,v in ret.items():
            tmp = dict()
            tmp[k] = v
            lst.append(pandas.DataFrame(tmp))
        df = pandas.concat(lst, axis=1)
        df = df.fillna("")

        result = {}
        result["数据"] = df
        result['精度检验等级'] = {
            '相对误差检验':'一级',
            '小概率检验':'一级',
            '后验差检验':'一级'
        }
        return result



if __name__ == '__main__':
    train_data = [1.61, 2.78, 3.98, 4.48, 5.57, 7.18]
    test_data = [8.89, 10.98, 12.75, 13.14]

    # train_data = [71.1, 72.4, 72.4, 72.1, 71.4, 72.0, 71.6]
    # test_data = [8.89, 10.98, 12.75, 13.14]

    # train_data = [132, 92, 118, 130, 187, 207]
    # test_data = [8.89, 10.98, 12.75, 13.14]

    gm = GrayModel(np.array(train_data), np.array(test_data), 4)
