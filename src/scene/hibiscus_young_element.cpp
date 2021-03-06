#include "scene/hibiscus_young_element.hpp"

namespace moana {

HibiscusYoungElement::HibiscusYoungElement()
{
    const std::string moanaRoot = MOANA_ROOT;

    m_elementName = "isHibiscusYoung";

    m_mtlLookup = {
        "branches",
        "flowerHibiscus",
        "leafHibiscus",
        "trunk",
    };

    m_materialOffset = 56;

    m_baseObjs = {
        moanaRoot + "/island/obj/isHibiscusYoung/isHibiscusYoung.obj",
    };

    m_objArchivePaths = {
        moanaRoot + "/island/obj/isHibiscus/archives/archiveHibiscusFlower0001_mod.obj",
        moanaRoot + "/island/obj/isHibiscus/archives/archiveHibiscusLeaf0001_mod.obj",
        moanaRoot + "/island/obj/isHibiscus/archives/archiveHibiscusLeaf0002_mod.obj",
        moanaRoot + "/island/obj/isHibiscus/archives/archiveHibiscusLeaf0003_mod.obj",
    };

    m_elementInstancesBinPaths = {
        "../scene/isHibiscusYoung.bin",
    };

    m_primitiveInstancesBinPaths = {
        {"../scene/isHibiscusYoung_xgBonsai--archiveHibiscusLeaf0003_mod.bin", "../scene/isHibiscusYoung_xgBonsai--archiveHibiscusLeaf0002_mod.bin", "../scene/isHibiscusYoung_xgBonsai--archiveHibiscusLeaf0001_mod.bin", "../scene/isHibiscusYoung_xgBonsai--archiveHibiscusFlower0001_mod.bin"},
    };

    m_primitiveInstancesHandleIndices = {
        {3, 2, 1, 0},
    };

    m_curveBinPathsByElementInstance = {
        {},
    };

    m_curveMtlIndicesByElementInstance = {
        {},
    };


}




}
