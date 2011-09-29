package se.pulp.dodo;

import android.content.Context;
import android.util.DisplayMetrics;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.GridView;
import android.widget.ImageView;

public class ImageAdapter extends BaseAdapter {
    private Context mContext;
    private Thumbnails thumbnails;
    private int displayWidth;
    private int preferredSize;
    
    public ImageAdapter(Context c, Thumbnails t) {
        mContext = c;
        thumbnails = t;
        
        DisplayMetrics displayMetrics = mContext.getApplicationContext().getResources().getDisplayMetrics();
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
            imageView = new ImageView(mContext);
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