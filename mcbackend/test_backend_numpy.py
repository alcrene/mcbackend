import random

import hagelkorn
import numpy

from mcbackend.meta import Variable

from .backends.numpy import NumPyBackend, NumPyChain, NumPyRun
from .core import RunMeta
from .test_utils import CheckBehavior


class TestNumPyBackend(CheckBehavior):
    cls_backend = NumPyBackend
    cls_run = NumPyRun
    cls_chain = NumPyChain

    def test_targets(self):
        imb = NumPyBackend(preallocate=123)
        rm = RunMeta(
            rid=hagelkorn.random(),
            variables=[
                Variable("tensor", "int8", (3, 4, 5)),
                Variable("scalar", "float64", ()),
                Variable("changeling", "uint16", (3, 0)),
            ],
        )
        run = imb.init_run(rm)
        chain = run.init_chain(0)
        # Shape flexibility detection
        assert chain._is_rigid["tensor"]
        assert chain._is_rigid["scalar"]
        assert not chain._is_rigid["changeling"]
        # Types of targets
        assert isinstance(chain._samples["tensor"], numpy.ndarray)
        assert isinstance(chain._samples["scalar"], numpy.ndarray)
        assert isinstance(chain._samples["changeling"], numpy.ndarray)
        # Shapes and dtypes
        assert chain._samples["tensor"].shape == (123, 3, 4, 5)
        assert chain._samples["scalar"].shape == (123,)
        assert chain._samples["changeling"].shape == (123,)
        assert chain._samples["tensor"].dtype == "int8"
        assert chain._samples["scalar"].dtype == "float64"
        assert chain._samples["changeling"].dtype == object
        pass

    def test_growing(self):
        imb = NumPyBackend(preallocate=15)
        rm = RunMeta(
            rid=hagelkorn.random(),
            variables=[
                Variable(
                    "A",
                    "float32",
                    (2,),
                ),
                Variable(
                    "B",
                    "float32",
                    (0,),
                ),
            ],
        )
        run = imb.init_run(rm)
        chain = run.init_chain(0)
        assert chain._samples["A"].shape == (15, 2)
        assert chain._samples["B"].shape == (15,)
        for _ in range(22):
            draw = {
                "A": numpy.random.uniform(size=(2,)),
                "B": numpy.random.uniform(size=(random.randint(0, 10),)),
            }
            chain.add_draw(draw)
        # Growth: 15 → 17 → 19 → 21 → 24
        assert chain._samples["A"].shape == (24, 2)
        assert chain._samples["B"].shape == (24,)
        assert chain.get_variable("A").shape == (22, 2)
        assert chain.get_variable("B").shape == (22,)
        pass
