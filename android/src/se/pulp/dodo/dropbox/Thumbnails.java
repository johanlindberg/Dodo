package se.pulp.dodo.dropbox;

import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;

import android.app.ProgressDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.DialogInterface.OnClickListener;
import android.graphics.drawable.Drawable;
import android.os.AsyncTask;
import android.widget.GridView;
import android.widget.Toast;

import com.dropbox.client2.DropboxAPI;
import com.dropbox.client2.DropboxAPI.Entry;
import com.dropbox.client2.DropboxAPI.ThumbFormat;
import com.dropbox.client2.DropboxAPI.ThumbSize;
import com.dropbox.client2.exception.DropboxException;
import com.dropbox.client2.exception.DropboxIOException;
import com.dropbox.client2.exception.DropboxParseException;
import com.dropbox.client2.exception.DropboxPartialFileException;
import com.dropbox.client2.exception.DropboxServerException;
import com.dropbox.client2.exception.DropboxUnlinkedException;

public class Thumbnails extends AsyncTask<Void, Long, Boolean> {
	
	private Context context;
    private final ProgressDialog mDialog;
    private DropboxAPI<?> dropbox;
    private String path;
    private ArrayList<Drawable> drawables = new ArrayList<Drawable>();

    private FileOutputStream fos;

    private boolean canceled;
    private Long numberOfThumbnails;
    private String err = null;
    
    private GridView view;

    public Thumbnails(Context context, DropboxAPI<?> api, String path, GridView view) {
        // We set the context this way so we don't accidentally leak activities
        this.context = context.getApplicationContext();

        this.dropbox = api;
        this.path = path;
        
        this.view = view;

        mDialog = new ProgressDialog(context);
        mDialog.setMessage("Loading " + path);
        mDialog.setButton("Cancel", new OnClickListener() {
            public void onClick(DialogInterface dialog, int which) {
                canceled = true;
                err = "Canceled";

                // This will cancel the getThumbnail operation by closing
                // its stream
                if (fos != null) {
                    try {
                        fos.close();
                    } catch (IOException e) {
                    }
                }
            }
        });

        mDialog.show();
    }

    @Override
    protected Boolean doInBackground(Void... params) {
        try {
            if (canceled) {
                return false;
            }

            // Get the metadata for a directory
            Entry dirent = dropbox.metadata(path, 0, null, true, null);

            if (!dirent.isDir || dirent.contents == null) {
                // It's not a directory, or there's nothing in it
                err = "File or empty directory";
                return false;
            }

            // Make a list of everything in it that we can get a thumbnail for
            ArrayList<Entry> thumbs = new ArrayList<Entry>();
            numberOfThumbnails = new Long(dirent.contents.size());
            for (Entry ent: dirent.contents) {
                if (ent.thumbExists) {
                    // Add it to the list of thumbs we can choose from
                    thumbs.add(ent);

                    String cachePath = context.getDir("Thumbs", Context.MODE_PRIVATE).getAbsolutePath() + ent.path;
                    try {
                    	fos = new FileOutputStream(cachePath);
    		            dropbox.getThumbnail(ent.path, fos, ThumbSize.BESTFIT_480x320, ThumbFormat.JPEG, null);
						fos.close();
                    } catch (FileNotFoundException e) {
                    	err = "Couldn't create a local file to store the image";
                    	return false;
					} catch (IOException e) {
                    	err = "Couldn't create a local file to store the image";
                    	return false;
					}
		            
		            if (canceled) {
		                return false;
		            }
		            
		            Drawable drawable = Drawable.createFromPath(cachePath);
		            drawables.add(drawable);
                }
            }
            
            numberOfThumbnails = new Long(thumbs.size());

        } catch (DropboxUnlinkedException e) {
        	err = "Idiot!";
        } catch (DropboxPartialFileException e) {
            err = "Download canceled";
        } catch (DropboxServerException e) {
            if (e.error == DropboxServerException._304_NOT_MODIFIED) {
            	err = "Not modified";
            } else if (e.error == DropboxServerException._401_UNAUTHORIZED) {
            	err = "Unauthorized";
            } else if (e.error == DropboxServerException._403_FORBIDDEN) {
            	err = "Forbidden";
            } else if (e.error == DropboxServerException._404_NOT_FOUND) {
            	err = "Not found";
            } else if (e.error == DropboxServerException._406_NOT_ACCEPTABLE) {
            	err = "Not acceptable";
            } else if (e.error == DropboxServerException._415_UNSUPPORTED_MEDIA) {
            	err = "Unsupported media";
            } else if (e.error == DropboxServerException._507_INSUFFICIENT_STORAGE) {
            	err = "Insufficient storage";
            } else {
                // Something else
            	err = "whatever!";
            }
            // This gets the Dropbox error, translated into the user's language
            err = e.body.userError;
            if (err == null) {
                err = e.body.error;
            }
        } catch (DropboxIOException e) {
            // Happens all the time, probably want to retry automatically.
            err = "Network error. Try again.";
        } catch (DropboxParseException e) {
            // Probably due to Dropbox server restarting, should retry
            err = "Dropbox error. Try again.";
        } catch (DropboxException e) {
            // Unknown error
            err = "Unknown error. Try again.";
        }
        
        return err == null;
    }

    @Override
    protected void onProgressUpdate(Long... progress) {
        int percent = (int)(100.0*(double)progress[0]/numberOfThumbnails + 0.5);
        mDialog.setProgress(percent);
    }

    @Override
    protected void onPostExecute(Boolean result) {
        mDialog.dismiss();
        if (err == null) {
        	this.view.forceLayout();
        } else {
        	Toast.makeText(context, err, Toast.LENGTH_SHORT).show();	
        }
    }
    
    public ArrayList<Drawable> getDrawables() {
    	return drawables;
    }

}
