[app]
# (str) Title of your application
title = AwesomeVHS

# (str) Package name
package.name = awesomevhs

# (str) Package domain (needed for android/ios packaging)
package.domain = org.nxptunx

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 0.1

# (list) Application requirements
# Added numpy and opencv-python for live camera frame manipulation
requirements = python3,kivy,numpy,opencv-python

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (list) Permissions
# Explicitly added CAMERA, RECORD_AUDIO, and Storage permissions
android.permissions = CAMERA, RECORD_AUDIO, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API supported
android.minapi = 24

# (str) Android NDK version
android.ndk = 25b

# (list) List of Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable, 1 = enable)
warn_on_root = 1
