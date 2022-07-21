r"""
./Plugins/EmbossingRepresentations/pqExtrusionPropertyWidgetDecorator.cxx
./Qt/Components/pqCompositePropertyWidgetDecorator.cxx
./Qt/Components/pqPropertyWidgetDecorator.cxx
./Qt/ApplicationComponents/pqCTHArraySelectionDecorator.cxx
./Qt/ApplicationComponents/pqSessionTypeDecorator.cxx
./Qt/ApplicationComponents/pqSpreadSheetViewDecorator.cxx
./Qt/ApplicationComponents/pqAnimationShortcutDecorator.cxx
"""
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AdvancedDecorator:
    advance_mode = False

    def __init__(self, proxy, hint):
        self._proxy = proxy
        self._name = hint.get("name")
        self._property = self._proxy.GetProperty(self._name)
        self._default_rep = self._property.GetPanelVisibilityDefaultForRepresentation()
        self._rep_property = self._proxy.GetProperty("Representation")
        if self._default_rep:
            self._default_rep = self._default_rep.lower()

    def can_show(self):
        if self._default_rep:
            selected = self._rep_property.GetElement(0).lower()
            return selected == self._default_rep
        return AdvancedDecorator.advance_mode

    def enable_widget(self):
        return True

    def can_query(self):
        return True


class DecoratorMode:
    VISIBILITY = "visibility"
    ENABLED_STATE = "enabled_state"


class GenericDecorator:
    def __init__(self, proxy, hint):
        self._proxy = proxy
        self._index = 0
        self._values = None
        self._inverse = False
        self._enabled = True
        self._visible = True
        self._nb_components = -1
        self._mode = DecoratorMode.ENABLED_STATE
        #
        self._property = None
        #
        self._configure(hint)

    def _configure(self, xml_element):
        # property (mandatory)
        prop_name = xml_element.get("property")

        if prop_name is None:
            return

        self._property = self._proxy.GetProperty(prop_name)
        if self._property is None:
            return

        # index
        self._index = int(xml_element.get("index", 0))

        # value / values
        value = xml_element.get("value")
        if value is None:
            value = xml_element.get("values")
            if value is not None:
                self._values = []
                for item in value.split(" "):
                    v = item.strip()
                    if len(v):
                        self._values.append(v)
        else:
            self._values = [value]

        # mode
        self._mode = xml_element.get("mode")

        # inverse
        if xml_element.get("inverse") == "1":
            self._inverse = True

        # number_of_components
        nb_comp = xml_element.get("number_of_components")
        if nb_comp is not None:
            self._nb_components = int(nb_comp)

    def _value_match(self):
        if self._property is None:
            return not self._inverse

        try:
            nb_elements = self._property.GetNumberOfElements()
        except Exception:
            nb_elements = self._property.GetNumberOfProxies()

        if nb_elements == 0:
            status = len(self._values) == 1 and self._values[0] == "null"
            return (not status) if self._inverse else status

        if self._property.IsA("vtkSMProxyProperty"):
            if self._property.FindDomain("vtkSMProxyListDomain"):
                status = False
                active = self._property.GetUncheckedProxy(0).GetXMLName()
                for value in self._values:
                    status = status or (value == active)
                return (not status) if self._inverse else status

            if (
                len(self._values) == 1
                and self._values[0] == "null"
                and nb_elements == 1
            ):
                return (
                    (not self._inverse)
                    if self._property.GetUncheckedProxy(0) is None
                    else self._inverse
                )

            return False

        # The "number_of_components" attribute is used to enable/disable a widget based on
        # whether the referenced property value refers to an array in the input that has
        # the specified number of components.
        if self._nb_components > -1:
            if not self._property.IsA("vtkSMStringVectorProperty") or nb_elements != 5:
                return False

            # Look for array list domain
            array_list_domain = self._property.FindDomain("vtkSMArrayListDomain")
            if array_list_domain is None:
                return False

            array_association = int(self._property.GetUncheckedElement(self._index - 1))
            array_name = str(self._property.GetUncheckedElement(self._index))
            data_info = array_list_domain.GetInputDataInformation("Input")

            if data_info is None:
                return False

            # Array components could be 0 if arrayName is the NoneString
            array_components = 0
            array_info = data_info.GetArrayInformation(array_name, array_association)
            if array_info is not None:
                array_components = array_info.GetNumberOfComponents()

            status = array_components == self._nb_components
            return (not status) if self._inverse else status

        value = str(self._property.GetUncheckedElement(self._index))
        status = False
        for v in self._values:
            status = status or (v == value)

        return (not status) if self._inverse else status

    def _update_state(self):
        if self._mode == DecoratorMode.VISIBILITY:
            self._visible = self._value_match()

        if self._mode == DecoratorMode.ENABLED_STATE:
            self._enabled = self._value_match()

    def can_show(self):
        self._update_state()
        return self._visible

    def enable_widget(self):
        self._update_state()
        return self._enabled

    def can_query(self):
        return self.can_show()


# -----------------------------------------------------------------------------


class InputDataTypeDecorator:
    def __init__(self, proxy, hint):
        self._proxy = proxy
        self._mode = hint.get("mode")
        self._exclude = hint.get("exclude")
        self._parts = hint.get("name").split(" ")

        # Handle exclude string attr => bool
        self._exclude = self._exclude is not None and self._exclude != "0"

    def _process_state(self):
        property = self._proxy.GetProperty("Input") if self._proxy is not None else None

        if property is not None:
            input_proxy = property.GetUncheckedProxy(0)
            if input_proxy is None:
                return False
            data_info = input_proxy.GetDataInformation()
            for part in self._parts:
                match = data_info.DataSetTypeIsA(part)
                if part == "Structured":
                    match = data_info.IsDataStructured()
                return (not self._exclude) if match else self._exclude

            if len(self._parts) == 0:
                return False

        return True

    def can_show(self):
        if self._mode == DecoratorMode.VISIBILITY:
            return self._process_state()

        return True

    def enable_widget(self):
        if self._mode == DecoratorMode.ENABLED_STATE:
            return self._process_state()

        return True

    def can_query(self):
        return self.can_show()


# -----------------------------------------------------------------------------


def operation_and(a, b):
    return a and b


def operation_or(a, b):
    return a or b


OPERATION_TYPES = {
    "and": operation_and,
    "or": operation_or,
}

OPERATION_TYPES_INITIAL = {
    "and": True,
    "or": False,
}


def to_decorator(proxy, entry):
    _type = entry.get("type")
    if _type in OPERATION_TYPES:
        return ExpressionDecorator(proxy, entry)

    return get_decorator(proxy, entry)


class ExpressionDecorator:
    def __init__(self, proxy, hint):
        self._proxy = proxy
        self._initial = OPERATION_TYPES_INITIAL[hint.get("type")]
        self._operation = OPERATION_TYPES[hint.get("type")]
        self._children = []
        for entry in hint.get("children", []):
            decorator = to_decorator(proxy, entry)
            if decorator is not None:
                self._children.append(decorator)

    def can_show(self):
        value = self._initial
        for decorator in self._children:
            value = self._operation(value, decorator.can_show())

        return value

    def enable_widget(self):
        value = self._initial
        for decorator in self._children:
            value = self._operation(value, decorator.enable_widget())
        return value

    def can_query(self):
        return self.can_show()


class CompositeDecorator:
    def __init__(self, proxy, hint):
        import json

        self._msg = json.dumps(hint, indent=2)
        self._internal = to_decorator(proxy, hint["children"][0])

    def can_show(self):
        return self._internal.can_show()

    def enable_widget(self):
        return self._internal.enable_widget()

    def can_query(self):
        return self.can_show()


# -----------------------------------------------------------------------------


class BoolPropertyDecorator:
    def __init__(self, proxy, hint):
        _config = hint["children"][0]
        #
        self._proxy = proxy
        self._bool_prop = True
        self._property = self._proxy.GetProperty(_config["name"])
        self._index = int(_config.get("index", "0"))
        self._function = _config.get("function", "boolean")
        self._value = _config.get("value", "0")

    def _update(self):
        _current_value = self._property.GetUncheckElement(self._index)
        if self._function == "boolean":
            self._bool_prop = int(_current_value) != 0
        elif self._function == "boolean_invert":
            self._bool_prop = int(_current_value) == 0
        elif self._function == "greaterthan":
            self._bool_prop = _current_value > float(self._value)
        elif self._function == "lessthan":
            self._bool_prop = _current_value < float(self._value)
        elif self._function == "equals":
            self._bool_prop = str(_current_value) == self._value
        elif self._function == "contains":
            self._bool_prop = self._value in str(_current_value)

    @property
    def value(self):
        return self._bool_prop

    def can_show(self):
        return True

    def enable_widget(self):
        return True

    def can_query(self):
        return self.can_show()


class ShowWidgetDecorator(BoolPropertyDecorator):
    def can_show(self):
        return self.value


class EnableWidgetDecorator(BoolPropertyDecorator):
    def enable_widget(self):
        return self.value


# -----------------------------------------------------------------------------


class OSPRayHidingDecorator:
    # Should be set at initialization
    OSPRAY_AVAILABLE = False

    def __init__(self, proxy, hint):
        pass

    def can_show(self):
        return OSPRayHidingDecorator.OSPRAY_AVAILABLE

    def enable_widget(self):
        return True

    def can_query(self):
        return self.can_show()


# -----------------------------------------------------------------------------


class MultiComponentsDecorator:
    def __init__(self, proxy, hint):
        self._proxy = proxy
        self._components = [int(v) for v in hint.get("components", "").split()]

    def can_show(self):
        info = self._proxy.GetArrayInformationForColorArray()
        if info is None:
            return False
        return info.GetNumberOfComponents() in self._components

    def enable_widget(self):
        return True

    def can_query(self):
        return self.can_show()


# -----------------------------------------------------------------------------


def get_decorator(proxy, config):
    _type = config.get("type")
    if _type in globals():
        return globals()[_type](proxy, config)

    logger.info(f"~~~ no decorator for {_type} ~~~")
