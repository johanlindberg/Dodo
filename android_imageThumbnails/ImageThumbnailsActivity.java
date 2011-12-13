package image.Thumbnails;


import java.io.File;
import java.io.IOException;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.res.Configuration;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.media.MediaPlayer;
import android.os.Bundle;
import android.provider.MediaStore;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.BaseAdapter;
import android.widget.GridView;
import android.widget.ImageView;


public class ImageThumbnailsActivity extends Activity
{
	
    private int count;
    /**
     * Caching this is a trade off in memory versus performance.
     * We deliberated use the smallest thumbnails so the size of each should be small (92x92x1 byte = about 10kb each)
     * but can be significant if there are thousands of images on the device.
     */
    public MediaStructure mediaStructure;
    public MediaStructure activeStructure;
    public MediaData[] windows;
    public ImageAdapter ia;
    public MediaPlayer mediaPlay;
    
    
    
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        init_phone_image_grid();
    }
    @Override public void onConfigurationChanged(Configuration newConfig)
    {   
    	super.onConfigurationChanged(newConfig); 
    	this.ia.notifyDataSetChanged();
    	setContentView(R.layout.main); 
    } 
    
    
    @Override
    public void onBackPressed() {
    	if (activeStructure.parentStructure != null)
    	{
    		activeStructure=activeStructure.parentStructure;
    		this.windows=activeStructure.media;
    		this.count=windows.length; 
    		this.ia.notifyDataSetChanged();
    	}
    }


    private void init_phone_image_grid()
    {
        
    	this.mediaStructure = new MediaStructure("/mnt/sdcard/Images/");
        activeStructure = mediaStructure;
        this.count=this.mediaStructure.media.length;
        this.windows=this.mediaStructure.media;
        this.mediaPlay = new MediaPlayer();  
        GridView imagegrid = (GridView) findViewById(R.id.PhoneImageGrid);
        this.ia = new ImageAdapter(getApplicationContext());
        imagegrid.setAdapter(ia);
        imagegrid.setOnItemClickListener(new OnItemClickListener() {
            public void onItemClick(@SuppressWarnings("rawtypes") AdapterView parent, View v, int position, long id)
            {
            	if (windows[position].isDir)
            	{
            		if (windows[position].isSound) playSound(windows[position].audioFilename);
            		int dirIndex=activeStructure.media[position].dirIndex;
            		activeStructure=activeStructure.subStructure[dirIndex];
            		windows=activeStructure.media;
            		count=windows.length;
            		ia.notifyDataSetChanged();            		            		
            	}
            	else 
            	{
            		//Show single image
            		if (activeStructure.media[position].isSound) playSound(windows[position].audioFilename);
            		final Intent intent = new Intent(ImageThumbnailsActivity.this, ViewImage.class);
                	intent.putExtra("filename", windows[position].filename);
                    startActivity(intent);
            	}
            }
        });
        //imageCursor.close();
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
    
    public class MediaData
    {
    	public String filename;
    	public Bitmap image;
    	public boolean isDir;
    	public boolean isSound;
    	public int dirIndex;
    	public String audioFilename;
    	public MediaData (String fname,Bitmap img, boolean isDirectory, int index, String audioFname)
    	{
    		
    		dirIndex=index;
    		image=img;
    		filename=fname;
    		isDir=isDirectory;
    		isSound = (audioFname.length()>0);
    		audioFilename=audioFname;    			
    	}
    }
    
    
    public class MediaStructure
    {
    	public MediaStructure[] subStructure;
    	private MediaData[] media;
    	
    	private int nrOfImages;
    	private int nrOfDirs;
    	public MediaStructure parentStructure;
    	private String path;
    	private int[] idArray;
    	public MediaStructure(String dirPath)
    	{
    		final String[] columns = { MediaStore.Images.Media._ID , MediaStore.Images.Media.DATA };
            final String orderBy = MediaStore.Images.Media.DATA;
            this.path=dirPath;
            String tempPath= "%" + path + "%"; 	
            String [] queryPath = {tempPath};
            Cursor imageCursor = managedQuery(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, columns,MediaStore.Images.Media.DATA + " like ? ", queryPath,orderBy);
            
            final String[] columnsAudio = { MediaStore.Audio.Media._ID , MediaStore.Audio.Media.DATA };
            Cursor audioCursor = getContentResolver().query(MediaStore.Audio.Media.EXTERNAL_CONTENT_URI, columnsAudio, MediaStore.Images.Media.DATA + " like ? ",queryPath, MediaStore.Audio.Media._ID);
            audioCursor.moveToFirst();
            int dataColIndexAudio = -1;
            if (audioCursor.getCount() > 0)
            {
            	dataColIndexAudio = audioCursor.getColumnIndex(MediaStore.Audio.Media.DATA);
            
            	String audioName= audioCursor.getString(dataColIndexAudio);
            }
            
            
            int dataColIndex = imageCursor.getColumnIndex(MediaStore.Images.Media.DATA);
            int image_column_index = imageCursor.getColumnIndex(MediaStore.Images.Media._ID);
            this.nrOfImages = getNrOfImages(imageCursor, this.path, dataColIndex);
            idArray=new int[this.nrOfImages];
            
            // Create array idArray with index for images located in path folder.
            
            int k=0;
            for(int i=0;i<imageCursor.getCount();i++) 
            {
            	
            	imageCursor.moveToPosition(i);
        		String s2 = stripFileExtension(imageCursor.getString(dataColIndex));
        		if (path.lastIndexOf("/") == s2.lastIndexOf("/"))
        		{
        					idArray[k]=i;
                          	k++;
        		}
            }
            
            
            
            // Build an array of MediaData getting data from cursor at indexes in idArray 
            media = new MediaData [this.nrOfImages];
            nrOfDirs = 0;
            for(int j=0;j<(this.nrOfImages);j++)        		
            {
                imageCursor.moveToPosition(idArray[j]);
                Bitmap img = MediaStore.Images.Thumbnails.getThumbnail(getApplicationContext().getContentResolver(),imageCursor.getInt(image_column_index), MediaStore.Images.Thumbnails.MICRO_KIND, null);
                String filename= imageCursor.getString(dataColIndex);
                File dir = new File (stripFileExtension(filename));
                boolean isDir = (dir.isDirectory());
                if (isDir) 
                {
                	nrOfDirs++;                	
                }
                if (audioCursor.getCount() > 0)
                {
                media[j]=new MediaData(filename,img,isDir,nrOfDirs-1,getAudioFilename(audioCursor,filename,dataColIndexAudio));
                }
                else
                {
                	media[j]=new MediaData(filename,img,isDir,nrOfDirs-1,"");
                }
                	
            }
            
            // If any of the images has a dir, do recursive call to create mediastructure for this
            subStructure = new MediaStructure[nrOfDirs];
    		int i = 0;
            for(int l=0;l<(this.nrOfImages);l++)
            {
            	if (media[l].isDir)
            	{
            		String path_= stripFileExtension(media[l].filename);
            		path_ = path_ + "/";
            		subStructure[i]=new MediaStructure(path_);
            		subStructure[i].parentStructure=this;
            		i++;
            	}
            }
    		            	
    	}    	
    
    }
    
    
    public static String stripFileExtension(String fileName)
    {
        int dotInd = fileName.lastIndexOf('.');

        // if dot is in the first position,
        // we are dealing with a hidden file rather than an extension
        return (dotInd > 0) ? fileName.substring(0, dotInd) : fileName;
    }
    
    
    public int getNrOfImages(Cursor imageCursor, String path, int dataColIndex)
    {
    	String[] s3= new String[imageCursor.getCount()];
    	int picsInDir = 0;
    	for(int j=0;j<(imageCursor.getCount());j++)
            
    	{
    	
    		imageCursor.moveToPosition(j);
    		//if (path.lastIndexOf("/") != stripFileExtension(imageCursor.getString(dataColIndex)).lastIndexOf("/"))
    		String s2 = stripFileExtension(imageCursor.getString(dataColIndex));
    		s3[j]=s2;
    		
    		if (path.lastIndexOf("/") == stripFileExtension(imageCursor.getString(dataColIndex)).lastIndexOf("/"))
            	
    		{
        		picsInDir++;
        	}
            
        }
    	return picsInDir;
    }
    
    
   
    public String getAudioFilename(Cursor audioCursor, String filename, int dataColIndexAudio)
    {
    	//String [] s5 = new String [audioCursor.getCount()];
    	//String s6;
    	//String s7;
    	if (audioCursor.getCount()==0) return "";
    	for(int j=0;j<(audioCursor.getCount());j++)
    	{
    		audioCursor.moveToPosition(j);
			String s2 = stripFileExtension(audioCursor.getString(dataColIndexAudio));
			//s5[j]=s2;
			//s6=stripFileExtension(filename);
			//s7=stripFileExtension(audioCursor.getString(dataColIndexAudio));
			if (stripFileExtension(filename).equalsIgnoreCase(stripFileExtension(audioCursor.getString(dataColIndexAudio))))
			{
				return audioCursor.getString(dataColIndexAudio);
			}
    	}
    	return "";    		
    }
    
    
    
    
    
    public class ImageAdapter extends BaseAdapter
    {
        private Context mContext;

        public ImageAdapter(Context c)
        {
            mContext = c;
        }

        @Override
        public int getCount()
        {
            return count;
        }

        @Override
        public Object getItem(int position)
        {
            return position;
        }

        @Override
        public long getItemId(int position)
        {
            return position;
        }
        

        @Override
        public View getView(int position, View convertView, ViewGroup parent)
        {
            ImageView i = (ImageView)convertView;
            if(i!=null)
            {
               i.setImageBitmap(windows[position].image);
            }
            else
            {
                i = new ImageView(mContext.getApplicationContext());
                i.setImageBitmap(windows[position].image);
                i.setLayoutParams(new GridView.LayoutParams(250, 250));
            }
            return i;
        }
    }
}