# -*- coding: utf-8 -*-
import os, sys, json, argparse
import trimesh

def try_import_occ():
    try:
        from OCC.Core import STEPControl, IFSelect, BRepBuilderAPI, BRep, gp
        return True
    except Exception:
        return False

def decimate(m, target_faces):
    if target_faces and m.faces.shape[0] > target_faces:
        try: m = m.simplify_quadratic_decimation(int(target_faces))
        except: pass
    return m

def export_step(mesh_path, out_step, target_faces):
    if not try_import_occ():
        print("[ERR] pythonocc-core нет в окружении", flush=True); return False
    from OCC.Core.BRep import BRep_Builder
    from OCC.Core.TopoDS import TopoDS_Compound
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
    from OCC.Core.gp import gp_Pnt
    from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs

    m = trimesh.load(mesh_path, force='mesh')
    m = decimate(m, target_faces)
    V, F = m.vertices, m.faces

    builder = BRep_Builder()
    comp = TopoDS_Compound(); builder.MakeCompound(comp)
    for tri in F:
        a,b,c = V[tri[0]], V[tri[1]], V[tri[2]]
        poly = BRepBuilderAPI_MakePolygon()
        poly.Add(gp_Pnt(*map(float,a))); poly.Add(gp_Pnt(*map(float,b))); poly.Add(gp_Pnt(*map(float,c))); poly.Close()
        face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()
        builder.Add(comp, face)

    w = STEPControl_Writer(); w.Transfer(comp, STEPControl_AsIs)
    return w.Write(out_step) == 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--target-faces", type=int, default=80000); ap.add_argument("--export-step", action="store_true")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    rep = {"input": a.input, "out": a.out, "target_faces": a.target_faces, "stages": []}
    ok = False
    if a.export_step:
        ok = export_step(a.input, os.path.join(a.out, "reconstructed.step"), a.target_faces)
        rep["stages"].append({"export_step": {"ok": bool(ok)}})
    json.dump(rep, open(os.path.join(a.out, "report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    sys.exit(0 if ok else 1)

if __name__ == "__main__": main()
