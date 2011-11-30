import cv

img = cv.LoadImage("dots.png", cv.CV_LOAD_IMAGE_COLOR );

tpl = cv.LoadImage("dots_part.png", cv.CV_LOAD_IMAGE_COLOR );

img_width  = img.width;
img_height = img.height;
tpl_width  = tpl.width;
tpl_height = tpl.height;
res_width  = img_width - tpl_width + 1;
res_height = img_height - tpl_height + 1;

res = cv.CreateImage( (res_width, res_height) , cv.IPL_DEPTH_32F, 1 );

cv.MatchTemplate( img, tpl, res, cv.CV_TM_SQDIFF );

minval, maxval, minloc, maxloc = cv.MinMaxLoc( res );

cv.Rectangle( img, 
			 ( minloc[0], minloc[1] ), 
			 ( minloc[0] + tpl_width, minloc[1] + tpl_height ),
			 cv.Scalar( 0, 0, 255, 0 ), 1, 0, 0 );	

cv.NamedWindow( "reference", cv.CV_WINDOW_AUTOSIZE );
cv.NamedWindow( "template", cv.CV_WINDOW_AUTOSIZE );
cv.ShowImage( "reference", img );
cv.ShowImage( "template", tpl );

cv.WaitKey( 0 );

cv.DestroyWindow( "reference" );
cv.DestroyWindow( "template" );
cv.ReleaseImage( img );
cv.ReleaseImage( tpl );
cv.ReleaseImage( res );

