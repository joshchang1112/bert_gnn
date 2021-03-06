import os
import argparse
import pickle
import torch
from tqdm import tqdm
from torch.utils.data import DataLoader
from utils import load_data
from dataset import CitationDataset
from metrics import Accuracy
from transformers import BertForSequenceClassification
from utils import set_seed

def run_iter(batch, model, device, training):
    context, context_lens = batch['context'].to(device), batch['length'].to(device)
    batch_size = context.size()[0]
    max_context_len = context.size()[1]
    padding_mask = []
    for j in range(batch_size):
        if context_lens[j] < max_context_len:
            tmp = [1] * context_lens[j] + [0] * (max_context_len - context_lens[j])
        else:
            tmp = [1] * max_context_len
        padding_mask.append(tmp)

    padding_mask = torch.Tensor(padding_mask).to(device)
    if training:
        prob = model(context, attention_mask=padding_mask)[0]
    else:
        with torch.no_grad():
            prob = model(context, attention_mask=padding_mask)[0]
    return prob

def training(args, train_loader, valid_loader, model, optimizer, device):
    train_metrics = Accuracy()
    best_valid_acc = 0
    total_iter = 0
    criterion = torch.nn.CrossEntropyLoss()
    for epoch in range(args.epochs):
        train_trange = tqdm(enumerate(train_loader), total=len(train_loader), desc='training')
        train_loss = 0
        train_metrics.reset()
        for i, batch in train_trange:
            model.train()
            prob = run_iter(batch, model, device, training=True)
            answer = batch['label'].to(device)
            loss = criterion(prob, answer)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_iter += 1
            train_loss += loss.item()
            train_metrics.update(prob, answer)
            train_trange.set_postfix(loss= train_loss/(i+1),
                                     **{train_metrics.name: train_metrics.print_score()})
            
            if total_iter % args.eval_steps == 0:
                valid_acc = testing(valid_loader, model, device, valid=True)
                if valid_acc > best_valid_acc:
                    best_valid_acc = valid_acc
                    torch.save(model, os.path.join(args.model_dir, 'fine-tuned_bert_{}.pkl'.format(args.seed)))
    
    # Final validation
    valid_acc = testing(valid_loader, model, device, valid=True)
    if valid_acc > best_valid_acc:
        best_valid_acc = valid_acc
        torch.save(model, os.path.join(args.model_dir, 'fine-tuned_bert_{}.pkl'.format(args.seed)))
    print('Best Valid Accuracy:{}'.format(best_valid_acc))


def testing(dataloader, model, device, valid):
    metrics = Accuracy()
    criterion = torch.nn.CrossEntropyLoss()
    trange = tqdm(enumerate(dataloader), total=len(dataloader), desc='validation' if valid else 'testing')
    model.eval()
    total_loss = 0
    metrics.reset()
    for k, batch in trange:
        model.eval()
        prob = run_iter(batch, model, device, training=False)
        answer = batch['label'].to(device)
        loss = criterion(prob, batch['label'].to(device))
        total_loss += loss.item()
        metrics.update(prob, answer)
        trange.set_postfix(loss= total_loss/(k+1),
                           **{metrics.name: metrics.print_score()})
    acc = metrics.match / metrics.n
    return acc

def main():
    parser = argparse.ArgumentParser(description='OGBN-Arxiv (GNN)')
    parser.add_argument('--device', type=int, default=0) 
    parser.add_argument('--num_classes', type=int, default=40)
    parser.add_argument('--max_seq_length', type=int, default=400)
    parser.add_argument('--batch_size', type=int, default=4)
    parser.add_argument('--lr', type=float, default=2e-5)
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--eval_steps', type=int, default=8000)
    parser.add_argument('--pretrain_model', type=str, default='bert')
    parser.add_argument('--model_dir', default='models', type=str,
                        help='Directory to the model checkpoint.')
    args = parser.parse_args()
    
    if os.path.isdir(args.model_dir) == False:
        os.makedirs(args.model_dir)
        print('Create folder: {}'.format(args.model_dir))
    else:
        print('{} exists!'.format(args.model_dir))

    device = torch.device('cuda:{}'.format(args.device) if torch.cuda.is_available()
                          else 'cpu')

    set_seed(SEED=args.seed)
    train, valid, test = load_data('config.json')
    train_dataset = CitationDataset(train, max_length=args.max_seq_length)
    valid_dataset = CitationDataset(valid, max_length=args.max_seq_length)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, 
                              shuffle=True, collate_fn=train_dataset.collate_fn)
    valid_loader = DataLoader(valid_dataset, batch_size=args.batch_size, 
                              shuffle=False, collate_fn=valid_dataset.collate_fn)
    test_dataset = CitationDataset(test, max_length=args.max_seq_length)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False,
                             collate_fn=test_dataset.collate_fn)

    model = BertForSequenceClassification.from_pretrained('bert-base-uncased', 
                                                          num_labels=args.num_classes).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    training(args, train_loader, valid_loader, model, optimizer, device) 
    model = torch.load(os.path.join(args.model_dir, 'fine-tuned_bert_{}.pkl'.format(args.seed)))
    
    test_acc = testing(test_loader, model, device, valid=False)
    print("Test Accuracy:{}".format(test_acc))
    
if __name__ == '__main__':
    main()
