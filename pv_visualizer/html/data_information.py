from trame.widgets import vuetify

# -----------------------------------------------------------------------------
# Utils
# -----------------------------------------------------------------------------


def create_group(title, **kwargs):
    content = None
    with vuetify.VCol(classes="px-0 mx-0", **kwargs):
        vuetify.VRow(
            title, classes="text-subtitle-1 px-4", style="border-bottom: solid 1px #333"
        )
        content = vuetify.VCol(classes="px-0 mx-0")

    return content


def create_na_line(available):
    vuetify.VCol(
        "(n/a)", v_if=(f"!{available}",), classes="text-body-2 text--disabled px-0 ma-0"
    )


def create_line(available, label, value, label_size=4):
    with vuetify.VRow(v_if=(available,), classes="pa-0 ma-0"):
        vuetify.VCol(label, classes="text-body-1 py-0 my-0", cols=label_size)
        vuetify.VCol(value, classes="text-body-2 pa-0 ma-0", cols=12 - label_size)


# -----------------------------------------------------------------------------
# Groups
# -----------------------------------------------------------------------------


def create_file_property():
    available = "active_data_information.file"
    with create_group("File Properties", v_if=(available,)):
        create_na_line(available)
        create_line(available, "Name", "{{ active_data_information.file.name }}")
        create_line(available, "Path", "{{ active_data_information.file.path }}")


# -----------------------------------------------------------------------------
def create_data_stats():
    available = "active_data_information.data_stats"
    with create_group("Data Statistics", v_if=(available,)):
        create_na_line(available)
        create_line(available, "Type", "{{ active_data_information.data_stats.type }}")
        create_line(
            available, "# Cells", "{{ active_data_information.data_stats.cell }}"
        )
        create_line(
            available, "# Points", "{{ active_data_information.data_stats.point }}"
        )
        create_line(
            available, "# Edges", "{{ active_data_information.data_stats.edge }}"
        )
        create_line(available, "# Rows", "{{ active_data_information.data_stats.row }}")
        create_line(
            available, "Memory", "{{ active_data_information.data_stats.memory }}"
        )
        create_line(
            available, "Bounds", "{{ active_data_information.data_stats.bounds }}"
        )


# -----------------------------------------------------------------------------


def create_data_arrays():
    with create_group("Data Arrays", v_if=("active_data_information.arrays",)):
        with vuetify.VDataTable(
            dense=True,
            height=200,
            classes="px-0 mx-0",
            disable_filtering=True,
            disable_pagination=True,
            hide_default_footer=True,
            headers=("active_data_information.arrays.header",),
            items=("active_data_information.arrays.values",),
        ):
            with vuetify.Template(
                v_slot_item_name="{item}",
                __properties=[("v_slot_item_name", "v-slot:item.name")],
            ) as t:
                vuetify.VIcon(x_small=True, v_text=("item.location",))
                t.add_child("{{ item.name }}")


def create_time():
    with create_group("Time", v_if=("active_data_information.times",)):
        vuetify.VDataTable(
            height=200,
            dense=True,
            disable_filtering=True,
            disable_pagination=True,
            hide_default_footer=True,
            headers=("active_data_information.times.header",),
            items=("active_data_information.times.values",),
        )


# -----------------------------------------------------------------------------

GROUPS = [
    create_file_property,
    create_data_stats,
    create_data_arrays,
    create_time,
]

# -----------------------------------------------------------------------------


class DataInformation(vuetify.VCard):
    def __init__(self, *argc, **kwargs):
        super().__init__(*argc, v_if=("active_data_information",), **kwargs)

        with self:
            # vuetify.VCardTitle("Data Information", classes="py-2")
            # vuetify.VDivider()
            # with vuetify.VCardText(classes="px-0") as content:
            for group in GROUPS:
                group()
