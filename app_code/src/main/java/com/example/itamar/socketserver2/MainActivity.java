package com.example.itamar.socketserver2;

import android.content.res.Resources;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.drawable.BitmapDrawable;
import android.speech.tts.TextToSpeech;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.util.LongSparseArray;
import android.widget.ImageView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {

    private TextToSpeech tts;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        tts = new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                tts.setLanguage(Locale.US);
            }
        });
        new SocketServerThread().start();

    }


    private class SocketServerThread extends Thread {

        static final int SocketServerPORT = 8888;

        @Override
        public void run() {
            try {
                final ImageView iv = (ImageView) findViewById(R.id.imgview);
                ServerSocket serverSocket;
                runOnUiThread(new Runnable() {

                    @Override
                    public void run() {

                    }
                });
                Log.i("TAG","binding for port:" + SocketServerPORT );

                serverSocket = new ServerSocket(); // <-- create an unbound socket first
                serverSocket.setReuseAddress(true);
                serverSocket.bind(new InetSocketAddress(SocketServerPORT)); // <-- now bind it

                Log.i("TAG","listening for client" );

                Socket socket = serverSocket.accept();
                Log.i("TAG","connected with client" + socket);
                PrintWriter out = new PrintWriter(socket.getOutputStream());
                BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));

                while(true){

                    String msg = "";
                    //wait for something to be in buffer
                    while(!in.ready()){

                    }
                    while(in.ready()){
                        int c = in.read();

                        msg += (char)c;

                    }

                    if(msg.startsWith("detections:")){
                        Log.i("TAG","got detection data:" + msg.substring("detections:".length()));

                        //TODO: process detection data
                        processDetection(msg.substring("detection:".length()));

                    }else {
                        Log.i("TAG","got image data");

                        byte[] imgBytes = null;
                        try {
                            imgBytes = Base64.decode(msg.getBytes(), Base64.DEFAULT);
                        } catch (IllegalArgumentException e) {
                            out.write("BAD");
                            out.flush();
                            continue;
                        }
                        final Bitmap bitmap = BitmapFactory.decodeByteArray(imgBytes, 0, imgBytes.length);
                        if (bitmap == null) {
                            out.write("BAD");
                            out.flush();
                            continue;
                        }
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                iv.setImageBitmap(bitmap);
                            }
                        });
                        //  Log.i("TAG","total read length:" + msg.length());
                    }
                    out.write("OK");
                    out.flush();
                    // break;
                }

            } catch (SocketException e1) {
                e1.printStackTrace();
            } catch (IOException e1) {
                e1.printStackTrace();
            }

        }

    }

    private void processDetection(String detectionJsonStr) {
//        //TODO: for DBG
//        Bitmap bmp = getCurrentFrameBmp();
//        makeDangerAlert(bmp, "car", "person");
//        setCurrentFrameBmp(bmp);

        try {
            Bitmap currentFrame = getCurrentFrameBmp();

            JSONArray detectJson = new JSONObject(detectionJsonStr).getJSONArray("arr"); //0->Danger, 1->Bounding rects
            //process bounding rects
            JSONArray rectsJson = detectJson.getJSONArray(1);
            for(int i = 0; i < rectsJson.length(); i++){
                JSONArray rectJson = rectsJson.getJSONArray(i);
                int left = Integer.valueOf(rectJson.getString(2));
                int top = Integer.valueOf(rectJson.getString(3));
                int right = Integer.valueOf(rectJson.getString(4));
                int bottom = Integer.valueOf(rectJson.getString(5));
                drawRect(currentFrame, left, top, right, bottom);
            }

            //process danger warning
            JSONArray dangerJson = detectJson.getJSONArray(0);
            boolean isDanger = dangerJson.getString(0).equals("True");
            if(isDanger){ // danger detected
                String obj1 = dangerJson.getString(1);
                String obj2 = dangerJson.getString(2);
                makeDangerAlert(currentFrame, obj1, obj2);
            }
            setCurrentFrameBmp(currentFrame);

        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    private void makeDangerAlert(Bitmap frame, String obj1, String obj2) {
        // Draw 'DANGER" string on frame
        final String TEXT = "DANGER";
        Resources resources = getApplicationContext().getResources();
        float scale = resources.getDisplayMetrics().density;

        android.graphics.Bitmap.Config bitmapConfig =
                frame.getConfig();
        // set default bitmap config if none
        if(bitmapConfig == null) {
            bitmapConfig = android.graphics.Bitmap.Config.ARGB_8888;
        }

        Canvas canvas = new Canvas(frame);
        // new antialised Paint
        Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        // text color - #3D3D3D
        paint.setColor(Color.rgb(61, 61, 61));
        // text size in pixels
        paint.setTextSize((int) (14 * scale));
        // text shadow
        paint.setShadowLayer(1f, 0f, 1f, Color.WHITE);

        // draw text to the Canvas center
        Rect bounds = new Rect();
        paint.getTextBounds(TEXT, 0, TEXT.length(), bounds);
        int x = (frame.getWidth() - bounds.width())/2;
        int y = (frame.getHeight() + bounds.height())/2;

        canvas.drawText(TEXT, x, y, paint);

        // describe the danger vocally using text to speech
        final String DANGER_TEXT = "DANGER: Collision between " + obj1 + " and " + obj2;
        this.speak(DANGER_TEXT);

    }

    private void drawRect(Bitmap currentFrame, int left, int top, int right, int bottom) {
        final int RECT_WIDTH = 3;
        final int RECT_COLOR = Color.RED;

        for(int row = top; row <= bottom; row++){
            for(int i = -RECT_WIDTH/2; i <= RECT_WIDTH/2 + 1; i++){
                currentFrame.setPixel(left + i, row, RECT_COLOR);
                currentFrame.setPixel(right + i, row, RECT_COLOR);
            }
        }
        for(int col = left; col <= right; col++){
            for(int i = -RECT_WIDTH/2; i <= RECT_WIDTH/2 + 1; i++) {
                currentFrame.setPixel(col, top + i, RECT_COLOR);
                currentFrame.setPixel(col, bottom + i, RECT_COLOR);
            }
        }
    }

    private void speak(final String text){
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null);
    }

    private Bitmap getCurrentFrameBmp() {
        final ImageView iv = (ImageView) findViewById(R.id.imgview);

        Bitmap bmp = ((BitmapDrawable)iv.getDrawable() == null ? null : ((BitmapDrawable)iv.getDrawable()).getBitmap());
        android.graphics.Bitmap.Config bitmapConfig =
                bmp.getConfig();
        // set default bitmap config if none
        if(bitmapConfig == null) {
            bitmapConfig = android.graphics.Bitmap.Config.ARGB_8888;
        }
        return bmp.copy(bitmapConfig, true);
    }

    private void setCurrentFrameBmp(final Bitmap bmp){
        final ImageView iv = (ImageView) findViewById(R.id.imgview);
        if(iv != null){
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    iv.setImageBitmap(bmp);

                }
            });
        }
    }

}


