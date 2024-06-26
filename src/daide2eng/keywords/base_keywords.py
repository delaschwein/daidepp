from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, Union

from typing_extensions import get_args

from daide2eng.constants import *
from daide2eng.keywords.daide_object import _DAIDEObject
from daide2eng.keywords.keyword_utils import and_items, unit_dict

_prov_no_coast = [prov for lit in get_args(ProvinceNoCoast) for prov in get_args(lit)]


@dataclass(eq=True, frozen=True)
class Location:
    province: ProvinceNoCoast
    coast: Optional[Coast] = None

    def __init__(
        self, province: Union[ProvinceNoCoast, Location], coast: Optional[Coast] = None
    ) -> None:
        if isinstance(province, Location):
            object.__setattr__(self, "province", province.province)
        else:
            object.__setattr__(self, "province", province)

        object.__setattr__(self, "coast", coast)

    def __str__(self) -> str:
        if self.coast:
            return f"({self.province} {self.coast})"
        return self.province

    def __hash__(self) -> int:
        return hash(str(self))

    def __lt__(self, o):
        if self.province == o.province:
            return self.coast < o.coast
        return self.province < o.province


@dataclass(eq=True, frozen=True)
class Unit(_DAIDEObject):
    power: Power
    unit_type: UnitType
    location: Location

    def __post_init__(self):
        if isinstance(self.location, str):
            object.__setattr__(self, "location", Location(province=self.location))
        super().__post_init__()

    def __str__(self):
        unit = unit_dict[self.unit_type]
        return f"{self.power}'s {unit} in {self.location} "


@dataclass(eq=True, frozen=True)
class HLD(_DAIDEObject):
    unit: Unit

    def __str__(self):
        return f"holding {self.unit} "

    @property
    def location(self) -> Location:
        return self.unit.location


@dataclass(eq=True, frozen=True)
class MTO(_DAIDEObject):
    unit: Unit
    location: Location

    def __str__(self):
        return f"moving {self.unit} to {self.location} "


@dataclass(eq=True, frozen=True)
class SUP(_DAIDEObject):
    supporting_unit: Unit
    supported_unit: Unit
    province_no_coast: Optional[ProvinceNoCoast] = None

    @property
    def unit(self) -> Unit:
        """Unit attribute to keep API consistent

        Returns:
            Unit: The supporting unit (i.e. the one executing the order)
        """
        return self.supporting_unit

    @property
    def province_no_coast_location(self) -> Optional[Location]:
        if self.province_no_coast is None:
            return self.province_no_coast
        else:
            return Location(self.province_no_coast)

    @property
    def location(self) -> Location:
        return self.unit.location

    def __str__(self):
        if not self.province_no_coast:
            return f"using {self.supporting_unit} to support {self.supported_unit} "
        else:
            return f"using {self.supporting_unit} to support {self.supported_unit} moving into {self.province_no_coast} "


@dataclass(eq=True, frozen=True)
class CVY(_DAIDEObject):
    convoying_unit: Unit
    convoyed_unit: Unit
    province: Location

    def __post_init__(self):
        if isinstance(self.province, str):
            object.__setattr__(self, "province", Location(province=self.province))
        super().__post_init__()

    def __str__(self):
        return f"using {self.convoying_unit} to convoy {self.convoyed_unit} into {self.province} "

    @property
    def unit(self) -> Unit:
        """Unit attribute to keep API consistent

        Returns:
            Unit: The convoying unit (i.e. the fleet)
        """
        return self.convoying_unit

    @property
    def location(self) -> Location:
        return self.unit.location


@dataclass(eq=True, frozen=True)
class MoveByCVY(_DAIDEObject):
    unit: Unit
    province: Location
    province_seas: Tuple[ProvinceSea]

    def __init__(self, unit, province, *province_seas):
        object.__setattr__(self, "unit", unit)
        object.__setattr__(self, "province", province)
        object.__setattr__(self, "province_seas", tuple(province_seas))
        self.__post_init__()

    def __post_init__(self):
        super().__post_init__()
        if not self.province_seas:
            raise ValueError(
                "Movement via convoy must include at least one sea province."
            )

    def __str__(self):
        return (
            f"moving {self.unit} by convoy into {self.province} via "
            + and_items(list(map(lambda x: str(x), self.province_seas)))
        )

    @property
    def location(self) -> Location:
        return self.province


@dataclass(eq=True, frozen=True)
class RTO(_DAIDEObject):
    unit: Unit
    location: Location

    def __str__(self):
        return f"retreating {self.unit} to {self.location} "


@dataclass(eq=True, frozen=True)
class DSB(_DAIDEObject):
    unit: Unit

    def __str__(self):
        return f"disbanding {self.unit} "

    @property
    def location(self) -> None:
        return None


@dataclass(eq=True, frozen=True)
class BLD(_DAIDEObject):
    unit: Unit

    def __str__(self):
        return f"building {self.unit} "

    @property
    def location(self) -> Location:
        return self.unit.location


@dataclass(eq=True, frozen=True)
class REM(_DAIDEObject):
    unit: Unit

    def __str__(self):
        return f"removing {self.unit} "

    @property
    def location(self) -> None:
        return None


@dataclass(eq=True, frozen=True)
class WVE(_DAIDEObject):
    """Wave a build"""

    power: Power

    def __str__(self):
        return f"waiving {self.power} "

    @property
    def location(self) -> None:
        return None


@dataclass(eq=True, frozen=True)
class Turn(_DAIDEObject):
    season: Season
    year: int

    def __str__(self):
        return f"{self.season} {self.year} "


Order = Union[
    HLD,
    MTO,
    SUP,
    CVY,
    MoveByCVY,
]
Build = Union[BLD, REM, WVE]
Retreat = Union[RTO, DSB]

Command = Union[Order, Retreat, Build]
