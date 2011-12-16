package image.Thumbnails;
import java.io.IOException;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.media.MediaPlayer;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.Window;
import android.widget.ImageView;
import android.widget.TextView;

public class ViewImage extends Activity {
      private String filename;
      private String caption;
      private String audioFileName;
      private String s;
      public MediaPlayer mediaPlay;
      @Override
      public void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            this.requestWindowFeature(Window.FEATURE_NO_TITLE);
            System.gc();
            this.mediaPlay = new MediaPlayer();  
            Intent i = getIntent();
            Bundle extras = i.getExtras();
            BitmapFactory.Options bfo = new BitmapFactory.Options();
            bfo.inSampleSize = 2;
            filename = extras.getString("filename");
            caption = extras.getString("caption");
            audioFileName=extras.getString("audioFileName");
            setContentView(R.layout.image);
            
            
            TextView text = (TextView) findViewById(R.id.imgText);
            ImageView imBack = (ImageView) findViewById(R.id.BackImView);
            ImageView imView = (ImageView) findViewById(R.id.imView);
            text.setText(caption);
            Bitmap bm = BitmapFactory.decodeFile(filename, bfo);
            imView.setImageBitmap(bm);
            
            imBack.setOnClickListener(new OnClickListener() {
    			@Override
    			public void onClick(View arg0) {
    				finish();
    			}
            });
            
            imView.setOnClickListener(new OnClickListener() {
    			@Override
    			public void onClick(View arg0) {
    				playSound(audioFileName);
    			}
            });
            
            
            
            
            
      } 
      
      public void playSound(String audioFile)
      {
      	try {
      		mediaPlay.reset();
  			mediaPlay.setDataSource(audioFile);
  		} catch (IllegalArgumentException e) {
  			// TODO Auto-generated catch block
  			e.printStackTrace();
  		} catch (IllegalStateException e) {
  			// TODO Auto-generated catch block
  			e.printStackTrace();
  		} catch (IOException e) {
  			// TODO Auto-generated catch block
  			e.printStackTrace();
  		}  
      	try {
  			mediaPlay.prepare();
  		} catch (IllegalStateException e) {
  			// TODO Auto-generated catch block
  			e.printStackTrace();
  		} catch (IOException e) {
  			// TODO Auto-generated catch block
  			e.printStackTrace();
  		} 
      	mediaPlay.start(); 
      }
      
}

