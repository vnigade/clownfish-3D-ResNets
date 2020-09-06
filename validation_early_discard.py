import torch
from torch.autograd import Variable
import time
import sys
import numpy as np

from utils import AverageMeter


def print_output(outputs, target):
    scores = outputs.cpu().detach().numpy().flatten().tolist()
    action = np.argmax(np.asarray(scores, dtype=float))
    print("Validation output: ", action, target)


tot_contexts = 0
pred_contexts = 0
tot_background = 0
pred_background = 0


def calculate_accuracy(outputs, targets):
    global tot_contexts, pred_contexts, tot_background, pred_background
    _threshold = 0.5
    outputs = torch.sigmoid(outputs)
    for j in range(len(outputs)):
        pred = 1.0 if outputs[j].item() >= _threshold else 0.0
        print("Stats: ", outputs[j].item(), targets[j].item(), pred)
        if targets[j].item() == 1.0:
            tot_contexts += 1
            if pred == 1.0:
                pred_contexts += 1
        else:
            tot_background += 1
            if pred == 0.0:
                pred_background += 1
    return 0.0


def val_epoch(epoch, data_loader, model, criterion, opt, logger):
    '''
    @todo: The function is not very well tested.
    '''
    print('validation at epoch {}'.format(epoch))

    model.eval()

    batch_time = AverageMeter()
    data_time = AverageMeter()
    losses = AverageMeter()
    accuracies = AverageMeter()

    end_time = time.time()
    for i, (inputs, targets, _) in enumerate(data_loader):
        data_time.update(time.time() - end_time)

        if not opt.no_cuda:
            targets = targets.cuda(async=True)
        inputs = Variable(inputs, volatile=True)
        targets = Variable(targets, volatile=True)
        outputs = model(inputs)
        # print_output(outputs, targets)
        loss = criterion(outputs, targets)
        acc = calculate_accuracy(outputs, targets)

        losses.update(loss.item(), inputs.size(0))
        accuracies.update(acc, inputs.size(0))

        batch_time.update(time.time() - end_time)
        end_time = time.time()

        # print('Epoch: [{0}][{1}/{2}]\t'
        #      'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
        #      'Data {data_time.val:.3f} ({data_time.avg:.3f})\t'
        #      'Loss {loss.val:.4f} ({loss.avg:.4f})\t'
        #      'Acc {acc.val:.3f} ({acc.avg:.3f})'.format(
        #          epoch,
        #          i + 1,
        #          len(data_loader),
        #          batch_time=batch_time,
        #          data_time=data_time,
        #          loss=losses,
        #          acc=accuracies))

    # logger.log({'epoch': epoch, 'loss': losses.avg, 'acc': accuracies.avg})
    global tot_contexts, pred_contexts, tot_background, pred_background
    print("Contexts: {}/{}, Background: {}/{}".format(tot_contexts,
                                                      pred_contexts, tot_background, pred_background))
    return losses.avg
