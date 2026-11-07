# Build

Run the PyInstaller build for Sona.

Steps:
1. Ensure the virtual environment is active
2. Run `./build.sh`
3. Report the build result
4. If the build fails, analyze the error output and suggest fixes

The build produces a macOS app bundle at `./dist/Sona/`. It bundles ffmpeg and whisper assets, and codesigns the executable.

$ARGUMENTS
