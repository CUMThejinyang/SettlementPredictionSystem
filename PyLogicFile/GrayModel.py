import numpy as np
import pandas as pd
import cgitb

cgitb.enable(format="text")


class GrayModel:

    def __init__(self, train_data: np.ndarray, test_data: np.ndarray, predict_cnt: int):
        self.train_data = train_data
        self.train_data_copy = train_data
        self.test_data = test_data
        self.predict_cnt = predict_cnt
        self.train_length = len(self.train_data)
        self.GM()
        self.__ret = self.ordinaryGMPredict()
        self.__accuracy = self.__accuracyDescription

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


    def getAccuracy(self):
        return self.__accuracy

    @property
    def __accuracyDescription(self):
        # 1. 相对残差检验
        ret = {}
        relative_err_test_result = self.relativeResidualTest()
        if relative_err_test_result <= 0.01:
            ret['相对残差检验'] = (round(relative_err_test_result, 3), '一级')
        elif 0.01 < relative_err_test_result <= 0.05:
            ret['相对残差检验'] = (round(relative_err_test_result, 3), '二级')
        elif 0.05 < relative_err_test_result <= 0.1:
            ret['相对残差检验'] = (round(relative_err_test_result, 3), '三级')
        elif 0.1 < relative_err_test_result <= 0.2:
            ret['相对残差检验'] = (round(relative_err_test_result, 3), '四级')
        else:
            ret['相对残差检验'] = (round(relative_err_test_result, 3), '未通过')
        # 2. 均方差比值检验
        std_ratio_err = self.squareErrorRatio()
        if std_ratio_err <= 0.35:
            ret['均方差比值检验'] = (round(std_ratio_err, 3), '一级')
        elif 0.35 < std_ratio_err <= 0.5:
            ret['均方差比值检验'] = (round(std_ratio_err, 3), '二级')
        elif 0.5 < std_ratio_err <= 0.65:
            ret['均方差比值检验'] = (round(std_ratio_err, 3), '三级')
        elif 0.65 < std_ratio_err <= 0.8:
            ret['均方差比值检验'] = (round(std_ratio_err, 3), '四级')
        else:
            ret['均方差比值检验'] = (round(std_ratio_err, 3), '未通过')

        # 3. 小误差概率检验
        little_err_probility = self.littleProbabilityTest()
        if little_err_probility >= 0.95:
            ret['小误差概率检验'] = (round(little_err_probility, 3), '一级')
        elif 0.8 <= little_err_probility < 0.95:
            ret['小误差概率检验'] = (round(little_err_probility, 3), '二级')
        elif 0.7 <= little_err_probility < 0.8:
            ret['小误差概率检验'] = (round(little_err_probility, 3), '三级')
        elif 0.6 <= little_err_probility < 0.7:
            ret['小误差概率检验'] = (round(little_err_probility, 3), '四级')
        else:
            ret['小误差概率检验'] = (round(little_err_probility, 3), '未通过')
        return ret

    # 相对残差检验计算
    def relativeResidualTest(self):
        realDataList = self.train_data
        self.predictDataList = []
        for i in range(self.train_length):
            self.predictDataList.append(self.grayFunc(i))
        self.relative_err_lst: np.ndarray = np.abs(np.array(realDataList) - np.array(self.predictDataList)) / np.array(
            realDataList)
        return self.relative_err_lst.mean()

    # 均方差比值计算
    def squareErrorRatio(self):
        s1 = self.train_data.std()
        s2 = self.relative_err_lst.std()
        return s2 / s1

    # 小概率计算
    def littleProbabilityTest(self):
        return self.relative_err_lst[np.where(
            abs(self.relative_err_lst - self.relative_err_lst.mean()) < 0.6745 * self.train_data.std())].shape[0] / \
               self.relative_err_lst.shape[0]

    # 灰数递补模型
    def getGrayNumberFillModelResult(self):
        self.train_data = self.train_data_copy
        usenum = len(self.train_data)
        predict_lst = []


        for i in range(self.predict_cnt):
            # 1. 计算参数
            self.GM()
            # 2. 预测一次
            tmp = self.grayFunc(usenum)
            predict_lst.append(round(tmp, 4))
            self.train_data = np.append(self.train_data[1:], round(tmp, 4))
        ret = dict()



        ret['实际值'] = self.test_data
        ret['预测值'] = predict_lst

        length = min(len(self.test_data), len(predict_lst))
        ret['误差'] = [round(predict_lst[i] - self.test_data[i], 4) for i in range(length)]
        ret['相对误差(%)'] = [round(abs((predict_lst[i] - self.test_data[i]) * 100 / self.test_data[i]), 4) for i in
                          range(length)]




        df_lst = []
        for k,v in ret.items():
            tmp = {}
            tmp[k] = list(map(lambda x:round(x, 3), v))
            df_lst.append(pd.DataFrame(tmp))
        df = pd.concat(df_lst,axis=1)
        df = df.fillna("")

        tmp_df = self.__ret.loc[:self.train_length-1, ['实际值', '预测值', '误差', '相对误差(%)']]
        df = pd.concat([tmp_df, df]).reset_index(drop=True).fillna("")

        return df


    def getMetabolicModelResult(self):
        self.train_data = self.train_data_copy
        usenum = len(self.train_data)
        predict_lst = []
        for i in range(self.predict_cnt):
            # 1. 计算参数
            self.GM()
            # 2. 预测一次
            tmp = self.grayFunc(usenum)
            predict_lst.append(round(tmp, 4))
            self.train_data = np.append(self.train_data[1:], self.test_data[i])
        ret = dict()

        ret['实际值'] = self.test_data
        ret['预测值'] = predict_lst
        length = min(len(self.test_data), len(predict_lst))
        ret['误差'] = [round(predict_lst[i] - self.test_data[i], 4) for i in range(length)]
        ret['相对误差(%)'] = [round(abs((predict_lst[i] - self.test_data[i]) * 100 / self.test_data[i]), 4) for i in
                          range(length)]
        df_lst = []
        for k, v in ret.items():
            tmp = {}
            tmp[k] = list(map(lambda x:round(x, 3), v))
            df_lst.append(pd.DataFrame(tmp))
        df = pd.concat(df_lst, axis=1)
        df = df.fillna("")
        tmp_df = self.__ret.loc[:self.train_length - 1, ['实际值', '预测值', '误差', '相对误差(%)']]
        df = pd.concat([tmp_df, df]).reset_index(drop=True).fillna("")
        return df


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

        lst = []
        for k, v in ret.items():
            tmp = dict()
            tmp[k] = list(map(lambda x:round(x, 3), v))
            lst.append(pd.DataFrame(tmp))
        df = pd.concat(lst, axis=1)
        df = df.fillna("")
        return df



if __name__ == '__main__':
    train_data = [1.61, 2.78, 3.98, 4.48, 5.57, 7.18]
    test_data = [8.89, 10.98, 12.75, 13.14]

    # train_data = [71.1, 72.4, 72.4, 72.1, 71.4, 72.0, 71.6]
    # test_data = [8.89, 10.98, 12.75, 13.14]

    # train_data = [132, 92, 118, 130, 187, 207]
    # test_data = [8.89, 10.98, 12.75, 13.14]

    gm = GrayModel(np.array(train_data), np.array(test_data), 5)
