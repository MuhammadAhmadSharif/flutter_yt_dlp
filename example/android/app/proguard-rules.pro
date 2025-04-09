# Keep Flutter plugin classes
-keep class com.example.flutter_yt_dlp.FlutterYtDlpPlugin { *; }
-keep class * implements io.flutter.plugin.common.PluginRegistry.PluginRegistrantCallback { *; }
-dontwarn com.example.flutter_yt_dlp.**

# Keep Google Play Core classes for deferred components
-keep class com.google.android.play.core.splitcompat.** { *; }
-keep class com.google.android.play.core.splitinstall.** { *; }
-keep class com.google.android.play.core.tasks.** { *; }
-dontwarn com.google.android.play.core.**

# Keep Java beans (for Jackson/Flutter internals)
-keep class java.beans.** { *; }
-dontwarn java.beans.**

# Keep javax.lang.model (for error-prone annotations)
-keep class javax.lang.model.element.** { *; }
-dontwarn javax.lang.model.element.**

# Keep Process and I/O for yt-dlp execution
-keep class java.lang.Process { *; }
-keep class java.io.** { *; }