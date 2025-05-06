# Keep Flutter YT-DLP package classes
-keep class com.example.flutter_yt_dlp.** { *; }

# Specifically keep the onProgress method for callbacks
-keepclassmembers class * {
    void onProgress(long, long);
}

# Keep Python-related classes
-keep class com.chaquo.python.** { *; }