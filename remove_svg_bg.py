#!/usr/bin/env python3
"""
Remove large background rectangles and make an SVG transparent.
Usage:
    python remove_svg_bg.py input.svg output.svg
    python remove_svg_bg.py *.svg   # batch mode (saves as *_transparent.svg)
"""

import sys, re, xml.etree.ElementTree as ET, os

def parse_float(x):
    try:
        return float(re.sub(r"[^\d.\-eE]", "", str(x)))
    except:
        return None

def is_near_canvas_rect(elem, canvas_w, canvas_h):
    """Detects a rectangle that is likely a full background"""
    if elem.tag.split("}")[-1] != "rect":
        return False

    x = parse_float(elem.attrib.get("x", 0))
    y = parse_float(elem.attrib.get("y", 0))
    w = parse_float(elem.attrib.get("width", None))
    h = parse_float(elem.attrib.get("height", None))
    style = elem.attrib.get("style", "")
    
    # Ignore if explicitly fill:none
    if "fill:none" in style.replace(" ", "").lower():
        return False
    if w is None or h is None:
        return False

    near_origin = (abs(x or 0) <= 2) and (abs(y or 0) <= 2)

    if canvas_w and canvas_h:
        near_canvas = (w >= 0.95 * canvas_w) and (h >= 0.95 * canvas_h)
    else:
        near_canvas = (w > 500 and h > 300)  # fallback

    return near_origin and near_canvas

def clean_svg(in_path, out_path):
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    tree = ET.ElementTree(ET.fromstring(open(in_path, "r", encoding="utf-8").read()))
    root = tree.getroot()

    # Get canvas size
    canvas_w = parse_float(root.attrib.get("width"))
    canvas_h = parse_float(root.attrib.get("height"))
    if (canvas_w is None or canvas_h is None) and root.attrib.get("viewBox"):
        parts = [parse_float(p) for p in root.attrib["viewBox"].replace(",", " ").split()]
        if len(parts) == 4:
            _, _, canvas_w, canvas_h = parts

    # Remove large background rects
    removed = 0
    for parent in list(tree.iter()):
        for child in list(parent):
            if is_near_canvas_rect(child, canvas_w, canvas_h):
                parent.remove(child)
                removed += 1

    # Remove background styles from root
    if "style" in root.attrib:
        style = root.attrib["style"]
        style = re.sub(r"background(?:-color)?\s*:\s*[^;]+;?", "", style, flags=re.I)
        style = re.sub(r"(^|;)\s*fill\s*:\s*[^;]+;?", r"\1", style, flags=re.I)
        style = re.sub(r";{2,}", ";", style).strip().strip(";")
        root.attrib["style"] = style

    for attr in list(root.attrib):
        if attr.lower() in ("background", "background-color"):
            del root.attrib[attr]

    # Force transparent background
    from xml.etree.ElementTree import SubElement
    defs = root.find(".//{http://www.w3.org/2000/svg}defs")
    if defs is None:
        defs = SubElement(root, "{http://www.w3.org/2000/svg}defs")
    style_el = SubElement(defs, "{http://www.w3.org/2000/svg}style")
    style_el.text = "svg{background:none !important;}"

    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    return removed

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python remove_svg_bg.py input.svg [output.svg]")
        sys.exit(1)

    if len(sys.argv) == 2 and "*" in sys.argv[1]:
        # Batch mode using shell glob expansion
        for in_path in sys.argv[1:]:
            if not in_path.lower().endswith(".svg"):
                continue
            out_path = in_path.rsplit(".", 1)[0] + "_transparent.svg"
            removed = clean_svg(in_path, out_path)
            print(f"[OK] {in_path} → {out_path} (removed {removed} background rects)")
    elif len(sys.argv) == 2:
        in_path = sys.argv[1]
        out_path = in_path.rsplit(".", 1)[0] + "_transparent.svg"
        removed = clean_svg(in_path, out_path)
        print(f"[OK] {in_path} → {out_path} (removed {removed} background rects)")
    else:
        in_path, out_path = sys.argv[1], sys.argv[2]
        removed = clean_svg(in_path, out_path)
        print(f"[OK] {in_path} → {out_path} (removed {removed} background rects)")

