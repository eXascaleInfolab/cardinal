select page_title, rev_comment, rev_user_text, rev_timestamp from revisions where rev_comment like '%[[Property:%]]%[[Q%'  order by rev_id INTO OUTFILE 'edits.csv';
