import numpy as np
import torch

from pytorch_lightning.metrics.metric import Metric, TensorMetric, NumpyMetric


class DummyTensorMetric(TensorMetric):
    def __init__(self):
        super().__init__('dummy')

    def forward(self, input1, input2):
        assert isinstance(input1, torch.Tensor)
        assert isinstance(input2, torch.Tensor)
        return 1.


class DummyNumpyMetric(NumpyMetric):
    def __init__(self):
        super().__init__('dummy')

    def forward(self, input1, input2):
        assert isinstance(input1, np.ndarray)
        assert isinstance(input2, np.ndarray)
        return 1.


def _test_metric(metric: Metric):
    input1, input2 = torch.tensor([1.]), torch.tensor([2.])

    def change_and_check_device_dtype(device, dtype):
        metric.to(device=device, dtype=dtype)

        metric_val = metric(input1, input2)
        assert isinstance(metric_val, torch.Tensor)

        if device is not None:
            assert metric.device in [device, torch.device(device)]
            assert metric_val.device in [device, torch.device(device)]

        if dtype is not None:
            assert metric.dtype == dtype
            assert metric_val.dtype == dtype

    devices = [None, 'cpu']
    if torch.cuda.is_available():
        devices += ['cuda:0']

    for device in devices:
        for dtype in [None, torch.float32, torch.float64]:
            change_and_check_device_dtype(device=device, dtype=dtype)

    if torch.cuda.is_available():
        metric.cuda(0)
        assert metric.device == torch.device('cuda', index=0)
        assert metric(input1, input2).device == torch.device('cuda', index=0)

    metric.cpu()
    assert metric.device == torch.device('cpu')
    assert metric(input1, input2).device == torch.device('cpu')

    metric.type(torch.int8)
    assert metric.dtype == torch.int8
    assert metric(input1, input2).dtype == torch.int8

    metric.float()
    assert metric.dtype == torch.float32
    assert metric(input1, input2).dtype == torch.float32

    metric.double()
    assert metric.dtype == torch.float64
    assert metric(input1, input2).dtype == torch.float64

    if torch.cuda.is_available():
        metric.cuda()
        metric.half()
        assert metric.dtype == torch.float16
        assert metric(input1, input2).dtype == torch.float16


def test_tensor_metric():
    _test_metric(DummyTensorMetric())


def test_numpy_metric():
    _test_metric(DummyNumpyMetric())
