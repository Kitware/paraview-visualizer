VTK_DATA_TYPES = [
    "void",  # define VTK_VOID 0
    "bit",  # define VTK_BIT 1
    "int8",  # define VTK_CHAR 2
    "unit8",  # define VTK_UNSIGNED_CHAR 3
    "int16",  # define VTK_SHORT 4
    "uint16",  # define VTK_UNSIGNED_SHORT 5
    "int32",  # define VTK_INT 6
    "uint32",  # define VTK_UNSIGNED_INT 7
    "int64",  # define VTK_LONG 8
    "uint64",  # define VTK_UNSIGNED_LONG 9
    "float32",  # define VTK_FLOAT 10
    "float64",  # define VTK_DOUBLE 11
    "idtype",  # define VTK_ID_TYPE 12
    "string",  # define VTK_STRING 13
    "opaque",  # define VTK_OPAQUE 14
    "char",  # define VTK_SIGNED_CHAR 15
    "longLong",  # define VTK_LONG_LONG 16
    "ulonglong",  # define VTK_UNSIGNED_LONG_LONG 17
    "18",  # 18
    "19",  # 19
    "variant",  # define VTK_VARIANT 20
    "vtkObj",  # define VTK_OBJECT 21
]

VTK_DATASET_TYPES = [
    "PolyData",  # define VTK_POLY_DATA 0
    "Structured Points",  # define VTK_STRUCTURED_POINTS 1
    "Structured Grid",  # define VTK_STRUCTURED_GRID 2
    "Rectilinear Grid",  # define VTK_RECTILINEAR_GRID 3
    "Unstructured Grid",  # define VTK_UNSTRUCTURED_GRID 4
    "Piecewise Function",  # define VTK_PIECEWISE_FUNCTION 5
    "ImageData",  # define VTK_IMAGE_DATA 6
    "Data Object",  # define VTK_DATA_OBJECT 7
    "DataSet",  # define VTK_DATA_SET 8
    "Pointset",  # define VTK_POINT_SET 9
    "Uniform Grid",  # define VTK_UNIFORM_GRID 10
    "Composite DataSet",  # define VTK_COMPOSITE_DATA_SET 11
    "Multi-group DataSet",  # define VTK_MULTIGROUP_DATA_SET 12
    "Multi-block DataSet",  # define VTK_MULTIBLOCK_DATA_SET 13
    "Hierarchical DataSet",  # define VTK_HIERARCHICAL_DATA_SET 14
    "Hierarchical Box DataSet",  # define VTK_HIERARCHICAL_BOX_DATA_SET 15
    "Generic DataSet",  # define VTK_GENERIC_DATA_SET 16
    "Hyper Octree",  # define VTK_HYPER_OCTREE 17
    "Temporal DataSet",  # define VTK_TEMPORAL_DATA_SET 18
    "Table",  # define VTK_TABLE 19
    "Graph",  # define VTK_GRAPH 20
    "Tree",  # define VTK_TREE 21
    "Selection",  # define VTK_SELECTION 22
    "Directed Graph",  # define VTK_DIRECTED_GRAPH 23
    "Undirected Graph",  # define VTK_UNDIRECTED_GRAPH 24
    "Multi-piece DataSet",  # define VTK_MULTIPIECE_DATA_SET 25
    "VTK_DIRECTED_ACYCLIC_GRAPH",  # define VTK_DIRECTED_ACYCLIC_GRAPH 26
    "VTK_ARRAY_DATA",  # define VTK_ARRAY_DATA 27
    "VTK_REEB_GRAPH",  # define VTK_REEB_GRAPH 28
    "VTK_UNIFORM_GRID_AMR",  # define VTK_UNIFORM_GRID_AMR 29
    "VTK_NON_OVERLAPPING_AMR",  # define VTK_NON_OVERLAPPING_AMR 30
    "VTK_OVERLAPPING_AMR",  # define VTK_OVERLAPPING_AMR 31
    "VTK_HYPER_TREE_GRID",  # define VTK_HYPER_TREE_GRID 32
    "Molecule",  # define VTK_MOLECULE 33
    "VTK_PISTON_DATA_OBJECT",  # define VTK_PISTON_DATA_OBJECT 34
    "VTK_PATH",  # define VTK_PATH 35
    "VTK_UNSTRUCTURED_GRID_BASE",  # define VTK_UNSTRUCTURED_GRID_BASE 36
    "VTK_PARTITIONED_DATA_SET",  # define VTK_PARTITIONED_DATA_SET 37
    "VTK_PARTITIONED_DATA_SET_COLLECTION",  # define VTK_PARTITIONED_DATA_SET_COLLECTION 38
    "VTK_UNIFORM_HYPER_TREE_GRID",  # define VTK_UNIFORM_HYPER_TREE_GRID 39
    "VTK_EXPLICIT_STRUCTURED_GRID",  # define VTK_EXPLICIT_STRUCTURED_GRID 40
    "VTK_DATA_OBJECT_TREE",  # define VTK_DATA_OBJECT_TREE 41
    "VTK_ABSTRACT_ELECTRONIC_DATA",  # define VTK_ABSTRACT_ELECTRONIC_DATA 42
    "VTK_OPEN_QUBE_ELECTRONIC_DATA",  # define VTK_OPEN_QUBE_ELECTRONIC_DATA 43
    "VTK_ANNOTATION",  # define VTK_ANNOTATION 44
    "VTK_ANNOTATION_LAYERS",  # define VTK_ANNOTATION_LAYERS 45
    "VTK_BSP_CUTS",  # define VTK_BSP_CUTS 46
    "VTK_GEO_JSON_FEATURE",  # define VTK_GEO_JSON_FEATURE 47
    "VTK_IMAGE_STENCIL_DATA",  # define VTK_IMAGE_STENCIL_DATA 48
]


def data_information_transform_array(location, array):
    result = []
    for value in array.values():
        result.append(
            {
                "location": location,
                "type": VTK_DATA_TYPES[value.get("DataType")],
                "name": value.get("Name"),
                "components": len(value.get("Components")) - 1,
                "kind": f"{VTK_DATA_TYPES[value.get('DataType')]}({len(value.get('Components')) - 1})",
            }
        )

    return result


def data_information_transform(data_info):
    result = {}

    result["file"] = None

    result["data_stats"] = {
        "type": VTK_DATASET_TYPES[data_info.get("DataSetType")],
        "point": data_info.get("NumberOfElements")[0],
        "cell": data_info.get("NumberOfElements")[1],
        "field": data_info.get("NumberOfElements")[2],
        "point_cell": data_info.get("NumberOfElements")[3],
        "vertex": data_info.get("NumberOfElements")[4],
        "edge": data_info.get("NumberOfElements")[5],
        "row": data_info.get("NumberOfElements")[6],
        "memory": data_info.get("MemorySize"),
        "bounds": data_info.get("Bounds"),
    }

    result["arrays"] = {
        "header": [
            {"text": "Name", "value": "name"},
            {"text": "Kind", "value": "kind"},
        ],
        "values": [
            *data_information_transform_array(
                "mdi-dots-triangle",
                data_info.get("AttributeInformation0").get("arrays", []),
            ),
            *data_information_transform_array(
                "mdi-triangle", data_info.get("AttributeInformation1").get("arrays", [])
            ),
            *data_information_transform_array(
                "mdi-database", data_info.get("AttributeInformation2").get("arrays", [])
            ),
        ],
    }

    result["times"] = {
        "header": [
            {"text": "Index", "value": "idx"},
            {"text": "Time", "value": "value"},
        ],
        "values": [
            {"idx": 0, "value": 0},
        ],
    }

    return result


def data_information_transform_proxy(proxy):
    if proxy is None:
        return {}

    result = {}
    data_info = proxy.GetDataInformation().DataInformation

    result["data_stats"] = {
        "type": VTK_DATASET_TYPES[data_info.GetDataSetType()],
        "point": data_info.GetNumberOfElements(0),
        "cell": data_info.GetNumberOfElements(1),
        "field": data_info.GetNumberOfElements(2),
        "point_cell": data_info.GetNumberOfElements(3),
        "vertex": data_info.GetNumberOfElements(4),
        "edge": data_info.GetNumberOfElements(5),
        "row": data_info.GetNumberOfElements(6),
        "memory": data_info.GetMemorySize(),
        "bounds": data_info.GetBounds(),
    }

    array_values = []
    result["arrays"] = {
        "header": [
            {"text": "Name", "value": "name"},
            {"text": "Kind", "value": "kind"},
        ],
        "values": array_values,
    }

    # points
    location = "mdi-dots-triangle"
    fields = data_info.GetPointDataInformation()
    size = fields.GetNumberOfArrays()
    for i in range(size):
        array = fields.GetArrayInformation(i)
        array_values.append(
            {
                "location": location,
                "name": array.GetName(),
                "kind": f"{VTK_DATA_TYPES[array.GetDataType()]}({array.GetNumberOfComponents()})",
            }
        )

    # cells
    location = "mdi-triangle"
    fields = data_info.GetCellDataInformation()
    size = fields.GetNumberOfArrays()
    for i in range(size):
        array = fields.GetArrayInformation(i)
        array_values.append(
            {
                "location": location,
                "name": array.GetName(),
                "kind": f"{VTK_DATA_TYPES[array.GetDataType()]}({array.GetNumberOfComponents()})",
            }
        )

    # fields
    location = "mdi-database"
    fields = data_info.GetFieldDataInformation()
    size = fields.GetNumberOfArrays()
    for i in range(size):
        array = fields.GetArrayInformation(i)
        array_values.append(
            {
                "location": location,
                "name": array.GetName(),
                "kind": f"{VTK_DATA_TYPES[array.GetDataType()]}({array.GetNumberOfComponents()})",
            }
        )

    return result


def get_data_information(proxy):
    return data_information_transform_proxy(proxy)
    # state.active_data_information = data_information_transform(SAMPLE_DATA_INFORMATION)
