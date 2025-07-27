# PyInstaller Options Explained

## Basic Command Structure
```bash
pyinstaller [options] your_script.py
```

## Essential Options

### Output Control
- `--onefile` - Create single .exe file (vs folder with many files)
- `--onedir` - Create folder with .exe + dependencies (default)
- `--name MyApp` - Name your executable
- `--distpath ./dist` - Where to put the result

### Interface Options
- `--windowed` - GUI app (no console window)
- `--console` - Console app (shows terminal, default)
- `--noconsole` - Same as --windowed

### Including Files
- `--add-data "source;dest"` - Include data files (Windows uses ; Linux uses :)
- `--add-binary "source;dest"` - Include binary files
- `--icon icon.ico` - Add icon to executable

### Performance
- `--upx-dir UPX_DIR` - Compress with UPX
- `--exclude-module MODULE` - Don't include unnecessary modules

### Advanced
- `--hidden-import MODULE` - Force include modules PyInstaller misses
- `--collect-all PACKAGE` - Include entire package
- `--debug` - Add debugging info

## Spec File vs Command Line

### Command Line (Simple)
```bash
pyinstaller --onefile --windowed --name "MyApp" main.py
```

### Spec File (Advanced)
- More control over the build process
- Can include complex file collections
- Reusable configuration
- Better for complex applications

## Your AndyLibrary Example

### Current Spec File Does:
1. **Collects WebPages** - Includes all HTML/CSS/JS files
2. **Hidden Imports** - Ensures FastAPI/Uvicorn work
3. **Excludes** - Removes unused heavy libraries (numpy, torch)
4. **Console Mode** - Shows output for debugging
5. **UPX Compression** - Smaller file size

### GitHub Actions Does:
1. **Windows VM** - Provides Windows environment
2. **Python Setup** - Installs Python 3.11
3. **Dependencies** - Installs from requirements.txt
4. **PyInstaller** - Runs the build
5. **Artifact Upload** - Makes .exe downloadable