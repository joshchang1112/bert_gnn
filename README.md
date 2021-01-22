# Multi-class Classification with fine-tuned BERT &amp; GNN

## Overview

BERT is the most powerful neural networks model in NLP area. Graph Neural Networks(GNN) is also one of the most popular model now. 
Therefore, we want to bring the advantages in BERT to the citation network, and evaluate that how much improvement can BERT help GNN models work.

In this repository, we will explore the use of fine-tuned BERT, how to encode node features using BERT model, 
and using citation graph and node features to train GNN models. 
Also, we will provide *colab notebook* for developers to run our code easily.

**Now, it supports both Pytorch and Tensorflow framework!**

The step is as follows:

1.  Download `ogbn-arxiv` dataset from [Open Graph Benchmark](https://ogb.stanford.edu/).
2.  Fine-tuned BERT with arxiv dataset and select the model which has the best accuracy in validation set as encoder.
3.  Encode the node features using fine-tuned BERT.
4.  Train and evaluate the GNN model.

You can see the details about how to train the code in `pytorch` and `tensorflow` directory.

## Experiments

Model   |  Test Accuracy  | Validation Accuracy | Hardware |
:-----: | :-------------:| :-------------:| :-------------:|
GCN <br/> (official, Rank 27 in Leaderboard) | 0.7174 &pm; <br/> 0.0029 | 0.7300 &pm; 0.0017 | GeForce RTX 2080 <br/> (11GB GPU)
GAT+label reuse+self KD <br/> (official, **Rank 1** in Leaderboard) | **0.7416** &pm; <br/> 0.0008 | 0.7514 &pm; 0.0004 | GeForce RTX 2080Ti <br/> (11GB GPU)
GCN (this repo.)    |  0.7184 &pm; <br/> 0.0020 | 0.7311 &pm; 0.0008   | GeForce GTX 1080 Ti <br/> (11GB GPU)
GAT     |    |    | 
Fine-tuned BERT    |  0.7155 &pm; <br/> 0.0025   | 0.7294 &pm; 0.0018   |  GeForce GTX 1080 Ti <br/> (11GB GPU)
Fine-tuned BERT+GCN <br/> (**Beat Rank 1!**) |   **0.7491** &pm; <br/> 0.0024 | 0.7642 &pm; 0.0004   | GeForce GTX 1080 Ti <br/> (11GB GPU)
Fine-tuned BERT+GAT <br/>  |    |    | 

