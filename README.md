# remove_svg_bg.py

A standalone Python script to remove large background rectangles in SVG files and make the background transparent. Supports single files and batch mode.

## Features

- Detects and removes background rectangles covering the canvas.
- Cleans background-color and fill styles from the SVG root.
- Inserts CSS to force transparent backgrounds.
- Works on individual files or multiple files in batch mode.

## Usage

### 1. Save the script

Save `remove_svg_bg.py` to your computer.

### 2. Run on a single SVG file

```bash
python remove_svg_bg.py myfile.svg
```

- This will create `myfile_transparent.svg` with the background removed.

### 3. Batch mode (multiple SVGs)

```bash
python remove_svg_bg.py *.svg
```

- This will create a new file for each input, named `*_transparent.svg`.

### 4. Custom output filename

```bash
python remove_svg_bg.py input.svg output.svg
```

## Example

```bash
python remove_svg_bg.py logo.svg
# [OK] logo.svg → logo_transparent.svg (removed 1 background rects)
```

## Requirements

- Python 3

## How it works

- Scans for `<rect>` elements matching the SVG canvas size (likely backgrounds).
- Removes those rectangles if found.
- Cleans up any background style attributes.
- Adds CSS to the SVG for full transparency.

## License

MIT License

## Author

Shima Mahmoudi
