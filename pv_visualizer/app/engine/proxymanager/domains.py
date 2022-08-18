import logging
from trame_simput.core.domains import PropertyDomain, register_property_domain
from . import paraview, decorators
from .const import (
    PANEL_WIDGETS,
    WIDGETS,
    DOMAIN_TYPES,
    DOMAIN_TYPE_DEFAULT,
    DOMAINS_TO_SKIP,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -----------------------------------------------------------------------------
# Generic ParaView domain adapter
# -----------------------------------------------------------------------------


class ParaViewDomain(PropertyDomain):
    def __init__(self, _proxy, _property, **kwargs):
        super().__init__(_proxy, _property, **kwargs)
        self._pv_proxy = paraview.unwrap(_proxy.object)
        self._pv_property = paraview.unwrap(self._pv_proxy.GetProperty(_property))
        self._pv_class = kwargs.get("pv_class")
        self._pv_name = kwargs.get("pv_name")
        self._available = DOMAIN_TYPES.get(self._pv_class, DOMAIN_TYPE_DEFAULT)
        self._pv_domain = None

        if self._pv_property is None:
            # logger.info(f"!> No property {_property} on proxy {self._pv_proxy.GetXMLName()}")
            # logger.info("~" * 80)
            return

        # Find PV domain instance
        iter = self._pv_property.NewDomainIterator()
        iter.Begin()
        while not iter.IsAtEnd():
            domain = iter.GetDomain()
            domain_class = domain.GetClassName()
            domain_name = domain.GetXMLName()

            if self._pv_class == domain_class and self._pv_name == domain_name:
                self._pv_domain = domain

            iter.Next()

        self._message = kwargs.get(
            "message", f"{_property}>{self._pv_class}::{self._pv_name}"
        )

    def set_value(self):
        # Do PV domain have API to set value?
        return False

    def available(self):
        if self._pv_domain is None:
            return []

        values = self._available(self._pv_domain)
        # logger.info(f"{self._pv_class}::{self._pv_name}", values)
        return values

    def valid(self, required_level=2):
        if self._level < required_level:
            return True
        # What method to call on PV domain?
        return True


# -----------------------------------------------------------------------------


class ParaViewDecoratorDomain(PropertyDomain):
    def __init__(self, _proxy, _property, **kwargs):
        super().__init__(_proxy, _property, **kwargs)
        self._decorator = decorators.get_decorator(
            paraview.unwrap(_proxy.object),
            kwargs.get("properties"),
        )

    def set_value(self):
        # Do PV domain have API to set value?
        return False

    def available(self):
        if self._decorator:
            # DEBUG decorator state ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # logger.info(f"{self._property_name}")
            # logger.info(f"  > show({self._decorator.can_show()})")
            # logger.info(f"  > enable({self._decorator.enable_widget()})")
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            return {
                "show": self._decorator.can_show(),
                "enable": self._decorator.enable_widget(),
                "query": self._decorator.can_query(),
            }

        return {}

    def valid(self, required_level=2):
        if self._level < required_level:
            return True
        # What method to call on PV domain?
        return True


# -----------------------------------------------------------------------------


def register_domains():
    register_property_domain("ParaViewDomain", ParaViewDomain)
    register_property_domain("ParaViewDecoratorDomain", ParaViewDecoratorDomain)


# -----------------------------------------------------------------------------
# UI handling
# -----------------------------------------------------------------------------


def get_property_size(property):
    if hasattr(property, "GetNumberOfElements"):
        return property.GetNumberOfElements()

    if hasattr(property, "GetNumberOfProxies"):
        return property.GetNumberOfProxies()

    return 0


def get_domain_widget(domain):
    keep = True
    name = domain.GetXMLName()
    widget = WIDGETS.get(domain.GetClassName(), "sw-text-field")
    property = domain.GetProperty()
    ui_attributes = {}

    # Map custom PV widgets to simput widgets
    if property.GetPanelWidget():
        panel_widget = property.GetPanelWidget()
        custom_widget = PANEL_WIDGETS.get(panel_widget)
        if custom_widget:
            widget = custom_widget
            # logger.info(
            #     f"Use custom widget {property.GetXMLName()} {panel_widget} => {widget}"
            # )
        elif custom_widget is None:
            logger.info(f"Missing custom widget key: {panel_widget}")

    # Try to adjust layout base on property size
    if get_property_size(property) == 6:
        ui_attributes["layout"] = "l2"

    if widget == "sw-select":
        name = "List"

    if domain.GetClassName() in ["vtkSMDoubleRangeDomain", "vtkSMIntRangeDomain"]:
        keep = domain.GetMinimumExists(0) and domain.GetMaximumExists(0)

    if keep and name in DOMAINS_TO_SKIP:
        keep = False

    return keep, name, widget, ui_attributes
