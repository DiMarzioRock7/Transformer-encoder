import copy
import torch
import torch.nn as nn
from utils import init_embedding, init_lstm, init_linear

from transformer.Layers import PositionalEncoding, Encoder, Decoder


class Transformer(nn.Module):
    def __init__(self, args):
        super(Transformer, self).__init__()
        self.device = args.device
        self.n_layer = args.n_layer
        self.d_model = args.d_model
        self.d_inner = args.d_inner
        self.n_head = args.n_head
        self.d_k = args.d_k
        self.d_v = args.d_v
        self.dropout = args.dropout

        self.n_word = args.n_word
        self.n_gram = args.n_gram

        # embedding layer
        self.embedding = nn.Embedding(self.n_word, self.d_model)
        init_embedding(self.embedding)
        self.pos_enc = PositionalEncoding(self.d_model, self.n_gram, self.device)

        # transformer
        self.encoder = Encoder(self.n_layer, self.d_model, self.d_inner, self.n_head, self.d_k, self.d_v, self.dropout)
        self.decoder = Decoder(self.n_layer, self.d_model, self.d_inner, self.n_head, self.d_k, self.d_v, self.dropout)

        # predictor
        self.fc1 = nn.Linear(self.d_model, self.n_word, bias=True)
        self.fc1.weight = self.embedding.weight

    def forward(self, inputs):
        inputs = self.embedding(inputs)
        inputs += self.pos_enc(inputs)

        enc_outputs, enc_slf_attn = self.encoder(inputs)
        dec_outputs, dec_slf_attn, dec_enc_attn = self.decoder(inputs, enc_outputs)

        outputs = self.fc1(dec_outputs[:, -1, :].squeeze(1))

        return outputs, enc_slf_attn, dec_slf_attn, dec_enc_attn


