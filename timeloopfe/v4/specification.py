import time
from . import arch, constraints, problem, variables
from ..common.nodes import DictNode, ListNode, Node, TypeSpecifier, CombineableListNode
from .arch import Architecture
from .constraints import Constraints, ConstraintsList
from .problem import Problem
from .variables import Variables
from .components import Components
from .mapper import Mapper
from .sparse_optimizations import SparseOptimizations
from .globals import Globals
from .version import assert_version
from .mapspace import Mapspace
from ..common.processor import ProcessorError, References2CopiesProcessor

from typing import Any, Dict, List, Optional, Union
from ..common.base_specification import BaseSpecification


class Specification(BaseSpecification):
    @classmethod
    def declare_attrs(cls, *args, **kwargs):
        super().declare_attrs(*args, **kwargs)
        super().add_attr("architecture", Architecture)
        super().add_attr(
            "components", Components, {"version": 0.4}, part_name_match=True
        )
        super().add_attr(
            "constraints", Constraints, {"version": 0.4}, part_name_match=True
        )
        super().add_attr("mapping", ConstraintsList, [], part_name_match=True)
        super().add_attr("mapper", Mapper, {"version": 0.4})
        super().add_attr("problem", Problem)
        super().add_attr("sparse_optimizations", SparseOptimizations, {"version": 0.4})
        super().add_attr("variables", Variables, {"version": 0.4})
        super().add_attr("mapspace", Mapspace, {"version": 0.4})
        super().add_attr("globals", Globals, {"version": 0.4})

    def __init__(self, *args, **kwargs):
        from .processors import REQUIRED_PROCESSORS

        assert "_required_processors" not in kwargs, "Cannot set _required_processors"
        kwargs["_required_processors"] = REQUIRED_PROCESSORS
        super().__init__(*args, **kwargs)
        self.architecture: arch.Architecture = self["architecture"]
        self.constraints: constraints.Constraints = self["constraints"]
        self.mapping: constraints.Constraints = self["mapping"]
        self.problem: problem.Problem = self["problem"]
        self.variables: variables.Variables = self["variables"]
        self.components: ListNode = self["components"]
        self.mapper: Mapper = self["mapper"]
        self.sparse_optimizations: SparseOptimizations = self["sparse_optimizations"]
        self.mapspace: Mapspace = self["mapspace"]

    def parse_expressions(
        self,
        symbol_table: Optional[Dict[str, Any]] = None,
        parsed_ids: Optional[set] = None,
    ):
        if self.needs_processing([References2CopiesProcessor]):
            raise ProcessorError(
                f"Must run References2CopiesProcessor before "
                f"parsing expressions. Either call __init__ with "
                f"preserve_references=False or call process() with "
                f"any arguments."
            )
        symbol_table = {} if symbol_table is None else symbol_table.copy()
        parsed_ids = set() if parsed_ids is None else parsed_ids
        parsed_ids.add(id(self))
        parsed_ids.add(id(self.variables))
        symbol_table["spec"] = self
        parsed_variables = self.variables.parse_expressions(symbol_table, parsed_ids)
        symbol_table.update(parsed_variables)
        symbol_table["variables"] = parsed_variables
        super().parse_expressions(symbol_table, parsed_ids)


Specification.declare_attrs()