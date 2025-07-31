# PDF Combiner Pro - Assets

This directory contains application assets like icons used for building executables.

## Icons

- `icon.ico` - Windows icon file (256x256 or multiple sizes)
- `icon.icns` - macOS icon file (multiple resolutions)

## Creating Icons

### For macOS (.icns):
1. Create a 1024x1024 PNG image
2. Use the following command to convert:
   ```bash
   mkdir icon.iconset
   sips -z 16 16 icon_1024.png --out icon.iconset/icon_16x16.png
   sips -z 32 32 icon_1024.png --out icon.iconset/icon_16x16@2x.png
   sips -z 32 32 icon_1024.png --out icon.iconset/icon_32x32.png
   sips -z 64 64 icon_1024.png --out icon.iconset/icon_32x32@2x.png
   sips -z 128 128 icon_1024.png --out icon.iconset/icon_128x128.png
   sips -z 256 256 icon_1024.png --out icon.iconset/icon_128x128@2x.png
   sips -z 256 256 icon_1024.png --out icon.iconset/icon_256x256.png
   sips -z 512 512 icon_1024.png --out icon.iconset/icon_256x256@2x.png
   sips -z 512 512 icon_1024.png --out icon.iconset/icon_512x512.png
   sips -z 1024 1024 icon_1024.png --out icon.iconset/icon_512x512@2x.png
   iconutil -c icns icon.iconset
   ```

### For Windows (.ico):
Use an online converter or tools like GIMP to convert PNG to ICO format.

## Note

If you don't have custom icons, the build process will use default system icons.
