import torch
from torch import nn
import Bert
from torch.nn.utils import fusion as F

class SeqClassifier(nn.Module):

    def __init__(self, H=200, emb_size=768, out=11):
        super(SeqClassifier, self).__init__()
        self.lstm = nn.LSTM(bidirectional=True, num_layers=2, dropout=0.5,
                            input_size=emb_size, hidden_size=H,
                            batch_first=True)

        self.classifier = nn.LSTM(bidirectional=False, num_layers=1, dropout=0.5,
                            input_size=H*2, hidden_size=out,
                            batch_first=True)

    def forward(self, x):
        x, _ = self.lstm(x)
        logits,_ = self.classifier(x)
        return logits

class MLP(nn.Module):
    def __init__(self,inputs=768,H=200,out=11):
        super(MLP,self).__init__()
        self.l1=nn.Linear(inputs,H)
        self.l2=nn.Linear(H,out)
    
    def forward(self, x):
        x=self.l1(x)
        x=self.l2(x)
        return x



class BertRecNER(nn.Module):
    def __init__(self, out=11,pub=5,dim_em=6, bert_type='bert'):
        super(BertRecNER, self).__init__()
        _, self.bert_model = Bert.get_bert(bert_type=bert_type)

        # self.level1=SeqClassifier()
        # self.level2=SeqClassifier(emb_size=768+out)
        # self.level3=SeqClassifier(emb_size=768+out)

        # self.level1=nn.Linear(768,out)
        # self.pub_em = nn.Embedding(pub,5)
        # self.level2=nn.Linear(768+out,out)
        # self.level3=nn.Linear(768+out,out)


        self.level1=MLP(inputs=768)
        self.pub_em = nn.Embedding(pub,dim_em)
        self.level2=MLP(inputs=768+out)
        self.level3=MLP(inputs=768+out)
        self.three_levels_pub=MLP(out+pub)
        self.pub_logits=MLP(inputs=dim_em,out=5)

    def forward(self, x,corpus):
        if(corpus=='pgx_pub'):
            rep_vects, _ = self.bert_model(x['bert_inputs'])
            rep_pub = self.pub_em(x['pub_inputs'])
            if not isinstance(rep_vects, torch.Tensor):
                rep_vects = rep_vects[-1]
            if not isinstance(rep_pub, torch.Tensor):
                rep_pub = rep_pub[-1]
            rep_logits=self.pub_logits(rep_pub)
            level1_logits= self.level1(rep_vects)
            level2_inputs = torch.cat((rep_vects,level1_logits),dim=2)
            level2_logits = self.level2(level2_inputs)
            level3_inputs = torch.cat((rep_vects,level2_logits),dim=2)
            level3_logits = self.level3(level3_inputs)
            all_level=torch.cat((level1_logits, level2_logits, level3_logits),dim=1)##torch.Size([32, 243, 11])
            all_level_pub=torch.cat((all_level,rep_logits),dim=2) ##torch.Size([32, 243, 17])
            return all_level_pub

        elif(corpus=='pgx'):
            rep_vects, _ = self.bert_model(x)
            if not isinstance(rep_vects, torch.Tensor):
                rep_vects = rep_vects[-1]
            level1_logits= self.level1(rep_vects)
            level2_inputs = torch.cat((rep_vects,level1_logits),dim=2)
            level2_logits = self.level2(level2_inputs)
            level3_inputs = torch.cat((rep_vects,level2_logits),dim=2)
            level3_logits = self.level3(level3_inputs)
            outputs=torch.cat((level1_logits, level2_logits, level3_logits),dim=1)

            return outputs
