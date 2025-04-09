package com.example.flutter_yt_dlp;

import android.os.Bundle;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import io.flutter.app.FlutterActivity;
import io.flutter.plugin.common.MethodCall;
import io.flutter.plugin.common.MethodChannel;

public class MainActivity extends FlutterActivity {
    private static final String CHANNEL = "yt_dlp_channel";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        new MethodChannel(getFlutterView(), CHANNEL).setMethodCallHandler(
            new MethodChannel.MethodCallHandler() {
                @Override
                public void onMethodCall(MethodCall call, MethodChannel.Result result) {
                    Python py = Python.getInstance();
                    PyObject module = py.getModule("yt_dlp_helper");

                    if (call.method.equals("getVideoInfo")) {
                        String url = call.argument("url");
                        String info = module.callAttr("get_video_info", url).toString();
                        result.success(info);
                    } else if (call.method.equals("downloadFormat")) {
                        String url = call.argument("url");
                        String formatId = call.argument("formatId");
                        String outputPath = call.argument("outputPath");
                        boolean overwrite = call.argument("overwrite");
                        ProgressCallback progressCallback = new ProgressCallback(result);
                        module.callAttr("download_format", url, formatId, outputPath, overwrite, progressCallback);
                    } else {
                        result.notImplemented();
                    }
                }
            });
    }

    private static class ProgressCallback {
        private final MethodChannel.Result result;

        ProgressCallback(MethodChannel.Result result) {
            this.result = result;
        }

        public void onProgress(long downloaded, long total) {
            result.success(new long[]{downloaded, total});
        }
    }
}