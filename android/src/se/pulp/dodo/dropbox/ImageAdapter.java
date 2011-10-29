package se.pulp.dodo.dropbox;

import android.content.Context;
import android.util.DisplayMetrics;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.GridView;
import android.widget.ImageView;

import com.dropbox.client2.DropboxAPI;

public class ImageAdapter extends BaseAdapter {
    
	private Context context;
    private Thumbnails thumbnails;
    
    private int displayWidth;
    private int preferredSize;
    
    public ImageAdapter(Context c, DropboxAPI dropbox, String path, GridView view) {
        context = c;
        
        thumbnails = new Thumbnails(context, dropbox, path, view);
        thumbnails.execute();
        
        DisplayMetrics displayMetrics = context.getApplicationContext().getResources().getDisplayMetrics();
        displayWidth = displayMetrics.widthPixels;
        
        // preferredSize assumes 3 columns and a padding of 4px
        preferredSize = (displayWidth / 3) - 8;
    }

    public int getCount() {
        return thumbnails.getDrawables().size();
    }

    public Object getItem(int position) {
        return null;
    }

    public long getItemId(int position) {
        return 0;
    }

    public View getView(int position, View convertView, ViewGroup parent) {
    	ImageView imageView;
        if (convertView == null) {
            imageView = new ImageView(context);
            imageView.setLayoutParams(new GridView.LayoutParams(preferredSize, preferredSize));

            imageView.setScaleType(ImageView.ScaleType.CENTER_CROP);
            imageView.setPadding(4, 4, 4, 4);
            
        } else {
            imageView = (ImageView) convertView;
        }

        imageView.setImageDrawable(thumbnails.getDrawables().get(position));
        return imageView;
    }

}