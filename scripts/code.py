import hardcoded_data

def _class_name_from_element_name(element_name):
    return f"{element_name[2:]}Element"

def _file_stem_from_element_name(element_name):
    return "".join([
        "_" + letter.lower() if letter.isupper() else letter
        for letter in element_name[2:]
    ]).lstrip("_") + "_element"

def _header_filename_from_element_name(element_name):
    stem = _file_stem_from_element_name(element_name)
    return f"scene/{stem}.hpp"

def _source_filename_from_element_name(element_name):
    stem = _file_stem_from_element_name(element_name)
    return f"scene/{stem}.cpp"

def generate_code(
    element_name,
    sbt_manager,
    base_objs,
    element_instances_bin_paths,
    obj_archives,
    primitive_instances_bin_paths,
    primitive_instances_handle_indices,
    curve_records_by_element_instance,
    requires_overflow,
    should_split_primitive_instances,
):
    header_filename = _header_filename_from_element_name(element_name)
    source_filename = _source_filename_from_element_name(element_name)
    return {
        header_filename: _generate_header(element_name, requires_overflow),
        source_filename: _generate_src(
            element_name,
            sbt_manager,
            base_objs,
            element_instances_bin_paths,
            obj_archives,
            primitive_instances_bin_paths,
            primitive_instances_handle_indices,
            curve_records_by_element_instance,
            requires_overflow,
            should_split_primitive_instances,
        )
    }

def _generate_header(element_name, requires_overflow):
    def class_definition(class_name):
        return f"""\
class {class_name} : public Element {{
public:
    {class_name}();
}};
"""
    class_name = _class_name_from_element_name(element_name)

    class_code = class_definition(class_name)
    overflow_class_code = ""
    if requires_overflow:
        overflow_class_code = class_definition(f"{class_name}Overflow")

    return f"""\
#pragma once

#include "scene/element.hpp"

namespace moana {{

{class_code}

{overflow_class_code}

}}
"""

def _generate_src(
    element_name,
    sbt_manager,
    base_objs,
    element_instances_bin_paths,
    obj_archives,
    primitive_instances_bin_paths,
    primitive_instances_handle_indices,
    curve_records_by_element_instance,
    requires_overflow,
    should_split_primitive_instances,
):
    header_filename = _header_filename_from_element_name(element_name)

    class_name = _class_name_from_element_name(element_name)
    if requires_overflow:
        impl_base_objs = [ base_objs[0] ]
        overflow_base_objs = [ base_objs[1] ]
    else:
        impl_base_objs = base_objs
        overflow_base_objs = []

    impl = _generate_impl(
        element_name,
        class_name,
        sbt_manager,
        impl_base_objs,
        element_instances_bin_paths,
        obj_archives,
        primitive_instances_bin_paths,
        primitive_instances_handle_indices,
        curve_records_by_element_instance,
        should_split_primitive_instances,
    )

    overflow_impl = ""
    if requires_overflow:
        overflow_impl = _generate_impl(
            element_name,
            f"{class_name}Overflow",
            sbt_manager,
            overflow_base_objs,
            element_instances_bin_paths,
            [],
            [[]],
            [[]],
            [[]],
            False
        )

    return f"""\
#include "{header_filename}"

namespace moana {{

{impl}

{overflow_impl}

}}
"""

def _generate_impl(
    element_name,
    class_name,
    sbt_manager,
    base_objs,
    element_instances_bin_paths,
    obj_archives,
    primitive_instances_bin_paths,
    primitive_instances_handle_indices,
    curve_records_by_element_instance,
    should_split_primitive_instances,
):

    base_obj_items = "\n".join([
        f"{' ' * 8}{base_obj.code_path},"
        for base_obj
        in base_objs
    ])

    material_offset = sbt_manager.get_material_offset(element_name)

    mtl_lookup_items = "\n".join(
        f"{' ' * 8}\"{material_name}\","
        for material_name
        in sbt_manager.get_names(element_name)
    )

    obj_archives_items = "\n".join(
        f"{' ' * 8}moanaRoot + \"/island/{obj_archive}\","
        for obj_archive
        in obj_archives
    )

    element_instances_bin_path_items = "\n".join(
        f"{' ' * 8}\"{element_instances_bin_path}\","
        for element_instances_bin_path
        in element_instances_bin_paths
    )

    primitive_instances_bin_paths_items = "\n".join(
        f"{' ' * 8}{{" + ", ".join(
            f"\"{bin_path}\""
            for bin_path
            in primitive_instance_bin_paths
        ) + "},"
        for primitive_instance_bin_paths
        in primitive_instances_bin_paths
    )

    primitive_instances_handle_indices_items = "\n".join(
        f"{' ' * 8}{{" + ", ".join(
            str(index)
            for index
            in primitive_instance_handle_indices
        ) + "},"
        for primitive_instance_handle_indices
        in primitive_instances_handle_indices
    )

    curve_bin_paths_items = "\n".join(
        f"{' ' * 8}{{" + ", ".join(
            f"\"{record.bin_path}\""
            for record
            in curve_records
        ) + "},"
        for curve_records
        in curve_records_by_element_instance
    )

    curve_mtl_indices_items = "\n".join(
        f"{' ' * 8}{{" + ", ".join(
            f"{sbt_manager.get_mtl_index_for_curve(element_name, record.assignment_name)}"
            for record
            in curve_records
        ) + "},"
        for curve_records
        in curve_records_by_element_instance
    )

    split_instances_item = ""
    if should_split_primitive_instances:
        split_instances_item = f"{' ' * 4}m_shouldSplitPrimitiveInstances = true;"

    return f"""\
{class_name}::{class_name}()
{{
    const std::string moanaRoot = MOANA_ROOT;

    m_elementName = "{element_name}";

    m_mtlLookup = {{
{mtl_lookup_items}
    }};

    m_materialOffset = {material_offset};

    m_baseObjs = {{
{base_obj_items}
    }};

    m_objArchivePaths = {{
{obj_archives_items}
    }};

    m_elementInstancesBinPaths = {{
{element_instances_bin_path_items}
    }};

    m_primitiveInstancesBinPaths = {{
{primitive_instances_bin_paths_items}
    }};

    m_primitiveInstancesHandleIndices = {{
{primitive_instances_handle_indices_items}
    }};

    m_curveBinPathsByElementInstance = {{
{curve_bin_paths_items}
    }};

    m_curveMtlIndicesByElementInstance = {{
{curve_mtl_indices_items}
    }};

{split_instances_item}
}}
"""

def generate_sbt_array(sbt_manager):
    colors_annotated = sbt_manager.get_base_colors_annotated()
    color_items = "\n".join(
        f"{' '*4}float3{{ {c[0]}, {c[1]}, {c[2]} }}, // {comment} [{i}]"
        for i, (c, comment) in enumerate(colors_annotated)
    )

    return f"""\
std::vector<float3> baseColors = {{
{color_items}
}};
"""

def generate_bsdf_types_array(sbt_manager):
    bsdf_types_annotated = sbt_manager.get_bsdf_types_annotated()
    bsdf_type_items = "\n".join(
        f"{' '*4}{t}, // {comment} [{i}]"
        for i, (t, comment) in enumerate(bsdf_types_annotated)
    )

    return f"""\
std::vector<BSDFType> bsdfTypes = {{
{bsdf_type_items}
}};
"""

def generate_texture_filenames_data(ptx_files):
    texture_filenames = "\n".join(
        f"X(\"{ptx}\") // [{i}]"
        for i, ptx in enumerate(ptx_files)
    )

    return texture_filenames
