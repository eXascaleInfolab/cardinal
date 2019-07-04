    SELECT
        page_title,
        rev_comment,
        rev_user_text,
        rev_timestamp 
    FROM
        revisions 
    WHERE
        rev_comment LIKE '%[[Property:%]]%[[Q%'
    ORDER BY
        rev_id 
    INTO
        OUTFILE 'edits_wikidatawiki-20181001-pages.csv';
