"""
Widgets is a super special reserved  word in Katana so we can't use that
so I made this Widgets2, because it is also Widgets in here that I'd like to reuse...

DO NOT RE ARRANGE THIS!!!  OR IT GOES KABOOMY (becuase I didn't
really think this through very well lmao)
"""


from .AbstractNodegraphWidget import AbstractNodegraphWidget
from .AbstractParametersDisplayWidget import AbstractParametersDisplayWidget
from .AbstractSuperToolEditor import AbstractSuperToolEditor
try:
    from .AbstractSuperToolNode import AbstractSuperToolNode
except NameError:
    pass
from .AbstractUserBooleanWidget import AbstractUserBooleanWidget
from .TwoFaceSuperToolWidget import TwoFacedSuperToolWidget
