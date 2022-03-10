r"""
./Plugins/EmbossingRepresentations/pqExtrusionPropertyWidgetDecorator.cxx
./Qt/Components/pqCompositePropertyWidgetDecorator.cxx
./Qt/Components/pqPropertyWidgetDecorator.cxx
./Qt/ApplicationComponents/pqShowWidgetDecorator.cxx
./Qt/ApplicationComponents/pqOSPRayHidingDecorator.cxx
./Qt/ApplicationComponents/pqCTHArraySelectionDecorator.cxx
./Qt/ApplicationComponents/pqSessionTypeDecorator.cxx
./Qt/ApplicationComponents/pqSpreadSheetViewDecorator.cxx
./Qt/ApplicationComponents/pqAnimationShortcutDecorator.cxx
./Qt/ApplicationComponents/pqBoolPropertyWidgetDecorator.cxx
./Qt/ApplicationComponents/pqMultiComponentsDecorator.cxx
./Qt/ApplicationComponents/pqInputDataTypeDecorator.cxx
./Qt/ApplicationComponents/pqGenericPropertyWidgetDecorator.cxx
./Qt/ApplicationComponents/pqEnableWidgetDecorator.cxx
"""

# -----------------------------------------------------------------------------
# PARAVIEW_SRC/VTKExtensions/FiltersGeneral/Resources/general_filters.xml
# -----------------------------------------------------------------------------
#   <PropertyWidgetDecorator type="InputDataTypeDecorator"
#                            name="vtkHyperTreeGrid"
#                            exclude="1"
#                            mode="visibility"/>
# -----------------------------------------------------------------------------
#   <PropertyWidgetDecorator type="InputDataTypeDecorator"
#                            name="vtkHyperTreeGrid"
#                            mode="visibility"/>
# -----------------------------------------------------------------------------
#   <PropertyWidgetDecorator type="CompositeDecorator">
#     <Expression type="or">
#       <PropertyWidgetDecorator type="GenericDecorator"
#                                mode="visibility"
#                                property="ClipFunction"
#                                value="Scalar" />
#       <PropertyWidgetDecorator type="GenericDecorator"
#                                mode="visibility"
#                                property="HyperTreeGridClipFunction"
#                                value="Scalar" />
#     </Expression>
#   </PropertyWidgetDecorator>
# -----------------------------------------------------------------------------
#   <PropertyWidgetDecorator type="CompositeDecorator">
#     <Expression type="or">
#       <PropertyWidgetDecorator type="GenericDecorator"
#                                mode="visibility"
#                                property="ClipFunction"
#                                value="Scalar" />
#       <PropertyWidgetDecorator type="GenericDecorator"
#                                mode="visibility"
#                                property="HyperTreeGridClipFunction"
#                                value="Scalar" />
#     </Expression>
#   </PropertyWidgetDecorator>
# -----------------------------------------------------------------------------
#   <PropertyWidgetDecorator type="CompositeDecorator">
#     <Expression type="and">
#       <PropertyWidgetDecorator type="InputDataTypeDecorator"
#                                mode="visibility"
#                                exclude="1"
#                                name="vtkHyperTreeGrid" />
#       <PropertyWidgetDecorator type="GenericDecorator"
#                                mode="visibility"
#                                property="ClipFunction"
#                                value="Scalar"
#                                inverse="1" />
#     </Expression>
#   </PropertyWidgetDecorator>
# -----------------------------------------------------------------------------
#   <PropertyWidgetDecorator type="CompositeDecorator">
#     <Expression type="and">
#       <PropertyWidgetDecorator type="GenericDecorator" mode="visibility" property="ClipFunction" value="Box" inverse="0" />
#       <PropertyWidgetDecorator type="GenericDecorator" mode="enabled_state" property="Invert" value="1" />
#       <PropertyWidgetDecorator type="GenericDecorator" mode="enabled_state" property="PreserveInputCells" value="0" />
#     </Expression>
#   </PropertyWidgetDecorator>
# -----------------------------------------------------------------------------

# GenericDecorator
# InputDataTypeDecorator
# CompositeDecorator


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
        if xml_element.get("index") is not None:
            self._index = int(xml_element.get("index"))

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
        except:
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


class CompositeDecorator:
    def __init__(self, proxy, hint):
        import json

        self._msg = json.dumps(hint, indent=2)
        self._internal = to_decorator(proxy, hint["children"][0])

    def can_show(self):
        # print("~~~ CAN SHOW ~~~: ", self._internal.can_show())
        # print(self._msg)
        # print("~"*60)
        return self._internal.can_show()

    def enable_widget(self):
        return self._internal.enable_widget()


# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------


def get_decorator(proxy, config):
    _type = config.get("type")
    if _type in globals():
        return globals()[_type](proxy, config)
