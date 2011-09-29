package se.pulp.dodo;

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
    private String err;

    public Thumbnails(Context context, DropboxAPI<?> api, String path) {
        // We set the context this way so we don't accidentally leak activities
        this.context = context.getApplicationContext();

        this.dropbox = api;
        this.path = path;

        mDialog = new ProgressDialog(context);
        mDialog.setMessage("Downloading Images");
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
            for (Entry ent: dirent.contents) {
                if (ent.thumbExists) {
                    // Add it to the list of thumbs we can choose from
                    thumbs.add(ent);
                }
            }

            if (canceled) {
                return false;
            }

            if (thumbs.size() == 0) {
                // No thumbs in that directory
                err = "No pictures in that directory";
                return false;
            }

            // Populate GridView with thumbnails
            for (Entry entry: thumbs) {
            	String cachePath = context.getCacheDir().getAbsolutePath() + "/" + entry.path;
            	try {
            		fos = new FileOutputStream(cachePath);
            	} catch (FileNotFoundException e) {
            		err = "Couldn't create a local file to store the image";
            		return false;
            	}

	            // This downloads a smaller, thumbnail version of the file.  The
	            // API to download the actual file is roughly the same.
	            dropbox.getThumbnail(path, fos, ThumbSize.BESTFIT_960x640, ThumbFormat.JPEG, null);
	            if (canceled) {
	                return false;
	            }
	
	            drawables.add(Drawable.createFromPath(cachePath));
            }
            
            return true;

        } catch (DropboxUnlinkedException e) {
            // The AuthSession wasn't properly authenticated or user unlinked.
        } catch (DropboxPartialFileException e) {
            // We canceled the operation
            err = "Download canceled";
        } catch (DropboxServerException e) {
            // Server-side exception.  These are examples of what could happen,
            // but we don't do anything special with them here.
            if (e.error == DropboxServerException._304_NOT_MODIFIED) {
                // won't happen since we don't pass in revision with metadata
            } else if (e.error == DropboxServerException._401_UNAUTHORIZED) {
                // Unauthorized, so we should unlink them.  You may want to
                // automatically log the user out in this case.
            } else if (e.error == DropboxServerException._403_FORBIDDEN) {
                // Not allowed to access this
            } else if (e.error == DropboxServerException._404_NOT_FOUND) {
                // path not found (or if it was the thumbnail, can't be
                // thumbnailed)
            } else if (e.error == DropboxServerException._406_NOT_ACCEPTABLE) {
                // too many entries to return
            } else if (e.error == DropboxServerException._415_UNSUPPORTED_MEDIA) {
                // can't be thumbnailed
            } else if (e.error == DropboxServerException._507_INSUFFICIENT_STORAGE) {
                // user is over quota
            } else {
                // Something else
            }
            // This gets the Dropbox error, translated into the user's language
            err = e.body.userError;
            if (err == null) {
                err = e.body.error;
            }
        } catch (DropboxIOException e) {
            // Happens all the time, probably want to retry automatically.
            err = "Network error.  Try again.";
        } catch (DropboxParseException e) {
            // Probably due to Dropbox server restarting, should retry
            err = "Dropbox error.  Try again.";
        } catch (DropboxException e) {
            // Unknown error
            err = "Unknown error.  Try again.";
        }
        return false;
    }

    @Override
    protected void onProgressUpdate(Long... progress) {
        int percent = (int)(100.0*(double)progress[0]/numberOfThumbnails + 0.5);
        mDialog.setProgress(percent);
    }

    @Override
    protected void onPostExecute(Boolean result) {
        mDialog.dismiss();
    }
    
    public ArrayList<Drawable> getDrawables() {
    	return drawables;
    }

}
