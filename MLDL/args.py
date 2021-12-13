import argparse

parser = argparse.ArgumentParser(description='dataset and model params.')
# dataset params
parser.add_argument('-t', '--threshold', dest='threshold', default=0.1, type=float)
# shift 1: predict yesterday. -1: predict tomorrow
parser.add_argument('-f', '--freq', dest='freq', default="day", type=str)
parser.add_argument('-s', '--shift', dest='shift', default=0, type=int)
parser.add_argument('-sm', '--smooth', dest='smooth', default=0, type=int)
parser.add_argument('-w', '--window_size', dest='window_size', default=30, type=int)
parser.add_argument('-ts', '--test_size', dest='test_size', default=0.1, type=float)
parser.add_argument('-vs', '--valid_size', dest='valid_size', default=0.1, type=float)
parser.add_argument('-d', '--dataset', dest='dataset', default='btc', choices=['btc', 'btc_trend', 'btc_wiki', 'btc_trend_wiki', 'btc_text', 'all'])
parser.add_argument('-rt', '--range_tolerance', dest='range_tolerance', default=0.03, type=float)
# model params
parser.add_argument('-ep', '--epochs', dest='epochs', default=300, type=int)
parser.add_argument('-b', '--batch_size', dest='batch_size', default=16, type=int)
parser.add_argument('-p', '--patience', dest='patience', default=100, type=int)
parser.add_argument('-dv', '--device', dest='device', default='cpu', choices=['cpu', 'gpu'])
parser.add_argument('-md', '--max_dilation', dest='max_dilation', default=7, type=int)
parser.add_argument('-nf', '--n_filters', dest='n_filters', default=64, type=int)
parser.add_argument('-fd', '--filter_width', dest='filter_width', default=2, type=int)
parser.add_argument('-lr', '--learning_rate', dest='learning_rate', default=3e-6, type=float)
parser.add_argument('-lw', '--auto_loss_weight', dest='auto_loss_weight', default=1, type=int)

args = parser.parse_args()
