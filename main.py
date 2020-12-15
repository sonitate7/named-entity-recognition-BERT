import os
from sklearn.metrics import precision_recall_fscore_support, classification_report
import Bert
import Cross_validation
from Corpus import Corpus
from Parameters import global_param
from Train import train_save, prediction
from itertools import chain

corpus=Corpus('data/PGxCorpus','pgx')
X_app,Y_app = corpus.get_data()

###### param sup #######
do_valid=True
fold_num=10
do_cross_valid=True

nb_epoch = global_param.traning_param['num_ep'] # 5
lr= global_param.traning_param['lr'] # 3e-5
bert_type= global_param.model_param['bert'] # 'bert'
F_type= global_param.traning_param['F_type']  # 'macro'
exp_name= global_param.traning_param['exp_tag']


machine_name = os.uname()[1]

X_valid,Y_valid=corpus.data
X_test,Y_test=[],[]

global_param.model_param['bert']

def Experence():
    _,model=Bert.get_bert(bert_type='scibert')
    model.to(global_param.device)


    train_param = {
            'model': model,
            'X_app': X_app,
            'Y_app': Y_app,
            'nb_epoch': nb_epoch,
            'F_type': F_type,
            'lr': lr,
            'do_valid': False
        }


    if not do_cross_valid:
        print("///////////////////////////////////////////////////////////////////////////////")
        print("///////////////////////////////////////////////////////////////////////////////")
        print("/////////////////////////         Training       ///////////////////////////////")

        best_model, path = train_save(**train_param)

        print("///////////////////////////////////////////////////////////////////////////////")
        print("///////////////////////////////////////////////////////////////////////////////")
        print("/////////////////////////         TEST          ///////////////////////////////")

        pred = prediction(best_model, X_test)

    else:

        print("///////////////////////////////////////////////////////////////////////////////")
        print("///////////////////////////////////////////////////////////////////////////////")
        print("/////////////////////////         CROSS RESULT          ///////////////////////////////")

        pred, Y_test = Cross_validation.cross_validation(train_param, train_save, fold_num)
        
        chain.from_iterable([[1]])
        
        
        pred, Y_test = list(chain.from_iterable(pred)), list(chain.from_iterable(Y_test))
        

        raport = classification_report(y_pred=pred, y_true=Y_test)

        print(raport)

        file = open("result_" + machine_name + "_" + F_type + ".pred", "a+")
        y, p = "", ""
        for xp, xy in zip(pred, Y_test):
            y += ' ' + str(xy)
            p += ' ' + str(xp)
        print("Y" + y + '\nP' + p, file=file)
        file.close()

    return precision_recall_fscore_support(y_pred=pred, y_true=Y_test, average=F_type), raport

for k in range(10):
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~     Experence {}      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~".format(k))

    raport, raport_det = Experence()
    file = open(exp_name + "result_" + machine_name + "_" + F_type + ".res", "a+")
    print(str(raport[0]) + " " + str(raport[1]) + " " + str(raport[2]), file=file)
    file.close()

    file = open(exp_name + "result_" + machine_name + "_" + F_type + ".det", "a+")
    print(str(raport_det), file=file)
    file.close()
    # os.rmdir(path)
