from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.database import crud
from backend.models.schemas import RevisionComparisonResponse, ComponentBase, InterfaceBase


class ComparisonService:
    def compare_revisions(self, db: Session, doc_v1_id: int, doc_v2_id: int) -> RevisionComparisonResponse:
        """
        Compare two HLD document revisions and generate architectural diff:
        - Added / Removed / Modified Components
        - Added / Removed / Modified Interfaces
        - Potential Inconsistencies & Breaking Changes
        """
        doc_v1 = crud.get_document_by_id(db, doc_v1_id)
        doc_v2 = crud.get_document_by_id(db, doc_v2_id)

        if not doc_v1 or not doc_v2:
            raise ValueError("One or both document IDs are invalid.")

        v1_comps = {c.name: c for c in crud.get_components_by_document(db, doc_v1_id)}
        v2_comps = {c.name: c for c in crud.get_components_by_document(db, doc_v2_id)}

        v1_ifaces = {(i.name, i.source, i.target): i for i in crud.get_interfaces_by_document(db, doc_v1_id)}
        v2_ifaces = {(i.name, i.source, i.target): i for i in crud.get_interfaces_by_document(db, doc_v2_id)}

        # 1. Compare Components
        added_comp_names = set(v2_comps.keys()) - set(v1_comps.keys())
        removed_comp_names = set(v1_comps.keys()) - set(v2_comps.keys())
        common_comp_names = set(v1_comps.keys()) & set(v2_comps.keys())

        added_components = [
            ComponentBase(
                name=v2_comps[n].name,
                type=v2_comps[n].type,
                description=v2_comps[n].description,
                page=v2_comps[n].page,
                ports_in=v2_comps[n].ports_in or [],
                ports_out=v2_comps[n].ports_out or [],
                asil_level=v2_comps[n].asil_level or "ASIL-B"
            ) for n in added_comp_names
        ]

        removed_components = [
            ComponentBase(
                name=v1_comps[n].name,
                type=v1_comps[n].type,
                description=v1_comps[n].description,
                page=v1_comps[n].page,
                ports_in=v1_comps[n].ports_in or [],
                ports_out=v1_comps[n].ports_out or [],
                asil_level=v1_comps[n].asil_level or "ASIL-B"
            ) for n in removed_comp_names
        ]

        modified_components = []
        for name in common_comp_names:
            c1 = v1_comps[name]
            c2 = v2_comps[name]
            diffs = []
            if c1.asil_level != c2.asil_level:
                diffs.append(f"ASIL changed: {c1.asil_level} -> {c2.asil_level}")
            if c1.type != c2.type:
                diffs.append(f"Type changed: {c1.type} -> {c2.type}")
            if len(c1.ports_out or []) != len(c2.ports_out or []):
                diffs.append(f"Output ports modified: {len(c1.ports_out or [])} -> {len(c2.ports_out or [])}")

            if diffs:
                modified_components.append({
                    "name": name,
                    "changes": diffs,
                    "v1_page": c1.page,
                    "v2_page": c2.page
                })

        # 2. Compare Interfaces
        added_iface_keys = set(v2_ifaces.keys()) - set(v1_ifaces.keys())
        removed_iface_keys = set(v1_ifaces.keys()) - set(v2_ifaces.keys())
        common_iface_keys = set(v1_ifaces.keys()) & set(v2_ifaces.keys())

        added_interfaces = [
            InterfaceBase(
                name=v2_ifaces[k].name,
                source=v2_ifaces[k].source,
                target=v2_ifaces[k].target,
                description=v2_ifaces[k].description,
                page=v2_ifaces[k].page,
                interface_type=v2_ifaces[k].interface_type,
                signals=v2_ifaces[k].signals or []
            ) for k in added_iface_keys
        ]

        removed_interfaces = [
            InterfaceBase(
                name=v1_ifaces[k].name,
                source=v1_ifaces[k].source,
                target=v1_ifaces[k].target,
                description=v1_ifaces[k].description,
                page=v1_ifaces[k].page,
                interface_type=v1_ifaces[k].interface_type,
                signals=v1_ifaces[k].signals or []
            ) for k in removed_iface_keys
        ]

        modified_interfaces = []
        for k in common_iface_keys:
            i1 = v1_ifaces[k]
            i2 = v2_ifaces[k]
            diffs = []
            if i1.interface_type != i2.interface_type:
                diffs.append(f"Interface type changed: {i1.interface_type} -> {i2.interface_type}")
            if len(i1.signals or []) != len(i2.signals or []):
                diffs.append(f"Signals payload changed: {len(i1.signals or [])} -> {len(i2.signals or [])}")
            if diffs:
                modified_interfaces.append({
                    "name": i1.name,
                    "source": i1.source,
                    "target": i1.target,
                    "changes": diffs
                })

        # 3. Detect Inconsistencies & Breaking Changes
        inconsistencies = []
        for rem_comp in removed_components:
            # Check if any new/existing interface still attempts to route to removed component
            for ifc in added_interfaces:
                if ifc.target == rem_comp.name:
                    inconsistencies.append({
                        "type": "Broken Link / Dangling Interface",
                        "severity": "High",
                        "description": f"Interface '{ifc.name}' targets '{rem_comp.name}' which was removed in {doc_v2.name}.",
                        "action": "Remove invalid interface or restore component."
                    })

        for mod_comp in modified_components:
            for chg in mod_comp["changes"]:
                if "ASIL changed" in chg:
                    inconsistencies.append({
                        "type": "Safety ASIL Alteration",
                        "severity": "Medium",
                        "description": f"Component '{mod_comp['name']}' had safety integrity level change ({chg}). Verify impact with HARA & ISO 26262.",
                        "action": "Execute Safety Analysis review."
                    })

        summary = (
            f"Revision comparison between **{doc_v1.name} (v{doc_v1.version})** and **{doc_v2.name} (v{doc_v2.version})** identified: "
            f"**+{len(added_components)}** added components, **-{len(removed_components)}** removed components, "
            f"**~{len(modified_components)}** modified components, **+{len(added_interfaces)}** added interfaces, "
            f"and **{len(inconsistencies)}** architectural inconsistencies/risks."
        )

        crud.create_audit_log(
            db=db,
            user="Automotive Lead",
            action="Revision Comparison",
            document=f"{doc_v1.name} vs {doc_v2.name}",
            result=f"Found {len(added_components)} additions, {len(removed_components)} removals, {len(inconsistencies)} risks.",
            details=summary
        )

        return RevisionComparisonResponse(
            doc_v1_name=doc_v1.name,
            doc_v1_version=doc_v1.version,
            doc_v2_name=doc_v2.name,
            doc_v2_version=doc_v2.version,
            added_components=added_components,
            removed_components=removed_components,
            modified_components=modified_components,
            added_interfaces=added_interfaces,
            removed_interfaces=removed_interfaces,
            modified_interfaces=modified_interfaces,
            inconsistencies=inconsistencies,
            summary=summary
        )


comparison_service = ComparisonService()
