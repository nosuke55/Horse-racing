#lightgbmのイストール必須
import lightgbm as lgb
from sklearn import metrics
#ふうう
class LightGBM():
        # 初期処理
    def __init__(self) :
        #
        print("start")

    def hyperparm(self):
        # LightGBM のハイパーパラメータ
        lgbm_params = {
            'boosting': 'dart',          # dart (drop out trees) often performs better
            'application': 'binary',     # Binary classification
            'learning_rate': 0.05,       # Learning rate, controls size of a gradient descent step
            'min_data_in_leaf': 20,      # Data set is quite small so reduce this a bit
            'feature_fraction': 0.7,     # Proportion of features in each boost, controls overfitting
            'num_leaves': 41,            # Controls size of tree since LGBM uses leaf wise splits
            'metric': 'auc',  # Area under ROC curve as the evaulation metric
            'drop_rate': 0.15
            }
        return lgbm_params
        
    #学習データ作成
    def train_data(self,X_train,y_train,lgb):
        lgb_train = lgb.Dataset(X_train, label=y_train)
        return lgb_train
    
    def test_data(self,X_test,y_test,train_data,lgb):
        lgb_eval = lgb.Dataset(X_test, label=y_test, reference=train_data)
        return lgb_eval

    def fit(self,lgbm_params,train_data,test_data,lgb):
        #lgbmでの学習
        evaluation_results = {}
        model=lgb.train(lgbm_params,
                        train_data,
                        valid_sets=[train_data, test_data], 
                        valid_names=['Train', 'Test'],
                        evals_result=evaluation_results,
                        num_boost_round=500,
                        early_stopping_rounds=100,
                        verbose_eval=20)
                        #valid_sets=test_data)
        optimum_boost_rounds = model.best_iteration
        return model,optimum_boost_rounds

    def predict(self,X_test,model):
        y_pred = model.predict(X_test)#,num_iteration=model.best_iteration)
        return y_pred

    def accuracy_rate(self,y_test,y_pred):
        self.fpr, self.tpr, thresholds = metrics.roc_curve(y_test, y_pred)
        auc = metrics.auc(self.fpr, self.tpr)
        print("正解率",auc)
        return self.fpr,self.tpr

